import json
import os
import re

from colorama import Fore, init

init(autoreset=True)


def check_line_for_errors(
    line: str, line_number: int, verbose: bool, relative_file_path: str
) -> list[str]:
    errors = []
    matches = re.finditer(r"&([^a-zA-Z1-9\s])", line)
    for match in matches:
        error_message = f"SyntaxError: Invalid character '{match.group(1)}' after '&' at line {line_number}\n    {line}"
        if verbose:
            print(f"[{relative_file_path}] {Fore.RED}{error_message}")
        else:
            print(
                f"[{relative_file_path}] {Fore.RED}SyntaxError: Invalid character after '&' at line {line_number}"
            )
        errors.append(f"[{relative_file_path}] {error_message}")
    return errors


def check_json_file(
    file_path: str, relative_file_path: str, verbose: bool
) -> list[str]:
    errors = []
    try:
        with open(file_path, "r", encoding="utf-8-sig") as file:
            try:
                json.load(file)
            except json.JSONDecodeError as e:
                error_message = f"JSONDecodeError: {e.msg} at line {e.lineno}"
                print(f"[{relative_file_path}] {Fore.RED}{error_message}")
                errors.append(f"[{relative_file_path}] {error_message}")
                return errors

            file.seek(0)
            for line_number, line in enumerate(file, start=1):
                if ":" in line:
                    _, value = line.split(":", 1)
                    errors.extend(
                        check_line_for_errors(
                            value.strip(), line_number, verbose, relative_file_path
                        )
                    )
    except Exception as e:
        error_message = f"无法打开文件：{relative_file_path}，错误：{e}"
        print(f"{Fore.RED}{error_message}")
        errors.append(error_message)
    return errors


def check_directory(directory_path: str, verbose: bool) -> list[str]:
    errors = []
    found_json = False
    for root, _, files in os.walk(directory_path):
        json_files = [f for f in files if f.endswith(".json")]
        found_json = found_json or bool(json_files)
        for file_name in json_files:
            file_path = os.path.join(root, file_name)
            relative_file_path = os.path.relpath(file_path, start=directory_path)
            errors.extend(check_json_file(file_path, relative_file_path, verbose))
    if not found_json:
        print(Fore.YELLOW + f"目录 '{directory_path}' 中没有找到任何 JSON 文件")
    return errors


def save_errors_to_file(errors: list[str]) -> None:
    with open("error_report.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(errors))
    print("错误信息已保存到 error_report.txt")


def main() -> None:
    print(
        Fore.YELLOW
        + "FTB任务颜色字符合法检查 [版本 1.1 (2024)]\n作者：Wulian233（捂脸）\n"
    )
    path = input("请输入 JSON 文件或目录路径：").strip()
    verbose = input("是否显示详细错误信息？(y/n): ").strip().lower() == "y"

    if os.path.isdir(path):
        errors = check_directory(path, verbose)
    elif os.path.isfile(path) and path.endswith(".json"):
        errors = check_json_file(
            path, os.path.relpath(path, start=os.path.dirname(path)), verbose
        )
    else:
        print(Fore.RED + "输入的路径无效，请输入有效的 JSON 文件路径或目录。")
        return

    if errors:
        save_errors_to_file(errors)
    else:
        print(Fore.GREEN + "文件检查通过，没有发现错误。")

    input("按任意键（关机键除外）退出...")


if __name__ == "__main__":
    main()
