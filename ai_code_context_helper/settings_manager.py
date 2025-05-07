import json
from pathlib import Path
import os
import sys


class SettingsManager:
    """管理应用程序设置的类"""

    def __init__(self, languages):
        script_dir = Path(os.path.dirname(os.path.abspath(sys.argv[0])))
        # 如果是开发模式，使用当前包目录
        if os.path.exists(os.path.join(script_dir, "resources")):
            self.settings_file = script_dir / "resources" / "default_settings.json"
        # 如果是打包后的程序，使用打包后的路径
        else:
            self.settings_file = script_dir / "default_settings.json"
        self.languages = languages

        # 默认设置
        self.PATH_PREFIX = "文件路径: "
        self.PATH_SUFFIX = "\n"
        self.CODE_PREFIX = "```\n"
        self.CODE_SUFFIX = "\n```\n"
        self.show_hidden_value = False
        self.show_files_value = True
        self.show_folders_value = True
        self.use_relative_path_value = True
        self.max_depth_value = 0
        self.file_filter_value = ""
        self.preserve_tree_state_value = True
        self.dir_history = []
        self.current_language = "en_US"
        self.texts = self.languages.get(self.current_language, self.languages["en_US"])

        self.settings_changed = False
        self.max_history_items = 20

        self.load_settings()

    def load_settings(self):
        """从配置文件加载应用程序设置"""
        try:
            if self.settings_file.exists():
                with open(self.settings_file, "r", encoding="utf-8") as f:
                    settings = json.load(f)

                    if "path_prefix" in settings:
                        self.PATH_PREFIX = settings["path_prefix"]
                    if "path_suffix" in settings:
                        self.PATH_SUFFIX = settings["path_suffix"]
                    if "code_prefix" in settings:
                        self.CODE_PREFIX = settings["code_prefix"]
                    if "code_suffix" in settings:
                        self.CODE_SUFFIX = settings["code_suffix"]

                    self.show_hidden_value = settings.get("show_hidden", False)
                    self.show_files_value = settings.get("show_files", True)
                    self.show_folders_value = settings.get("show_folders", True)
                    self.use_relative_path_value = settings.get(
                            "use_relative_path", True
                    )
                    self.max_depth_value = settings.get("max_depth", 0)
                    self.file_filter_value = settings.get("file_filter", "")
                    self.preserve_tree_state_value = settings.get(
                            "preserve_tree_state", True
                    )

                    # 加载语言设置
                    self.current_language = settings.get("language", "en_US")
                    if self.current_language not in self.languages:
                        self.current_language = "en_US"
                    self.texts = self.languages[self.current_language]

                    if "dir_history" in settings:
                        # 加载历史记录时标准化路径格式
                        from ai_code_context_helper.file_utils import normalize_path
                        self.dir_history = [
                            normalize_path(path)
                            for path in settings["dir_history"]
                        ]
                        if len(self.dir_history) > self.max_history_items:
                            self.dir_history = self.dir_history[
                                               : self.max_history_items
                                               ]

                    self.settings_changed = False
        except Exception as e:
            print(f"{self.texts['load_settings_failed'].format(e)}")

    def save_settings(self):
        """将当前设置保存到配置文件"""
        if self.settings_changed:
            try:
                settings = {
                    "path_prefix": self.PATH_PREFIX,
                    "path_suffix": self.PATH_SUFFIX,
                    "code_prefix": self.CODE_PREFIX,
                    "code_suffix": self.CODE_SUFFIX,
                    "show_hidden": self.show_hidden_value,
                    "show_files": self.show_files_value,
                    "show_folders": self.show_folders_value,
                    "use_relative_path": self.use_relative_path_value,
                    "max_depth": self.max_depth_value,
                    "file_filter": self.file_filter_value,
                    "preserve_tree_state": self.preserve_tree_state_value,
                    "language": self.current_language,
                    "dir_history": self.dir_history,
                }

                with open(self.settings_file, "w", encoding="utf-8") as f:
                    json.dump(settings, f, ensure_ascii=False, indent=2)

                self.settings_changed = False
                return True
            except Exception:
                return False
        return True