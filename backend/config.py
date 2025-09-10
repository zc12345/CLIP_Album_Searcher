import os
from dotenv import load_dotenv

load_dotenv()
# load_dotenv(dotenv_path="disk.env")

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    # Flask配置
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'
    DEBUG = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    
    # 跨域配置
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*').split(',')
    
    # 文件上传配置
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', 'uploads')

    # 日志配置
    LOG_DIR = os.path.join(basedir, 'logs')
    LOG_LEVEL = 'INFO'
    LOG_MAX_BYTES = 10 * 1024 * 1024  # 10MB
    LOG_BACKUP_COUNT = 10
    
    # 相册配置
    ROOT_PATH = os.environ.get('ROOT_PATH', 'D:\\documents\\images')
    DUMP_PATH = os.environ.get('DUMP_PATH', 'db.pt')
    BACKUP_PATH = os.environ.get('BACKUP_PATH', 'backup')
    ALBUM_LANGUAGE = os.environ.get("ALBUM_LANG", "en")
    
    # HuggingFace镜像配置
    HF_ENDPOINT = os.environ.get('HF_ENDPOINT', 'https://hf-mirror.com')
    HF_HUB_ENABLE_HF_TRANSFER = os.environ.get('HF_HUB_ENABLE_HF_TRANSFER', 'True').lower() == 'true'
    
    # API配置
    API_VERSION = 'v1.3'
    MAX_RESULTS = int(os.environ.get('MAX_RESULTS', 50))
    DEFAULT_THRESHOLD = float(os.environ.get('DEFAULT_THRESHOLD', 0.))
    
    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    DEBUG = True
    LOG_LEVEL = 'DEBUG'

class ProductionConfig(Config):
    DEBUG = False
    LOG_LEVEL = 'DEBUG'

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}