import sys
import argparse
import tkinter as tk
from config import Config, validate_config
from converter import MarkdownConverter
from ui import MarkdownEditorUI
from logger import log_info, log_error, log_warning, log_debug

def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='NextMD - Markdown编辑器')
    parser.add_argument('--host', type=str, help='部署地址')
    parser.add_argument('--port', type=int, help='部署端口')
    return parser.parse_args()

def main():
    """主程序入口"""
    try:
        # 解析命令行参数
        args = parse_arguments()
        
        # 初始化配置
        config = Config()
        config.update_from_cli(args)
        
        # 验证配置
        if not validate_config(config):
            log_warning("配置验证失败，程序将使用默认配置继续运行")
        else:
            log_debug("配置验证通过")
        
        # 显示配置信息
        log_info(f"启动 {config.app_name} v{config.app_version}")
        log_info(f"部署地址: {config.get_deployment_url()}")
        
        # 初始化Tkinter根窗口
        root = tk.Tk()
        
        # 设置窗口标题
        root.title(f"{config.app_name} - Markdown编辑器")
        
        # 创建并显示编辑器界面
        editor = MarkdownEditorUI(root)
        
        # 启动主事件循环
        root.mainloop()
    except KeyboardInterrupt:
        log_info("程序被用户中断")
    except Exception as e:
        log_error(f"程序运行出错: {str(e)}")
        # 在Windows下，添加一个暂停以便用户看到错误信息
        if sys.platform.startswith('win'):
            try:
                import msvcrt
                print("按任意键退出...")
                msvcrt.getch()
            except Exception:
                pass
    finally:
        log_info("程序已退出")

if __name__ == "__main__":
    main()