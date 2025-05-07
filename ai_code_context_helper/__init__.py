import tkinter as tk
from ai_code_context_helper.version import __version__
from ai_code_context_helper.code_context_generator import CodeContextGenerator

def main():
    """应用程序入口点，创建主窗口并启动事件循环"""
    root = tk.Tk()
    app = CodeContextGenerator(root)
    root.mainloop()

if __name__ == "__main__":
    main()