import os
import argparse
from PIL import Image
import numpy as np
import streamlit as st

from album import Album

@st.cache_resource
def get_album(root_path, dump_path, backup_path):
    album = Album(root_path, dump_path, backup_path)
    return album

def run(album):
    st.title("webui")
    st.write("上传一张图像或输入一个文本查询")

    # 输入区域
    query = st.text_input("输入文本查询")
    uploaded_file = st.file_uploader("上传一张图像", type=["jpg", "jpeg", "png"])
    k = st.slider("选择最多展示多少张图片", 0, 20, 5, 1)

    # 处理输入并输出结果
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image", use_column_width=True)
        img = Image.fromarray(np.array(image).astype('uint8'), 'RGB')
        paths, probs = album.image_search(img, k)
        for i, (path, prob) in enumerate(zip(paths, probs)):
            img = Image.open(path)
            st.image(img, caption=f"{i} path:{path}, prob={prob}", use_column_width=True)
    elif query:
        paths, probs = album.text_search([query], k)
        for i, (path, prob) in enumerate(zip(paths, probs)):
            img = Image.open(path)
            st.image(img, caption=f"{i} path:{path}, prob={prob}", use_column_width=True)
    else:
        st.text("请上传一张图像或输入一个文本查询相似的图像")
        
if __name__ == "__main__":
    # 定义模型参数
    parser = argparse.ArgumentParser()
    parser.add_argument("--root_path", type=str, default="D:\documents\images")
    parser.add_argument("--dump_path", type=str, default="db.pt")
    parser.add_argument("--backup_path", type=str, default="backup")
    args = parser.parse_args()
    
    album = get_album(args.root_path, args.dump_path, args.backup_path)
    
    run(album)