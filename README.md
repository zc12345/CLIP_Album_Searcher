# CLIP 智能相册搜索系统 v1.1

基于 Flask + Vue 的现代化相册搜索系统，支持文本搜索、图像搜索和Random Walk功能。

## 🚀 快速开始

### 系统要求
- Python 3.8+
- Node.js 16+
- 8GB+ 内存

### 一键启动

双击运行 `启动相册搜索_Flask+Vue版.bat` 或 `快速启动.bat` 即可启动系统。

启动后访问：http://localhost:5173

## 🏗️ 架构说明

### 后端 (Flask)
- **框架**: Flask + Flask-CORS
- **AI模型**: OpenAI CLIP (ViT-B-16)
- **数据库**: PyTorch 张量存储
- **API**: RESTful API

### 前端 (Vue 3)
- **框架**: Vue 3 + Composition API
- **UI库**: Element Plus
- **构建工具**: Vite
- **状态管理**: Pinia
- **路由**: Vue Router 4

## 📁 项目结构

```
CLIP_album_search/
├── backend/                    # 后端代码
│   ├── app.py                 # Flask应用入口
│   ├── config.py              # 配置文件
│   ├── models/                # 数据模型
│   │   └── album.py          # 相册搜索核心逻辑
│   ├── requirements.txt       # Python依赖
│   └── .env                   # 环境变量
├── frontend/                   # 前端代码
│   ├── src/
│   │   ├── views/            # 页面组件
│   │   │   ├── RandomWalk.vue
│   │   │   ├── Search.vue
│   │   │   └── Stats.vue
│   │   ├── services/         # API服务
│   │   └── utils/            # 工具函数
│   ├── package.json          # Node.js依赖
│   └── vite.config.js        # Vite配置
├── 启动相册搜索_Flask+Vue版.bat  # 完整启动脚本
├── 快速启动.bat              # 快速启动脚本
└── README.md                 # 说明文档
```

## ✨ 功能特点

### 🎲 Random Walk
- 随机展示相册中的图片
- 点击图片搜索相似图片
- 可调整显示数量

### 🔍 智能搜索
- **文本搜索**: 输入描述性文字搜索图片
- **图像搜索**: 上传图片搜索相似图片
- **智能过滤**: 可设置相似度阈值

### 📊 统计信息
- 相册基本信息统计
- 系统状态监控
- 操作日志记录

### 🎨 现代化界面
- 响应式设计，支持移动端
- 美观的UI界面
- 流畅的用户体验

## 🔧 配置说明

### 后端配置 (backend/.env)
```env
# Flask配置
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=your-secret-key-here

# 相册配置
ROOT_PATH=D:\documents\images    # 图片根目录
DUMP_PATH=db.pt                  # 特征数据库路径
BACKUP_PATH=backup              # 备份目录

# 搜索配置
MAX_RESULTS=50                  # 最大返回结果数
DEFAULT_THRESHOLD=0.3          # 默认相似度阈值

# HuggingFace镜像
HF_ENDPOINT=https://hf-mirror.com
HF_HUB_ENABLE_HF_TRANSFER=True
```

## 📖 API文档

### 健康检查
```
GET /api/health
```

### 获取随机图片
```
GET /api/images/random?count=12
```

### 文本搜索
```
POST /api/images/search/text
Content-Type: application/json

{
  "query": "一只可爱的小猫",
  "k": 20,
  "threshold": 0.3
}
```

### 图像搜索
```
POST /api/images/search/image
Content-Type: multipart/form-data

image: [图片文件]
k: 20
threshold: 0.3
```

### 获取统计信息
```
GET /api/images/stats
```

## 🛠️ 开发说明

### 后端开发
```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

### 前端开发
```bash
cd frontend
npm install
npm run dev
```

### 构建部署
```bash
cd frontend
npm run build
```

## 🔄 版本对比

| 功能 | Streamlit版本 | Flask+Vue版本 |
|------|-------------|---------------|
| 界面美观度 | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 交互体验 | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 响应速度 | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| 可维护性 | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| 扩展性 | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| 部署难度 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |

## 🐛 常见问题

### 1. 后端启动失败
- 检查Python环境是否正确安装
- 确认虚拟环境是否创建成功
- 检查依赖是否安装完整

### 2. 前端启动失败
- 检查Node.js环境是否正确安装
- 确认npm依赖是否安装完整
- 检查端口5173是否被占用

### 3. 图片加载失败
- 检查backend/.env中的ROOT_PATH配置
- 确认图片目录是否存在
- 检查图片格式是否支持

### 4. 搜索功能异常
- 确认后端服务正常运行
- 检查HuggingFace镜像设置
- 查看后端日志排查问题

## 📄 许可证

本项目采用MIT许可证，详见LICENSE文件。

## 🤝 贡献

欢迎提交Issue和Pull Request来改进这个项目！

---

**注意**: 首次运行时会下载CLIP模型，请确保网络连接正常。如果下载失败，请检查HuggingFace镜像设置。