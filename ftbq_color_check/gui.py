import os
import tkinter as tk
from tkinter import filedialog, ttk
from tkinter.scrolledtext import ScrolledText

from core import check_directory, check_json, generate_html_report

__version__ = "2.0"
__author__ = "Wulian233（捂脸）"


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("FTB任务颜色字符合法检查")
        self.root.geometry("850x600")

        self.path_var = tk.StringVar()
        self.errors = []

        # 顶部输入框和按钮
        frame = ttk.Frame(root)
        frame.pack(pady=10, padx=10, fill=tk.X)

        self.entry = ttk.Entry(frame, textvariable=self.path_var, width=50)
        self.entry.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)

        btn_file = ttk.Button(
            frame, text="选择 JSON 文件", command=self.select_json_file
        )
        btn_file.pack(side=tk.LEFT, padx=5)

        btn_dir = ttk.Button(frame, text="选择文件夹", command=self.select_directory)
        btn_dir.pack(side=tk.LEFT, padx=5)

        btn_check = ttk.Button(frame, text="检查", command=self.check_paths)
        btn_check.pack(side=tk.LEFT, padx=5)

        # 日志显示框
        self.log_area = ScrolledText(
            root, wrap=tk.WORD, height=25, font=("Consolas", 12)
        )
        self.log_area.pack(padx=10, pady=10, expand=True, fill=tk.BOTH)
        self.log_area.config(state=tk.DISABLED)

        # 颜色标签
        self.log_area.tag_configure("red", foreground="red")
        self.log_area.tag_configure("green", foreground="green")
        self.log_area.tag_configure("blue", foreground="blue")
        self.log_area.tag_configure("cyan", foreground="dark cyan")
        self.log_area.tag_configure("black", foreground="black")

        self.append_log(
            f"FTB任务颜色字符合法检查 [版本 {__version__} (2025)] 作者：{__author__}\n",
            "black",
        )

    def select_json_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("JSON", "*.json")])
        if file_path:
            self.path_var.set(file_path)

    def select_directory(self):
        dir_path = filedialog.askdirectory()
        if dir_path:
            self.path_var.set(dir_path)

    def check_paths(self):
        self.log_area.delete(1.0, tk.END)
        path = self.path_var.get().strip()

        if not path:
            self.append_log("请选择路径！\n", "red")
            return

        self.errors.clear()

        if not os.path.exists(path):
            self.append_log(f"路径不存在: {path}\n", "red")
        elif os.path.isdir(path):
            self.errors.extend(check_directory(path))
        else:
            self.errors.extend(check_json(path))

        self.display_errors()
        if self.errors:
            report_path = generate_html_report(self.errors)
            self.append_log(f"错误信息已保存到 {report_path}\n", "green")

    def display_errors(self):
        if not self.errors:
            self.append_log("检查通过，无错误。\n", "green")
        else:
            for error in self.errors:
                self.append_log(f"文件: {error.file_path}\n", "blue")
                self.append_log(f"键: {error.key}\n", "cyan")
                self.append_log(f"值: {error.value}\n", "black")
                self.append_log(f"错误: {error.error_message}\n\n", "red")

    def append_log(self, message, tag):
        self.log_area.config(state=tk.NORMAL)
        self.log_area.insert(tk.END, message, tag)
        self.log_area.see(tk.END)
        self.log_area.config(state=tk.DISABLED)
