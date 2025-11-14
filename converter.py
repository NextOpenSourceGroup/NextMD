import markdown
from bs4 import BeautifulSoup
import os
from logger import log_info, log_error, log_warning, log_debug

class MarkdownConverter:
    """
    Markdown和HTML之间的转换工具类
    提供MD转HTML和HTML转MD的功能
    """
    
    def __init__(self):
        """初始化转换器"""
        log_info("Markdown转换器初始化完成")
    
    @staticmethod
    def md_to_html(md_content):
        """
        将Markdown内容转换为HTML
        
        Args:
            md_content (str): Markdown格式的文本内容
            
        Returns:
            str: 转换后的HTML内容
        """
        if not md_content:
            return ""
            
        try:
            # 使用markdown库进行转换，启用扩展以支持更多特性
            html_content = markdown.markdown(
                md_content, 
                extensions=['fenced_code', 'tables', 'toc', 'codehilite']
            )
            
            # 包装成完整的HTML文档
            full_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Converted from Markdown</title>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; padding: 20px; max-width: 800px; margin: 0 auto; }}
        h1, h2, h3, h4, h5, h6 {{ color: #333; }}
        pre {{ background-color: #f5f5f5; padding: 10px; border-radius: 5px; overflow-x: auto; }}
        code {{ font-family: 'Courier New', Courier, monospace; background-color: #f5f5f5; padding: 2px 4px; border-radius: 3px; }}
        blockquote {{ border-left: 4px solid #ddd; padding-left: 16px; margin-left: 0; color: #666; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #ddd; padding: 8px 12px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
    </style>
</head>
<body>
{html_content}
</body>
</html>"""
            
            log_debug(f"Markdown转HTML成功，输入长度: {len(md_content)} 字符")
            return full_html
        except Exception as e:
            error_msg = f"Markdown转HTML错误: {str(e)}"
            log_error(error_msg)
            return f"<p>转换错误: {str(e)}</p>"
    
    @staticmethod
    def html_to_md(html_content):
        """
        将HTML内容转换为Markdown
        
        Args:
            html_content (str): HTML格式的文本内容
            
        Returns:
            str: 转换后的Markdown内容
        """
        if not html_content:
            return ""
            
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # 移除script和style标签
            for script in soup(['script', 'style']):
                script.decompose()
            
            md_content = []
            
            # 处理HTML标签，转换为Markdown格式
            for element in soup.find('body', recursive=False).children if soup.body else soup.children:
                md_content.append(MarkdownConverter._convert_element(element))
            
            result = '\n'.join(md_content)
            log_debug(f"HTML转Markdown成功，输入长度: {len(html_content)} 字符")
            return result
        except Exception as e:
            error_msg = f"HTML转Markdown错误: {str(e)}"
            log_error(error_msg)
            return f"转换错误: {str(e)}"
    
    @staticmethod
    def _convert_element(element):
        """递归处理HTML元素，转换为Markdown格式"""
        if element.name is None:
            # 文本节点
            return element.strip() if element.strip() else ''
        
        # 处理不同的HTML标签
        if element.name == 'h1':
            return '# ' + MarkdownConverter._get_text_content(element)
        elif element.name == 'h2':
            return '## ' + MarkdownConverter._get_text_content(element)
        elif element.name == 'h3':
            return '### ' + MarkdownConverter._get_text_content(element)
        elif element.name == 'h4':
            return '#### ' + MarkdownConverter._get_text_content(element)
        elif element.name == 'h5':
            return '##### ' + MarkdownConverter._get_text_content(element)
        elif element.name == 'h6':
            return '###### ' + MarkdownConverter._get_text_content(element)
        elif element.name == 'p':
            return MarkdownConverter._get_text_content(element)
        elif element.name == 'strong' or element.name == 'b':
            return '**' + MarkdownConverter._get_text_content(element) + '**'
        elif element.name == 'em' or element.name == 'i':
            return '*' + MarkdownConverter._get_text_content(element) + '*'
        elif element.name == 'a':
            href = element.get('href', '')
            text = MarkdownConverter._get_text_content(element)
            return f'[{text}]({href})'
        elif element.name == 'img':
            src = element.get('src', '')
            alt = element.get('alt', 'Image')
            return f'![{alt}]({src})'
        elif element.name == 'code':
            # 检查是否是代码块（在pre标签内）
            if element.parent and element.parent.name == 'pre':
                return '```\n' + element.get_text() + '\n```'
            else:
                return '`' + element.get_text() + '`'
        elif element.name == 'pre':
            # 已经在code标签处理中处理
            return ''
        elif element.name == 'blockquote':
            content = MarkdownConverter._get_text_content(element)
            return '> ' + '\n> '.join(content.split('\n'))
        elif element.name == 'ul':
            items = []
            for li in element.find_all('li', recursive=False):
                items.append('- ' + MarkdownConverter._get_text_content(li))
            return '\n'.join(items)
        elif element.name == 'ol':
            items = []
            for i, li in enumerate(element.find_all('li', recursive=False), 1):
                items.append(f'{i}. ' + MarkdownConverter._get_text_content(li))
            return '\n'.join(items)
        elif element.name == 'hr':
            return '---'
        elif element.name == 'table':
            # 简单处理表格
            rows = []
            # 添加表头
            headers = element.find_all('th')
            if headers:
                row_content = '| ' + ' | '.join([MarkdownConverter._get_text_content(h) for h in headers]) + ' |'
                rows.append(row_content)
                # 添加分隔行
                rows.append('| ' + ' | '.join(['---'] * len(headers)) + ' |')
            # 添加表体行
            for tr in element.find_all('tr'):
                cells = tr.find_all('td')
                if cells:
                    row_content = '| ' + ' | '.join([MarkdownConverter._get_text_content(cell) for cell in cells]) + ' |'
                    rows.append(row_content)
            return '\n'.join(rows)
        
        # 对于未专门处理的标签，递归处理其子元素
        result = []
        for child in element.children:
            result.append(MarkdownConverter._convert_element(child))
        return ''.join(result)
    
    @staticmethod
    def _get_text_content(element):
        """获取元素的文本内容，处理子元素"""
        result = []
        for child in element.children:
            result.append(MarkdownConverter._convert_element(child))
        return ''.join(result)
    
    @staticmethod
    def convert_file(input_path, output_path):
        """
        转换文件格式
        根据文件扩展名判断转换方向
        
        Args:
            input_path (str): 输入文件路径
            output_path (str): 输出文件路径
            
        Returns:
            bool: 转换是否成功
        """
        try:
            log_info(f"开始转换文件: {input_path} -> {output_path}")
            
            # 检查输入文件是否存在
            if not os.path.exists(input_path):
                error_msg = f"输入文件不存在: {input_path}"
                log_error(error_msg)
                return False
            
            # 读取输入文件
            try:
                with open(input_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                log_debug(f"成功读取输入文件，大小: {len(content)} 字符")
            except UnicodeDecodeError:
                error_msg = f"无法解码文件: {input_path}，请检查文件编码"
                log_error(error_msg)
                return False
            except Exception as e:
                error_msg = f"读取文件时出错: {str(e)}"
                log_error(error_msg)
                return False
            
            # 根据文件扩展名判断转换方向
            input_ext = os.path.splitext(input_path)[1].lower()
            output_ext = os.path.splitext(output_path)[1].lower()
            
            # 执行转换
            if input_ext in ['.md', '.markdown'] and output_ext in ['.html', '.htm']:
                result = MarkdownConverter.md_to_html(content)
            elif input_ext in ['.html', '.htm'] and output_ext in ['.md', '.markdown']:
                result = MarkdownConverter.html_to_md(content)
            else:
                error_msg = f"不支持的文件格式转换: {input_ext} -> {output_ext}"
                log_error(error_msg)
                return False
            
            # 确保输出目录存在
            output_dir = os.path.dirname(output_path)
            if output_dir and not os.path.exists(output_dir):
                try:
                    os.makedirs(output_dir)
                    log_debug(f"创建输出目录: {output_dir}")
                except Exception as e:
                    error_msg = f"无法创建输出目录: {str(e)}"
                    log_error(error_msg)
                    return False
            
            # 写入输出文件
            try:
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(result)
                log_info(f"文件转换成功: {output_path}")
                return True
            except Exception as e:
                error_msg = f"写入输出文件时出错: {str(e)}"
                log_error(error_msg)
                return False
        except Exception as e:
            error_msg = f"文件转换错误: {str(e)}"
            log_error(error_msg)
            return False