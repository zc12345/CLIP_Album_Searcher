import os
from PIL import Image
import io
import base64
import threading
from functools import wraps

def synchronized(lock):
    """同步装饰器，确保线程安全"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            with lock:
                return func(*args, **kwargs)
        return wrapper
    return decorator


def convert_results(paths, scores):
    # 转换结果
    results = []
    for path, score in zip(paths, scores):
        try:
            with Image.open(path) as img:
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                img.thumbnail((400, 400), Image.Resampling.LANCZOS)
                
                buffer = io.BytesIO()
                img.save(buffer, format='JPEG', quality=85)
                img_base64 = base64.b64encode(buffer.getvalue()).decode()
                
                results.append({
                    'path': path,
                    'filename': os.path.basename(path),
                    'score': round(score, 4),
                    'image_data': f'data:image/jpeg;base64,{img_base64}'
                })
        except Exception as e:
            print(f"Error processing image {path}: {e}")
            continue
    return results
