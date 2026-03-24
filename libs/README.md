# 依赖说明

此脚本使用 Python 标准库，无需额外安装外部依赖。

## 使用的标准库

- tkinter - GUI 界面
- os, sys - 系统操作
- json - JSON 处理
- shutil - 文件操作
- sqlite3 - 数据库操作
- pathlib - 路径处理
- dataclasses - 数据类
- typing - 类型提示
- datetime - 时间处理

## 打包说明

使用 PyInstaller 打包：

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name "WindsurfDataManager" windsurf_data_manager_gui.py
```

打包后的 exe 文件位于 `dist/` 目录。
