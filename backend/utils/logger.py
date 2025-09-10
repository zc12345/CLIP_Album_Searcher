from flask import request
import os
import logging
from logging.handlers import RotatingFileHandler

def setup_logger(app):
    """设置应用日志"""
    
    # 创建日志目录
    log_dir = app.config.get('LOG_DIR', 'logs')
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # 设置日志格式
    formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 清除现有的处理器
    app.logger.handlers.clear()
    
    # 设置应用日志级别
    log_level = getattr(logging, app.config.get('LOG_LEVEL', 'INFO').upper())
    app.logger.setLevel(log_level)
    
    # 文件处理器 - 按大小轮转
    file_handler = RotatingFileHandler(
        filename=os.path.join(log_dir, 'flask_app.log'),
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=10,
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(log_level)
    
    # 错误文件处理器 - 只记录错误
    error_file_handler = RotatingFileHandler(
        filename=os.path.join(log_dir, 'flask_errors.log'),
        maxBytes=5 * 1024 * 1024,  # 5MB
        backupCount=5,
        encoding='utf-8'
    )
    error_file_handler.setFormatter(formatter)
    error_file_handler.setLevel(logging.ERROR)
    
    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.DEBUG if app.debug else logging.INFO)
    
    # 添加处理器到应用日志
    app.logger.addHandler(file_handler)
    app.logger.addHandler(error_file_handler)
    app.logger.addHandler(console_handler)
    
    # 设置其他库的日志级别
    werkzeug_level = logging.WARNING if log_level > logging.WARNING else log_level
    logging.getLogger('werkzeug').setLevel(werkzeug_level)
    logging.getLogger('PIL').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('waitress').setLevel(logging.INFO)
    
    # 添加请求日志中间件
    @app.before_request
    def log_request_info():
        """记录请求信息"""
        app.logger.info(f'Request: {request.method} {request.path} - IP: {request.remote_addr}')
        if request.method in ['POST', 'PUT']:
            if request.content_type and 'application/json' in request.content_type:
                try:
                    data = request.get_json(silent=True) or {}
                    # 不记录敏感信息
                    filtered_data = {k: v for k, v in data.items() if 'password' not in k.lower() and 'token' not in k.lower()}
                    app.logger.debug(f'Request JSON: {filtered_data}')
                except:
                    app.logger.debug('Request contains non-JSON data')
    
    @app.after_request
    def log_response_info(response):
        """记录响应信息"""
        app.logger.info(f'Response: {request.method} {request.path} - Status: {response.status_code}')
        return response
