import argparse
import json
import os
import re
import sys
from collections.abc import Generator
from dataclasses import dataclass
from pathlib import Path
from typing import Union


@dataclass
class ErrorRecord:
    file_path: str
    key: str
    value: str
    error_message: str


def check_line_for_errors(
    line: str, file_path: str, key: str
) -> Generator[ErrorRecord, None, None]:
    pattern = re.compile(r"&([^a-v0-9\s\\#])")

    for match in pattern.finditer(line):
        if match.start() > 0 and line[match.start() - 1] == "\\":
            continue
        yield ErrorRecord(
            file_path, key, line.strip(), f"'&'后包含非法字符 '{match.group(1)}'"
        )

    stripped_line = line.rstrip("&")
    if line != stripped_line and not line.strip().endswith("\\&"):
        yield ErrorRecord(file_path, key, line.strip(), "行尾包含非法字符 '&'")


def check_json(file_path: str) -> Generator[ErrorRecord, None, None]:
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            json_data = json.load(file)

        def process_value(value: Union[str, list, dict], parent_key: str = ""):
            if isinstance(value, str):
                for i, line in enumerate(value.split("\n")):
                    line_key = (
                        f"{parent_key}[line {i + 1}]" if "\n" in value else parent_key
                    )
                    yield from check_line_for_errors(line, file_path, line_key)
            elif isinstance(value, list):
                for index, item in enumerate(value):
                    yield from process_value(item, f"{parent_key}[{index}]")
            elif isinstance(value, dict):
                for k, v in value.items():
                    yield from process_value(
                        v, f"{parent_key}.{k}" if parent_key else k
                    )

        yield from process_value(json_data)
    except json.JSONDecodeError:
        yield ErrorRecord(file_path, "-", "-", "JSON 解析失败，请检查 JSON 格式")
    except FileNotFoundError:
        yield ErrorRecord(file_path, "-", "-", "文件未找到")
    except Exception as e:
        yield ErrorRecord(file_path, "-", "-", f"打开或读取文件时出错：{str(e)}")


def check_directory(dir_path: str) -> Generator[ErrorRecord, None, None]:
    """递归检查指定目录下的所有 JSON 文件"""
    print(f"正在检查目录: {dir_path}")
    json_files_found = 0
    for entry in Path(dir_path).rglob("*.json"):
        if "patchouli_books" in entry.parts or "productivemetalworks" in entry.parts:
            continue
        json_files_found += 1
        yield from check_json(str(entry))
    if json_files_found == 0:
        print(f"在目录 {dir_path} 中未找到任何 .json 文件。")


def generate_html_report(
    errors: list[ErrorRecord], output_path="error_report.html"
) -> str:
    html_content = f"""<!DOCTYPE html>
<html lang="zh">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FTB任务颜色字符错误报告</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; background-color: #f5f5f5; text-align: center; }}
        h1 {{ color: #333; }}
        table {{ margin: 20px auto; border-collapse: collapse; background: #fff; box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1); table-layout: auto; width: 90%; }}
        th, td {{ padding: 12px; border-bottom: 1px solid #ddd; text-align: left; word-break: break-word; }}
        th {{ background-color: #007bff; color: white; }}
        .error {{ color: red; font-weight: bold; }}
        .highlight {{ color: red; font-weight: bold; background-color: #ffddcc; }}
        table tr {{ transition: background-color 0.3s ease, transform 0.2s ease; }}
        table tr:hover {{ background-color: #f1f1f1; }}

        th:nth-child(1), td:nth-child(1) {{ min-width: 100px; max-width: 250px; }}
        th:nth-child(2), td:nth-child(2) {{ min-width: 100px; max-width: 200px; }}
        th:nth-child(3), td:nth-child(3) {{ min-width: 200px; max-width: 400px; }}
        th:nth-child(4), td:nth-child(4) {{ min-width: 150px; }}


        @media (prefers-color-scheme: dark) {{
            body {{ background-color: #333333; color: #f0f0f0; }}
            h1 {{ color: #eee; }}
            table {{ background: #444444; box-shadow: 0 4px 10px rgba(255, 255, 255, 0.1); }}
            th {{ background-color: #0056b3; color: #f5f5f5; }}
            .highlight {{ background-color: #992222; color: #f5f5f5; }}
            .error {{ color: #ff6666; }}
            table tr:hover {{ background-color: #555555; }}
        }}
    </style>
</head>
<body>
    <h1>FTB任务颜色字符错误报告</h1>
    <p>总共发现 {len(errors)} 个错误。</p>
    <table>
        <thead>
            <tr><th>文件路径</th><th>键</th><th>值</th><th>错误描述</th></tr>
        </thead>
        <tbody>
    """

    for error in errors:
        import html

        escaped_value = html.escape(error.value)

        highlighted_value = re.sub(
            r"&([^a-v0-9\s\\#])", r'&<span class="highlight">\1</span>', escaped_value
        )

        if error.error_message == "行尾包含非法字符 '&'" and escaped_value.endswith(
            "&"
        ):
            highlighted_value = (
                highlighted_value[:-1] + '<span class="highlight">&</span>'
            )

        html_content += f"<tr><td>{html.escape(error.file_path)}</td><td>{html.escape(error.key)}</td><td>{highlighted_value}</td><td class='error'>{html.escape(error.error_message)}</td></tr>\n"

    html_content += """</tbody>
    </table>
</body>
</html>"""

    try:
        with open(output_path, "w", encoding="utf-8") as file:
            file.write(html_content)
        print(f"错误报告已生成到: {output_path}")
        return output_path
    except Exception as e:
        print(f"生成报告文件时出错: {str(e)}", file=sys.stderr)
        return ""


def main():
    parser = argparse.ArgumentParser(description="FTB任务颜色字符合法检查")
    parser.add_argument(
        "path", help="要检查的 JSON 文件或包含 JSON 文件的目录的路径", type=str
    )
    parser.add_argument(
        "--report-output",
        help="HTML 错误报告的输出路径 (默认为 error_report.html)",
        default="error_report.html",
        type=str,
    )

    args = parser.parse_args()
    check_path = args.path
    report_output_path = args.report_output

    if not os.path.exists(check_path):
        print(f"错误: 路径不存在 -> {check_path}", file=sys.stderr)
        sys.exit(1)

    errors: list[ErrorRecord] = []

    if os.path.isdir(check_path):
        errors.extend(check_directory(check_path))
    elif os.path.isfile(check_path) and check_path.lower().endswith(".json"):
        errors.extend(check_json(check_path))
    else:
        print(
            f"错误: 无效的路径类型或文件格式 -> {check_path} (需要 .json 文件或目录)",
            file=sys.stderr,
        )
        sys.exit(1)

    print(f"\n检查完成。总共发现 {len(errors)} 个错误。")

    if errors:
        generated_report_path = generate_html_report(errors, report_output_path)
        if generated_report_path:
            print(f"详细错误报告请查看文件: {generated_report_path}")
        sys.exit(0)


if __name__ == "__main__":
    main()
