import os
import random
import torch
from loguru import logger

from models.utils import get_indices_by_threshold, get_topk_indices, get_device
from models.model import get_model, get_tokenizer
from models.database import get_database, DataBase


class Album:
    def __init__(self, root_path, dump_path=None, backup_path="backup", max_workers=4, lang="en"):
        self.database: DataBase = get_database(
            root_path=root_path,
            dump_path=dump_path,
            backup_path= backup_path,
            max_workers=max_workers,
            lang=lang
        )
        self.db_paths = self.database.get_paths()
        self.db_features = self.database.get_features()

        self.device = get_device()
        logger.info(f"使用设备: {self.device}")

        self.model, self.preprocess = get_model(self.device, lang=lang)
        self.tokenizer = get_tokenizer(lang=lang)
    
    def query_clip_features(self, query_feature: torch.Tensor):
        """查询特征相似度"""
        query_feature /= query_feature.norm(dim=-1, keepdim=True)
        # 使用归一化的数据库特征
        db_features_norm = self.db_features / self.db_features.norm(dim=-1, keepdim=True)
        similarity = query_feature @ db_features_norm.T
    
        probs = (100.0 * similarity).softmax(dim=-1)
        return probs
    
    def text_search(self, queries, k=20, threshold=0.0):
        """文本搜索"""
        try:
            # 编码文本
            text_tokens = self.tokenizer(queries)
            with torch.no_grad():
                text_features = self.model.encode_text(text_tokens)
            
            # 查询相似度
            probs = self.query_clip_features(text_features)
            
            # 获取结果
            if threshold > 0:
                indices = get_indices_by_threshold(probs, threshold)
                k = min(len(indices), k)
                indices = indices[:k]
            else:
                indices = get_topk_indices(probs, k)
            
            # 返回结果
            paths = [self.db_paths[i] for i in indices if i < len(self.db_paths)]
            scores = [probs[0][i].item() for i in indices if i < len(self.db_paths)]
            
            return paths, scores
        except Exception as e:
            logger.error(f"Error in text search: {e}")
            return [], []
    
    def image_search(self, image, k=20, threshold=0.0):
        """图像搜索"""
        try:
            # 提取图像特征
            image_tensor = self.preprocess(image).unsqueeze(0)
            with torch.no_grad():
                image_features = self.model.encode_image(image_tensor)
            
            # 查询相似度
            probs = self.query_clip_features(image_features)
            
            # 获取结果
            if threshold > 0:
                indices = get_indices_by_threshold(probs, threshold)
                k = min(len(indices), k)
                indices = indices[:k]
            else:
                indices = get_topk_indices(probs, k)
            
            # 返回结果
            paths = [self.db_paths[i] for i in indices if i < len(self.db_paths)]
            scores = [probs[0][i].item() for i in indices if i < len(self.db_paths)]
            
            return paths, scores
        except Exception as e:
            logger.error(f"Error in image search: {e}")
            return [], []
    
    def get_random_images(self, count=12):
        """获取随机图片"""
        if not self.db_paths:
            return [], []
        
        random_paths = random.sample(self.db_paths, min(count, len(self.db_paths)))
        return random_paths
    
    def get_stats(self):
        """获取统计信息"""
        total_images = len(self.db_paths)
        feature_count = self.db_features.shape[0] if self.db_features.shape[0] > 0 else 0
        feature_dim = self.db_features.shape[1] if self.db_features.ndim > 1 else 0
        
        # 计算总大小
        total_size = 0
        for path in self.db_paths:
            if os.path.exists(path):
                try:
                    total_size += os.path.getsize(path)
                except:
                    pass
        
        return {
            'total_images': total_images,
            'feature_count': feature_count,
            'feature_dim': feature_dim,
            'total_size_mb': round(total_size / (1024 * 1024), 1),
            'total_size_gb': round(total_size / (1024 * 1024 * 1024), 1),
        }
    
if __name__ == "__main__":
    album = Album(
        root_path="D:\documents\images",
        dump_path="db_zh.pt",
        lang="zh-cn"
    )