import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
from converter import MarkdownConverter
from logger import log_info, log_error, log_warning, log_debug

class MarkdownEditorUI:
    """
    Markdown编辑器的用户界面类
    提供直观的界面用于创建、编辑、保存Markdown文件，以及格式转换功能
    """
    
    def __init__(self, root):
        """
        初始化编辑器界面
        
        Args:
            root: Tkinter的根窗口对象
        """
        try:
            self.root = root
            self.root.title("NextMD - Markdown编辑器")
            self.root.geometry("1000x600")
            
            # 设置中文字体支持
            self.font_family = "SimHei"  # 中文支持的字体
            self.font_size = 12
            self.current_file = None
            
            log_info("初始化Markdown编辑器用户界面")
            
            # 尝试启用拖放功能
            try:
                self._enable_drag_and_drop()
            except Exception as e:
                log_warning(f"拖放功能初始化失败，但不影响程序运行: {str(e)}")
            
            # 创建菜单栏
            self._create_menu()
            
            # 创建工具栏
            self._create_toolbar()
            
            # 创建主框架，用于放置编辑区域和预览区域
            self.main_frame = ttk.Frame(root)
            self.main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            
            # 创建编辑区域
            self._create_editor()
            
            # 创建状态栏
            self._create_statusbar()
            
            # 绑定事件
            self._bind_events()
            
            log_info("用户界面初始化完成")
        except Exception as e:
            log_error(f"初始化用户界面失败: {str(e)}")
            messagebox.showerror("错误", f"初始化界面失败: {str(e)}")
    
    def _create_menu(self):
        """创建菜单栏"""
        try:
            self.menu_bar = tk.Menu(self.root)
            
            # 文件菜单
            self.file_menu = tk.Menu(self.menu_bar, tearoff=0)
            self.file_menu.add_command(label="新建", command=self.new_file, accelerator="Ctrl+N")
            self.file_menu.add_command(label="打开", command=self.open_file, accelerator="Ctrl+O")
            self.file_menu.add_command(label="保存", command=self.save_file, accelerator="Ctrl+S")
            self.file_menu.add_command(label="另存为...", command=self.save_file_as, accelerator="Ctrl+Shift+S")
            self.file_menu.add_separator()
            self.file_menu.add_command(label="退出", command=self.root.quit, accelerator="Ctrl+Q")
            self.menu_bar.add_cascade(label="文件", menu=self.file_menu)
            
            # 编辑菜单
            self.edit_menu = tk.Menu(self.menu_bar, tearoff=0)
            self.edit_menu.add_command(label="撤销", command=self.undo, accelerator="Ctrl+Z")
            self.edit_menu.add_command(label="重做", command=self.redo, accelerator="Ctrl+Y")
            self.edit_menu.add_separator()
            self.edit_menu.add_command(label="查找...", command=self.find_text, accelerator="Ctrl+F")
            self.edit_menu.add_command(label="替换...", command=self.replace_text, accelerator="Ctrl+H")
            self.menu_bar.add_cascade(label="编辑", menu=self.edit_menu)
            
            # 转换菜单
            self.convert_menu = tk.Menu(self.menu_bar, tearoff=0)
            self.convert_menu.add_command(label="Markdown转HTML", command=self.convert_md_to_html)
            self.convert_menu.add_command(label="HTML转Markdown", command=self.convert_html_to_md)
            self.menu_bar.add_cascade(label="转换", menu=self.convert_menu)
            
            # 帮助菜单
            self.help_menu = tk.Menu(self.menu_bar, tearoff=0)
            self.help_menu.add_command(label="关于", command=self.show_about)
            self.menu_bar.add_cascade(label="帮助", menu=self.help_menu)
            
            # 设置菜单栏
            self.root.config(menu=self.menu_bar)
            
            log_debug("菜单栏创建完成")
        except Exception as e:
            log_error(f"创建菜单栏失败: {str(e)}")
    
    def _create_toolbar(self):
        """创建工具栏"""
        self.toolbar = ttk.Frame(self.root)
        self.toolbar.pack(side=tk.TOP, fill=tk.X, padx=5, pady=2)
        
        # 文件操作按钮
        self.new_btn = ttk.Button(self.toolbar, text="新建", command=self.new_file)
        self.new_btn.pack(side=tk.LEFT, padx=2)
        
        self.open_btn = ttk.Button(self.toolbar, text="打开", command=self.open_file)
        self.open_btn.pack(side=tk.LEFT, padx=2)
        
        self.save_btn = ttk.Button(self.toolbar, text="保存", command=self.save_file)
        self.save_btn.pack(side=tk.LEFT, padx=2)
        
        ttk.Separator(self.toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=5, fill=tk.Y)
        
        # 转换按钮
        self.md_to_html_btn = ttk.Button(self.toolbar, text="MD转HTML", command=self.convert_md_to_html)
        self.md_to_html_btn.pack(side=tk.LEFT, padx=2)
        
        self.html_to_md_btn = ttk.Button(self.toolbar, text="HTML转MD", command=self.convert_html_to_md)
        self.html_to_md_btn.pack(side=tk.LEFT, padx=2)
    
    def _create_editor(self):
        """创建编辑区域"""
        # 创建一个分割窗口，左边是Markdown编辑，右边是HTML预览
        self.paned_window = ttk.PanedWindow(self.main_frame, orient=tk.HORIZONTAL)
        self.paned_window.pack(fill=tk.BOTH, expand=True)
        
        # 左边Markdown编辑区域
        self.md_frame = ttk.Frame(self.paned_window, width=500)
        self.paned_window.add(self.md_frame, weight=1)
        
        # 添加编辑区域的标签
        self.md_label = ttk.Label(self.md_frame, text="Markdown编辑区")
        self.md_label.pack(anchor=tk.W, padx=5, pady=2)
        
        # 创建滚动条
        self.md_scrollbar = ttk.Scrollbar(self.md_frame)
        self.md_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 创建文本编辑区域，启用撤销功能
        self.text_editor = tk.Text(
            self.md_frame,
            wrap=tk.WORD,
            undo=True,
            font=(self.font_family, self.font_size),
            yscrollcommand=self.md_scrollbar.set
        )
        self.text_editor.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.md_scrollbar.config(command=self.text_editor.yview)
        
        # 右边HTML预览区域
        self.html_frame = ttk.Frame(self.paned_window, width=500)
        self.paned_window.add(self.html_frame, weight=1)
        
        # 添加预览区域的标签
        self.html_label = ttk.Label(self.html_frame, text="HTML预览区")
        self.html_label.pack(anchor=tk.W, padx=5, pady=2)
        
        # 创建HTML预览文本框
        self.html_scrollbar = ttk.Scrollbar(self.html_frame)
        self.html_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.html_preview = tk.Text(
            self.html_frame,
            wrap=tk.WORD,
            font=(self.font_family, self.font_size),
            yscrollcommand=self.html_scrollbar.set
        )
        self.html_preview.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.html_scrollbar.config(command=self.html_preview.yview)
        
        # 设置预览区域为只读
        self.html_preview.config(state=tk.DISABLED)
    
    def _create_statusbar(self):
        """创建状态栏"""
        self.statusbar = ttk.Frame(self.root)
        self.statusbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.status_label = ttk.Label(self.statusbar, text="就绪", anchor=tk.W)
        self.status_label.pack(side=tk.LEFT, padx=5)
    
    def _enable_drag_and_drop(self):
        """启用文件拖放功能"""
        try:
            # 尝试注册拖放目标
            if hasattr(self.root, 'drop_target_register'):
                self.root.drop_target_register("*", "DND_Files")
                
                # 绑定拖放事件
                self.root.dnd_bind('<<Drop>>', self._on_drop)
                log_info("文件拖放功能已启用")
            else:
                log_warning("当前Tkinter版本不支持拖放功能")
        except Exception as e:
            log_warning(f"启用文件拖放功能失败: {str(e)}")
    
    def _on_drop(self, event):
        """处理文件拖放事件"""
        try:
            # 获取拖入的文件路径
            file_paths = self.root.tk.splitlist(event.data)
            
            if not file_paths:
                return
            
            # 只处理第一个文件
            file_path = file_paths[0]
            
            # 检查文件扩展名
            file_ext = os.path.splitext(file_path)[1].lower()
            if file_ext not in ['.md', '.markdown', '.html', '.htm']:
                messagebox.showwarning("不支持的文件类型", "仅支持打开.md、.markdown、.html和.htm文件")
                return
            
            # 检查当前文件是否有未保存的更改
            if self._check_unsaved_changes():
                return
            
            # 打开拖入的文件
            with open(file_path, "r", encoding="utf-8") as file:
                content = file.read()
            
            # 清空编辑区域并加载文件内容
            self.text_editor.delete("1.0", tk.END)
            self.text_editor.insert(tk.END, content)
            
            # 设置当前文件路径
            self.current_file = file_path
            self.root.title(f"NextMD - {os.path.basename(file_path)}")
            
            # 根据文件类型自动转换预览
            if file_ext in [".md", ".markdown"]:
                self._update_preview()
            elif file_ext in [".html", ".htm"]:
                # HTML文件直接显示内容
                self.html_preview.config(state=tk.NORMAL)
                self.html_preview.delete("1.0", tk.END)
                self.html_preview.insert(tk.END, content)
                self.html_preview.config(state=tk.DISABLED)
            
            # 更新状态栏
            self._on_text_modified()
            
        except Exception as e:
            messagebox.showerror("错误", f"打开拖入的文件失败: {str(e)}")
    
    def _bind_events(self):
        """绑定事件"""
        # 绑定快捷键
        self.root.bind("\u003cControl-n\u003e", lambda event: self.new_file())
        self.root.bind("\u003cControl-o\u003e", lambda event: self.open_file())
        self.root.bind("\u003cControl-s\u003e", lambda event: self.save_file())
        self.root.bind("\u003cControl-Shift-S\u003e", lambda event: self.save_file_as())
        self.root.bind("\u003cControl-q\u003e", lambda event: self.root.quit())
        self.root.bind("\u003cControl-z\u003e", lambda event: self.undo())
        self.root.bind("\u003cControl-y\u003e", lambda event: self.redo())
        self.root.bind("\u003cControl-f\u003e", lambda event: self.find_text())
        self.root.bind("\u003cControl-h\u003e", lambda event: self.replace_text())
        
        # 当编辑内容变化时更新状态栏
        self.text_editor.bind("<<Modified>>", self._on_text_modified)
    
    def _on_text_modified(self, event=None):
        """当文本内容变化时更新状态栏"""
        # 获取文本的行数和字符数
        content = self.text_editor.get("1.0", tk.END)
        lines = len(content.splitlines())
        chars = len(content) - 1  # 减去最后的换行符
        
        # 更新状态栏
        file_name = os.path.basename(self.current_file) if self.current_file else "未命名"
        self.status_label.config(text=f"文件: {file_name} | 行数: {lines} | 字符数: {chars}")
        
        # 重新设置修改标志，以便下次变化时再次触发
        self.text_editor.edit_modified(False)
    
    def new_file(self):
        """新建文件"""
        try:
            log_info("执行新建文件操作")
            
            # 检查当前文件是否有未保存的更改
            if self._check_unsaved_changes():
                log_debug("用户取消新建文件操作")
                return
            
            # 清空编辑区域
            self.text_editor.delete("1.0", tk.END)
            self.html_preview.config(state=tk.NORMAL)
            self.html_preview.delete("1.0", tk.END)
            self.html_preview.config(state=tk.DISABLED)
            
            # 重置当前文件路径
            self.current_file = None
            self.root.title("NextMD - Markdown编辑器")
            
            # 更新状态栏
            self._on_text_modified()
            
            log_debug("新建文件完成")
        except Exception as e:
            log_error(f"新建文件失败: {str(e)}")
            messagebox.showerror("错误", f"新建文件失败: {str(e)}")
    
    def open_file(self):
        """打开文件"""
        try:
            log_info("执行打开文件操作")
            
            # 检查当前文件是否有未保存的更改
            if self._check_unsaved_changes():
                log_debug("用户取消打开文件操作")
                return
            
            # 打开文件对话框
            file_path = filedialog.askopenfilename(
                defaultextension=".md",
                filetypes=[
                    ("Markdown文件", "*.md;*.markdown"),
                    ("HTML文件", "*.html;*.htm"),
                    ("所有文件", "*.*")
                ]
            )
            
            if file_path:
                try:
                    # 检查文件是否存在
                    if not os.path.exists(file_path):
                        raise FileNotFoundError(f"文件不存在: {file_path}")
                    
                    # 检查文件大小
                    file_size = os.path.getsize(file_path)
                    log_debug(f"尝试打开文件: {file_path}, 大小: {file_size} 字节")
                    
                    # 如果文件太大，给出警告
                    if file_size > 10 * 1024 * 1024:  # 10MB
                        if not messagebox.askyesno("警告", "文件较大，可能会影响性能。是否继续打开？"):
                            return
                    
                    with open(file_path, "r", encoding="utf-8") as file:
                        content = file.read()
                    
                    # 清空编辑区域并加载文件内容
                    self.text_editor.delete("1.0", tk.END)
                    self.text_editor.insert(tk.END, content)
                    
                    # 设置当前文件路径
                    self.current_file = file_path
                    self.root.title(f"NextMD - {os.path.basename(file_path)}")
                    
                    # 根据文件类型自动转换预览
                    file_ext = os.path.splitext(file_path)[1].lower()
                    if file_ext in [".md", ".markdown"]:
                        self._update_preview()
                    elif file_ext in [".html", ".htm"]:
                        # HTML文件直接显示内容
                        self.html_preview.config(state=tk.NORMAL)
                        self.html_preview.delete("1.0", tk.END)
                        self.html_preview.insert(tk.END, content)
                        self.html_preview.config(state=tk.DISABLED)
                    
                    # 更新状态栏
                    self._on_text_modified()
                    
                    log_info(f"成功打开文件: {file_path}")
                except UnicodeDecodeError:
                    error_msg = "无法解码文件，请检查文件编码"
                    log_error(f"打开文件编码错误: {file_path} - {error_msg}")
                    messagebox.showerror("编码错误", error_msg)
                except FileNotFoundError as e:
                    log_error(f"打开文件失败: {str(e)}")
                    messagebox.showerror("文件不存在", str(e))
                except Exception as e:
                    log_error(f"打开文件失败: {str(e)}")
                    messagebox.showerror("错误", f"无法打开文件: {str(e)}")
        except Exception as e:
            log_error(f"打开文件操作失败: {str(e)}")
            messagebox.showerror("错误", f"打开文件操作失败: {str(e)}")
    
    def save_file(self):
        """保存文件"""
        try:
            log_info("执行保存文件操作")
            
            if self.current_file:
                try:
                    content = self.text_editor.get("1.0", tk.END)
                    
                    # 确保文件所在目录存在
                    directory = os.path.dirname(self.current_file)
                    if directory and not os.path.exists(directory):
                        os.makedirs(directory)
                        log_debug(f"创建目录: {directory}")
                    
                    with open(self.current_file, "w", encoding="utf-8") as file:
                        file.write(content)
                    
                    log_info(f"成功保存文件: {self.current_file}")
                    messagebox.showinfo("成功", "文件已保存")
                except Exception as e:
                    log_error(f"保存文件失败: {str(e)}")
                    messagebox.showerror("错误", f"保存文件失败: {str(e)}")
            else:
                # 如果没有当前文件，则调用另存为
                log_debug("当前无文件路径，执行另存为操作")
                self.save_file_as()
        except Exception as e:
            log_error(f"保存文件操作失败: {str(e)}")
            messagebox.showerror("错误", f"保存文件操作失败: {str(e)}")
    
    def save_file_as(self):
        """另存为文件"""
        try:
            log_info("执行另存为操作")
            
            file_path = filedialog.asksaveasfilename(
                defaultextension=".md",
                filetypes=[
                    ("Markdown文件", "*.md"),
                    ("HTML文件", "*.html"),
                    ("所有文件", "*.*")
                ]
            )
            
            if file_path:
                log_debug(f"用户选择保存路径: {file_path}")
                self.current_file = file_path
                self.root.title(f"NextMD - {os.path.basename(file_path)}")
                self.save_file()
            else:
                log_debug("用户取消另存为操作")
        except Exception as e:
            log_error(f"另存为操作失败: {str(e)}")
            messagebox.showerror("错误", f"另存为操作失败: {str(e)}")
    
    def _check_unsaved_changes(self):
        """检查是否有未保存的更改"""
        try:
            log_debug("检查未保存的更改")
            
            # 这里简化处理，实际应用中应该检查文本是否被修改
            response = messagebox.askyesnocancel(
                "未保存的更改", 
                "当前文件有未保存的更改，是否保存?"
            )
            
            if response is None:  # 用户点击取消
                log_debug("用户取消操作，因为有未保存的更改")
                return True
            elif response:  # 用户点击是
                log_debug("用户选择保存未保存的更改")
                self.save_file()
            
            return False
        except Exception as e:
            log_error(f"检查未保存更改时出错: {str(e)}")
            return False
    
    def _update_preview(self):
        """更新HTML预览"""
        try:
            log_debug("更新HTML预览")
            
            # 获取Markdown内容并转换为HTML
            md_content = self.text_editor.get("1.0", tk.END)
            log_debug(f"转换Markdown内容到HTML，长度: {len(md_content)} 字符")
            
            html_content = MarkdownConverter.md_to_html(md_content)
            
            # 更新预览区域
            self.html_preview.config(state=tk.NORMAL)
            self.html_preview.delete("1.0", tk.END)
            self.html_preview.insert(tk.END, html_content)
            self.html_preview.config(state=tk.DISABLED)
            
            log_debug("HTML预览更新成功")
        except Exception as e:
            log_error(f"更新HTML预览失败: {str(e)}")
            messagebox.showerror("转换错误", f"Markdown转HTML失败: {str(e)}")
    
    def convert_md_to_html(self):
        """将当前Markdown内容转换为HTML并保存"""
        try:
            log_info("执行Markdown转HTML操作")
            
            md_content = self.text_editor.get("1.0", tk.END)
            log_debug(f"转换Markdown内容，长度: {len(md_content)} 字符")
            
            # 如果当前文件是Markdown文件，默认使用相同文件名但不同扩展名
            default_filename = None
            if self.current_file and os.path.splitext(self.current_file)[1].lower() in [".md", ".markdown"]:
                default_filename = os.path.splitext(self.current_file)[0] + ".html"
                log_debug(f"检测到当前文件为Markdown，默认HTML文件名: {default_filename}")
            
            # 打开保存对话框
            file_path = filedialog.asksaveasfilename(
                defaultextension=".html",
                filetypes=[("HTML文件", "*.html")],
                initialfile=default_filename
            )
            
            if file_path:
                try:
                    log_debug(f"用户选择保存路径: {file_path}")
                    
                    # 确保目录存在
                    directory = os.path.dirname(file_path)
                    if directory and not os.path.exists(directory):
                        os.makedirs(directory)
                        log_debug(f"创建目录: {directory}")
                    
                    # 转换并保存
                    html_content = MarkdownConverter.md_to_html(md_content)
                    with open(file_path, "w", encoding="utf-8") as file:
                        file.write(html_content)
                    
                    log_info(f"成功保存HTML文件: {file_path}")
                    messagebox.showinfo("成功", f"HTML文件已保存至: {file_path}")
                except IOError as e:
                    log_error(f"保存HTML文件失败: IO错误 - {str(e)}")
                    messagebox.showerror("错误", f"保存HTML文件失败: 磁盘可能已满或文件被占用")
                except Exception as e:
                    log_error(f"保存HTML文件失败: {str(e)}")
                    messagebox.showerror("错误", f"保存HTML文件失败: {str(e)}")
            else:
                log_debug("用户取消保存HTML文件")
        except Exception as e:
            log_error(f"执行Markdown转HTML操作失败: {str(e)}")
            messagebox.showerror("错误", f"转换失败: {str(e)}")
    
    def convert_html_to_md(self):
        """将HTML文件转换为Markdown"""
        try:
            log_info("执行HTML转Markdown操作")
            
            # 打开HTML文件
            file_path = filedialog.askopenfilename(
                defaultextension=".html",
                filetypes=[("HTML文件", "*.html;*.htm")]
            )
            
            if file_path:
                try:
                    log_debug(f"打开HTML文件: {file_path}")
                    
                    # 检查文件是否存在
                    if not os.path.exists(file_path):
                        raise FileNotFoundError(f"文件不存在: {file_path}")
                    
                    # 检查文件大小
                    file_size = os.path.getsize(file_path)
                    if file_size > 10 * 1024 * 1024:  # 10MB
                        if not messagebox.askyesno("警告", "文件较大，转换可能需要时间。是否继续？"):
                            return
                    
                    # 读取HTML内容
                    with open(file_path, "r", encoding="utf-8") as file:
                        html_content = file.read()
                    
                    log_debug(f"读取HTML内容完成，长度: {len(html_content)} 字符")
                    
                    # 转换为Markdown
                    md_content = MarkdownConverter.html_to_md(html_content)
                    
                    # 保存Markdown文件
                    default_filename = os.path.splitext(file_path)[0] + ".md"
                    save_path = filedialog.asksaveasfilename(
                        defaultextension=".md",
                        filetypes=[("Markdown文件", "*.md")],
                        initialfile=default_filename
                    )
                    
                    if save_path:
                        log_debug(f"保存Markdown文件到: {save_path}")
                        
                        # 确保目录存在
                        directory = os.path.dirname(save_path)
                        if directory and not os.path.exists(directory):
                            os.makedirs(directory)
                            log_debug(f"创建目录: {directory}")
                        
                        with open(save_path, "w", encoding="utf-8") as file:
                            file.write(md_content)
                        
                        log_info(f"成功保存Markdown文件: {save_path}")
                        
                        # 询问是否在编辑器中打开
                        if messagebox.askyesno("完成", f"转换完成，是否在编辑器中打开?"):
                            log_debug("用户选择在编辑器中打开转换后的文件")
                            self.new_file()  # 先清空当前内容
                            self.text_editor.insert(tk.END, md_content)
                            self.current_file = save_path
                            self.root.title(f"NextMD - {os.path.basename(save_path)}")
                            self._update_preview()
                            self._on_text_modified()
                    else:
                        log_debug("用户取消保存Markdown文件")
                except UnicodeDecodeError:
                    error_msg = "无法解码文件，请检查文件编码是否为UTF-8"
                    log_error(f"HTML文件解码错误: {file_path} - {error_msg}")
                    messagebox.showerror("编码错误", error_msg)
                except FileNotFoundError as e:
                    log_error(f"HTML文件不存在: {str(e)}")
                    messagebox.showerror("错误", str(e))
                except Exception as e:
                    log_error(f"HTML转Markdown失败: {str(e)}")
                    messagebox.showerror("错误", f"HTML转Markdown失败: {str(e)}")
            else:
                log_debug("用户取消选择HTML文件")
        except Exception as e:
            log_error(f"执行HTML转Markdown操作失败: {str(e)}")
            messagebox.showerror("错误", f"转换操作失败: {str(e)}")
    
    def undo(self):
        """撤销操作"""
        try:
            log_debug("执行撤销操作")
            self.text_editor.edit_undo()
            log_debug("撤销操作成功")
        except tk.TclError:
            # 没有可撤销的操作
            log_debug("没有可撤销的操作")
            pass
        except Exception as e:
            log_error(f"撤销操作失败: {str(e)}")
    
    def redo(self):
        """重做操作"""
        try:
            log_debug("执行重做操作")
            self.text_editor.edit_redo()
            log_debug("重做操作成功")
        except tk.TclError:
            # 没有可重做的操作
            log_debug("没有可重做的操作")
            pass
        except Exception as e:
            log_error(f"重做操作失败: {str(e)}")
    
    def find_text(self):
        """查找文本"""
        try:
            log_info("执行查找文本操作")
            
            # 创建查找对话框
            find_dialog = tk.Toplevel(self.root)
            find_dialog.title("查找")
            find_dialog.geometry("300x120")
            find_dialog.transient(self.root)
            find_dialog.resizable(False, False)
            
            # 布局
            ttk.Label(find_dialog, text="查找内容:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
            
            find_entry = ttk.Entry(find_dialog, width=25)
            find_entry.grid(row=0, column=1, padx=5, pady=5)
            find_entry.focus()
            
            # 大小写敏感选项
            case_var = tk.BooleanVar()
            case_check = ttk.Checkbutton(find_dialog, text="区分大小写", variable=case_var)
            case_check.grid(row=1, column=0, columnspan=2, padx=5, sticky=tk.W)
            
            # 按钮
            btn_frame = ttk.Frame(find_dialog)
            btn_frame.grid(row=2, column=0, columnspan=2, pady=10)
            
            def do_find():
                search_text = find_entry.get()
                if not search_text:
                    return
                
                log_debug(f"执行查找: '{search_text}' {'(区分大小写)' if case_var.get() else '(不区分大小写)'}")
                
                # 获取当前光标位置
                current_pos = self.text_editor.index(tk.INSERT)
                
                # 查找选项
                options = {} if case_var.get() else {"nocase": True}
                
                # 从当前位置开始查找
                try:
                    start_pos = self.text_editor.search(search_text, current_pos, tk.END, **options)
                    if not start_pos:
                        log_debug("从当前位置未找到，从头开始查找")
                        # 如果从当前位置没找到，从头开始查找
                        start_pos = self.text_editor.search(search_text, "1.0", current_pos, **options)
                    
                    if start_pos:
                        log_debug(f"找到文本，位置: {start_pos}")
                        # 计算结束位置
                        end_pos = f"{start_pos}+{len(search_text)}c"
                        
                        # 选择找到的文本
                        self.text_editor.tag_remove("search", "1.0", tk.END)
                        self.text_editor.tag_add("search", start_pos, end_pos)
                        self.text_editor.tag_config("search", background="yellow", foreground="black")
                        
                        # 移动光标到找到的位置
                        self.text_editor.mark_set(tk.INSERT, end_pos)
                        self.text_editor.see(start_pos)
                    else:
                        log_debug(f"未找到文本: '{search_text}'")
                        messagebox.showinfo("查找", f"找不到 '{search_text}'")
                except Exception as e:
                    log_error(f"查找过程中出错: {str(e)}")
                    messagebox.showerror("错误", f"查找失败: {str(e)}")
            
            ttk.Button(btn_frame, text="查找下一个", command=do_find).pack(side=tk.LEFT, padx=5)
            ttk.Button(btn_frame, text="取消", command=find_dialog.destroy).pack(side=tk.LEFT, padx=5)
            
            # 绑定Enter键执行查找
            find_entry.bind("\u003cReturn\u003e", lambda event: do_find())
        except Exception as e:
            log_error(f"创建查找对话框失败: {str(e)}")
            messagebox.showerror("错误", f"打开查找对话框失败: {str(e)}")
    
    def replace_text(self):
        """替换文本"""
        try:
            log_info("执行替换文本操作")
            
            # 创建替换对话框
            replace_dialog = tk.Toplevel(self.root)
            replace_dialog.title("替换")
            replace_dialog.geometry("350x180")
            replace_dialog.transient(self.root)
            replace_dialog.resizable(False, False)
            
            # 布局
            ttk.Label(replace_dialog, text="查找内容:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
            find_entry = ttk.Entry(replace_dialog, width=25)
            find_entry.grid(row=0, column=1, padx=5, pady=5)
            
            ttk.Label(replace_dialog, text="替换为:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
            replace_entry = ttk.Entry(replace_dialog, width=25)
            replace_entry.grid(row=1, column=1, padx=5, pady=5)
            
            # 选项
            options_frame = ttk.Frame(replace_dialog)
            options_frame.grid(row=2, column=0, columnspan=2, sticky=tk.W, padx=5)
            
            case_var = tk.BooleanVar()
            case_check = ttk.Checkbutton(options_frame, text="区分大小写", variable=case_var)
            case_check.pack(side=tk.LEFT, padx=5)
            
            # 按钮
            btn_frame = ttk.Frame(replace_dialog)
            btn_frame.grid(row=3, column=0, columnspan=2, pady=10)
            
            # 当前查找位置
            current_find_pos = ["1.0"]
            
            # 处理查找下一个
            def do_find():
                search_text = find_entry.get()
                if not search_text:
                    return
                
                log_debug(f"执行替换对话框中的查找: '{search_text}'")
                options = {} if case_var.get() else {"nocase": True}
                
                try:
                    start_pos = self.text_editor.search(search_text, current_find_pos[0], tk.END, **options)
                    if not start_pos:
                        log_debug("从当前位置未找到，从头开始查找")
                        start_pos = self.text_editor.search(search_text, "1.0", current_find_pos[0], **options)
                        if not start_pos:
                            log_debug(f"未找到文本: '{search_text}'")
                            messagebox.showinfo("查找", f"找不到 '{search_text}'")
                            return
                    
                    log_debug(f"找到文本，位置: {start_pos}")
                    # 计算结束位置
                    end_pos = f"{start_pos}+{len(search_text)}c"
                    
                    # 选择找到的文本
                    self.text_editor.tag_remove("search", "1.0", tk.END)
                    self.text_editor.tag_add("search", start_pos, end_pos)
                    self.text_editor.tag_config("search", background="yellow", foreground="black")
                    
                    # 移动光标到找到的位置
                    self.text_editor.mark_set(tk.INSERT, end_pos)
                    self.text_editor.see(start_pos)
                    
                    # 更新当前查找位置
                    current_find_pos[0] = end_pos
                except Exception as e:
                    log_error(f"查找过程中出错: {str(e)}")
                    messagebox.showerror("错误", f"查找失败: {str(e)}")
            
            # 处理替换
            def do_replace():
                search_text = find_entry.get()
                replace_text = replace_entry.get()
                
                if not search_text:
                    return
                
                log_debug(f"执行单替换: '{search_text}' -> '{replace_text}'")
                # 获取当前选中的文本
                try:
                    selected_text = self.text_editor.get("sel.first", "sel.last")
                    if selected_text and (case_var.get() and selected_text == search_text or 
                                         not case_var.get() and selected_text.lower() == search_text.lower()):
                        # 替换选中的文本
                        self.text_editor.delete("sel.first", "sel.last")
                        self.text_editor.insert("sel.first", replace_text)
                        log_debug("替换成功，继续查找下一个")
                        # 继续查找下一个
                        do_find()
                    else:
                        # 如果没有选中的文本或不匹配，先执行一次查找
                        do_find()
                except tk.TclError:
                    # 没有选中的文本，执行查找
                    do_find()
                except Exception as e:
                    log_error(f"单替换过程中出错: {str(e)}")
                    messagebox.showerror("错误", f"替换失败: {str(e)}")
            
            # 处理全部替换
            def do_replace_all():
                search_text = find_entry.get()
                replace_text = replace_entry.get()
                
                if not search_text:
                    return
                
                log_debug(f"执行全部替换: '{search_text}' -> '{replace_text}'")
                # 查找选项
                options = {} if case_var.get() else {"nocase": True}
                
                try:
                    # 获取全部文本
                    content = self.text_editor.get("1.0", tk.END)
                    log_debug(f"文档长度: {len(content)} 字符")
                    
                    # 执行替换
                    if case_var.get():
                        new_content = content.replace(search_text, replace_text)
                        count = content.count(search_text)
                        log_debug(f"区分大小写替换完成，替换数量: {count}")
                    else:
                        # 不区分大小写的替换需要更复杂的处理
                        import re
                        flags = 0 if case_var.get() else re.IGNORECASE
                        new_content = re.sub(re.escape(search_text), replace_text, content, flags=flags)
                        count = len(re.findall(re.escape(search_text), content, flags=flags))
                        log_debug(f"不区分大小写替换完成，替换数量: {count}")
                    
                    # 计算替换的次数
                    if case_var.get():
                        count = content.count(search_text)
                    else:
                        count = len(re.findall(re.escape(search_text), content, flags=flags))
                    
                    # 更新文本
                    self.text_editor.delete("1.0", tk.END)
                    self.text_editor.insert(tk.END, new_content)
                    
                    messagebox.showinfo("替换", f"已完成 {count} 处替换")
                    log_info(f"全部替换完成，共替换 {count} 处")
                    
                    # 重置当前查找位置
                    current_find_pos[0] = "1.0"
                except Exception as e:
                    log_error(f"全部替换过程中出错: {str(e)}")
                    messagebox.showerror("错误", f"替换失败: {str(e)}")
            
            ttk.Button(btn_frame, text="查找下一个", command=do_find).pack(side=tk.LEFT, padx=5)
            ttk.Button(btn_frame, text="替换", command=do_replace).pack(side=tk.LEFT, padx=5)
            ttk.Button(btn_frame, text="全部替换", command=do_replace_all).pack(side=tk.LEFT, padx=5)
            ttk.Button(btn_frame, text="取消", command=replace_dialog.destroy).pack(side=tk.LEFT, padx=5)
            
            # 绑定Enter键执行查找
            find_entry.bind("\u003cReturn\u003e", lambda event: do_find())
        except Exception as e:
            log_error(f"创建替换对话框失败: {str(e)}")
            messagebox.showerror("错误", f"打开替换对话框失败: {str(e)}")
    
    def show_about(self):
        """显示关于对话框"""
        try:
            log_info("显示关于对话框")
            messagebox.showinfo(
                "关于NextMD",
                "NextMD - Markdown编辑器 v1.0.0\n\n" +
                "一个功能完整的Markdown编辑器，支持Markdown和HTML之间的双向转换。\n\n" +
                "使用Python和Tkinter开发。"
            )
        except Exception as e:
            log_error(f"显示关于对话框失败: {str(e)}")
            # 如果对话框显示失败，尝试通过控制台显示信息
            try:
                print("NextMD - Markdown编辑器 v1.0.0")
                print("一个功能完整的Markdown编辑器，支持Markdown和HTML之间的双向转换。")
                print("使用Python和Tkinter开发。")
            except:
                pass