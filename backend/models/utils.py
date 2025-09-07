import os
import glob
import torch
from loguru import logger

def get_device():
    """自动检测设备，针对小显存优化"""
    if torch.cuda.is_available():
        # 检查显存大小
        torch.cuda.init()
        if torch.cuda.get_device_properties(0).total_memory < 4 * 1024**3:  # 小于4GB
            logger.warning("检测到小显存GPU，将使用CPU")
            return torch.device("cpu")
        return torch.device("cuda")
    else:
        return torch.device("cpu")

def glob_all_images(root_path, extensions=['*.jpg', '*.jpeg', '*.png', '*.bmp', '*.gif', '*.tiff', '*.webp']):
    """获取所有图片文件"""
    img_paths = []
    
    for ext in extensions:
        img_paths.extend(glob.glob(os.path.join(root_path, "**", ext), recursive=True))
        img_paths.extend(glob.glob(os.path.join(root_path, "**", ext.upper()), recursive=True))
    
    return list(set(img_paths))
    # return list(set(img_paths[:5000]))

def get_topk_indices(probs, k):
    """获取top-k索引"""
    indices = torch.argsort(probs, dim=-1, descending=True)
    return indices[0][:k]

def get_lastk_indices(probs, k):
    """获取last-k索引"""
    indices = torch.argsort(probs, dim=-1, descending=True)
    return indices[0][-k:]

def get_indices_by_threshold(probs, threshold):
    """根据阈值获取索引"""
    indices = torch.where(probs > threshold)
    return indices[1] if len(indices) > 1 else torch.tensor([])

if __name__ == "__main__":
    root_path = "D:\documents\images"
    extensions=['*.jpg', '*.jpeg', '*.png', '*.bmp', '*.gif', '*.tiff', '*.webp']
    img_paths = glob_all_images(root_path, extensions)
    print(f"find {len(img_paths)} imgs")
    