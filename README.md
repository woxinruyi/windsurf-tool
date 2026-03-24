# Windsurf 数据管理工具 / Windsurf Data Manager

## 概述 / Overview

这是一个用于管理 Windsurf IDE 本地数据的图形界面工具，帮助用户清理和管理 RAG 索引、对话历史、缓存等数据，解决内存占用过高的问题。

This is a GUI tool for managing Windsurf IDE local data, helping users clean and manage RAG indexes, conversation history, cache, and other data to solve high memory usage issues.

## 功能特性 / Features

### 1. RAG 索引管理（核心功能）/ RAG Index Management (Core Feature)

- **扫描位置 / Scan Location**: `~/.codeium/windsurf/` directory
- **支持目录 / Supported Directories**:
  - `cascade/` - 对话历史和上下文数据 / Conversation history and context data (.pb, .tmp files)
  - `implicit/` - 隐式上下文数据 / Implicit context data
  - `brain/` - 大脑记忆数据 / Brain memory data
  - `database/` - 嵌入向量数据库 / Embedding vector database
  - `code_tracker/` - 代码追踪索引 / Code tracking index
  - `codemaps/` - 代码地图 / Code maps
  - `rules/` - 规则文件 / Rules files
  - `recipes/` - 配方文件 / Recipes files
  - `context_state/` - 上下文状态 / Context state
  - `memories/` - 记忆数据 / Memory data
  - `global_workflows/` - 全局工作流 / Global workflows
  - `ask_continue_temp_photo/` - 临时图片 / Temporary photos

### 2. 工作区存储管理 / Workspace Storage Management

- 扫描 `%APPDATA%\Windsurf\User\workspaceStorage/` 目录 / Scan workspace storage directory
- 显示每个工作区的数据库大小和项目路径 / Display database size and project path for each workspace
- 支持删除单个工作区数据 / Support deleting single workspace data

### 3. 文件历史管理 / File History Management

- 扫描 `%APPDATA%\Windsurf\User\History/` 目录 / Scan file history directory
- 显示文件编辑历史记录 / Display file editing history
- 支持清理历史记录 / Support clearing history records

### 4. 缓存数据管理 / Cache Data Management

- 扫描所有 Windsurf 缓存目录 / Scan all Windsurf cache directories
- 显示缓存大小和文件数量 / Display cache size and file count
- 支持清理所有缓存 / Support clearing all caches

## 使用方法 / Usage

### 运行工具 / Run Tool

```bash
python windsurf_data_manager_gui.py
```

### 界面说明 / Interface Description

工具包含四个标签页 / The tool contains four tabs:

#### RAG 索引标签页（最重要）/ RAG Index Tab (Most Important)

- 显示所有 Codeium RAG 索引文件 / Display all Codeium RAG index files
- 按文件大小降序排列（最大的在前）/ Sort by file size in descending order (largest first)
- **关键操作 / Key Operations**:
  - **清理所有临时文件(.tmp) / Clear All Temp Files** - 安全删除临时缓存，释放内存 / Safely delete temporary cache, free memory
  - **删除选中 / Delete Selected** - 删除选中的文件（警告：.pb 文件包含对话历史）/ Delete selected files (Warning: .pb files contain conversation history)
  - **查看统计 / View Statistics** - 显示各分类大小和大文件列表 / Display size by category and large file list

#### 工作区存储标签页 / Workspace Storage Tab

- 显示所有工作区数据 / Display all workspace data
- 查看数据库表结构 / View database table structure
- 删除工作区数据 / Delete workspace data

#### 文件历史标签页 / File History Tab

- 显示文件编辑历史 / Display file editing history
- 清理历史记录 / Clear history records

#### 缓存数据标签页 / Cache Data Tab

- 显示所有缓存目录 / Display all cache directories
- 清理缓存 / Clear caches

## 内存占用问题 / Memory Usage Issue

### 原因分析 / Cause Analysis

Windsurf 使用 RAG (Retrieval-Augmented Generation) 索引代码库，这些索引文件可能非常大：
Windsurf uses RAG (Retrieval-Augmented Generation) to index codebase, these index files can be very large:

