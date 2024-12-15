import json
import os
from pathlib import Path
from typing import Union

import snbtlib
from colorama import Fore, init

init(autoreset=True)


def convert_list_to_string(data: Union[list, dict, str]) -> Union[str, dict]:
    """
    将 JSON 中的列表转换为单行字符串
    """
    if isinstance(data, list):
        # 将列表内容拼接成字符串并转义换行符
        result = "\\n".join(data)
        # 将 \\n 转换为 \n
        return result.replace("\\\\n", "\\n")
    elif isinstance(data, dict):
        # 递归处理字典中的值
        return {k: convert_list_to_string(v) for k, v in data.items()}
    else:
        return data


def convert_snbt_file(file_path: Path) -> None:
    try:
        snbt_data = file_path.read_text(encoding="utf-8")
        json_data = snbtlib.loads(snbt_data)
        json_data = convert_list_to_string(json_data)
        output_path = file_path.with_suffix(".json")

        output_path.write_text(
            json.dumps(json_data, indent=4, ensure_ascii=False), encoding="utf-8"
        )
        print(f"{Fore.CYAN}转换成功: {file_path} -> {output_path}")
    except Exception as e:
        print(f"{Fore.RED}转换失败: {file_path} - 错误: {e}")


def convert_snbt_directory(directory_path: Path) -> None:
    for root, _, files in os.walk(directory_path):
        for file in files:
            if file.endswith(".snbt"):
                snbt_file = Path(root) / file
                convert_snbt_file(snbt_file)


def main() -> None:
    print(
        Fore.LIGHTGREEN_EX
        + "snbt 转 json 工具[版本 1.0 (2024)]\n作者：Wulian233（捂脸）\n\n"
        + Fore.RESET
        + """VM之禅：
    一，即使翻译难易各异，译者应持己见自立。
    二，即使遇到词句争议，组员勿必同心共力。
    三，即使译途坏垣跌荡，仍应坚守质量保障。
    四，即使成果乏人褒奖，仍不计事后短长。
    五，即使面临质疑声涌，仍要对正道守望。
    六，即使译句翻乱无章，仍应看向前方、重塑文章。
        """
    )

    path = input("请输入 snbt 文件或目录路径：").strip()
    input_path = Path(path)

    if input_path.is_dir():
        convert_snbt_directory(input_path)
    elif input_path.is_file() and input_path.suffix == ".snbt":
        convert_snbt_file(input_path)
    else:
        print(f"{Fore.RED}输入的路径无效，请输入正确的 snbt 文件或目录。")
        return

    print(f"{Fore.GREEN}所有 snbt 文件已成功转换为 json！")
    input("按任意键（关机键除外）退出...")


if __name__ == "__main__":
    main()
