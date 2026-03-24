# Windsurf Data Manager

## Overview

This is a GUI tool for managing Windsurf IDE local data, helping users clean and manage RAG indexes, conversation history, cache, and other data to solve high memory usage issues.

## Features

### 1. RAG Index Management (Core Feature)

- **Scan Location**: `~/.codeium/windsurf/` directory
- **Supported Directories**:
  - `cascade/` - Conversation history and context data (.pb, .tmp files)
  - `implicit/` - Implicit context data
  - `brain/` - Brain memory data
  - `database/` - Embedding vector database
  - `code_tracker/` - Code tracking index
  - `codemaps/` - Code maps
  - `rules/` - Rules files
  - `recipes/` - Recipes files
  - `context_state/` - Context state
  - `memories/` - Memory data
  - `global_workflows/` - Global workflows
  - `ask_continue_temp_photo/` - Temporary photos

### 2. Workspace Storage Management

- Scan `%APPDATA%\Windsurf\User\workspaceStorage/` directory
- Display database size and project path for each workspace
- Support deleting single workspace data

### 3. File History Management

- Scan `%APPDATA%\Windsurf\User\History/` directory
- Display file editing history
- Support clearing history records

### 4. Cache Data Management

- Scan all Windsurf cache directories
- Display cache size and file count
- Support clearing all caches

## Usage

### Run Tool

```bash
python windsurf_data_manager_gui.py
```

### Interface Description

The tool contains four tabs:

#### RAG Index Tab (Most Important)

- Display all Codeium RAG index files
- Sort by file size in descending order (largest first)
- **Key Operations**:
  - **Clear All Temp Files** - Safely delete temporary cache, free memory
  - **Delete Selected** - Delete selected files (Warning: .pb files contain conversation history)
  - **View Statistics** - Display size by category and large file list

#### Workspace Storage Tab

- Display all workspace data
- View database table structure
- Delete workspace data

#### File History Tab

- Display file editing history
- Clear history records

#### Cache Data Tab

- Display all cache directories
- Clear caches

## Memory Usage Issue

### Cause Analysis

Windsurf uses RAG (Retrieval-Augmented Generation) to index codebase, these index files can be very large:

- `cascade/*.pb` files: 26MB, 17MB, 10MB, etc.
- `cascade/*.tmp` files: 29MB, 17MB, etc.
- `implicit/*.pb` files: 14MB, 10MB, etc.

These files are loaded into memory, which is the main cause of memory saturation.

### Solutions

1. **Clear Temp Files** (Recommended)
   - Use "Clear All Temp Files(.tmp)" button
   - Safely delete temporary cache without affecting conversation history
   - Can free large amount of memory

2. **Delete Old Conversation History** (Caution)
   - Select and delete .pb files no longer needed
   - Will lose corresponding conversation history
   - Recommend regular cleanup

3. **Clear Other Caches**
   - Regularly clean Windsurf cache directories
   - Clean workspace data (unused projects)

## Technical Details

### Data Storage Locations

**Windows**:
- Windsurf Data: `%APPDATA%\Windsurf\`
- Codeium RAG: `%USERPROFILE%\.codeium\windsurf\`

**macOS**:
- Windsurf Data: `~/Library/Application Support/Windsurf/`
- Codeium RAG: `~/.codeium/windsurf/`

**Linux**:
- Windsurf Data: `~/.config/Windsurf/`
- Codeium RAG: `~/.codeium/windsurf/`

### File Type Description

| Extension | Type | Description | Deletability |
|-----------|------|-------------|--------------|
| .pb | Protocol Buffer | Conversation history, context data | Caution (will lose history) |
| .tmp | Temp File | Temporary cache | Safe (regular cleanup) |
| .sqlite* | SQLite Database | Embedding vector database | Caution |
| .json | JSON Config | Configuration file | Caution |
| .md | Markdown | Document | Safe |

## Notes

1. **Backup Important Data**: Recommend backup before deleting files
2. **Close Windsurf**: Recommend closing Windsurf IDE before cleanup
3. **Caution Deleting .pb Files**: These files contain conversation history
4. **Regularly Clean .tmp Files**: These are temporary cache, can be safely deleted
5. **Cross-Platform Support**: Tool supports Windows, macOS, Linux

## Dependencies

- Python 3.7+
- tkinter (Python built-in)

No additional dependencies required.

## License

This project uses the **MIT License** open source license.

### License Permissions

You are granted the following rights:

- ✅ **Commercial Use** - Can use this tool for commercial purposes
- ✅ **Modify** - Can modify source code to fit your needs
- ✅ **Distribute** - Can distribute original or modified versions
- ✅ **Private Use** - Can use and modify privately
- ✅ **Secondary Development** - Can perform secondary development and extension based on this tool

### Conditions of Use

When using this tool, please comply with the following conditions:

1. **Retain Copyright Notice** - Include copyright notice in all copies or substantial parts
2. **Include License** - Include full license text in all copies or substantial parts
3. **Disclaimer** - Software is provided "as is", without any form of warranty

### Disclaimer

This tool is provided "as is", without any express or implied warranties, including but not limited to warranties of merchantability, fitness for a particular purpose, and non-infringement. In no event shall the authors or copyright holders be liable for any claim, damages, or other liability, whether in contract, tort, or otherwise, arising from, out of, or in connection with the software or the use or other dealings in the software.

### Contact

For questions or suggestions, please contact via:

- Project Address: WorkClaw Project
- Feedback: Submit Issue or Pull Request

---

**Thank you for using Windsurf Data Manager!**

## Other Information

### AI Community Group
- **QQ Group Number**: 642105456
- Welcome to join the community group for latest news and technical support

### AI Model API Aggregation Site
- **Global 534 Large Model API Aggregation Site**: https://aiyiwei.vip
- All basic models you want are available

### Registration Benefits
- Free 20 image-to-video generations upon registration
- Continue to receive gifts by logging in daily
- Also free one-click deployment lobster, first come first served

### Check-in Rewards
- Each account receives $0.2 to $1 per daily check-in
- $0.2 upon registration
- 100 days check-in gives $20 (about 140 CNY)
- 1000 days check-in gives 1400 CNY

### Top-up Discounts
- Minimum top-up amount is 1 CNY
- Top-up discount is about 10-20% of official website price
- Electronic invoice available for every top-up

### Multi-Account Support
- No IP restriction
- Operation Documentation: https://lcn5lluoc63n.feishu.cn/docx/LtPldsmm7oR9XaxdBP7casW0nUJ
- Support multiple account registration

### API Call Tutorials
- **Claude Code Call Tutorial**: https://migxy8em66.apifox.cn/doc-8196820
- **Cline Call Tutorial**: https://migxy8em66.apifox.cn/doc-8196827
- **Cursor Call Tutorial**: https://migxy8em66.apifox.cn/doc-8196829