- `cascade/*.pb` 文件 / files: 26MB, 17MB, 10MB, etc.
- `cascade/*.tmp` 文件 / files: 29MB, 17MB, etc.
- `implicit/*.pb` 文件 / files: 14MB, 10MB, etc.

这些文件会被加载到内存中，是内存占满的主要原因。
These files are loaded into memory, which is the main cause of memory saturation.

### 解决方案 / Solutions

1. **清理临时文件 / Clear Temp Files** (推荐 / Recommended)
   - 使用"清理所有临时文件(.tmp)"按钮 / Use "Clear All Temp Files(.tmp)" button
   - 安全删除临时缓存，不影响对话历史 / Safely delete temporary cache without affecting conversation history
   - 可释放大量内存 / Can free large amount of memory

2. **删除旧的对话历史 / Delete Old Conversation History** (谨慎 / Caution)
   - 选择不再需要的 .pb 文件删除 / Select and delete .pb files no longer needed
   - 会丢失对应的对话历史 / Will lose corresponding conversation history
   - 建议定期清理 / Recommend regular cleanup

3. **清理其他缓存 / Clear Other Caches**
   - 定期清理 Windsurf 缓存目录 / Regularly clean Windsurf cache directories
   - 清理工作区数据（不常用的项目）/ Clean workspace data (unused projects)

## 技术细节 / Technical Details

### 数据存储位置 / Data Storage Locations

