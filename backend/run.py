#!/usr/bin/env python3
import os
import sys
from app import create_app

def check_frontend_build():
    """检查前端是否已构建"""
    frontend_dist = os.path.join(os.path.dirname(__file__), '../frontend/dist')
    return os.path.exists(frontend_dist) and os.path.exists(os.path.join(frontend_dist, 'index.html'))

def main():
    # 判断运行环境
    if len(sys.argv) > 1 and sys.argv[1] == 'production':
        config_name = 'production'
        port = 8000
        debug = False
        
        # 检查前端构建
        if not check_frontend_build():
            print("❌ 前端未构建，请先运行: cd frontend && npm run build")
            print("💡 或者使用开发模式: python run.py development")
            return
    else:
        config_name = 'development'
        port = 8000
        debug = True

    # 创建应用实例
    app = create_app(config_name)
    
    # 启动信息
    print("🚀 启动 CLIP 相册搜索应用")
    print(f"📦 环境: {config_name.upper()}")
    print(f"🌐 地址: http://localhost:{port}")
    print(f"🔗 API: http://localhost:{port}/api")
    print(f"❤️  健康检查: http://localhost:{port}/api/health")
    
    if config_name == 'production':
        print("✅ 静态文件服务: 已启用")
    else:
        print("🔧 开发模式: 仅API服务")
        print("💡 前端开发服务器应运行在 http://localhost:3000")
    
    app.run(host='0.0.0.0', port=port, debug=debug)

if __name__ == '__main__':
    main()