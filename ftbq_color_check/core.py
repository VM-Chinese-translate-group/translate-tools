import json
import re
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

    if line.strip().endswith("&"):
        yield ErrorRecord(file_path, key, line.strip(), "行尾包含非法字符 '&'")


def check_json(file_path: str) -> Generator[ErrorRecord, None, None]:
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            json_data = json.load(file)

        def process_value(value: Union[str, list, dict], parent_key: str = ""):
            """递归检查 JSON 中的字符串值"""
            if isinstance(value, str):
                for line in value.split("\n"):
                    yield from check_line_for_errors(
                        line.strip(), file_path, parent_key
                    )
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
    except Exception as e:
        yield ErrorRecord(file_path, "-", "-", f"无法打开文件：{str(e)}")


def check_directory(dir_path: str) -> Generator[ErrorRecord, None, None]:
    for entry in Path(dir_path).rglob("*.json"):
        if "patchouli_books" in entry.parts:
            continue
        yield from check_json(str(entry))


def generate_html_report(
    errors: list[ErrorRecord], output_path="error_report.html"
) -> str:
    html_content = """<!DOCTYPE html>
<html lang="zh">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>错误报告</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background-color: #f5f5f5; text-align: center; }
        table { margin: 20px auto; border-collapse: collapse; background: #fff; box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1); table-layout: auto; }
        th, td { padding: 12px; border-bottom: 1px solid #ddd; text-align: left; }
        th { background-color: #007bff; color: white; }
        .error { color: red; font-weight: bold; }
        .highlight { color: red; font-weight: bold; background-color: #ffddcc; }
        table tr { transition: background-color 0.3s ease, transform 0.2s ease; }
        table tr:hover { background-color: #f1f1f1; }

        th:nth-child(1), td:nth-child(1) { min-width: 100px; max-width: 200px; word-wrap: break-word; resize: horizontal; }
        th:nth-child(2), td:nth-child(2) { min-width: 200px; max-width: 300px; word-wrap: break-word; resize: horizontal; }
        th:nth-child(3), td:nth-child(3) { min-width: 300px; max-width: 600px; word-wrap: break-word; resize: horizontal; }
        th:nth-child(4), td:nth-child(4) { word-wrap: break-word; }

        @media (prefers-color-scheme: dark) {
            body { background-color: #333333; color: #f0f0f0; }
            table { background: #444444; box-shadow: 0 4px 10px rgba(255, 255, 255, 0.1); }
            th { background-color: #0056b3; color: #f5f5f5; }
            .highlight { background-color: #992222; color: #f5f5f5; }
            .error { color: #ff6666; }
            table tr:hover { background-color: #555555; }
        }
    </style>
</head>
<body>
    <h1>错误报告</h1>
    <table>
        <thead>
            <tr><th>文件路径</th><th>键</th><th>值</th><th>错误描述</th></tr>
        </thead>
        <tbody>
    """

    for error in errors:
        highlighted_value = re.sub(r'&([^a-v0-9\\s\\#])', r'&<span class="highlight">\1</span>', error.value)
        html_content += (
            f"<tr><td>{error.file_path}</td><td>{error.key}</td><td>{highlighted_value}</td><td class='error'>{error.error_message}</td></tr>\n"
        )

    html_content += """</tbody>
    </table>
</body>
</html>"""

    with open(output_path, "w", encoding="utf-8") as file:
        file.write(html_content)

    return output_path
