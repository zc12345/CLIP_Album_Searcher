import platform
import subprocess
import threading
from flask import Flask, request, g, current_app, jsonify, send_file
from flask_cors import CORS
import os
from PIL import Image
from datetime import datetime

from config import config
from models.album import Album
from utils.utils import convert_results, synchronized
from utils.logger import setup_logger

# 设置HuggingFace镜像
os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'
os.environ['HF_HUB_ENABLE_HF_TRANSFER'] = '1'


_album_lock = threading.Lock()
_album_instance = None

@synchronized(_album_lock)
def get_album_instance():
    """获取或创建album实例（应用上下文单例，线程安全）"""
    global _album_instance
    
    # 首先检查全局实例是否存在
    if _album_instance is not None:
        return _album_instance
    
    # 如果全局实例不存在，检查g对象中是否有实例
    if hasattr(g, 'album_instance'):
        return g.album_instance
    
    # 创建新实例
    current_app.logger.info("Initializing Album instance")
    _album_instance = Album(
        root_path=current_app.config['ROOT_PATH'],
        dump_path=current_app.config['DUMP_PATH'],
        backup_path=current_app.config['BACKUP_PATH'],
        max_workers=current_app.config.get("MAX_WORKERS", 4),
        lang=current_app.config["ALBUM_LANGUAGE"]
    )
    
    # 同时设置到g对象中
    g.album_instance = _album_instance
    
    return _album_instance


