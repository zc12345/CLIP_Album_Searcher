import os
import time
from PIL import Image
from models.utils import glob_all_images, get_device
import torch
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
from contextlib import contextmanager
from loguru import logger
import functools
from models.model import get_model

@functools.lru_cache(maxsize=1)
def get_database(root_path, dump_path=None, backup_path="backup", max_workers=4, lang="en"):
    return DataBase(
        root_path=root_path,
        dump_path=dump_path,
        backup_path=backup_path,
        max_workers=max_workers,
        lang=lang,
    )


class DataBase:
    def __init__(self, root_path, dump_path=None, backup_path="backup", max_workers=4, lang="en"):
        self.root_path = root_path
        self.dump_path = dump_path
        self.backup_path = backup_path
        self.set_max_workers(max_workers)
        self.database_lang = lang

        self.device = get_device()
        logger.info(f"使用设备: {self.device}")

        self.img_paths = []
        self.ignore_paths = set()
        self.db_features = torch.empty(0)
        self.thread_local = threading.local()
        self.ignore_paths_lock = threading.Lock()

        self.allow_cleanup_invalid_paths = True
        self.allow_update_new_paths = True
        
        # 创建备份目录
        if not os.path.exists(self.backup_path):
            os.makedirs(self.backup_path, exist_ok=True)
        
        # 加载现有数据库
        if os.path.exists(self.dump_path):
            self.load_db_features(self.dump_path)

        self.update_db()

    def get_paths(self):
        return self.img_paths
    
    def get_features(self):
        return self.db_features

    @contextmanager
    def thread_model(self):
        """上下文管理器用于线程模型管理"""
        thread_id = threading.get_ident()
        if not hasattr(self.thread_local, 'model'):
            # 初始化线程本地模型
            model, preprocess = get_model(device=self.device, lang=self.database_lang)
            self.thread_local.model = model
            self.thread_local.preprocess = preprocess
            logger.debug(f"Initialized model for thread {thread_id}")
        
        try:
            yield self.thread_local.model, self.thread_local.preprocess
        finally:
            # 可选的清理代码
            if torch.cuda.is_available():
                torch.cuda.empty_cache()

    def get_invalid_indices_multi_thread(self):
        invalid_indices = []
        total_paths = len(self.img_paths)
        
        def check_path_exists(args):
            idx, img_path = args
            exists = os.path.exists(img_path)
            return idx, img_path, exists
        
        check_tasks = [(idx, img_path) for idx, img_path in enumerate(self.img_paths)]
        
        with ThreadPoolExecutor(max_workers=min(self.max_workers, 8)) as executor:
            futures = [executor.submit(check_path_exists, task) for task in check_tasks]
            
            completed = 0
            for future in as_completed(futures):
                try:
                    idx, img_path, exists = future.result()
                    if not exists:
                        invalid_indices.append(idx)
                    
                    completed += 1
                    if completed % 10000 == 0:
                        logger.info(f"Path validation progress: {completed}/{total_paths}")
                        
                except Exception as e:
                    logger.error(f"Error checking path {img_path}: {e}")
        return invalid_indices

    def get_invalid_indices(self):
        logger.info("Checking for invalid paths in database...")
        
        if not self.img_paths:
            return []
        if len(self.img_paths) < 1e4:
            invalid_indices = []
            for idx, img_path in enumerate(self.img_paths):
                if not os.path.exists(img_path):
                    invalid_indices.append(idx)
        else:
            invalid_indices = self.get_invalid_indices_multi_thread()
        return invalid_indices

    def cleanup_invalid_paths(self):
        """清理数据库中已不存在的文件路径"""            
        invalid_indices = self.get_invalid_indices()        
        if invalid_indices:
            invalid_indices.sort(reverse=True)
            logger.info(f"Found {len(invalid_indices)} invalid paths, removing...")
            
            # 从大到小排序索引，以便从后往前删除
            invalid_indices.sort(reverse=True)
            
            # 更新图片路径列表
            self.img_paths = [self.img_paths[i] for i in range(len(self.img_paths)) if i not in invalid_indices]
            
            # 更新特征张量
            if len(self.db_features) > 0:
                valid_features = []
                for i in range(len(self.db_features)):
                    if i not in invalid_indices:
                        valid_features.append(self.db_features[i].unsqueeze(0))
                
                if valid_features:
                    self.db_features = torch.cat(valid_features, dim=0)
                else:
                    self.db_features = torch.empty(0)
                logger.debug(f"valid features={self.db_features.shape}, valid_paths={len(self.img_paths)}, invalid_paths={len(invalid_indices)}, invalid_indices={invalid_indices}")
            
            logger.info(f"Removed {len(invalid_indices)} invalid paths from database")
        else:
            logger.info("No invalid paths found in database")
        return len(invalid_indices)

    def ensure_features_normalized(self):
        """确保所有特征向量都已归一化"""
        if len(self.db_features) > 0:
            norms = self.db_features.norm(dim=-1)
            if not torch.allclose(norms, torch.ones_like(norms), atol=1e-6):
                self.db_features /= self.db_features.norm(dim=-1, keepdim=True)
                logger.info("Normalized database features")

    def update_new_paths(self, root_path=None, use_multithreading=True):
        if root_path is None:
            root_path = self.root_path

        
        new_img_paths = self.get_update_img_paths(root_path)
        if use_multithreading and len(new_img_paths) > 100:
            new_img_paths, new_db_features = self.load_and_extract_multi_thread(new_img_paths)
        else:
            new_img_paths, new_db_features = self.load_and_extract_single_thread(new_img_paths)
        
        if not (len(new_db_features) == len(new_img_paths)):
            logger.error(f"features num={len(new_db_features)}, img num={len(new_img_paths)}, stop update database")
            return 0

        if len(new_img_paths) == 0:
            return 0
        
        self.img_paths += new_img_paths
        self.db_features = torch.cat([self.db_features, new_db_features], dim=0)
        return len(new_img_paths)
    
    def update_db(self):
        """更新数据库"""
        invalid_num = 0
        updated_num = 0

        if self.allow_cleanup_invalid_paths:
            invalid_num = self.cleanup_invalid_paths()
        if self.allow_update_new_paths:
            updated_num = self.update_new_paths()

        if (self.allow_cleanup_invalid_paths or self.allow_update_new_paths) and (invalid_num > 0 or updated_num > 0):
            self.update_mapping()
            self.dump_db_features(self.dump_path)
        else:
            logger.info(f"ignore update")
        return updated_num + invalid_num
    
    @functools.lru_cache(maxsize=1)
    def get_update_img_paths(self, root_path):
        """获取需要更新的图片路径"""
        img_paths = glob_all_images(root_path)
        new_img_paths = [img_path for img_path in img_paths if img_path not in set(self.img_paths)]
        logger.info(f"Found {len(img_paths)} images, {len(self.img_paths)} images in db, {len(new_img_paths)} new images")
        return new_img_paths
    
    def extract_clip_features(self, image_path):
        """提取图片特征"""
        try:
            with self.thread_model() as (model, preprocess):
                image = preprocess(Image.open(image_path)).unsqueeze(0)
                with torch.no_grad():
                    image_features = model.encode_image(image)
                image_features /= image_features.norm(dim=-1, keepdim=True)
                return image_features
        except Exception as e:
            logger.error(f"Error extracting features from {image_path}: {e}")
            logger.info(f"add to ignore paths: {image_path}")
            with self.ignore_paths_lock:  # 线程安全
                self.ignore_paths.add(image_path)
            return None
    
    def load_and_extract_single_thread(self, new_img_paths):
        """单线程版本的特征提取"""
        extracted_paths = []
        extracted_features = []
        
        if new_img_paths:
            logger.info(f"Extracting features for {len(new_img_paths)} new images (single-threaded)...")
            start_time = time.time()
            
            for img_path in new_img_paths:
                if img_path in self.ignore_paths:
                    logger.debug(f"ignore {img_path}")
                    continue
                feature = self.extract_clip_features(img_path)
                if feature is not None:
                    extracted_features.append(feature)
                    extracted_paths.append(img_path)
            
            if extracted_features:
                extracted_features = torch.cat(extracted_features, dim=0)
                elapsed_time = time.time() - start_time
                logger.info(f"Successfully extracted features for {len(extracted_features)} images in {elapsed_time:.2f}s")
            else:
                extracted_features = torch.empty(0)
        
        return extracted_paths, extracted_features
    
    def load_and_extract_multi_thread(self, new_img_paths):
        """多线程版本的特征提取"""
        extracted_paths = []
        extracted_features = []
        
        if new_img_paths:
            logger.info(f"Extracting features for {len(new_img_paths)} new images (multi-threaded, {self.max_workers} workers)...")
            start_time = time.time()
            
            # 使用线程池并行处理
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                # 提交所有任务
                future_to_path = {
                    executor.submit(self.extract_clip_features, img_path): img_path 
                    for img_path in new_img_paths
                }
                
                # 收集结果
                completed_count = 0
                for future in as_completed(future_to_path):
                    img_path = future_to_path[future]
                    try:
                        feature = future.result()
                        if feature is not None:
                            extracted_features.append(feature)
                            extracted_paths.append(img_path)
                        
                        completed_count += 1
                        if completed_count % 100 == 0:
                            logger.info(f"Progress: {completed_count}/{len(new_img_paths)} images processed")
                            
                    except Exception as e:
                        logger.error(f"Error processing {img_path}: {e}")
            
            if extracted_features:
                extracted_features = torch.cat(extracted_features, dim=0)
                elapsed_time = time.time() - start_time
                logger.info(f"Successfully extracted features for {len(extracted_features)} images in {elapsed_time:.2f}s (multi-threaded)")
            else:
                extracted_features = torch.empty(0)
        
        return extracted_paths, extracted_features

    def update_mapping(self):
        """更新路径-索引映射关系"""
        self.path_to_index = {path: idx for idx, path in enumerate(self.img_paths)}
        self.index_to_path = {idx: path for idx, path in enumerate(self.img_paths)}

    def get_feature_by_path(self, img_path):
        """根据图片路径获取对应的特征向量"""
        if img_path in self.path_to_index:
            index = self.path_to_index[img_path]
            if index < len(self.db_features):
                return self.db_features[index]
        return None

    def get_path_by_index(self, index):
        """根据索引获取图片路径"""
        if index in self.index_to_path:
            return self.index_to_path[index]
        return None

    def get_index_by_path(self, img_path):
        """根据路径获取索引"""
        return self.path_to_index.get(img_path, -1)
    
    def dump_db_features(self, dump_path):
        """保存特征数据库"""
        try:
            # 备份现有数据库
            if os.path.exists(dump_path):
                import datetime
                import shutil

                backup_name = f"db_backup_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.pt"
                backup_path = os.path.join(self.backup_path, backup_name)
                shutil.copy2(dump_path, backup_path)
                logger.info(f"Backed up existing database to {backup_path}")
            
            # 保存新数据库
            torch.save({
                'img_paths': self.img_paths,
                'features': self.db_features,
                'path_to_index': self.path_to_index,  # 保存映射
                'index_to_path': self.index_to_path,   # 保存映射
                'ignore_paths': list(self.ignore_paths)
            }, dump_path)
            logger.info(f"Saved database to {dump_path}")
        except Exception as e:
            logger.error(f"Error saving database: {e}")
    
    def load_db_features(self, dump_path):
        """加载特征数据库"""
        try:
            data = torch.load(dump_path, map_location='cpu')
            self.img_paths = data['img_paths']
            self.db_features = data['features']
            self.ensure_features_normalized()

            # 加载映射关系，如果不存在则重新创建
            if 'path_to_index' in data and 'index_to_path' in data:
                self.path_to_index = data['path_to_index']
                self.index_to_path = data['index_to_path']
            else:
                # 向后兼容：如果旧版本数据没有映射，则创建新的
                self.update_mapping()
                logger.info("Created new path-index mapping for legacy data")
            
            if 'ignore_paths' in data:
                self.ignore_paths = set(data['ignore_paths'])
 
            logger.info(f"Loaded database with {len(self.img_paths)} images")
        except Exception as e:
            logger.error(f"Error loading database: {e}")
            self.img_paths = []
            self.db_features = torch.empty(0)
            self.ignore_paths = set()
    
    def set_max_workers(self, max_workers):
        """设置最大线程数"""
        self.max_workers = max(1, min(max_workers, 8))  # 限制在1-8之间
        logger.info(f"Max workers set to {self.max_workers}")
    

if __name__ == "__main__":
    db = DataBase(
        root_path="D:\documents\images",
        dump_path="db_zh.pt",
        lang="zh-cn"
    )
    # db = DataBase(
    #     root_path="E:\\album\se",
    #     dump_path="db_zh_disk.pt",
    #     lang="zh-cn"
    # )