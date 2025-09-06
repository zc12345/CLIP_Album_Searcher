import time
import os
import glob
from tqdm import tqdm
from loguru import logger
from concurrent.futures import ThreadPoolExecutor, as_completed

import torch
from PIL import Image
import open_clip

class Album:
    def __init__(self, root_path, dump_path=None, backup_path="backup", num_workers=4):
        self.root_path = root_path
        self.dump_path = dump_path
        self.backup_path = backup_path
        self.num_workers = num_workers  # 新增：线程数参数
        
        self.model, _, self.preprocess = open_clip.create_model_and_transforms('ViT-B-32', pretrained='laion2b_s34b_b79k')
        self.tokenizer = open_clip.get_tokenizer('ViT-B-32')
        self.img_paths = []
        self.db_features = torch.empty(0)
        
        if not os.path.exists(self.backup_path):
            os.mkdir(self.backup_path)
        if os.path.exists(self.dump_path):
            self.load_db_features(self.dump_path)
        self.update_db(root_path)
            
    def update_db(self, root_path):
        new_img_paths, new_db_features = self.load_and_extract(root_path)
        self.img_paths += new_img_paths
        self.db_features = torch.cat([self.db_features, new_db_features], dim=0)
        self.dump_db_features(self.dump_path)

            
    def glob_all_images(self, root_path):
        img_paths = glob.glob(os.path.join(root_path, "**/*.jpg"), recursive=True) + \
                   glob.glob(os.path.join(root_path, "**/*.png"), recursive=True) + \
                   glob.glob(os.path.join(root_path, "**/*.jpeg"), recursive=True)
        return img_paths
    
    def get_update_img_paths(self, root_path):
        img_paths = self.glob_all_images(root_path)
        new_img_paths = [img_path for img_path in img_paths if img_path not in self.img_paths]
        logger.info(f"Found {len(img_paths)} images, {len(self.img_paths)} images in db, {len(new_img_paths)} new images")
        return new_img_paths

    def extract_clip_features(self, image_path):
        try:
            image = self.preprocess(Image.open(image_path)).unsqueeze(0)
            with torch.no_grad(), torch.cuda.amp.autocast():
                image_features = self.model.encode_image(image)
                image_features /= image_features.norm(dim=-1, keepdim=True)
            return image_path, image_features, None
        except Exception as e:
            return image_path, None, str(e)

    def query_clip_features(self, query_feature):
        query_feature /= query_feature.norm(dim=-1, keepdim=True)
        probs = (100.0 * query_feature @ self.db_features.T).softmax(dim=-1)
        return probs

    def get_topk_indices(self, probs, k):
        indices = torch.argsort(probs, dim=-1, descending=True)
        return indices[0][:k]
    
    def get_indices_by_threshold(self, probs, threshold):
        indices = torch.where(probs > threshold)
        return indices[0]
    
    def search_by_features(self, features, k, threshold):
        probs = self.query_clip_features(features)
        
        if k is not None:
            logger.warning("k is set, threshold will be ignored")
            selected_indices = self.get_topk_indices(probs, k)
        elif threshold is not None and k is None:
            selected_indices = self.get_indices_by_threshold(probs, threshold)
        else:
            logger.error("k and threshold are both None, please set one of them")
            return [], []
        
        selected_probs = probs[0][selected_indices]
        selected_paths = [self.img_paths[i] for i in selected_indices]
        return selected_paths, selected_probs
    
    def text_to_features(self, texts):
        logger.info(f"Searching by text: {texts}")
        text = self.tokenizer(texts)
        with torch.no_grad(), torch.cuda.amp.autocast():
            text_features = self.model.encode_text(text)
        return text_features
    
    def image_to_features(self, image):
        image = self.preprocess(image).unsqueeze(0)
        with torch.no_grad(), torch.cuda.amp.autocast():
            image_features = self.model.encode_image(image)
        return image_features
    
    def text_search(self, texts, k=None, threshold=None):
        text_features = self.text_to_features(texts)
        return self.search_by_features(text_features, k, threshold)
    
    def image_search(self, image, k=None, threshold=None):
        image_features = self.image_to_features(image)
        return self.search_by_features(image_features, k, threshold)

    def load_and_extract(self, root_path):
        """多线程版本的特征提取"""
        new_img_paths = self.get_update_img_paths(root_path)
        if not new_img_paths:
            return [], torch.empty(0)
        
        img_paths = []
        img_features_list = []
        error_count = 0
        
        # 使用ThreadPoolExecutor进行多线程处理
        with ThreadPoolExecutor(max_workers=self.num_workers) as executor:
            # 提交所有任务
            future_to_path = {
                executor.submit(self.extract_clip_features, path): path 
                for path in new_img_paths
            }
            
            # 使用tqdm显示进度
            with tqdm(total=len(new_img_paths), desc="Extracting features") as pbar:
                for future in as_completed(future_to_path):
                    path = future_to_path[future]
                    try:
                        result_path, features, error = future.result()
                        if error:
                            logger.error(f"Error extracting {path}: {error}")
                            error_count += 1
                        else:
                            img_paths.append(result_path)
                            img_features_list.append(features)
                    except Exception as e:
                        logger.error(f"Unexpected error with {path}: {e}")
                        error_count += 1
                    finally:
                        pbar.update(1)
                        pbar.set_postfix(errors=error_count)
        
        logger.info(f"Extraction completed: {len(img_features_list)} success, {error_count} errors")
        
        if img_features_list:
            img_features = torch.cat(img_features_list, dim=0)
        else:
            img_features = torch.empty(0)
            
        return img_paths, img_features
    
    def dump_db_features(self, db_features_path):
        self.clean_db(self.root_path)
        db = {
            "img_paths": self.img_paths,
            "db_features": self.db_features
        }
        torch.save(db, db_features_path)
        
    def load_db_features(self, db_features_path):
        db = torch.load(db_features_path)
        self.db_features, self.img_paths = db["db_features"], db["img_paths"]
    
    def remove_unused_features(self, img_paths):
        unused_indices = [i for i, img_path in enumerate(self.img_paths) if img_path not in img_paths]
        clean_indices = [i for i in range(len(self.img_paths)) if i not in unused_indices]
        unused_img_paths = [self.img_paths[i] for i in unused_indices]
        self.img_paths = [img_path for img_path in self.img_paths if img_path not in unused_img_paths]
        self.db_features = self.db_features[clean_indices]
        logger.info(f"Removed {len(unused_img_paths)} unused features, {len(self.img_paths)} features left")
        if unused_img_paths:
            logger.info(f"Top 10 removed paths: {unused_img_paths[:10]}")
        return unused_img_paths
        
    def backup_db(self):
        # generate a backup file
        local_time = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())
        backup_path = os.path.join(self.backup_path, self.dump_path + '.' + local_time)
        os.rename(self.dump_path, backup_path)
        logger.info(f"create a backup file: {backup_path}")
        
    def clean_db(self, root_path):
        unused_img_paths = self.remove_unused_features(self.glob_all_images(root_path))
        if self.dump_path is not None and len(unused_img_paths) > 0:
            self.backup_db()
            
    
if __name__ == "__main__":
    import matplotlib.pyplot as plt
    root_path = "D:\documents\images"
    
    # 使用多线程，设置线程数为8
    album = Album(root_path, dump_path="db.pt", num_workers=8)
    
    # 测试搜索功能
    paths, probs = album.text_search(["ice cream"], k=3)
    # paths, probs = album.image_search(Image.open("CLIP.png"), k=3)

    for img_path, prob in zip(paths, probs):
        print(f"{img_path}: {prob:.4f}")
        img = Image.open(img_path)
        plt.imshow(img)
        plt.title(f"Similarity: {prob:.4f}")
        plt.show()