def create_app(config_name='default'):
    # 根据配置决定是否启用静态文件服务
    frontend_dist = os.path.join(os.path.dirname(__file__), '../frontend/dist')
    is_production = config_name == 'production'
    has_frontend = is_production and os.path.exists(frontend_dist) and os.path.exists(os.path.join(frontend_dist, 'index.html'))
    
    if has_frontend:
        app = Flask(__name__, 
                    static_folder=frontend_dist,
                    static_url_path='')
        app.logger.info("✅ 生产环境：启用静态文件服务")
    else:
        app = Flask(__name__)
        if is_production:
            app.logger.warning("⚠️  生产环境：前端未构建，仅提供API服务")
        else:
            app.logger.info("🔧 开发环境：仅API服务")
    
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    # 设置日志
    setup_logger(app)
    
    app.logger.info(f"Application started with config: {config_name}")
    app.logger.debug(f"Config details: {dict(app.config)}")
    
    # 启用CORS
    CORS(app, resources={
        r"/api/*": {
            "origins": app.config['CORS_ORIGINS'],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })

    @app.teardown_appcontext
    def teardown_album_instance(exception):
        album_instance = g.pop('album_instance', None)
        if album_instance is not None:
            # 清理资源（如果需要）
            app.logger.debug("Cleaning up Album instance from g object")
            pass

    @app.before_request
    def log_request_info():
        """记录请求信息"""
        app.logger.debug(f'Headers: {dict(request.headers)}')

    # 错误处理
    @app.errorhandler(400)
    def bad_request(error):
        app.logger.warning(f"Bad request: {error}")
        return jsonify({'error': 'Bad request'}), 400
    
    @app.errorhandler(404)
    def not_found(error):
        app.logger.warning(f"Not found: {request.path}")
        return jsonify({'error': 'Not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f"Internal server error: {error}")
        return jsonify({'error': 'Internal server error'}), 500
    
    @app.route('/api/test/log', methods=['GET'])
    def test_log_levels():
        """测试日志级别"""
        app.logger.debug('This is a DEBUG message')
        app.logger.info('This is an INFO message')
        app.logger.warning('This is a WARNING message')
        app.logger.error('This is an ERROR message')
        app.logger.critical('This is a CRITICAL message')
        
        return jsonify({
            'success': True,
            'message': 'Log levels tested',
            'log_level': current_app.config.get('LOG_LEVEL', 'INFO')
        })
    
    # API路由
    @app.route('/api/health', methods=['GET'])
    def health_check():
        """健康检查"""
        app.logger.debug("Health check requested")
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'version': app.config["API_VERSION"]
        })
    
    @app.route('/api/images/random', methods=['GET'])
    def get_random_images():
        """获取随机图片"""
        album = get_album_instance()
        try:
            count = request.args.get('count', 12, type=int)
            count = min(max(count, 1), 50)  # 限制在1-50之间
            
            random_paths = album.get_random_images(count)
            scores_placeholder = [0] * len(random_paths)
            images_data = convert_results(random_paths, scores_placeholder)

            app.logger.info(f"Returned {len(images_data)} random images")
            return jsonify({
                'success': True,
                'data': images_data,
                'count': len(images_data)
            })
            
        except Exception as e:
            app.logger.error(f"Error in get_random_images: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/api/images/search/text', methods=['POST'])
    def text_search():
        """文本搜索"""
        album = get_album_instance()
        try:
            data = request.get_json()
            query = data.get('query', '')
            
            if not query:
                app.logger.warning("Text search called without query")
                return jsonify({
                    'success': False,
                    'error': 'Query is required'
                }), 400
            
            app.logger.info(f"Text search query: '{query}'")
            # 限制参数范围
            k = data.get('k', 8)
            threshold = data.get('threshold', app.config['DEFAULT_THRESHOLD'])
            k = min(max(k, 1), 50)
            threshold = max(min(threshold, 1.0), 0.0)
            
            paths, scores = album.text_search([query], k=k, threshold=threshold)
            results = convert_results(paths, scores)

            app.logger.info(f"Text search found {len(results)} results for query: '{query}'")
            return jsonify({
                'success': True,
                'data': results,
                'query': query,
                'total_results': len(results)
            })
            
        except Exception as e:
            app.logger.error(f"Error in text_search: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
        
    
    @app.route('/api/images/search/image', methods=['POST'])
    def image_search():
        """图像搜索"""
        album = get_album_instance()
        try:
            if 'image' not in request.files:
                app.logger.warning("Image search called without provide image")
                return jsonify({
                    'success': False,
                    'error': 'No image file provided'
                }), 400
            
            file = request.files['image']
            if file.filename == '':
                app.logger.warning("Image search called without selected image")
                return jsonify({
                    'success': False,
                    'error': 'No image selected'
                }), 400
            
            # 获取参数
            k = request.form.get('k', 8, type=int)
            threshold = request.form.get('threshold', app.config['DEFAULT_THRESHOLD'], type=float)
            k = min(max(k, 1), 50)
            threshold = max(min(threshold, 1.0), 0.0)
            
            # 处理上传的图片
            image = Image.open(file.stream)
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # 搜索相似图片
            paths, scores = album.image_search(image, k=k, threshold=threshold)
            results = convert_results(paths, scores)
            
            app.logger.info(f"Image search found {len(results)} results for query")
            return jsonify({
                'success': True,
                'data': results,
                'total_results': len(results)
            })
            
        except Exception as e:
            app.logger.error(f"Error in image_search: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/api/images/stats', methods=['GET'])
    def get_stats():
        """获取统计信息"""
        album = get_album_instance()
        try:
            stats = album.get_stats()
            return jsonify({
                'success': True,
                'data': stats
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/api/album/scan', methods=['POST'])
    def scan_album():
        """扫描相册更新"""
        album = get_album_instance()
        try:
            ret = album.database.update_db()
            if ret is not None:
                msg = f"update {ret} images"
            else:
                msg = "no update"
            return jsonify({
                'success': True,
                'message': f'Album scanned successfully, {msg}'
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    @app.route('/api/images/open-folder', methods=['POST'])
    def open_image_folder():
        """打开图片所在文件夹并选中图片"""
        try:
            data = request.get_json()
            image_path = data.get('path', '')
            
            if not image_path:
                return jsonify({
                    'success': False,
                    'error': 'Image path is required'
                }), 400
            
            if not os.path.exists(image_path):
                return jsonify({
                    'success': False,
                    'error': 'Image path does not exist'
                }), 404
            
            # 获取文件夹路径和文件名
            folder_path = os.path.dirname(image_path)
            file_name = os.path.basename(image_path)
            
            # 根据不同操作系统打开文件夹并选中文件
            system = platform.system()
            file_selected = True
            
            if system == "Windows":
                # Windows: 使用explorer打开文件夹并选中文件
                try:
                    # 确保路径使用双引号包裹，处理空格和特殊字符
                    subprocess.Popen(f'explorer /select,"{os.path.normpath(image_path)}"')
                except Exception as e:
                    app.logger.error(f"Windows explorer error: {e}")
                    # 备用方案：只打开文件夹
                    subprocess.Popen(f'explorer "{os.path.normpath(folder_path)}"')
                    file_selected = False
            
            elif system == "Darwin":  # macOS
                # macOS: 使用open命令打开文件夹并选中文件
                try:
                    subprocess.Popen(["open", "-R", image_path])
                except Exception as e:
                    app.logger.error(f"macOS open error: {e}")
                    # 备用方案：只打开文件夹
                    subprocess.Popen(["open", folder_path])
                    file_selected = False
            
            elif system == "Linux":
                # Linux: 尝试多种文件管理器
                linux_success = False
                file_managers = [
                    ["nautilus", "--select", image_path],      # GNOME
                    ["dolphin", "--select", image_path],       # KDE
                    ["thunar", "--select", image_path],        # XFCE
                    ["caja", "--select", image_path],          # MATE
                    ["nemo", "--select", image_path],          # Cinnamon
                    ["pcmanfm", "--select", image_path],       # LXDE
                ]
                
                for manager_cmd in file_managers:
                    try:
                        # 检查文件管理器是否存在
                        if subprocess.run(["which", manager_cmd[0]], 
                                        capture_output=True).returncode == 0:
                            subprocess.Popen(manager_cmd)
                            linux_success = True
                            break
                    except:
                        continue
                
                if not linux_success:
                    # 如果都不行，只打开文件夹
                    try:
                        subprocess.Popen(["xdg-open", folder_path])
                    except:
                        pass
                    file_selected = False
            
            else:
                return jsonify({
                    'success': False,
                    'error': f'Unsupported operating system: {system}'
                }), 400
            
            message = f'已打开文件夹{f"并选中文件 {file_name}" if file_selected else ""}'
            
            return jsonify({
                'success': True,
                'message': message,
                'folder_path': folder_path,
                'file_name': file_name,
                'file_selected': file_selected,
                'os': system
            })
            
        except Exception as e:
            app.logger.error(f"Open folder error: {e}")
            return jsonify({
                'success': False,
                'error': f'Failed to open folder: {str(e)}'
            }), 500
    
    @app.route('/api/images/original', methods=['GET'])
    def get_original_image():
        """获取原始图片文件"""
        try:
            image_path = request.args.get('path', '')
            
            if not image_path:
                return jsonify({
                    'success': False,
                    'error': 'Image path is required'
                }), 400
            
            # 安全检查：确保路径在允许的目录内
            album = get_album_instance()
            allowed_root = album.database.root_path
            
            # 规范化路径并进行安全检查
            image_path = os.path.abspath(image_path)
            if not image_path.startswith(allowed_root):
                return jsonify({
                    'success': False,
                    'error': 'Access denied: path outside allowed directory'
                }), 403
            
            if not os.path.exists(image_path):
                return jsonify({
                    'success': False,
                    'error': 'Image not found'
                }), 404
            
            if not os.path.isfile(image_path):
                return jsonify({
                    'success': False,
                    'error': 'Path is not a file'
                }), 400
            
            # 检查文件类型（只允许图片文件）
            allowed_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.tiff'}
            file_ext = os.path.splitext(image_path)[1].lower()
            if file_ext not in allowed_extensions:
                return jsonify({
                    'success': False,
                    'error': 'File type not allowed'
                }), 400
            
            # 设置适当的MIME类型
            mime_types = {
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg',
                '.png': 'image/png',
                '.gif': 'image/gif',
                '.bmp': 'image/bmp',
                '.webp': 'image/webp',
                '.tiff': 'image/tiff'
            }
            
            # 发送文件
            return send_file(
                image_path,
                mimetype=mime_types.get(file_ext, 'image/jpeg'),
                as_attachment=False,  # 不作为附件下载
                download_name=os.path.basename(image_path)  # 建议的文件名
            )
            
        except Exception as e:
            app.logger.error(f"Error serving original image: {e}")
            return jsonify({
                'success': False,
                'error': f'Failed to serve image: {str(e)}'
            }), 500

    @app.route('/api/config', methods=['GET'])
    def get_config():
        """获取配置信息"""
        album = get_album_instance()
        return jsonify({
            'success': True,
            'data': {
                'version': app.config["API_VERSION"],
                'root_path': album.database.root_path,
                'dump_path': album.database.dump_path,
                'max_results': app.config['MAX_RESULTS'],
                'default_threshold': app.config['DEFAULT_THRESHOLD']
            }
        })
    
    @app.route('/', methods=['GET'])
    def index():
        """首页"""
        if has_frontend:
            try:
                return app.send_static_file('index.html')
            except:
                # 如果无法加载前端，返回错误信息
                return jsonify({
                    'error': 'Failed to load frontend',
                    'message': 'Frontend build might be missing or corrupted'
                }), 500
        else:
            # 开发环境或生产环境但前端未构建：返回API信息
            return jsonify({
                'message': 'CLIP Album Search API',
                'version': app.config["API_VERSION"],
                'frontend_status': 'not_built' if is_production else 'development_mode',
                'endpoints': {
                    'health': '/api/health',
                    'random_images': '/api/images/random',
                    'text_search': '/api/images/search/text',
                    'image_search': '/api/images/search/image',
                    'stats': '/api/images/stats',
                    'scan_album': '/api/album/scan',
                    'config': '/api/config',
                    'open_folder': '/api/images/open-folder'
                }
            })
    
    # SPA路由处理（仅生产环境且有前端时）
    if has_frontend:
        @app.route('/<path:path>')
        def serve_spa(path):
            # 不处理API路由 - 这些应该已经被前面的路由处理了
            if path.startswith('api/'):
                return jsonify({'error': 'API route not found'}), 404
                
            try:
                # 尝试返回请求的静态文件
                return app.send_static_file(path)
            except:
                # 文件不存在，返回index.html由前端路由处理
                try:
                    return app.send_static_file('index.html')
                except:
                    return jsonify({
                        'error': 'Frontend not available',
                        'message': 'Please build the frontend: cd frontend && npm run build'
                    }), 503
                        
        @app.route('/assets/<path:filename>')
        def serve_assets(filename):
            """服务前端静态资源"""
            frontend_dist = os.path.join(os.path.dirname(__file__), '../frontend/dist')
            assets_path = os.path.join(frontend_dist, 'assets', filename)
            
            # 安全检查
            if not os.path.exists(assets_path) or not os.path.isfile(assets_path):
                return jsonify({'error': 'Asset not found'}), 404
            
            # 根据文件扩展名设置正确的MIME类型
            ext = os.path.splitext(filename)[1].lower()
            mime_types = {
                '.js': 'application/javascript',
                '.css': 'text/css',
                '.png': 'image/png',
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg',
                '.gif': 'image/gif',
                '.svg': 'image/svg+xml',
                '.ico': 'image/x-icon'
            }
            
            mimetype = mime_types.get(ext, 'application/octet-stream')
            
            return send_file(assets_path, mimetype=mimetype)

        # 同时确保vite.svg也能被访问
        @app.route('/vite.svg')
        def serve_vite_svg():
            frontend_dist = os.path.join(os.path.dirname(__file__), '../frontend/dist')
            vite_svg_path = os.path.join(frontend_dist, 'vite.svg')
            
            if os.path.exists(vite_svg_path):
                return send_file(vite_svg_path, mimetype='image/svg+xml')
            return jsonify({'error': 'vite.svg not found'}), 404

    return app

if __name__ == '__main__':
    app = create_app('development')
    try:
        app.logger.info("Starting Flask application")
        app.run(host='0.0.0.0', port=5000, debug=True)
    except Exception as e:
        app.logger.error(f"Failed to start application: {e}")
        raise