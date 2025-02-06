import json
import os
import re

from colorama import Fore, init

init(autoreset=True)


def check_line_for_errors(line: str, relative_file_path: str, key: str) -> list[str]:
    errors = []
    stripped_line = line.strip()

    # 在 & 结尾时报错
    if stripped_line.endswith("&"):
        error_message = f"SyntaxError{Fore.RESET}: {Fore.RED}Invalid character '&' at the end of the line\n    {Fore.RESET}Value: {stripped_line}\n    Key: {Fore.YELLOW}{key}"
        print(f"[{relative_file_path}] {Fore.RED}{error_message}")
        errors.append(f"[{relative_file_path}] {Fore.RED}{error_message}")
        return errors

    # 检查 & 后是否有非法字符
    matches = re.finditer(r"&([^a-v0-9\s\\#])", line)
    for match in matches:
        # 过滤掉反斜杠转义的情况
        if match.start() > 0 and line[match.start() - 1] == "\\":
            continue
        error_message = f"SyntaxError{Fore.RESET}: {Fore.RED}Invalid character '{match.group(1)}' after '&'\n    {Fore.RESET}Value: {stripped_line}\n    Key: {Fore.YELLOW}{key}"
        print(f"[{relative_file_path}] {Fore.RED}{error_message}")
        errors.append(f"[{relative_file_path}] {Fore.RED}{error_message}")

    return errors


def check_json_file(file_path: str, relative_file_path: str) -> list[str]:
    errors = []
    try:
        with open(file_path, "r", encoding="utf-8-sig") as file:
            try:
                json_data = json.load(file)
            except json.JSONDecodeError as e:
                error_message = f"JSONDecodeError: {e.msg} at line {e.lineno}"
                print(f"[{relative_file_path}] {Fore.RED}{error_message}")
                errors.append(f"[{relative_file_path}] {error_message}")
                return errors

            for key, value in json_data.items():
                for line in value.splitlines():
                    errors.extend(
                        check_line_for_errors(line.strip(), relative_file_path, key)
                    )
    except Exception as e:
        error_message = f"无法打开文件：{relative_file_path}，错误：{e}"
        print(f"{Fore.RED}{error_message}")
        errors.append(error_message)
    return errors


def check_directory(directory_path: str) -> list[str]:
    errors = []
    found_json = False
    for root, _, files in os.walk(directory_path):
        json_files = [f for f in files if f.endswith(".json")]
        found_json = found_json or bool(json_files)
        for file_name in json_files:
            file_path = os.path.join(root, file_name)
            relative_file_path = os.path.relpath(file_path, start=directory_path)
            errors.extend(check_json_file(file_path, relative_file_path))
    if not found_json:
        print(Fore.YELLOW + f"目录 '{directory_path}' 中没有找到任何 JSON 文件")
    return errors


def remove_color_codes(text: str) -> str:
    """去除所有 ANSI 转义字符"""
    return re.sub(r"\x1b\[[0-9;]*m", "", text)


def save_errors_to_file(errors: list[str]) -> None:
    with open("error_report.txt", "w", encoding="utf-8") as f:
        cleaned_errors = [remove_color_codes(error) for error in errors]
        f.write("\n".join(cleaned_errors))
    print("错误信息已保存到 error_report.txt")


def main() -> None:
    path = input("请输入 JSON 文件或目录路径：").strip()

    if os.path.isdir(path):
        errors = check_directory(path)
    elif os.path.isfile(path) and path.endswith(".json"):
        errors = check_json_file(
            path, os.path.relpath(path, start=os.path.dirname(path))
        )
    else:
        print(f"{Fore.RED}输入的路径无效，请输入有效的 JSON 文件路径或目录。")
        return

    if errors:
        save_errors_to_file(errors)
        if os.name == "nt":
            import winsound

            winsound.Beep(1000, 300)
    else:
        print(f"{Fore.GREEN}文件检查通过，没有发现错误。")
        if os.name == "nt":
            import winsound

            winsound.PlaySound("*", winsound.SND_ALIAS)

    input("按任意键（关机键除外）退出...")


if __name__ == "__main__":
    print(
        Fore.LIGHTGREEN_EX
        + "FTB任务颜色字符合法检查 [版本 1.6 (2025)]\n作者：Wulian233（捂脸）\n\n"
        + Fore.RESET
        + """VM之禅：
    一，即使翻译难易各异，译者应持己见自立。
    二，即使遇到词句争议，组员务必同心共力。
    三，即使译途坎坷跌宕，仍应坚守质量保障。
    四，即使成果乏人褒奖，仍不计事后短长。
    五，即使面临质疑声浪，仍要对正道守望。
    六，即使译句纷乱无章，仍应看向前方、重塑文章。
        """
    )
    main()
