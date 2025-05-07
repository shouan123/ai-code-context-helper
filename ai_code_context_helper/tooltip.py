import tkinter as tk
from tkinter import ttk

class ToolTip:
    """创建一个提示框，在用户将鼠标悬停在控件上时显示帮助文本"""

    def __init__(self, widget, text):
        """初始化工具提示"""
        self.widget = widget
        self.text = text
        self.tip_window = None
        self.id = None
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.leave)
        self.widget.bind("<ButtonPress>", self.leave)

    def enter(self, event=None):
        """当鼠标进入控件时，安排显示提示"""
        self.schedule()

    def leave(self, event=None):
        """当鼠标离开控件或按下按钮时，取消安排并隐藏提示"""
        self.unschedule()
        self.hide()

    def schedule(self):
        """安排提示在500毫秒后显示"""
        self.unschedule()
        self.id = self.widget.after(500, self.show)

    def unschedule(self):
        """取消之前安排的显示"""
        if self.id:
            self.widget.after_cancel(self.id)
            self.id = None

    def show(self):
        """显示提示窗口，位置在控件下方"""
        if self.tip_window:
            return

        x = self.widget.winfo_rootx()
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 5

        self.tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")

        label = ttk.Label(
                tw,
                text=self.text,
                justify=tk.LEFT,
                background="#ffffe0",
                relief=tk.SOLID,
                borderwidth=1,
                font=("微软雅黑", 9, "normal"),
        )
        label.pack(ipadx=5, ipady=3)

    def hide(self):
        """隐藏并销毁提示窗口"""
        tw = self.tip_window
        self.tip_window = None
        if tw:
            tw.destroy()


def create_tooltip(widget, text):
    """为控件创建工具提示的便捷函数"""
    return ToolTip(widget, text)