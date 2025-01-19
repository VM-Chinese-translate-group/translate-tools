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
        return "\\n".join(data).replace("\\\\n", "\\n")
    elif isinstance(data, dict):
        return {k: convert_list_to_string(v) for k, v in data.items()}
    return data


def convert_file(file_path: Path, to_json: bool) -> None:
    try:
        if to_json:
            # SNBT -> JSON
            snbt_data = file_path.read_text(encoding="utf-8")
            json_data = snbtlib.loads(snbt_data)
            json_data = convert_list_to_string(json_data)
            output_path = file_path.with_suffix(".json")
            output_path.write_text(
                json.dumps(json_data, indent=4, ensure_ascii=False), encoding="utf-8"
            )
        else:
            # JSON -> SNBT
            json_data = json.loads(file_path.read_text(encoding="utf-8"))
            snbt_data = snbtlib.dumps(json_data)
            output_path = file_path.with_suffix(".snbt")
            output_path.write_text(snbt_data, encoding="utf-8")
        print(f"{Fore.CYAN}转换成功: {file_path} -> {output_path}")
    except Exception as e:
        print(f"{Fore.RED}转换失败: {file_path} - 错误: {e}")


def convert_directory(directory_path: Path, to_json: bool) -> None:
    for root, _, files in os.walk(directory_path):
        for file in files:
            if (to_json and file.endswith(".snbt")) or (
                not to_json and file.endswith(".json")
            ):
                file_path = Path(root) / file
                convert_file(file_path, to_json)


def main() -> None:
    path = input("请输入文件或目录路径：").strip()
    input_path = Path(path)

    action = input("请选择操作：1. SNBT -> JSON  2. JSON -> SNBT\n").strip()
    if action not in {"1", "2"}:
        print(f"{Fore.RED}无效操作！请输入 1 或 2")
        return

    to_json = action == "1"

    if input_path.is_dir():
        convert_directory(input_path, to_json)
    elif input_path.is_file() and (
        (to_json and input_path.suffix == ".snbt")
        or (not to_json and input_path.suffix == ".json")
    ):
        convert_file(input_path, to_json)
    else:
        print(f"{Fore.RED}输入的路径无效，请输入正确的文件或目录")
        return

    print(f"{Fore.GREEN}所有文件已成功转换！")
    input("按任意键（关机键除外）退出...\n")


if __name__ == "__main__":
    print(
        Fore.LIGHTGREEN_EX
        + "snbt json 互转工具 [版本 1.2 (2025)]\n作者：Wulian233（捂脸）\n\n"
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
    main()
