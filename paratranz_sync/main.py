import asyncio
import json
import os
import re
import sys
from tkinter import END, filedialog, messagebox
from tkinter.ttk import Button, Checkbutton, Entry, Label, Progressbar

import aiohttp
import sv_ttk
from hidpi_tk import DPIAwareTk


class ParatranzUploader:
    CONFIG_FILE = "config.json"
    DEFAULT_TOKEN = "go to https://paratranz.cn/users/my"
    DEFAULT_VERSION = "1.7.0"

    def __init__(self, root: DPIAwareTk) -> None:
        self.root = root
        self.root.title("Paratranz译文同步")
        self.center_window()

        self.token = self.load_config()
        self.headers = {
            "Authorization": self.token,
            "accept": "*/*",
            "Content-Type": "application/json;charset=UTF-8",
        }
        self.create_widgets()
        self.update_info()

        if len(self.token) != 32:
            messagebox.showwarning(
                "警告",
                "当前未设置token，无法使用。\n请在https://paratranz.cn/users/my 点击设置获取并在config.json输入",
            )
            os.startfile("config.json")

    def load_config(self):
        if not os.path.exists(self.CONFIG_FILE):
            config = {"token": self.DEFAULT_TOKEN}
            with open(self.CONFIG_FILE, "w") as config_file:
                json.dump(config, config_file)
            return self.DEFAULT_TOKEN

        with open(self.CONFIG_FILE, "r") as config_file:
            config = json.load(config_file)
        return config.get("token", self.DEFAULT_TOKEN)

    def center_window(self) -> None:
        window_width, window_height = 800, 400
        screen_width, screen_height = (
            self.root.winfo_screenwidth(),
            self.root.winfo_screenheight(),
        )
        position_top, position_right = (screen_height - window_height) // 2, (
            screen_width - window_width
        ) // 2
        self.root.geometry(
            f"{window_width}x{window_height}+{position_right}+{position_top}"
        )

    def create_widgets(self) -> None:
        entries = {
            "项目ID：": (0, self.create_entry),
            "文件ID：": (1, self.create_entry),
            "译文路径：": (2, self.create_path_entry),
        }
        for label, (row, method) in entries.items():
            Label(self.root, text=label, font=("黑体", 12)).grid(
                row=row, column=0, padx=30, pady=10, sticky="w"
            )
            method(row)

        Button(
            self.root,
            text="上传译文",
            style="Accent.TButton",
            command=self.run_upload_translation,
            width=20,
        ).grid(row=3, column=0, columnspan=4, pady=20)
        Checkbutton(
            self.root,
            text="暗色模式",
            style="Switch.TCheckbutton",
            command=sv_ttk.toggle_theme,
        ).grid(row=3, column=2, pady=5, padx=30, sticky="w")
        Button(
            self.root, text="下载译文", command=self.run_download_translation, width=20
        ).grid(row=3, column=0, padx=30, pady=5)

        self.progress_bar = Progressbar(self.root)
        self.progress_bar.grid(row=4, column=0, columnspan=3, sticky="ew")
        self.progress_bar.grid_remove()  # 默认隐藏进度条

        self.version_label = Label(
            self.root, text=f"当前版本：{self.DEFAULT_VERSION}", font=("黑体", 12)
        )
        self.version_label.grid(
            row=5, column=0, columnspan=3, padx=10, pady=10, sticky="w"
        )

        self.update_label = Label(self.root, text="", font=("黑体", 12))
        self.update_label.grid(
            row=6, column=0, columnspan=3, padx=10, pady=10, sticky="w"
        )

        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(4, weight=1)

        self.root.update()

    def create_entry(self, row: int) -> None:
        entry = Entry(self.root)
        entry.grid(row=row, column=1, padx=10, pady=10, sticky="ew")
        setattr(self, f"entry_{row}", entry)

    def create_path_entry(self, row: int) -> None:
        self.file_path_entry = Entry(self.root)
        self.file_path_entry.grid(row=row, column=1, padx=10, pady=10, sticky="ew")
        Button(self.root, text="...", command=self.select_file_path).grid(
            row=row, column=2, padx=10, pady=10
        )

    def select_file_path(self) -> None:
        file = filedialog.askopenfile(
            filetypes=(("JSON", "*.json"), ("全部文件", "*.*"))
        )
        if file:
            self.file_path_entry.delete(0, END)
            self.file_path_entry.insert(0, file.name)

    def show_error(self, message: str):
        messagebox.showerror("错误", message)

    async def fetch_data(self, url: str) -> dict:
        async with aiohttp.ClientSession(headers=self.headers) as session:
            try:
                async with session.get(url) as response:
                    return await response.json()
            except aiohttp.ClientError as error:
                self.show_error(f"HTTP错误: {error}")
            except Exception as e:
                self.show_error(f"未知错误: {e}")
        return {}

    async def send_data(self, url: str, data: dict) -> int:
        async with aiohttp.ClientSession(headers=self.headers) as session:
            try:
                async with session.put(url, json=data) as response:
                    return response.status
            except aiohttp.ClientError as error:
                self.show_error(f"HTTP错误: {error}")
            except Exception as e:
                self.show_error(f"未知错误: {e}")
        return -1

    async def upload_translation(self) -> None:
        proj_id = self.entry_0.get()
        file_id_value = self.entry_1.get()

        if not proj_id or not file_id_value:
            self.show_error("请输入项目ID和文件ID（在Paratranz的url中可以查看）")
            return

        file_url = f"https://paratranz.cn/api/projects/{proj_id}/files/{file_id_value}/translation"
        file_json = await self.fetch_data(file_url)

        if not file_json or not os.path.isfile(self.file_path_entry.get()):
            self.show_error("请选择译文路径")
            return

        self.progress_bar.grid()
        self.progress_bar["maximum"] = len(file_json)
        self.progress_bar["value"] = 0

        with open(self.file_path_entry.get(), "r", encoding="utf-8") as file:
            zh_obj = json.load(file)

        tasks = []
        for info in file_json:
            str_id = info.get("id")
            translation = zh_obj.get(info.get("key"))
            if translation is not None:
                body = {key: info.get(key) for key in ("key", "original", "file")}
                body.update({"translation": translation, "stage": 1, "context": None})
                tasks.append(self.put_translation(proj_id, str_id, body))

        await asyncio.gather(*tasks)
        self.progress_bar.grid_remove()
        messagebox.showinfo("提示", "译文上传完成")

    async def download_translation(self):
        proj_id = self.entry_0.get()
        file_id_value = self.entry_1.get()

        if not proj_id or not file_id_value:
            self.show_error("请输入项目ID和文件ID（在Paratranz的url中可以查看）")
            return

        file_url = f"https://paratranz.cn/api/projects/{proj_id}/files/{file_id_value}/translation"
        out_file = await self.fetch_data(file_url)

        def get_translation(item):
            translation = item.get("translation")
            stage = item.get("stage")
            original = item.get("original")

            if translation and stage not in {0, -1}:
                return re.sub(r"\\n", "\n", translation)
            else:
                return re.sub(r"\\n", "\n", original)

        zh_cn_dict = {item["key"]: get_translation(item) for item in out_file}

        with open("./zh_cn.json", "w+", encoding="UTF-8") as f:
            json.dump(
                zh_cn_dict, f, ensure_ascii=False, indent=4, separators=(",", ":")
            )

        messagebox.showinfo("提示", "译文下载成功（下载位置为当前程序目录）")

    def run_upload_translation(self):
        asyncio.run(self.upload_translation())

    def run_download_translation(self):
        asyncio.run(self.download_translation())

    async def put_translation(self, proj_id, str_id, body):
        if (
            await self.send_data(
                f"https://paratranz.cn/api/projects/{proj_id}/strings/{str_id}", body
            )
            != 200
        ):
            self.show_error("Paratranz服务器异常，请重试")
        self.progress_bar["value"] += 1
        self.root.update()

    def update_info(self) -> None:
        update_content = "1. 下载后的译文key排序顺序现在按原文件的顺序排序"
        self.update_label.config(text=f"更新内容：\n{update_content}")


def main() -> None:
    py_version = sys.version_info
    if py_version < (3, 9):
        messagebox.showerror(
            "无法使用",
            f"当前Python版本过低，无法使用。当前版本为{py_version.major}.{py_version.minor}，请使用Python 3.9+",
        )
        sys.exit(0)

    root = DPIAwareTk()
    sv_ttk.use_light_theme()
    ParatranzUploader(root)

    import base64

    from icon import img

    with open("window_icon.ico", "wb+") as icon:
        icon.write(base64.b64decode(img))
    root.iconbitmap("window_icon.ico")
    os.remove("window_icon.ico")
    root.mainloop()


if __name__ == "__main__":
    main()
