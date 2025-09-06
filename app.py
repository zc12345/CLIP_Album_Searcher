import os
import argparse
import json
import random
from PIL import Image
import numpy as np
import streamlit as st

from album import Album

@st.cache_resource
def get_album(root_path, dump_path, backup_path):
    album = Album(root_path, dump_path, backup_path)
    return album

# 兼容性函数
def rerun_app():
    """兼容不同版本的rerun功能"""
    if hasattr(st, 'rerun'):
        rerun_app()
    elif hasattr(st, 'experimental_rerun'):
        st.experimental_rerun()
    elif hasattr(st.experimental, 'rerun'):
        st.experimental.rerun()
    else:
        # 备用方案：使用JavaScript刷新
        st.markdown("<meta http-equiv='refresh' content='0'>", unsafe_allow_html=True)


def create_image_gallery(images, paths, probs, cols=3, mode="search", album=None):
    """创建图片画廊"""
    if not images:
        return
    
    for i in range(0, len(images), cols):
        cols_images = images[i:i+cols]
        cols_paths = paths[i:i+cols]
        cols_probs = probs[i:i+cols]
        
        cols_container = st.columns(len(cols_images))
        
        for j, (img, path, prob) in enumerate(zip(cols_images, cols_paths, cols_probs)):
            with cols_container[j]:
                if mode == "random":
                    # Random walk模式 - 显示图片和搜索按钮
                    st.image(img, caption="点击下方按钮搜索相似图片", use_container_width=True)
                    # st.image(img, caption="点击下方按钮搜索相似图片")
                    if st.button(f"🔍 搜索相似图片", key=f"search_{i}_{j}", type="primary"):
                        # 按钮被点击，触发相似搜索
                        st.session_state.clicked_image_path = path
                        st.session_state.clicked_image = img
                        st.session_state.mode = "search_from_random"
                        rerun_app()
                else:
                    # 搜索模式 - 显示相似度
                    st.image(img, caption=f"相似度: {prob:.3f}", use_container_width=True)
                    # st.image(img, caption=f"相似度: {prob:.3f}")
                
                # 打开文件夹按钮
                if st.button(f"📁 打开文件夹", key=f"folder_{i}_{j}"):
                    folder_path = os.path.dirname(path)
                    try:
                        os.startfile(folder_path)
                    except:
                        st.error(f"无法打开文件夹: {folder_path}")
                
                # 显示文件名
                st.caption(f"📄 {os.path.basename(path)}")

def get_random_images(album, count=12):
    """获取随机图片"""
    if not album.img_paths:
        return [], []
    
    # 随机选择图片
    random_paths = random.sample(album.img_paths, min(count, len(album.img_paths)))
    random_images = []
    
    for path in random_paths:
        try:
            img = Image.open(path)
            random_images.append(img)
        except:
            continue
    
    return random_images, random_paths

