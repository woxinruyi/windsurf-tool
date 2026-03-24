# Windsurf 数据管理工具

<p align="center">
  <strong>Windsurf IDE 本地数据管理图形界面工具 / A GUI Tool for Managing Windsurf IDE Local Data</strong>
</p>

<p align="center">
  <a href="#功能特性">功能特性</a> •
  <a href="#使用方法">使用方法</a> •
  <a href="#安装">安装</a> •
  <a href="README.md">English</a>
</p>

---

## 概述

这是一个用于管理 Windsurf IDE 本地数据的图形界面工具，帮助用户清理和管理 RAG 索引、对话历史、缓存等数据，解决内存占用过高的问题。

**关键词 / Keywords**: Windsurf, Windsurf IDE, RAG索引, 内存管理, 缓存清理, Codeium, 数据管理工具, Memory Management, Cache Cleaner, Conversation History, Vector Database

## 功能特性

### 1. RAG 索引管理（核心功能）

- **扫描位置**: `~/.codeium/windsurf/` 目录
- **支持目录**:
  - `cascade/` - 对话历史和上下文数据（.pb, .tmp 文件）
  - `implicit/` - 隐式上下文数据
  - `brain/` - 大脑记忆数据
  - `database/` - 嵌入向量数据库
  - `code_tracker/` - 代码追踪索引
  - `codemaps/` - 代码地图
  - `rules/` - 规则文件
  - `recipes/` - 配方文件
  - `context_state/` - 上下文状态
  - `memories/` - 记忆数据
  - `global_workflows/` - 全局工作流
  - `ask_continue_temp_photo/` - 临时图片

### 2. 工作区存储管理

- 扫描 `%APPDATA%\Windsurf\User\workspaceStorage/` 目录
- 显示每个工作区的数据库大小和项目路径
- 支持删除单个工作区数据

### 3. 文件历史管理

- 扫描 `%APPDATA%\Windsurf\User\History/` 目录
- 显示文件编辑历史记录
- 支持清理历史记录

### 4. 缓存数据管理

- 扫描所有 Windsurf 缓存目录
- 显示缓存大小和文件数量
- 支持清理所有缓存

## 安装

### 环境要求

- Python 3.7+
- tkinter（Python 内置）

无需额外安装依赖。

### 运行工具

```bash
# 克隆仓库
git clone https://github.com/woxinruyi/windsurf-tool.git

# 进入目录
cd windsurf-tool

# 运行工具
python windsurf_data_manager_gui.py
```

## 使用方法

工具包含四个标签页：

### RAG 索引标签页（最重要）

- 显示所有 Codeium RAG 索引文件
- 按文件大小降序排列（最大的在前）
- **关键操作**:
  - **清理所有临时文件(.tmp)** - 安全删除临时缓存，释放内存
  - **删除选中** - 删除选中的文件（警告：.pb 文件包含对话历史）
  - **查看统计** - 显示各分类大小和大文件列表

### 工作区存储标签页

- 显示所有工作区数据
- 查看数据库表结构
- 删除工作区数据

### 文件历史标签页

- 显示文件编辑历史
- 清理历史记录

### 缓存数据标签页

- 显示所有缓存目录
- 清理缓存

## 内存占用问题

### 原因分析

Windsurf 使用 RAG (Retrieval-Augmented Generation) 索引代码库，这些索引文件可能非常大：

- `cascade/*.pb` 文件: 26MB, 17MB, 10MB 等
- `cascade/*.tmp` 文件: 29MB, 17MB 等
- `implicit/*.pb` 文件: 14MB, 10MB 等

这些文件会被加载到内存中，是内存占满的主要原因。

### 解决方案

1. **清理临时文件**（推荐）
   - 使用"清理所有临时文件(.tmp)"按钮
   - 安全删除临时缓存，不影响对话历史
   - 可释放大量内存

2. **删除旧的对话历史**（谨慎）
   - 选择不再需要的 .pb 文件删除
   - 会丢失对应的对话历史
   - 建议定期清理

3. **清理其他缓存**
   - 定期清理 Windsurf 缓存目录
   - 清理工作区数据（不常用的项目）

## 技术细节

### 数据存储位置

**Windows**:
- Windsurf 数据: `%APPDATA%\Windsurf\`
- Codeium RAG: `%USERPROFILE%\.codeium\windsurf\`

**macOS**:
- Windsurf 数据: `~/Library/Application Support/Windsurf/`
- Codeium RAG: `~/.codeium/windsurf/`

**Linux**:
- Windsurf 数据: `~/.config/Windsurf/`
- Codeium RAG: `~/.codeium/windsurf/`

### 文件类型说明

| 扩展名 | 类型 | 说明 | 可删除性 |
|--------|------|------|----------|
| .pb | Protocol Buffer | 对话历史、上下文数据 | 谨慎（会丢失历史） |
| .tmp | 临时文件 | 临时缓存 | 安全（定期清理） |
| .sqlite* | SQLite 数据库 | 嵌入向量数据库 | 谨慎 |
| .json | JSON 配置 | 配置文件 | 谨慎 |
| .md | Markdown | 文档 | 安全 |

## 注意事项

1. **备份重要数据**: 删除文件前建议备份
2. **关闭 Windsurf**: 清理前建议关闭 Windsurf IDE
3. **谨慎删除 .pb 文件**: 这些文件包含对话历史
4. **定期清理 .tmp 文件**: 这些是临时缓存，可以安全删除
5. **跨平台支持**: 工具支持 Windows、macOS、Linux

## 许可证

本项目采用 **MIT License** 开源许可证。

### 许可权限

您被授予以下权利：

- ✅ **商业使用** - 可以将此工具用于商业目的
- ✅ **修改** - 可以修改源代码以适应您的需求
- ✅ **分发** - 可以分发原始或修改后的版本
- ✅ **私人使用** - 可以私人使用和修改
- ✅ **二次开发** - 可以基于此工具进行二次开发和扩展

### 使用条件

使用本工具时，请遵守以下条件：

1. **保留版权声明** - 在所有副本或重要部分中包含版权声明
2. **包含许可证** - 在所有副本或重要部分中包含完整的许可证文本
3. **免责声明** - 软件按"原样"提供，不提供任何形式的保证

### 免责声明

本工具按"原样"提供，不提供任何形式的明示或暗示的保证，包括但不限于适销性、特定用途适用性和非侵权性的保证。在任何情况下，作者或版权持有人都不对任何索赔、损害或其他责任负责，无论是合同、侵权或其他方面的责任，由软件或软件的使用或其他交易引起、产生或与之相关。

## 联系方式

如有问题或建议，欢迎通过以下方式联系：

- **GitHub**: [https://github.com/woxinruyi/windsurf-tool](https://github.com/woxinruyi/windsurf-tool)
- **问题反馈**: 提交 Issue 或 Pull Request

---

**感谢使用 Windsurf 数据管理工具！**
