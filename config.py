import os
import sys
from dotenv import load_dotenv
from logger import log_info, log_error, log_warning, log_debug

# 确定.env文件的位置
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_FILE_PATH = os.path.join(BASE_DIR, '.env')

# 加载.env文件中的配置
load_dotenv(ENV_FILE_PATH)

# 默认配置
DEFAULT_HOST = "localhost"
DEFAULT_PORT = 3367
DEFAULT_APP_NAME = "NextMD"
DEFAULT_APP_VERSION = "1.0.0"

# 从环境变量中获取配置，如果没有则使用默认值
def get_env_host():
    """获取主机地址配置"""
    return os.getenv("HOST", DEFAULT_HOST)

def get_env_port():
    """获取端口配置，并确保是有效的整数"""
    try:
        port_str = os.getenv("PORT", str(DEFAULT_PORT))
        port = int(port_str)
        # 验证端口号是否在有效范围内
        if 0 <= port <= 65535:
            return port
        else:
            print(f"警告: 无效的端口号 {port}，使用默认端口 {DEFAULT_PORT}")
            return DEFAULT_PORT
    except ValueError:
        print(f"警告: 无法将 PORT={os.getenv('PORT')} 转换为整数，使用默认端口 {DEFAULT_PORT}")
        return DEFAULT_PORT

# 应用程序设置
APP_NAME = os.getenv("APP_NAME", DEFAULT_APP_NAME)
APP_VERSION = os.getenv("APP_VERSION", DEFAULT_APP_VERSION)

# 文件类型常量
FILE_TYPES = {
    "markdown": ["*.md", "*.markdown"],
    "html": ["*.html", "*.htm"]
}

# 定义应用程序的配置类
class Config:
    """
    应用程序配置类
    负责管理和验证所有配置参数
    """
    def __init__(self, host=None, port=None):
        """
        初始化配置
        
        Args:
            host (str, optional): 部署地址
            port (int, optional): 部署端口
        """
        self.host = host or get_env_host()
        self.port = port or get_env_port()
        self.app_name = APP_NAME
        self.app_version = APP_VERSION
        log_debug(f"配置初始化: 主机={self.host}, 端口={self.port}")
    
    def update_from_cli(self, args):
        """
        从命令行参数更新配置
        
        Args:
            args: 命令行参数对象
        """
        if hasattr(args, 'host') and args.host:
            log_debug(f"从命令行更新host: {args.host}")
            self.host = args.host
            log_info(f"配置已更新: 主机地址 = {self.host}")
            
        if hasattr(args, 'port') and args.port:
            log_debug(f"从命令行更新port: {args.port}")
            try:
                port = int(args.port)
                # 验证端口号
                if 0 <= port <= 65535:
                    self.port = port
                    log_info(f"配置已更新: 端口 = {self.port}")
                else:
                    log_error(f"端口号 {port} 超出有效范围 (0-65535)，使用现有配置")
            except ValueError:
                log_error(f"无效的端口号 {args.port}，使用现有配置")
    
    def get_deployment_url(self):
        """
        获取完整的部署URL
        
        Returns:
            str: 部署URL
        """
        return f"http://{self.host}:{self.port}"
    
    def validate(self):
        """
        验证配置有效性
        
        Returns:
            bool: 配置是否有效
        """
        # 验证主机地址
        if not self.host or not isinstance(self.host, str):
            print("错误: 主机地址无效")
            return False
        
        # 验证端口号
        if not isinstance(self.port, int) or self.port < 0 or self.port > 65535:
            print("错误: 端口号无效")
            return False
        
        return True
    
    def save_to_env_file(self, env_path=None):
        """
        保存当前配置到.env文件
        
        Args:
            env_path (str, optional): .env文件路径，如果未指定则使用默认路径
            
        Returns:
            bool: 保存是否成功
        """
        try:
            path = env_path or ENV_FILE_PATH
            with open(path, 'w', encoding='utf-8') as f:
                f.write(f"# NextMD 配置文件\n")
                f.write(f"HOST={self.host}\n")
                f.write(f"PORT={self.port}\n")
                f.write(f"APP_NAME={self.app_name}\n")
                f.write(f"APP_VERSION={self.app_version}\n")
            print(f"配置已保存到 {path}")
            return True
        except Exception as e:
            print(f"保存配置文件失败: {str(e)}")
            return False
    
    def __str__(self):
        """
        返回配置的字符串表示
        """
        return (
            f"配置信息:\n"
            f"  应用名称: {self.app_name}\n"
            f"  应用版本: {self.app_version}\n"
            f"  部署地址: {self.host}\n"
            f"  部署端口: {self.port}\n"
            f"  部署URL: {self.get_deployment_url()}"
        )

# 配置验证函数
def validate_config(config):
    """
    验证配置并处理可能的错误
    
    Args:
        config: 配置对象
        
    Returns:
        bool: 配置是否有效
    """
    if not isinstance(config, Config):
        log_error("无效的配置对象")
        return False
    
    log_debug("开始验证配置")
    return config.validate()