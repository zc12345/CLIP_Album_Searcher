import requests
import os
import time
from functools import wraps

# 计时装饰器
def timer(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"⏰ 耗时: {elapsed_time:.3f} 秒")
        return result
    return wrapper

# API基础URL
BASE_URL = "http://localhost:5000/api"

@timer
def test_health_check():
    """测试健康检查"""
    print("=== 测试健康检查 ===")
    response = requests.get(f"{BASE_URL}/health")
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.json()}")
    print()

@timer
def test_get_random_images():
    """测试获取随机图片"""
    print("=== 测试获取随机图片 ===")
    params = {'count': 5}
    response = requests.get(f"{BASE_URL}/images/random", params=params)
    print(f"状态码: {response.status_code}")
    data = response.json()
    print(f"获取到 {len(data.get('data', []))} 张图片")
    print(f"第一张图片信息: {data.get('data', [{}])[0].get('filename') if data.get('data') else '无数据'}")
    print()

@timer
def test_text_search():
    """测试文本搜索"""
    print("=== 测试文本搜索 ===")
    payload = {
        'query': 'a picture of cat',
        'k': 5,
        'threshold': 0.01
    }
    headers = {'Content-Type': 'application/json'}
    response = requests.post(f"{BASE_URL}/images/search/text", 
                           json=payload, 
                           headers=headers)
    print(f"状态码: {response.status_code}")
    data = response.json()
    print(f"搜索查询: {data.get('query')}")
    print(f"找到 {data.get('total_results', 0)} 个结果")
    if data.get('data'):
        for i, result in enumerate(data['data'][:3]):  # 显示前3个结果
            print(f"结果 {i+1}: {result.get('filename')} - 分数: {result.get('score')}")
    print()

@timer
def test_image_search(image_path):
    """测试图像搜索"""
    print("=== 测试图像搜索 ===")
    if not os.path.exists(image_path):
        print(f"图片文件不存在: {image_path}")
        return
    
    # 准备文件和数据
    files = {'image': open(image_path, 'rb')}
    data = {'k': 5, 'threshold': 0.3}
    
    response = requests.post(f"{BASE_URL}/images/search/image", 
                           files=files, 
                           data=data)
    print(f"状态码: {response.status_code}")
    data = response.json()
    print(f"找到 {data.get('total_results', 0)} 个相似图片")
    if data.get('data'):
        for i, result in enumerate(data['data'][:3]):
            print(f"相似结果 {i+1}: {result.get('filename')} - 分数: {result.get('score')}")
    print()

@timer
def test_get_stats():
    """测试获取统计信息"""
    print("=== 测试获取统计信息 ===")
    response = requests.get(f"{BASE_URL}/images/stats")
    print(f"状态码: {response.status_code}")
    data = response.json()
    stats = data.get('data', {})
    print(f"总图片数: {stats.get('total_images', 0)}")
    print(f"特征数量: {stats.get('feature_count', 0)}")
    print(f"总大小: {stats.get('total_size_mb', 0)} MB")
    print()

@timer
def test_scan_album():
    """测试扫描相册"""
    print("=== 测试扫描相册 ===")
    response = requests.post(f"{BASE_URL}/album/scan")
    print(f"状态码: {response.status_code}")
    data = response.json()
    print(f"扫描结果: {data.get('message')}")
    print()

@timer
def test_get_config():
    """测试获取配置信息"""
    print("=== 测试获取配置信息 ===")
    response = requests.get(f"{BASE_URL}/config")
    print(f"状态码: {response.status_code}")
    data = response.json()
    config = data.get('data', {})
    print(f"根路径: {config.get('root_path')}")
    print(f"最大结果数: {config.get('max_results')}")
    print(f"默认阈值: {config.get('default_threshold')}")
    print()

@timer
def test_index():
    """测试首页"""
    print("=== 测试首页 ===")
    response = requests.get("http://localhost:5000/")
    print(f"状态码: {response.status_code}")
    data = response.json()
    print(f"API信息: {data.get('message')}")
    print(f"可用端点: {list(data.get('endpoints', {}).keys())}")
    print()

def run_all_tests():
    """运行所有测试"""
    print("开始API测试...\n")
    
    try:
        test_health_check()
        test_get_random_images()
        test_text_search()
        test_get_stats()
        test_get_config()
        test_index()
        
        # 图像搜索需要实际图片文件，如果有的话才测试
        test_image_path = "../CLIP.png"  # 替换为您的测试图片路径
        if os.path.exists(test_image_path):
            test_image_search(test_image_path)
        else:
            print("跳过图像搜索测试（测试图片不存在）")
            print()
        
        test_scan_album()
        
    except requests.exceptions.ConnectionError:
        print("无法连接到服务器，请确保Flask应用正在运行")
    except Exception as e:
        print(f"测试过程中发生错误: {e}")

if __name__ == "__main__":
    run_all_tests()