**Windows**:
- Windsurf 数据 / Data: `%APPDATA%\Windsurf\`
- Codeium RAG: `%USERPROFILE%\.codeium\windsurf\`

**macOS**:
- Windsurf 数据 / Data: `~/Library/Application Support/Windsurf/`
- Codeium RAG: `~/.codeium/windsurf/`

**Linux**:
- Windsurf 数据 / Data: `~/.config/Windsurf/`
- Codeium RAG: `~/.codeium/windsurf/`

### 文件类型说明 / File Type Description

| 扩展名 / Extension | 类型 / Type | 说明 / Description | 可删除性 / Deletability |
|--------|------|------|---------|
| .pb | Protocol Buffer | 对话历史、上下文数据 / Conversation history, context data | 谨慎 / Caution (会丢失历史 / will lose history) |
| .tmp | 临时文件 / Temp File | 临时缓存 / Temporary cache | 安全 / Safe (定期清理 / regular cleanup) |
| .sqlite* | SQLite 数据库 / Database | 嵌入向量数据库 / Embedding vector database | 谨慎 / Caution |
| .json | JSON 配置 / Config | 配置文件 / Configuration file | 谨慎 / Caution |
| .md | Markdown | 文档 / Document | 安全 / Safe |

## 注意事项 / Notes

1. **备份重要数据 / Backup Important Data**: 删除文件前建议备份 / Recommend backup before deleting files
2. **关闭 Windsurf / Close Windsurf**: 清理前建议关闭 Windsurf IDE / Recommend closing Windsurf IDE before cleanup
3. **谨慎删除 .pb 文件 / Caution Deleting .pb Files**: 这些文件包含对话历史 / These files contain conversation history
4. **定期清理 .tmp 文件 / Regularly Clean .tmp Files**: 这些是临时缓存，可以安全删除 / These are temporary cache, can be safely deleted
5. **跨平台支持 / Cross-Platform Support**: 工具支持 Windows、macOS、Linux / Tool supports Windows, macOS, Linux

## 依赖 / Dependencies

- Python 3.7+
- tkinter（Python 内置 / Python built-in）

无需额外安装依赖 / No additional dependencies required.

## 许可 / License

本项目采用 **MIT License** 开源许可证。
This project uses the **MIT License** open source license.

### 许可权限 / License Permissions

您被授予以下权利 / You are granted the following rights:

- ✅ **商业使用 / Commercial Use** - 可以将此工具用于商业目的 / Can use this tool for commercial purposes
- ✅ **修改 / Modify** - 可以修改源代码以适应您的需求 / Can modify source code to fit your needs
- ✅ **分发 / Distribute** - 可以分发原始或修改后的版本 / Can distribute original or modified versions
- ✅ **私人使用 / Private Use** - 可以私人使用和修改 / Can use and modify privately
- ✅ **二次开发 / Secondary Development** - 可以基于此工具进行二次开发和扩展 / Can perform secondary development and extension based on this tool

### 使用条件 / Conditions of Use

使用本工具时，请遵守以下条件 / When using this tool, please comply with the following conditions:

1. **保留版权声明 / Retain Copyright Notice** - 在所有副本或重要部分中包含版权声明 / Include copyright notice in all copies or substantial parts
2. **包含许可证 / Include License** - 在所有副本或重要部分中包含完整的许可证文本 / Include full license text in all copies or substantial parts
3. **免责声明 / Disclaimer** - 软件按"原样"提供，不提供任何形式的保证 / Software is provided "as is", without any form of warranty

### 免责声明 / Disclaimer

本工具按"原样"提供，不提供任何形式的明示或暗示的保证，包括但不限于适销性、特定用途适用性和非侵权性的保证。在任何情况下，作者或版权持有人都不对任何索赔、损害或其他责任负责，无论是合同、侵权或其他方面的责任，由软件或软件的使用或其他交易引起、产生或与之相关。
This tool is provided "as is", without any express or implied warranties, including but not limited to warranties of merchantability, fitness for a particular purpose, and non-infringement. In no event shall the authors or copyright holders be liable for any claim, damages, or other liability, whether in contract, tort, or otherwise, arising from, out of, or in connection with the software or the use or other dealings in the software.

### 联系方式 / Contact

如有问题或建议，欢迎通过以下方式联系 / For questions or suggestions, please contact via:

- 项目地址 / Project Address: WorkClaw 项目 / Project
- 问题反馈 / Feedback: 提交 Issue 或 Pull Request / Submit Issue or Pull Request

---

**感谢使用 Windsurf 数据管理工具！/ Thank you for using Windsurf Data Manager!**

## 其它信息 / Other Information

### AI 交流群 / AI Community Group
- **QQ群号 / QQ Group Number**: 642105456
- 欢迎加入交流群，获取最新资讯和技术支持 / Welcome to join the community group for latest news and technical support

### AI 模型 API 聚合站 / AI Model API Aggregation Site
- **全球534个大模型API聚合站 / Global 534 Large Model API Aggregation Site**: https://aiyiwei.vip
- 你想要的基本模型都有 / All basic models you want are available

### 注册福利 / Registration Benefits
- 注册免费赠送20个图片生成视频 / Free 20 image-to-video generations upon registration
- 每天登陆继续赠送 / Continue to receive gifts by logging in daily
- 更有免费赠送一键部署龙虾，手慢则无 / Also free one-click deployment lobster, first come first served

### 签到奖励 / Check-in Rewards
- 每个账号每天登陆签到送0.2美元到1美元 / Each account receives $0.2 to $1 per daily check-in
- 注册送0.2美元 / $0.2 upon registration
- 签到100天赠送20美元（约140元）/ 100 days check-in gives $20 (about 140 CNY)
- 签到1000天赠送1400元 / 1000 days check-in gives 1400 CNY

### 充值优惠 / Top-up Discounts
- 最低充值额度下限为1元人民币 / Minimum top-up amount is 1 CNY
- 充值折扣约为官网1到2折 / Top-up discount is about 10-20% of official website price
- 每笔充值均可开具电子发票 / Electronic invoice available for every top-up

### 多账号支持 / Multi-Account Support
- 不限制IP / No IP restriction
- 操作文档说明 / Operation Documentation: https://lcn5lluoc63n.feishu.cn/docx/LtPldsmm7oR9XaxdBP7casW0nUJ
- 支持多账号注册 / Support multiple account registration

### 调用教程 / API Call Tutorials
- **Claude Code 调用使用教程 / Claude Code Call Tutorial**: https://migxy8em66.apifox.cn/doc-8196820
- **Cline 调用教程 / Cline Call Tutorial**: https://migxy8em66.apifox.cn/doc-8196827
- **Cursor 调用教程 / Cursor Call Tutorial**: https://migxy8em66.apifox.cn/doc-8196829
