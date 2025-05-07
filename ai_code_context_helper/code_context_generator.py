import re
import os
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, ttk
import webbrowser

from PIL import Image, ImageTk
from ai_code_context_helper.tooltip import create_tooltip
from ai_code_context_helper.file_utils import (
    normalize_path,
    is_text_file,
    read_file_content,
)
from ai_code_context_helper.settings_manager import SettingsManager
from ai_code_context_helper.languages import LANGUAGES
from ai_code_context_helper import __version__


class CodeContextGenerator:
    """代码上下文生成器应用程序主类"""

    def __init__(self, root):
        self.root = root

        # 初始化设置管理器
        self.settings = SettingsManager(LANGUAGES)

        # 从设置中获取当前语言和文本
        self.current_language = self.settings.current_language
        self.texts = self.settings.texts

        self.version = __version__

        self.root.title(f"{self.texts['app_title']} v{self.version}")
        self.root.geometry("800x600")
        self.root.minsize(600, 400)

        try:
            icon_path = Path(__file__).parent / "resources" / "icon.ico"
            self.root.iconbitmap(str(icon_path))
        except Exception as e:
            print(f"无法加载图标: {str(e)}")

        # 使用设置管理器中的值
        self.PATH_PREFIX = self.settings.PATH_PREFIX
        self.PATH_SUFFIX = self.settings.PATH_SUFFIX
        self.CODE_PREFIX = self.settings.CODE_PREFIX
        self.CODE_SUFFIX = self.settings.CODE_SUFFIX
        self.preserve_tree_state_value = self.settings.preserve_tree_state_value
        self.dir_history = self.settings.dir_history

        self.tree_items = {}
        self.checked_items = set()

        self.context_menu = tk.Menu(root, tearoff=0)

        self.style = ttk.Style()
        self.style.configure("TButton", font=("微软雅黑", 10))
        self.style.configure("TCheckbutton", font=("微软雅黑", 10))
        self.style.configure("TLabel", font=("微软雅黑", 10))
        self.style.configure("Treeview", font=("微软雅黑", 10))
        self.style.configure("Treeview.Heading", font=("微软雅黑", 10, "bold"))

        self.create_widgets()

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.center_window(self.root)

    def on_close(self):
        """窗口关闭时的处理函数，保存设置并销毁窗口"""
        self.settings.save_settings()
        self.root.destroy()

    def create_widgets(self):
        """创建并布局所有GUI控件"""

        self.status_var = tk.StringVar()
        self.status_bar = ttk.Label(
            self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W
        )
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM, pady=2)
        self.status_var.set(self.texts["ready"])
        create_tooltip(self.status_bar, self.texts["tooltip_status_bar"])

        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 创建工具栏框架
        toolbar_frame = ttk.Frame(main_frame)
        toolbar_frame.pack(fill=tk.X, pady=(0, 5))

        # 左侧为空白占位
        ttk.Label(toolbar_frame, text="").pack(side=tk.LEFT, expand=True, fill=tk.X)

        # 右侧添加关于按钮组
        self.changelog_btn = ttk.Button(
            toolbar_frame, text="更新日志", command=self.open_changelog
        )
        self.changelog_btn.pack(side=tk.LEFT, padx=2)
        create_tooltip(self.changelog_btn, "查看软件更新日志")

        self.qrcode_btn = ttk.Button(
            toolbar_frame, text="关于作者", command=self.show_qrcode
        )
        self.qrcode_btn.pack(side=tk.LEFT, padx=2)
        create_tooltip(self.qrcode_btn, "显示公众号二维码")

        self.control_frame = ttk.LabelFrame(
            main_frame, text=self.texts["settings"], padding="10"
        )
        self.control_frame.pack(fill=tk.X, pady=5)

        # 顶部控制区添加语言选择
        top_controls = ttk.Frame(self.control_frame)
        top_controls.pack(fill=tk.X, pady=5)

        # 语言选择
        self.lang_label = ttk.Label(top_controls, text=self.texts["language"])
        self.lang_label.pack(side=tk.LEFT, padx=5)

        # 构建语言显示名称列表
        self.language_names = {}  # 用于存储显示名称到代码的映射
        language_display_names = []

        for lang_code in LANGUAGES.keys():
            name = LANGUAGES[lang_code]["language_name"]
            self.language_names[name] = lang_code
            language_display_names.append(name)

        # 获取当前语言的显示名称
        current_display_name = LANGUAGES[self.current_language]["language_name"]

        self.language_var = tk.StringVar(value=current_display_name)
        self.language_combo = ttk.Combobox(
            top_controls,
            textvariable=self.language_var,
            values=language_display_names,
            width=15,
            state="readonly",
        )
        self.language_combo.pack(side=tk.LEFT, padx=5)
        self.language_combo.bind("<<ComboboxSelected>>", self.change_language)

        dir_frame = ttk.Frame(self.control_frame)
        dir_frame.pack(fill=tk.X, pady=5)

        self.dir_label = ttk.Label(dir_frame, text=self.texts["dir_path"])
        self.dir_label.pack(side=tk.LEFT, padx=5)
        create_tooltip(self.dir_label, self.texts["tooltip_dir_path"])

        self.dir_path = tk.StringVar()
        self.dir_entry = ttk.Combobox(dir_frame, textvariable=self.dir_path, width=50)
        self.dir_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        if self.dir_history:
            self.dir_entry["values"] = self.dir_history

        self.dir_entry.bind("<<ComboboxSelected>>", self.on_combobox_select)
        self.dir_entry.bind("<Button-3>", self.show_dir_history_menu)

        self.browse_btn = ttk.Button(
            dir_frame, text=self.texts["browse"], command=self.browse_directory
        )
        self.browse_btn.pack(side=tk.LEFT, padx=5)
        create_tooltip(self.browse_btn, self.texts["tooltip_browse"])

        options_frame = ttk.Frame(self.control_frame)
        options_frame.pack(fill=tk.X, pady=5)

        left_options = ttk.Frame(options_frame)
        left_options.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.show_hidden = tk.BooleanVar(value=self.settings.show_hidden_value)
        self.show_hidden_cb = ttk.Checkbutton(
            left_options,
            text=self.texts["show_hidden"],
            variable=self.show_hidden,
            command=self.on_setting_option_changed,
        )
        self.show_hidden_cb.pack(anchor=tk.W)
        create_tooltip(
            self.show_hidden_cb,
            self.texts["tooltip_show_hidden"],
        )

        self.show_files = tk.BooleanVar(value=self.settings.show_files_value)
        self.show_files_cb = ttk.Checkbutton(
            left_options,
            text=self.texts["show_files"],
            variable=self.show_files,
            command=self.on_setting_option_changed,
        )
        self.show_files_cb.pack(anchor=tk.W)
        create_tooltip(self.show_files_cb, self.texts["tooltip_show_files"])

        self.show_folders = tk.BooleanVar(value=self.settings.show_folders_value)
        self.show_folders_cb = ttk.Checkbutton(
            left_options,
            text=self.texts["show_folders"],
            variable=self.show_folders,
            command=self.on_setting_option_changed,
        )
        self.show_folders_cb.pack(anchor=tk.W)
        create_tooltip(self.show_folders_cb, self.texts["tooltip_show_folders"])

        self.preserve_tree_state = tk.BooleanVar(value=self.preserve_tree_state_value)
        self.preserve_tree_cb = ttk.Checkbutton(
            left_options,
            text=self.texts["preserve_tree"],
            variable=self.preserve_tree_state,
            command=self.on_setting_option_changed,
        )
        self.preserve_tree_cb.pack(anchor=tk.W)
        create_tooltip(
            self.preserve_tree_cb,
            self.texts["tooltip_preserve_tree"],
        )

        self.use_relative_path = tk.BooleanVar(
            value=self.settings.use_relative_path_value
        )
        self.relative_path_cb = ttk.Checkbutton(
            left_options,
            text=self.texts["use_relative_path"],
            variable=self.use_relative_path,
            command=self.on_setting_option_changed,
        )
        self.relative_path_cb.pack(anchor=tk.W)
        create_tooltip(self.relative_path_cb, self.texts["tooltip_use_relative"])

        self.format_btn = ttk.Button(
            left_options,
            text=self.texts["format_settings"],
            command=self.show_format_settings,
        )
        self.format_btn.pack(anchor=tk.W, pady=5)
        create_tooltip(self.format_btn, self.texts["tooltip_format_settings"])

        right_options = ttk.Frame(options_frame)
        right_options.pack(side=tk.LEFT, fill=tk.X, expand=True)

        depth_frame = ttk.Frame(right_options)
        depth_frame.pack(anchor=tk.W)
        self.depth_label = ttk.Label(depth_frame, text=self.texts["max_depth"])
        self.depth_label.pack(side=tk.LEFT)
        create_tooltip(self.depth_label, self.texts["tooltip_max_depth"])

        self.max_depth = tk.IntVar(value=self.settings.max_depth_value)
        self.depth_spinbox = ttk.Spinbox(
            depth_frame,
            from_=0,
            to=100,
            width=5,
            textvariable=self.max_depth,
            command=self.on_setting_option_changed,
        )
        self.depth_spinbox.pack(side=tk.LEFT, padx=5)
        create_tooltip(self.depth_spinbox, self.texts["tooltip_spinbox"])

        filter_frame = ttk.Frame(right_options)
        filter_frame.pack(anchor=tk.W, pady=5)
        self.filter_label = ttk.Label(filter_frame, text=self.texts["file_filter"])
        self.filter_label.pack(side=tk.LEFT)
        create_tooltip(
            self.filter_label,
            self.texts["tooltip_file_filter"],
        )

        self.file_filter = tk.StringVar(value=self.settings.file_filter_value)
        filter_entry = ttk.Entry(filter_frame, textvariable=self.file_filter, width=20)
        filter_entry.pack(side=tk.LEFT, padx=5)

        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=5)

        self.generate_btn = ttk.Button(
            btn_frame, text=self.texts["reset"], command=self.generate_tree
        )
        self.generate_btn.pack(side=tk.LEFT, padx=5)
        create_tooltip(
            self.generate_btn,
            self.texts["tooltip_reset"],
        )

        self.copy_btn = ttk.Button(
            btn_frame, text=self.texts["copy_tree"], command=self.copy_to_clipboard
        )
        self.copy_btn.pack(side=tk.LEFT, padx=5)
        create_tooltip(self.copy_btn, self.texts["tooltip_copy_tree"])

        self.save_btn = ttk.Button(
            btn_frame, text=self.texts["save_to_file"], command=self.save_to_file
        )
        self.save_btn.pack(side=tk.LEFT, padx=5)
        create_tooltip(self.save_btn, self.texts["tooltip_save_file"])

        self.result_frame = ttk.LabelFrame(
            main_frame, text=self.texts["dir_tree"], padding="10"
        )
        self.result_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        self.tree = ttk.Treeview(self.result_frame, selectmode="extended", show="tree")
        self.tree["columns"] = ("checked",)
        self.tree.column("#0", width=500, minwidth=200)
        self.tree.column("checked", width=50, minwidth=50, anchor=tk.CENTER)

        tree_scroll_y = ttk.Scrollbar(
            self.result_frame, orient="vertical", command=self.tree.yview
        )
        tree_scroll_x = ttk.Scrollbar(
            self.result_frame, orient="horizontal", command=self.tree.xview
        )
        self.tree.configure(
            yscrollcommand=tree_scroll_y.set, xscrollcommand=tree_scroll_x.set
        )

        tree_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        tree_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.tree.tag_configure("gray", foreground="gray")

        self.tree.bind("<ButtonRelease-1>", self.on_tree_click)
        self.tree.bind("<<TreeviewOpen>>", self.on_tree_open)
        self.tree.bind("<<TreeviewClose>>", self.on_tree_close)
        self.tree.bind("<Button-3>", self.show_context_menu)

        self.dir_path.trace_add("write", self.on_dir_changed)
        self.file_filter.trace_add("write", self.on_setting_option_changed)

    def open_changelog(self):
        """打开更新日志页面"""
        changelog_url = (
            "https://github.com/sansan0/ai-code-context-helper/blob/master/CHANGELOG.md"
        )
        webbrowser.open(changelog_url)

    def show_qrcode(self):
        """显示公众号二维码图片"""
        qrcode_window = tk.Toplevel(self.root)
        qrcode_window.title("关注公众号")
        qrcode_window.transient(self.root)
        qrcode_window.grab_set()

        qrcode_window.geometry("500x260")
        self.center_window(qrcode_window)

        # 创建一个框架来容纳图片和按钮
        frame = ttk.Frame(qrcode_window)
        frame.pack(fill=tk.BOTH, expand=True)

        qrcode_path = Path(__file__).parent / "resources" / "weixin.png"

        try:
            img = Image.open(qrcode_path)
            img = img.resize((500, 182), Image.LANCZOS)
            photo = ImageTk.PhotoImage(img)

            img_label = ttk.Label(frame, image=photo)
            img_label.image = photo  # 保持引用防止被垃圾回收
            img_label.pack(pady=10)

            text_label = ttk.Label(
                frame, text="扫码关注公众号，支持作者更新~", font=("微软雅黑", 10)
            )
            text_label.pack(pady=5)

        except Exception as e:
            error_label = ttk.Label(
                frame, text=f"无法加载图片: {str(e)}", foreground="red"
            )
            error_label.pack(pady=20)

    def change_language(self, *args):
        """更改界面语言"""
        selected_display_name = self.language_var.get()
        selected_language = self.language_names.get(selected_display_name)

        if selected_language and selected_language != self.current_language:
            self.current_language = selected_language
            self.texts = LANGUAGES[self.current_language]
            self.settings.current_language = self.current_language
            self.settings.texts = self.texts
            self.settings.settings_changed = True
            self.update_ui_texts()

    def update_ui_texts(self):
        """更新界面上的所有文本"""
        # 更新标签、按钮等控件文本
        self.status_var.set(self.texts["ready"])

        # 更新主窗口标题（包含版本号）
        self.app_title_text = self.texts["app_title"]
        self.root.title(f"{self.texts['app_title']} v{self.version}")

        # 更新设置框标题
        self.control_frame.configure(text=self.texts["settings"])

        # 更新语言标签
        self.lang_label.configure(text=self.texts["language"])

        # 更新路径标签
        self.dir_label.configure(text=self.texts["dir_path"])

        # 更新按钮文本
        self.browse_btn.configure(text=self.texts["browse"])
        self.generate_btn.configure(text=self.texts["reset"])
        self.copy_btn.configure(text=self.texts["copy_tree"])
        self.save_btn.configure(text=self.texts["save_to_file"])
        self.format_btn.configure(text=self.texts["format_settings"])

        # 更新复选框文本
        self.show_hidden_cb.configure(text=self.texts["show_hidden"])
        self.show_files_cb.configure(text=self.texts["show_files"])
        self.show_folders_cb.configure(text=self.texts["show_folders"])
        self.preserve_tree_cb.configure(text=self.texts["preserve_tree"])
        self.relative_path_cb.configure(text=self.texts["use_relative_path"])

        # 更新深度和过滤器标签
        self.depth_label.configure(text=self.texts["max_depth"])
        self.filter_label.configure(text=self.texts["file_filter"])

        # 更新目录树框标题
        self.result_frame.configure(text=self.texts["dir_tree"])

        # 更新工具提示
        self.update_tooltips()

    def update_tooltips(self):
        """更新所有工具提示"""
        create_tooltip(self.status_bar, self.texts["tooltip_status_bar"])
        create_tooltip(self.dir_label, self.texts["tooltip_dir_path"])
        create_tooltip(self.browse_btn, self.texts["tooltip_browse"])
        create_tooltip(self.show_hidden_cb, self.texts["tooltip_show_hidden"])
        create_tooltip(self.show_files_cb, self.texts["tooltip_show_files"])
        create_tooltip(self.show_folders_cb, self.texts["tooltip_show_folders"])
        create_tooltip(self.preserve_tree_cb, self.texts["tooltip_preserve_tree"])
        create_tooltip(self.relative_path_cb, self.texts["tooltip_use_relative"])
        create_tooltip(self.format_btn, self.texts["tooltip_format_settings"])
        create_tooltip(self.depth_label, self.texts["tooltip_max_depth"])
        create_tooltip(self.depth_spinbox, self.texts["tooltip_spinbox"])
        create_tooltip(self.filter_label, self.texts["tooltip_file_filter"])
        create_tooltip(self.generate_btn, self.texts["tooltip_reset"])
        create_tooltip(self.copy_btn, self.texts["tooltip_copy_tree"])
        create_tooltip(self.save_btn, self.texts["tooltip_save_file"])

    def add_to_history(self, directory):
        """将目录添加到历史记录中"""
        if not directory:
            return

        # 标准化路径格式为Windows风格
        directory = normalize_path(directory)

        if directory in self.dir_history:
            self.dir_history.remove(directory)

        self.dir_history.insert(0, directory)

        if len(self.dir_history) > self.settings.max_history_items:
            self.dir_history = self.dir_history[: self.settings.max_history_items]

        self.dir_entry["values"] = self.dir_history
        self.settings.dir_history = self.dir_history
        self.settings.settings_changed = True

    def remove_from_history(self, directory):
        """从历史记录中删除指定的目录"""
        if directory in self.dir_history:
            self.dir_history.remove(directory)
            self.dir_entry["values"] = self.dir_history
            self.settings.dir_history = self.dir_history
            self.settings.settings_changed = True
            self.status_var.set(self.texts["status_history_removed"].format(directory))

    def on_combobox_select(self, event):
        """当从Combobox中选择一个历史路径时的处理函数"""
        directory = self.dir_path.get().strip()
        if directory and Path(directory).is_dir():
            self.generate_tree()

    def show_dir_history_menu(self, event):
        """显示目录历史记录的右键菜单"""
        history_menu = tk.Menu(self.root, tearoff=0)

        current_dir = self.dir_path.get().strip()
        current_dir = normalize_path(current_dir)

        # 显示所有历史路径项
        if self.dir_history:
            for dir_path in self.dir_history:
                history_menu.add_command(
                    label=self.texts["remove_from_history"].format(dir_path),
                    command=lambda path=dir_path: self.remove_from_history(path),
                )

            history_menu.add_separator()
            history_menu.add_command(
                label=self.texts["clear_history"], command=self.clear_all_history
            )
        else:
            history_menu.add_command(label=self.texts["no_history"], state="disabled")

        history_menu.post(event.x_root, event.y_root)

    def clear_all_history(self):
        """清空所有目录历史记录"""
        self.dir_history = []
        self.dir_entry["values"] = []
        self.settings.dir_history = self.dir_history
        self.settings.settings_changed = True
        self.status_var.set(self.texts["status_history_cleared"])

    def expand_all(self):
        """递归展开选中的目录及其所有子目录"""
        selected_items = self.tree.selection()
        if not selected_items:
            return

        for item in selected_items:
            self._expand_item_recursively(item)

        self.status_var.set("已完全展开选中的目录")

    def _expand_item_recursively(self, item):
        """递归展开单个项目及其所有子项"""
        self.tree.item(item, open=True)

        children = self.tree.get_children(item)
        if not children:
            return

        has_dummy = False
        for child in children:
            tags = self.tree.item(child, "tags")
            if tags and "dummy" in tags:
                has_dummy = True
                self.tree.delete(child)

        if has_dummy:
            parent_path = None
            for path, tree_id in self.tree_items.items():
                if tree_id == item:
                    parent_path = path
                    break

            if parent_path:
                level = 0
                temp_id = item
                while temp_id != "":
                    parent = self.tree.parent(temp_id)
                    if parent != "":
                        level += 1
                    temp_id = parent

                is_parent_checked = item in self.checked_items

                if self.preserve_tree_state.get():
                    old_tree_items = self.tree_items.copy()
                    old_checked_items = self.checked_items.copy()
                    old_open_items = {
                        item_id
                        for item_id in self.tree_items.values()
                        if self.tree.item(item_id, "open")
                    }
                    self._populate_tree_with_state(
                        Path(parent_path),
                        item,
                        level,
                        old_tree_items,
                        old_checked_items,
                        old_open_items,
                    )
                else:
                    self._populate_tree(Path(parent_path), item, level)

                if not is_parent_checked:
                    self._uncheck_all_children(item)

        for child in self.tree.get_children(item):
            tags = self.tree.item(child, "tags")
            if tags and "dummy" in tags:
                continue

            self._expand_item_recursively(child)

    def on_setting_option_changed(self, *args):
        """当设置选项改变时的处理函数"""
        self.settings.show_hidden_value = self.show_hidden.get()
        self.settings.show_files_value = self.show_files.get()
        self.settings.show_folders_value = self.show_folders.get()
        self.settings.use_relative_path_value = self.use_relative_path.get()
        self.settings.max_depth_value = self.max_depth.get()
        self.settings.file_filter_value = self.file_filter.get()
        self.settings.preserve_tree_state_value = self.preserve_tree_state.get()
        self.settings.settings_changed = True

        directory = self.dir_path.get().strip()
        if directory and Path(directory).is_dir():
            self.generate_tree()

    def on_dir_changed(self, *args):
        """当目录路径改变时的处理函数"""
        directory = self.dir_path.get().strip()
        if directory and Path(directory).is_dir():
            self.add_to_history(directory)
            self.generate_tree()

    def show_format_settings(self):
        """显示文本格式设置对话框，允许用户配置路径和代码的前缀后缀"""
        format_window = tk.Toplevel(self.root)
        format_window.title(self.texts["format_settings"])
        format_window.geometry("500x350")
        format_window.minsize(500, 350)
        format_window.transient(self.root)
        format_window.grab_set()

        self.center_window(format_window)

        frame = ttk.LabelFrame(
            format_window, text=self.texts["format_settings"], padding="10"
        )
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        prefix_label = ttk.Label(frame, text=self.texts["path_prefix"])
        prefix_label.grid(row=0, column=0, sticky=tk.W, pady=5)
        create_tooltip(prefix_label, self.texts["tooltip_prefix_entry"])

        # 将实际换行符替换为可见的字符串表示
        display_path_prefix = self.PATH_PREFIX.replace("\n", "\\n")
        path_prefix_var = tk.StringVar(value=display_path_prefix)
        prefix_entry = ttk.Entry(frame, textvariable=path_prefix_var, width=40)
        prefix_entry.grid(row=0, column=1, sticky=tk.W + tk.E, pady=5)
        create_tooltip(prefix_entry, self.texts["tooltip_prefix_entry"])

        suffix_label = ttk.Label(frame, text=self.texts["path_suffix"])
        suffix_label.grid(row=1, column=0, sticky=tk.W, pady=5)
        create_tooltip(suffix_label, self.texts["tooltip_suffix_entry"])

        display_path_suffix = self.PATH_SUFFIX.replace("\n", "\\n")
        path_suffix_var = tk.StringVar(value=display_path_suffix)
        suffix_entry = ttk.Entry(frame, textvariable=path_suffix_var, width=40)
        suffix_entry.grid(row=1, column=1, sticky=tk.W + tk.E, pady=5)
        create_tooltip(suffix_entry, self.texts["tooltip_suffix_entry"])

        code_prefix_label = ttk.Label(frame, text=self.texts["code_prefix"])
        code_prefix_label.grid(row=2, column=0, sticky=tk.W, pady=5)
        create_tooltip(code_prefix_label, self.texts["tooltip_prefix_entry"])

        display_code_prefix = self.CODE_PREFIX.replace("\n", "\\n")
        code_prefix_var = tk.StringVar(value=display_code_prefix)
        code_prefix_entry = ttk.Entry(frame, textvariable=code_prefix_var, width=40)
        code_prefix_entry.grid(row=2, column=1, sticky=tk.W + tk.E, pady=5)
        create_tooltip(code_prefix_entry, self.texts["tooltip_prefix_entry"])

        code_suffix_label = ttk.Label(frame, text=self.texts["code_suffix"])
        code_suffix_label.grid(row=3, column=0, sticky=tk.W, pady=5)
        create_tooltip(code_suffix_label, self.texts["tooltip_suffix_entry"])

        display_code_suffix = self.CODE_SUFFIX.replace("\n", "\\n")
        code_suffix_var = tk.StringVar(value=display_code_suffix)
        code_suffix_entry = ttk.Entry(frame, textvariable=code_suffix_var, width=40)
        code_suffix_entry.grid(row=3, column=1, sticky=tk.W + tk.E, pady=5)
        create_tooltip(code_suffix_entry, self.texts["tooltip_suffix_entry"])

        # 添加自动换行功能，设置合适的宽度
        tip_label = ttk.Label(frame, text=self.texts["note"], wraplength=450)
        tip_label.grid(row=4, column=0, columnspan=2, sticky=tk.W, pady=10)

        btn_frame = ttk.Frame(format_window)
        btn_frame.pack(fill=tk.X, pady=10)

        def save_settings():
            self.PATH_PREFIX = path_prefix_var.get().replace("\\n", "\n")
            self.PATH_SUFFIX = path_suffix_var.get().replace("\\n", "\n")
            self.CODE_PREFIX = code_prefix_var.get().replace("\\n", "\n")
            self.CODE_SUFFIX = code_suffix_var.get().replace("\\n", "\n")

            # 更新设置管理器中的值
            self.settings.PATH_PREFIX = self.PATH_PREFIX
            self.settings.PATH_SUFFIX = self.PATH_SUFFIX
            self.settings.CODE_PREFIX = self.CODE_PREFIX
            self.settings.CODE_SUFFIX = self.CODE_SUFFIX
            self.settings.settings_changed = True

            format_window.destroy()
            self.status_var.set(self.texts["format_text_updated"])

        save_btn = ttk.Button(btn_frame, text=self.texts["save"], command=save_settings)
        save_btn.pack(side=tk.RIGHT, padx=5)
        create_tooltip(save_btn, self.texts["tooltip_save_btn"])

        cancel_btn = ttk.Button(
            btn_frame, text=self.texts["cancel"], command=format_window.destroy
        )
        cancel_btn.pack(side=tk.RIGHT, padx=5)
        create_tooltip(cancel_btn, self.texts["tooltip_cancel_btn"])

    def center_window(self, window):
        """将窗口居中显示在屏幕上"""
        window.update_idletasks()
        width = window.winfo_width()
        height = window.winfo_height()
        x = (window.winfo_screenwidth() // 2) - (width // 2)
        y = (window.winfo_screenheight() // 2) - (height // 2)
        window.geometry("{}x{}+{}+{}".format(width, height, x, y))

    def browse_directory(self):
        """打开文件夹选择对话框，允许用户浏览并选择目录"""
        directory = filedialog.askdirectory()
        if directory:
            # 标准化为Windows风格路径
            directory = normalize_path(directory)
            self.dir_path.set(directory)
            self.add_to_history(directory)

    def generate_tree(self):
        """生成并显示目录树结构"""
        directory = self.dir_path.get().strip()
        directory_path = Path(directory)
        if not directory or not directory_path.is_dir():
            self.status_var.set(self.texts["error_invalid_dir"])
            return

        old_tree_items = {}
        old_checked_items = set()
        old_open_items = set()

        if self.preserve_tree_state.get() and self.tree_items:
            old_tree_items = self.tree_items.copy()
            old_checked_items = self.checked_items.copy()
            old_open_items = {
                item_id
                for item_id in self.tree_items.values()
                if self.tree.item(item_id, "open")
            }

        self.tree.delete(*self.tree.get_children())
        self.tree_items = {}
        self.checked_items = set()
        self.status_var.set(self.texts["generating_tree"])
        self.root.update_idletasks()

        try:
            dir_name = directory_path.name
            if not dir_name:
                dir_name = str(directory_path)

            root_id = self.tree.insert(
                "", "end", text=dir_name, open=True, values=("✓",)
            )
            self.tree_items[str(directory_path)] = root_id
            self.checked_items.add(root_id)

            if self.preserve_tree_state.get():
                self._populate_tree_with_state(
                    directory_path,
                    root_id,
                    0,
                    old_tree_items,
                    old_checked_items,
                    old_open_items,
                )
            else:
                self._populate_tree(directory_path, root_id, 0)

            if self.preserve_tree_state.get():
                self.tree.item(root_id, open=True)

            self.status_var.set(self.texts["status_tree_generated"].format(directory))
        except Exception as e:
            self.status_var.set(self.texts["error_msg"].format(str(e)))

    def _populate_tree(self, directory_path, parent_id, level):
        """递归填充目录树视图"""
        max_depth = self.max_depth.get()
        if max_depth > 0 and level >= max_depth:
            return

        try:
            entries = list(directory_path.iterdir())
        except PermissionError:
            error_id = self.tree.insert(
                parent_id,
                "end",
                text=self.texts["error_permission_denied"],
                values=("",),
            )
            self.tree.item(error_id, tags=("gray",))
            return
        except Exception as e:
            error_id = self.tree.insert(
                parent_id,
                "end",
                text=self.texts["error_msg"].format(str(e)),
                values=("",),
            )
            self.tree.item(error_id, tags=("gray",))
            return

        if not self.show_hidden.get():
            entries = [
                e
                for e in entries
                if not e.name.startswith(".")
                and not (
                    os.name == "nt"
                    and e.is_file()
                    and bool(e.stat().st_file_attributes & 2)
                )
            ]

        filter_pattern = self.file_filter.get().strip()
        if filter_pattern:
            try:
                pattern = re.compile(filter_pattern)
                entries = [e for e in entries if pattern.search(e.name)]
            except re.error:
                pass

        dirs = []
        files = []

        for entry in sorted(entries, key=lambda e: e.name.lower()):
            if entry.is_dir():
                if self.show_folders.get():
                    dirs.append(entry)
            elif self.show_files.get():
                files.append(entry)

        for d in dirs:
            item_id = self.tree.insert(
                parent_id, "end", text=d.name, values=("✓",), open=False
            )
            self.tree_items[str(d)] = item_id
            self.checked_items.add(item_id)

            has_contents = False
            try:
                next(d.iterdir(), None)
                has_contents = True
            except (PermissionError, OSError, StopIteration):
                pass

            if has_contents:
                self.tree.insert(item_id, "end", text="", tags=("dummy",))

        for f in files:
            item_id = self.tree.insert(parent_id, "end", text=f.name, values=("✓",))
            self.tree_items[str(f)] = item_id
            self.checked_items.add(item_id)

    def _populate_tree_with_state(
        self,
        directory_path,
        parent_id,
        level,
        old_tree_items,
        old_checked_items,
        old_open_items,
    ):
        """带状态保留的目录树填充函数"""
        max_depth = self.max_depth.get()
        if max_depth > 0 and level >= max_depth:
            return

        try:
            entries = list(directory_path.iterdir())
        except PermissionError:
            error_id = self.tree.insert(
                parent_id,
                "end",
                text=self.texts["error_permission_denied"],
                values=("",),
            )
            self.tree.item(error_id, tags=("gray",))
            return
        except Exception as e:
            error_id = self.tree.insert(
                parent_id,
                "end",
                text=self.texts["error_msg"].format(str(e)),
                values=("",),
            )
            self.tree.item(error_id, tags=("gray",))
            return

        if not self.show_hidden.get():
            entries = [
                e
                for e in entries
                if not e.name.startswith(".")
                and not (
                    os.name == "nt"
                    and e.is_file()
                    and bool(e.stat().st_file_attributes & 2)
                )
            ]

        filter_pattern = self.file_filter.get().strip()
        if filter_pattern:
            try:
                pattern = re.compile(filter_pattern)
                entries = [e for e in entries if pattern.search(e.name)]
            except re.error:
                pass

        dirs = []
        files = []

        for entry in sorted(entries, key=lambda e: e.name.lower()):
            if entry.is_dir():
                if self.show_folders.get():
                    dirs.append(entry)
            elif self.show_files.get():
                files.append(entry)

        for d in dirs:
            path_str = str(d)

            old_id = None
            checked = True
            is_open = False

            for old_path, old_item_id in old_tree_items.items():
                if old_path == path_str:
                    old_id = old_item_id
                    checked = old_id in old_checked_items
                    is_open = old_id in old_open_items
                    break

            item_id = self.tree.insert(
                parent_id,
                "end",
                text=d.name,
                values=("✓" if checked else ""),
                open=is_open,
            )

            self.tree_items[path_str] = item_id

            if checked:
                self.checked_items.add(item_id)
            else:
                self.tree.item(item_id, tags=("gray",))

            has_contents = False
            try:
                next(d.iterdir(), None)
                has_contents = True
            except (PermissionError, OSError, StopIteration):
                pass

            if has_contents:
                if is_open:
                    self._populate_tree_with_state(
                        d,
                        item_id,
                        level + 1,
                        old_tree_items,
                        old_checked_items,
                        old_open_items,
                    )
                else:
                    self.tree.insert(item_id, "end", text="", tags=("dummy",))

        for f in files:
            path_str = str(f)

            old_id = None
            checked = True

            for old_path, old_item_id in old_tree_items.items():
                if old_path == path_str:
                    old_id = old_item_id
                    checked = old_id in old_checked_items
                    break

            item_id = self.tree.insert(
                parent_id, "end", text=f.name, values=("✓" if checked else "")
            )

            self.tree_items[path_str] = item_id

            if checked:
                self.checked_items.add(item_id)
            else:
                self.tree.item(item_id, tags=("gray",))

    def on_tree_open(self, event):
        """处理树节点展开事件，加载子节点内容"""
        item_id = self.tree.focus()

        children = self.tree.get_children(item_id)
        if not children:
            return

        has_dummy = False
        for child in children:
            tags = self.tree.item(child, "tags")
            if tags and "dummy" in tags:
                has_dummy = True
                self.tree.delete(child)

        if has_dummy:
            parent_path = None
            for path, tree_id in self.tree_items.items():
                if tree_id == item_id:
                    parent_path = path
                    break

            if parent_path:
                level = 0
                temp_id = item_id
                while temp_id != "":
                    parent = self.tree.parent(temp_id)
                    if parent != "":
                        level += 1
                    temp_id = parent

                is_parent_checked = item_id in self.checked_items

                if self.preserve_tree_state.get():
                    old_tree_items = self.tree_items.copy()
                    old_checked_items = self.checked_items.copy()
                    old_open_items = {
                        item_id
                        for item_id in self.tree_items.values()
                        if self.tree.item(item_id, "open")
                    }
                    self._populate_tree_with_state(
                        Path(parent_path),
                        item_id,
                        level,
                        old_tree_items,
                        old_checked_items,
                        old_open_items,
                    )
                else:
                    self._populate_tree(Path(parent_path), item_id, level)

                if not is_parent_checked:
                    self._uncheck_all_children(item_id)

    def on_tree_close(self, event):
        """处理树节点关闭的事件"""
        pass

    def _check_all_children(self, parent):
        """递归选中所有子项"""
        for child in self.tree.get_children(parent):
            tags = self.tree.item(child, "tags")
            if tags and "dummy" in tags:
                continue

            self.tree.item(child, values=("✓",))
            self.checked_items.add(child)
            self.tree.item(child, tags=())
            self._check_all_children(child)

    def on_tree_click(self, event):
        """处理树节点点击事件，切换选中状态"""
        item = self.tree.identify_row(event.y)
        if not item:
            return

        column = self.tree.identify_column(event.x)

        if column == "#1":
            values = self.tree.item(item, "values")
            if values and values[0] == "✓":
                self.tree.item(item, values=("",))
                self.checked_items.discard(item)
                self.tree.item(item, tags=("gray",))
                self._uncheck_all_children(item)
            else:
                self.tree.item(item, values=("✓",))
                self.checked_items.add(item)
                self.tree.item(item, tags=())
                self._check_all_children(item)
                self._ensure_parents_checked(item)

    def _uncheck_all_children(self, parent):
        """递归取消选中所有子项"""
        for child in self.tree.get_children(parent):
            tags = self.tree.item(child, "tags")
            if tags and "dummy" in tags:
                continue

            self.tree.item(child, values=("",))
            self.checked_items.discard(child)
            self.tree.item(child, tags=("gray",))
            self._uncheck_all_children(child)

    def _ensure_parents_checked(self, item):
        """确保所有父项都被选中"""
        parent = self.tree.parent(item)
        if parent:
            if parent not in self.checked_items:
                self.tree.item(parent, values=("✓",))
                self.checked_items.add(parent)
                self.tree.item(parent, tags=())
            self._ensure_parents_checked(parent)

    def _update_parent_check_state(self, parent):
        """更新父项的选中状态，基于子项的状态"""
        if parent:
            children = self.tree.get_children(parent)
            any_checked = False

            for child in children:
                tags = self.tree.item(child, "tags")
                if tags and "dummy" in tags:
                    continue

                if child in self.checked_items:
                    any_checked = True
                    break

            if any_checked:
                if parent not in self.checked_items:
                    self.tree.item(parent, values=("✓",))
                    self.checked_items.add(parent)
                    self.tree.item(parent, tags=())
            else:
                self.tree.item(parent, values=("",))
                self.checked_items.discard(parent)
                self.tree.item(parent, tags=("gray",))
                self._update_parent_check_state(self.tree.parent(parent))

    def copy_to_clipboard(self):
        """将选中的目录树文本表示复制到剪贴板"""
        text = self._get_tree_text()

        if text:
            self.root.clipboard_clear()
            self.root.clipboard_append(text)
            self.status_var.set(self.texts["status_copied_to_clipboard"])
        else:
            self.status_var.set(self.texts["status_no_selection"])

    def _get_tree_text(self):
        """获取目录树的文本表示，只包含选中的且可见的项目"""
        text = ""

        root_items = self.tree.get_children()
        if not root_items:
            return text

        root_item = root_items[0]
        if root_item in self.checked_items:
            root_text = self.tree.item(root_item, "text")
            text = root_text + "\n"
            text = self._build_tree_text(root_item, "", text)

        return text

    def _build_tree_text(self, parent_id, prefix, text):
        """递归构建目录树的文本表示"""
        is_open = self.tree.item(parent_id, "open")

        children = self.tree.get_children(parent_id)
        if not children or not is_open:
            return text

        checked_children = [c for c in children if c in self.checked_items]
        if not checked_children:
            return text

        for i, child in enumerate(children):
            tags = self.tree.item(child, "tags")
            if tags and "dummy" in tags:
                continue

            if child not in self.checked_items:
                continue

            is_last = (i == len(children) - 1) or all(
                c not in self.checked_items for c in children[i + 1 :]
            )

            if is_last:
                line_prefix = prefix + "└── "
                next_prefix = prefix + "    "
            else:
                line_prefix = prefix + "├── "
                next_prefix = prefix + "│   "

            item_text = self.tree.item(child, "text")
            text += line_prefix + item_text + "\n"
            text = self._build_tree_text(child, next_prefix, text)

        return text

    def save_to_file(self):
        """将目录树文本保存到文件"""
        text = self._get_tree_text()

        if not text:
            self.status_var.set(self.texts["status_no_selection"])
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")],
        )

        if file_path:
            try:
                Path(file_path).write_text(text, encoding="utf-8")
                self.status_var.set(self.texts["status_saved_to"].format(file_path))
            except Exception as e:
                self.status_var.set(self.texts["status_save_failed"].format(str(e)))

    def get_relative_path(self, path):
        """获取相对于根目录的路径"""
        if self.use_relative_path.get():
            root_dir = Path(normalize_path(self.dir_path.get().strip()))
            path_obj = Path(normalize_path(str(path)))
            try:
                rel_path = path_obj.relative_to(root_dir)
                # 使用反斜杠
                return f"{root_dir.name}\\{rel_path}".replace("/", "\\")
            except ValueError:
                return str(path_obj).replace("/", "\\")
        else:
            return str(Path(path)).replace("/", "\\")

    def format_path(self, path):
        """使用设定的前缀和后缀格式化路径"""
        return f"{self.PATH_PREFIX}{path}{self.PATH_SUFFIX}"

    def format_code(self, code):
        """使用设定的前缀和后缀格式化代码"""
        return f"{self.CODE_PREFIX}{code}{self.CODE_SUFFIX}"

    def show_context_menu(self, event):
        """显示右键上下文菜单"""
        item = self.tree.identify_row(event.y)
        if not item:
            return

        if not self.tree.selection():
            self.tree.selection_set(item)
        elif item not in self.tree.selection():
            self.tree.selection_set(item)

        self.context_menu.delete(0, tk.END)

        is_directory = False
        for path, tree_id in self.tree_items.items():
            if tree_id == item and Path(path).is_dir():
                is_directory = True
                break

        if is_directory:
            self.context_menu.add_command(
                label=self.texts["expand_all"], command=self.expand_all
            )

        self.context_menu.add_command(
            label=self.texts["copy_path_and_code"], command=self.copy_both
        )
        self.context_menu.add_command(
            label=self.texts["copy_path"], command=self.copy_path
        )

        self.context_menu.add_command(
            label=self.texts["copy_code"], command=self.copy_code
        )
        self.context_menu.add_command(
            label=self.texts["copy_filename"], command=self.copy_filename
        )

        self.context_menu.post(event.x_root, event.y_root)

    def _collect_files_recursively(
        self, dir_path, checked_only=True, parent_checked=True
    ):
        """递归收集目录中的所有文件"""
        all_files = []

        try:
            for item in dir_path.iterdir():
                item_path_str = str(item)
                item_in_tree = item_path_str in self.tree_items

                if item_in_tree:
                    item_id = self.tree_items[item_path_str]
                    item_checked = item_id in self.checked_items
                else:
                    item_checked = parent_checked

                if checked_only and not item_checked:
                    continue

                if item.is_file():
                    all_files.append(item)
                elif item.is_dir():
                    all_files.extend(
                        self._collect_files_recursively(
                            item, checked_only, item_checked
                        )
                    )
        except Exception:
            pass

        return all_files

    def process_selected_files(self, content_processor=None):
        """通用文件处理函数，支持自定义内容处理器

        Args:
            content_processor: 接收path_obj并返回处理后内容的函数
                               如果为None，则仅收集路径

        Returns:
            处理结果的列表和处理文件数量
        """
        selected_items = self.tree.selection()
        if not selected_items:
            return [], 0

        results = []
        processed_paths = set()

        for item in selected_items:
            if item not in self.checked_items:
                continue

            path = None
            for p, tree_id in self.tree_items.items():
                if tree_id == item:
                    path = p
                    break

            if not path:
                continue

            path_obj = Path(path)

            if path_obj.is_file():
                if str(path_obj) not in processed_paths:
                    processed_paths.add(str(path_obj))

                    if content_processor:
                        try:
                            if is_text_file(str(path_obj)):
                                result = content_processor(path_obj)
                                if result:
                                    results.append(result)
                        except Exception as e:
                            self.status_var.set(f"处理文件出错: {str(e)}")
                    else:
                        # 仅添加路径
                        results.append(
                            self.format_path(self.get_relative_path(path_obj))
                        )

            elif path_obj.is_dir():
                all_files = self._collect_files_recursively(path_obj, True, True)
                for file in all_files:
                    if str(file) not in processed_paths:
                        processed_paths.add(str(file))

                        if content_processor:
                            try:
                                if is_text_file(str(file)):
                                    result = content_processor(file)
                                    if result:
                                        results.append(result)
                            except Exception:
                                # 跳过无法处理的文件
                                continue
                        else:
                            # 仅添加路径
                            results.append(
                                self.format_path(self.get_relative_path(file))
                            )

        return results, len(results)

    def copy_path(self):
        """复制选中文件或目录的路径到剪贴板"""
        results, count = self.process_selected_files()

        if results:
            combined = "\n".join(results)
            self.root.clipboard_clear()
            self.root.clipboard_append(combined)
            self.status_var.set(self.texts["status_paths_copied"].format(count))
        else:
            self.status_var.set(self.texts["status_no_paths"])

    def copy_code(self):
        """复制选中文件的代码内容到剪贴板"""

        def code_processor(path_obj):
            try:
                code = read_file_content(path_obj)
                return self.format_code(code)
            except:
                return None

        results, count = self.process_selected_files(code_processor)

        if results:
            combined = "\n\n".join(results)
            self.root.clipboard_clear()
            self.root.clipboard_append(combined)
            self.status_var.set(self.texts["status_code_copied"].format(count))
        else:
            self.status_var.set(self.texts["status_no_text_files"])

    def copy_filename(self):
        """复制选中文件或目录的文件名到剪贴板"""
        selected_items = self.tree.selection()
        if not selected_items:
            self.status_var.set(self.texts["status_no_selection"])
            return

        filenames = []
        for item in selected_items:
            if item not in self.checked_items:
                continue

            # 查找item对应的路径
            path = None
            for p, tree_id in self.tree_items.items():
                if tree_id == item:
                    path = p
                    break

            if path:
                path_obj = Path(path)
                filenames.append(path_obj.name)

        if filenames:
            combined = "\n".join(filenames)
            self.root.clipboard_clear()
            self.root.clipboard_append(combined)
            self.status_var.set(
                self.texts["status_filenames_copied"].format(len(filenames))
            )
        else:
            self.status_var.set(self.texts["status_no_selection"])

    def copy_both(self):
        """同时复制选中文件的路径和代码内容到剪贴板"""

        def both_processor(path_obj):
            try:
                code = read_file_content(path_obj)
                formatted_path = self.format_path(self.get_relative_path(path_obj))
                formatted_code = self.format_code(code)
                return f"{formatted_path}\n\n{formatted_code}\n\n\n\n"
            except:
                return None

        results, count = self.process_selected_files(both_processor)

        if results:
            combined = "".join(results)
            self.root.clipboard_clear()
            self.root.clipboard_append(combined)
            self.status_var.set(self.texts["status_path_code_copied"].format(count))
        else:
            self.status_var.set(self.texts["status_no_text_files"])