def run(album):
    # 初始化session state
    if 'mode' not in st.session_state:
        st.session_state.mode = "random"
    if 'random_count' not in st.session_state:
        st.session_state.random_count = 12
    if 'clicked_image_path' not in st.session_state:
        st.session_state.clicked_image_path = None
    if 'clicked_image' not in st.session_state:
        st.session_state.clicked_image = None
    
    # 添加CSS样式
    st.markdown("""
    <style>
        .main-header {
            text-align: center;
            color: #1f77b4;
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 1rem;
        }
        .mode-container {
            background-color: #f8f9fa;
            padding: 1.5rem;
            border-radius: 10px;
            margin-bottom: 2rem;
        }
        .search-container {
            background-color: #ffffff;
            padding: 2rem;
            border-radius: 10px;
            margin-bottom: 2rem;
            border: 1px solid #e9ecef;
        }
        .result-container {
            background-color: #ffffff;
            padding: 1rem;
            border-radius: 10px;
            border: 1px solid #e9ecef;
        }
        .random-container {
            background-color: #f8f9fa;
            padding: 1rem;
            border-radius: 10px;
            margin-bottom: 1rem;
        }
        .stButton button {
            background-color: #007bff;
            color: white;
            border: none;
            padding: 0.5rem 1rem;
            border-radius: 5px;
            font-size: 0.9rem;
        }
        .stButton button:hover {
            background-color: #0056b3;
        }
        .mode-button {
            background-color: #28a745 !important;
        }
        .mode-button:hover {
            background-color: #218838 !important;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # 标题
    st.markdown("<h1 class='main-header'>🖼️ CLIP 智能相册搜索</h1>", unsafe_allow_html=True)
    
    # 模式选择区域
    st.markdown("<div class='mode-container'>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("🎲 Random Walk", type="primary" if st.session_state.mode == "random" else "secondary", 
                    key="mode_random", use_container_width=True):
            st.session_state.mode = "random"
            rerun_app()
    
    with col2:
        if st.button("🔍 智能搜索", type="primary" if st.session_state.mode == "search" else "secondary", 
                    key="mode_search", use_container_width=True):
            st.session_state.mode = "search"
            rerun_app()
    
    with col3:
        if st.button("📊 统计信息", type="primary" if st.session_state.mode == "stats" else "secondary", 
                    key="mode_stats", use_container_width=True):
            st.session_state.mode = "stats"
            rerun_app()
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # 根据模式显示不同内容
    if st.session_state.mode == "random":
        # Random Walk 模式
        st.markdown("<div class='random-container'>", unsafe_allow_html=True)
        st.subheader("🎲 Random Walk - 随机探索你的相册")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.write("点击任意图片，自动搜索相似的图片！")
        
        with col2:
            random_count = st.number_input("显示图片数量", min_value=6, max_value=50, value=st.session_state.random_count, step=6)
            if random_count != st.session_state.random_count:
                st.session_state.random_count = random_count
                rerun_app()
        
        if st.button("🔄 换一批", type="primary", use_container_width=True):
            rerun_app()
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # 显示随机图片
        with st.spinner("正在加载随机图片..."):
            random_images, random_paths = get_random_images(album, st.session_state.random_count)
            
            if random_images:
                st.markdown("<div class='result-container'>", unsafe_allow_html=True)
                st.subheader(f"📸 随机图片 (共 {len(random_images)} 张)")
                
                # 创建虚拟的probs列表
                dummy_probs = [0.0] * len(random_images)
                create_image_gallery(random_images, random_paths, dummy_probs, mode="random", album=album)
                
                st.markdown("</div>", unsafe_allow_html=True)
            else:
                st.warning("未找到图片，请检查图片目录设置")
    
    elif st.session_state.mode == "search":
        # 搜索模式
        st.markdown("<div class='search-container'>", unsafe_allow_html=True)
        st.subheader("🔍 智能搜索")
        
        # 搜索模式选择
        search_type = st.radio("选择搜索方式", ["文本搜索", "图像搜索"], horizontal=True)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            if search_type == "文本搜索":
                query = st.text_input("输入文本描述", placeholder="例如：一只可爱的小猫、蓝天白云、美丽的风景...")
            else:
                uploaded_file = st.file_uploader("上传一张图像", type=["jpg", "jpeg", "png", "bmp", "gif"])
        
        with col2:
            k = st.number_input("返回图片数量", min_value=1, max_value=50, value=8, step=1)
            threshold = st.slider("相似度阈值", 0.0, 1.0, 0.3, 0.05, help="只显示相似度高于此值的图片")
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # 搜索按钮
        search_button = st.button("🚀 开始搜索", type="primary", use_container_width=True)
        
        # 结果显示区域
        if search_button:
            if search_type == "文本搜索" and query:
                with st.spinner("正在搜索中..."):
                    paths, probs = album.text_search([query], k)
                    # 过滤结果
                    filtered_paths = []
                    filtered_probs = []
                    for path, prob in zip(paths, probs):
                        if prob >= threshold:
                            filtered_paths.append(path)
                            filtered_probs.append(prob)
                    
                    if filtered_paths:
                        st.markdown("<div class='result-container'>", unsafe_allow_html=True)
                        st.subheader(f"📸 搜索结果 (找到 {len(filtered_paths)} 张图片)")
                        st.success(f"搜索完成！找到 {len(filtered_paths)} 张相似图片")
                        
                        # 加载图片
                        images = []
                        for path in filtered_paths:
                            try:
                                img = Image.open(path)
                                images.append(img)
                            except:
                                continue
                        
                        # 创建图片画廊
                        create_image_gallery(images, filtered_paths, filtered_probs, mode="search")
                        st.markdown("</div>", unsafe_allow_html=True)
                    else:
                        st.warning("未找到符合条件的图片，请尝试降低相似度阈值或修改搜索词")
                        
            elif search_type == "图像搜索" and uploaded_file is not None:
                with st.spinner("正在搜索中..."):
                    image = Image.open(uploaded_file)
                    st.image(image, caption="上传的图片", use_container_width=True)
                    # st.image(image, caption="上传的图片")
                    img = Image.fromarray(np.array(image).astype('uint8'), 'RGB')
                    paths, probs = album.image_search(img, k)
                    
                    # 过滤结果
                    filtered_paths = []
                    filtered_probs = []
                    for path, prob in zip(paths, probs):
                        if prob >= threshold:
                            filtered_paths.append(path)
                            filtered_probs.append(prob)
                    
                    if filtered_paths:
                        st.markdown("<div class='result-container'>", unsafe_allow_html=True)
                        st.subheader(f"📸 搜索结果 (找到 {len(filtered_paths)} 张图片)")
                        st.success(f"搜索完成！找到 {len(filtered_paths)} 张相似图片")
                        
                        # 加载图片
                        images = []
                        for path in filtered_paths:
                            try:
                                img = Image.open(path)
                                images.append(img)
                            except:
                                continue
                        
                        # 创建图片画廊
                        create_image_gallery(images, filtered_paths, filtered_probs, mode="search")
                        st.markdown("</div>", unsafe_allow_html=True)
                    else:
                        st.warning("未找到符合条件的图片，请尝试降低相似度阈值")
                        
            else:
                st.error("请输入搜索文本或上传图片")
    
    elif st.session_state.mode == "stats":
        # 统计信息模式
        st.markdown("<div class='result-container'>", unsafe_allow_html=True)
        st.subheader("📊 相册统计信息")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("总图片数", len(album.img_paths))
        
        with col2:
            st.metric("特征向量", album.db_features.shape[0])
        
        with col3:
            st.metric("特征维度", album.db_features.shape[1])
        
        with col4:
            if album.img_paths:
                total_size = sum(os.path.getsize(path) for path in album.img_paths if os.path.exists(path))
                st.metric("总大小", f"{total_size / (1024*1024):.1f} MB")
            else:
                st.metric("总大小", "0 MB")
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    # 处理从random walk点击图片后的搜索
    if st.session_state.mode == "search_from_random" and st.session_state.clicked_image_path:
        st.markdown("<div class='result-container'>", unsafe_allow_html=True)
        st.subheader("🔍 基于选中图片的相似搜索")
        
        # 显示选中的图片
        if st.session_state.clicked_image:
            st.image(st.session_state.clicked_image, caption="选中的图片", use_container_width=True)
            # st.image(st.session_state.clicked_image, caption="选中的图片")
        
        # 搜索相似图片
        with st.spinner("正在搜索相似图片..."):
            img = Image.fromarray(np.array(st.session_state.clicked_image).astype('uint8'), 'RGB')
            paths, probs = album.image_search(img, 12)
            
            # 过滤结果
            filtered_paths = []
            filtered_probs = []
            for path, prob in zip(paths, probs):
                if prob >= 0.2:  # 设置一个合理的阈值
                    filtered_paths.append(path)
                    filtered_probs.append(prob)
            
            if filtered_paths:
                st.success(f"找到 {len(filtered_paths)} 张相似图片")
                
                # 加载图片
                images = []
                for path in filtered_paths:
                    try:
                        img = Image.open(path)
                        images.append(img)
                    except:
                        continue
                
                # 创建图片画廊
                create_image_gallery(images, filtered_paths, filtered_probs, mode="search")
            else:
                st.warning("未找到相似的图片")
        
        # 返回按钮
        if st.button("🔙 返回Random Walk", type="secondary"):
            st.session_state.mode = "random"
            st.session_state.clicked_image_path = None
            st.session_state.clicked_image = None
            rerun_app()
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    # 使用说明
    with st.expander("📖 使用说明"):
        st.markdown("""
        **功能特点：**
        - 🎲 **Random Walk**: 随机展示图片，点击图片自动搜索相似图片
        - 🔍 **智能搜索**: 支持文本和图像搜索
        - 📊 **统计信息**: 查看相册的基本统计信息
        - 📁 **打开文件夹**: 点击按钮直接跳转到图片所在位置
        
        **使用步骤：**
        1. **Random Walk模式**: 点击"换一批"获取新的随机图片，点击任意图片搜索相似图片
        2. **搜索模式**: 输入文本或上传图片进行搜索
        3. **统计模式**: 查看相册的基本信息和统计数据
        """)
        
def load_config(config_path):
    """加载配置文件"""
    default_config = {
        "root_path": "D:\\documents\\images",
        "dump_path": "db.pt",
        "backup_path": "backup",
        "host": "localhost",
        "port": 8501,
        "model_name": "ViT-B-32",
        "pretrained": "laion2b_s34b_b79k",
        "max_results": 20,
        "default_threshold": 0.0
    }
    
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                # 合并默认配置
                default_config.update(config)
        except Exception as e:
            print(f"配置文件加载失败，使用默认配置: {e}")
    
    return default_config

if __name__ == "__main__":
    # 定义模型参数
    parser = argparse.ArgumentParser()
    parser.add_argument("--root_path", type=str, help="图片根目录路径")
    parser.add_argument("--dump_path", type=str, help="特征向量数据库路径")
    parser.add_argument("--backup_path", type=str, help="备份路径")
    parser.add_argument("--config", type=str, default="config.json", help="配置文件路径")
    args = parser.parse_args()
    
    # 加载配置
    config = load_config(args.config)
    
    # 命令行参数优先于配置文件
    root_path = args.root_path if args.root_path else config["root_path"]
    dump_path = args.dump_path if args.dump_path else config["dump_path"]
    backup_path = args.backup_path if args.backup_path else config["backup_path"]
    
    print(f"启动参数:")
    print(f"  图片目录: {root_path}")
    print(f"  数据库: {dump_path}")
    print(f"  备份目录: {backup_path}")
    
    # 验证路径
    if not os.path.exists(root_path):
        print(f"警告: 图片目录不存在: {root_path}")
        print("请修改配置文件中的 root_path 路径")
        # 设置页面样式
    st.set_page_config(
        page_title="CLIP 相册搜索",
        page_icon="🖼️",
        layout="wide"
    )

    album = get_album(root_path, dump_path, backup_path)
    run(album)