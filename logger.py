import logging
import os
import datetime

# 获取当前目录作为日志保存位置
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.path.join(BASE_DIR, 'logs')

# 确保日志目录存在
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# 生成日志文件名（包含日期）
LOG_FILE = os.path.join(LOG_DIR, f'nextmd_{datetime.datetime.now().strftime("%Y-%m-%d")}.log')

# 配置日志记录器
logger = logging.getLogger('NextMD')
logger.setLevel(logging.DEBUG)

# 创建文件处理器
file_handler = logging.FileHandler(LOG_FILE, encoding='utf-8')
file_handler.setLevel(logging.DEBUG)

# 创建控制台处理器
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)  # 控制台只显示INFO及以上级别的日志

# 创建日志格式器
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# 避免重复添加处理器
if not logger.handlers:
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

def log_debug(message):
    """记录调试信息"""
    logger.debug(message)

def log_info(message):
    """记录一般信息"""
    logger.info(message)

def log_warning(message):
    """记录警告信息"""
    logger.warning(message)

def log_error(message):
    """记录错误信息"""
    logger.error(message, exc_info=True)

def log_critical(message):
    """记录严重错误信息"""
    logger.critical(message, exc_info=True)

def get_log_file_path():
    """获取当前日志文件路径"""
    return LOG_FILE