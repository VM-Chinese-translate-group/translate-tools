#include <iostream>
#include <fstream>
#include <string>
#include <cctype>

using namespace std;

#ifdef _WIN32
#include <windows.h>
#endif

void set_console_encoding() {
#ifdef _WIN32
    SetConsoleOutputCP(CP_UTF8);
#endif
}

bool is_valid_char(char c) {
    return isalnum(static_cast<unsigned char>(c));
}

void check_line_for_errors(const string& line, int line_number, const string& key, const string& value, bool& has_errors, bool verbose) {
    auto pos = line.find('&');
    while (pos != string::npos) {
        if (pos + 1 < line.length() && !is_valid_char(line[pos + 1])) {
            if (verbose) {
                cerr << "错误：在第 " << line_number << " 行，在 '&' 后面发现无效字符" << endl;
                cerr << "键：" << key << endl;
                cerr << "值：" << value << endl;
            } else {
                cerr << "错误：在第 " << line_number << " 行，在 '&' 后面发现无效字符" << endl;
            }
            has_errors = true;
        }
        pos = line.find('&', pos + 1);
    }
}

void check_json(const string& file_path, bool verbose) {
    ifstream file(file_path);
    if (!file) {
        cerr << "无法打开文件：" << file_path << endl;
        return;
    }

    string line;
    int line_number = 0;
    bool has_errors = false;

    while (getline(file, line)) {
        ++line_number;

        auto colon_pos = line.find(':');
        if (colon_pos != string::npos) {
            string key = line.substr(0, colon_pos);
            string value = line.substr(colon_pos + 1);

            check_line_for_errors(key, line_number, key, value, has_errors, verbose);
            check_line_for_errors(value, line_number, key, value, has_errors, verbose);
        }
    }

    if (!has_errors) {
        cout << "所有 JSON 内容都是有效的。" << endl;
    }
}

int main() {
    set_console_encoding(); // 设置控制台编码（Windows 上有效）

    string file_path;
    bool verbose = false;

    cout << "请输入 JSON 文件路径：";
    cin >> file_path;

    cout << "是否显示包含键名与内容的详细错误信息？(y/n): ";
    char choice;
    cin >> choice;
    verbose = (choice == 'y' || choice == 'Y');

    check_json(file_path, verbose);

    // 等待用户输入后关闭
    cout << "按任意键退出……";
    cin.ignore();
    cin.get();

    return 0;
}
