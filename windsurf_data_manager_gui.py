#!/usr/bin/env python3
"""
temp_windsurf_data_manager_gui.py
Windsurf 数据管理器 - 离线 GUI 工具

功能说明：
- 扫描和管理 Windsurf IDE 的本地数据存储
- 包括工作区存储、文件历史、缓存数据
- 支持可视化和清理操作

Windsurf 数据结构说明（基于官方文档）：
- RAG索引：Windsurf 使用 RAG (Retrieval-Augmented Generation) 索引代码库
- 本地索引存储在 workspaceStorage 的 state.vscdb 数据库中
- 企业版支持远程索引服务，索引存储在云端

数据目录结构：
Windows: %APPDATA%\Windsurf\
macOS: ~/Library/Application Support/Windsurf/
Linux: ~/.config/Windsurf/

主要子目录：
- User/workspaceStorage/ - 每个项目的工作区数据，包含 state.vscdb 数据库
- User/History/ - 文件编辑历史记录
- Cache/, GPUCache/, CachedData/ - 各种缓存数据
- Local Storage/, Session Storage/ - 浏览器存储数据

官方文档参考：
- Context Awareness: https://docs.windsurf.com/context-awareness/overview
- Remote Indexing: https://docs.windsurf.com/context-awareness/remote-indexing

================================================================================
数据流程图 (Data Flow Diagram)
================================================================================

用户操作                    GUI界面                    数据管理器                  文件系统
   │                          │                           │                          │
   │  1. 启动程序             │                           │                          │
   ├─────────────────────────>│                           │                          │
   │                          │  2. 初始化                 │                          │
   │                          ├──────────────────────────>│                          │
   │                          │                           │  3. 扫描数据目录          │
   │                          │                           ├─────────────────────────>│
   │                          │                           │                          │
   │                          │                           │  4. 返回文件列表          │
   │                          │                           │<─────────────────────────┤
   │                          │  5. 返回数据结构           │                          │
   │                          │<──────────────────────────┤                          │
   │                          │                           │                          │
   │  6. 显示数据             │                           │                          │
   │<─────────────────────────┤                          │                          │
   │                          │                           │                          │
   │  7. 选择项目             │                           │                          │
   ├─────────────────────────>│                           │                          │
   │                          │  8. 更新选择状态           │                          │
   │                          │                           │                          │
   │  9. 执行删除             │                           │                          │
   ├─────────────────────────>│                           │                          │
   │                          │  10. 调用删除方法          │                          │
   │                          ├──────────────────────────>│                          │
   │                          │                           │  11. 删除文件/目录        │
   │                          │                           ├─────────────────────────>│
   │                          │                           │                          │
   │                          │                           │  12. 确认删除成功         │
   │                          │                           │<─────────────────────────┤
   │                          │  13. 返回操作结果          │                          │
   │                          │<──────────────────────────┤                          │
   │  14. 显示结果            │                           │                          │
   │<─────────────────────────┤                          │                          │
   │                          │                           │                          │

数据存储结构:

┌─────────────────────────────────────────────────────────────────────────────┐
│                        Windsurf 数据目录                                      │
│                    %APPDATA%\Windsurf\ (Windows)                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │ User/                                                                 │   │
│  │  ├── workspaceStorage/                                                │   │
│  │  │    ├── {workspace_id_1}/                                           │   │
│  │  │    │    ├── state.vscdb      ← SQLite数据库 (RAG索引+对话历史)      │   │
│  │  │    │    └── workspace.json   ← 项目路径映射                         │   │
│  │  │    ├── {workspace_id_2}/                                           │   │
│  │  │    │    └── ...                                                    │   │
│  │  │    └── ...                                                         │   │
│  │  │                                                                    │   │
│  │  ├── History/                   ← 文件编辑历史                        │   │
│  │  │    ├── {history_id_1}/                                            │   │
│  │  │    │    ├── entries.json     ← 原始文件路径                         │   │
│  │  │    │    └── {file_content}   ← 历史版本内容                         │   │
│  │  │    └── ...                                                         │   │
│  │  │                                                                    │   │
│  │  ├── settings.json             ← 用户设置                             │   │
│  │  └── snippets/                 ← 代码片段                             │   │
│  │                                                                       │   │
│  ├── Cache/                       ← 通用缓存                             │   │
│  ├── Code Cache/                  ← 代码缓存                             │   │
│  ├── GPUCache/                    ← GPU渲染缓存                           │   │
│  ├── CachedData/                  ← 数据缓存                             │   │
│  ├── CachedExtensionVSIXs/        ← 扩展安装包缓存                        │   │
│  ├── Local Storage/               ← 浏览器本地存储                        │   │
│  ├── Session Storage/             ← 浏览器会话存储                        │   │
│  ├── DawnCache/                   ← Dawn图形库缓存                        │   │
│  └── blob_storage/                ← 二进制大对象存储                      │   │
│                                                                          │   │
└─────────────────────────────────────────────────────────────────────────────┘

================================================================================
业务流程图 (Business Process Flow)
================================================================================

程序启动流程:

    ┌─────────────┐
    │   开始      │
    └──────┬──────┘
           │
           ▼
    ┌─────────────────────┐
    │  检测操作系统        │
    │  (Windows/macOS/Linux)│
    └──────────┬──────────┘
               │
               ▼
    ┌─────────────────────┐
    │  确定数据路径        │
    │  (APPDATA环境变量)   │
    └──────────┬──────────┘
               │
               ▼
    ┌─────────────────────┐
    │  初始化GUI界面       │
    └──────────┬──────────┘
               │
               ▼
    ┌─────────────────────┐
    │  扫描工作区存储      │──────┐
    └──────────┬──────────┘      │
               │                 │
               ▼                 ▼
    ┌─────────────────────┐  ┌─────────────────┐
    │  扫描历史记录        │  │  扫描缓存目录    │
    └──────────┬──────────┘  └────────┬────────┘
               │                      │
               └──────────┬───────────┘
                          │
                          ▼
    ┌─────────────────────┐
    │  显示数据统计        │
    └──────────┬──────────┘
               │
               ▼
    ┌─────────────────────┐
    │  进入主事件循环      │
    └──────────┬──────────┘
               │
               ▼
    ┌─────────────┐
    │   等待用户操作    │
    └─────────────┘


用户操作流程:

    ┌─────────────────────────────────────────────────────────────────────┐
    │                         用户操作选择                                 │
    └──────────────────────────────┬──────────────────────────────────────┘
                                   │
        ┌──────────────────────────┼──────────────────────────┐
        │                          │                          │
        ▼                          ▼                          ▼
┌───────────────┐         ┌───────────────┐         ┌───────────────┐
│  工作区管理    │         │  历史记录管理  │         │  缓存管理     │
└───────┬───────┘         └───────┬───────┘         └───────┬───────┘
        │                         │                         │
        ▼                         ▼                         ▼
┌───────────────┐         ┌───────────────┐         ┌───────────────┐
│ • 查看工作区   │         │ • 查看历史条目 │         │ • 查看缓存大小 │
│ • 选择工作区   │         │ • 选择历史记录 │         │ • 清理缓存     │
│ • 删除工作区   │         │ • 删除历史记录 │         │ • 释放空间     │
│ • 查看数据库表 │         │ • 清理全部历史 │         │               │
└───────┬───────┘         └───────┬───────┘         └───────┬───────┘
        │                         │                         │
        └─────────────────────────┼─────────────────────────┘
                                  │
                                  ▼
                    ┌─────────────────────┐
                    │  确认操作           │
                    │  (弹出确认对话框)   │
                    └──────────┬──────────┘
                               │
                    ┌──────────┴──────────┐
                    │                      │
                    ▼                      ▼
            ┌─────────────┐        ┌─────────────┐
            │   确认      │        │   取消      │
            └──────┬──────┘        └──────┬──────┘
                   │                      │
                   ▼                      ▼
            ┌─────────────┐        ┌─────────────┐
            │  执行操作   │        │  返回主界面  │
            └──────┬──────┘        └─────────────┘
                   │
                   ▼
            ┌─────────────────────┐
            │  记录操作日志       │
            └──────────┬──────────┘
                       │
                       ▼
            ┌─────────────────────┐
            │  刷新数据列表       │
            └──────────┬──────────┘
                       │
                       ▼
            ┌─────────────────────┐
            │  显示操作结果       │
            └─────────────────────┘


删除操作详细流程:

    ┌─────────────────┐
    │  用户选择项目    │
    └────────┬────────┘
             │
             ▼
    ┌─────────────────┐
    │  点击删除按钮    │
    └────────┬────────┘
             │
             ▼
    ┌─────────────────────────┐
    │  检查是否有选中项目     │
    └────────┬────────────────┘
             │
        ┌────┴────┐
        │         │
        ▼         ▼
    ┌───────┐  ┌───────────────┐
    │ 无    │  │   有选中项目   │
    └───┬───┘  └───────┬───────┘
        │              │
        ▼              ▼
    ┌───────────┐  ┌───────────────────┐
    │ 显示警告   │  │ 弹出确认对话框     │
    └───────────┘  └─────────┬─────────┘
                            │
                   ┌────────┴────────┐
                   │                 │
                   ▼                 ▼
            ┌───────────┐     ┌───────────┐
            │  用户确认  │     │  用户取消  │
            └─────┬─────┘     └─────┬─────┘
                  │                 │
                  ▼                 ▼
            ┌─────────────────┐  ┌───────────┐
            │ 遍历选中项目     │  │ 返回主界面 │
            └────────┬────────┘  └───────────┘
                     │
                     ▼
            ┌─────────────────┐
            │ 调用删除方法     │
            │ shutil.rmtree() │
            └────────┬────────┘
                     │
                ┌────┴────┐
                │         │
                ▼         ▼
            ┌───────┐  ┌───────┐
            │ 成功  │  │ 失败  │
            └───┬───┘  └───┬───┘
                │          │
                ▼          ▼
            ┌───────────────────┐
            │ 记录日志          │
            │ (成功/失败计数)   │
            └─────────┬─────────┘
                      │
                      ▼
            ┌───────────────────┐
            │ 刷新数据列表       │
            └─────────┬─────────┘
                      │
                      ▼
            ┌───────────────────┐
            │ 显示结果对话框     │
            └───────────────────┘

================================================================================
"""

# ==================== 路径配置 ====================
# 添加 libs 文件夹到 Python 路径
import sys
import os
from pathlib import Path

# 获取脚本所在目录
script_dir = Path(__file__).parent
# 添加 libs 文件夹到 Python 路径
libs_dir = script_dir / "libs"
if libs_dir.exists():
    sys.path.insert(0, str(libs_dir))

# ==================== 标准库导入 ====================
import json
import shutil
import sqlite3
from dataclasses import dataclass
from typing import List, Dict, Optional
from datetime import datetime

# ==================== GUI 库导入 ====================
# tkinter 是 Python 内置的 GUI 库，无需额外安装
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog


# ==================== 数据类定义 ====================

@dataclass
class WorkspaceInfo:
    """
    工作区信息数据类
    
    Windsurf 为每个打开的项目创建一个唯一的工作区存储目录
    目录名是项目路径的哈希值（如 00911f8a72a0732a36ca354b9910d705）
    
    属性：
        workspace_id: 工作区的唯一标识符（哈希值）
        workspace_path: 工作区存储目录的完整路径
        db_path: state.vscdb 数据库文件路径（存储工作区状态和可能的RAG索引）
        db_size: 数据库文件大小（字节）
        json_path: workspace.json 文件路径（存储项目路径映射）
        last_modified: 最后修改时间戳
        project_path: 项目实际路径（从 workspace.json 读取）
    """
    workspace_id: str
    workspace_path: Path
    db_path: Optional[Path] = None
    db_size: int = 0
    json_path: Optional[Path] = None
    last_modified: float = 0
    project_path: Optional[str] = None


@dataclass
class HistoryInfo:
    """
    历史记录信息数据类
    
    Windsurf 的 History 目录存储文件级别的编辑历史
    每个历史条目对应一个文件的历史版本
    
    注意：这不是对话历史，而是文件编辑历史
    对话历史（conversations）存储在 state.vscdb 数据库中
    
    属性：
        history_id: 历史记录的唯一标识符
        history_path: 历史记录目录路径
        file_count: 该历史条目包含的文件数量
        total_size: 总大小（字节）
        last_modified: 最后修改时间戳
        resource: 原始文件路径（从 entries.json 读取）
    """
    history_id: str
    history_path: Path
    file_count: int
    total_size: int
    last_modified: float
    resource: Optional[str] = None


@dataclass
class CodeiumRagInfo:
    """
    Codeium RAG 索引信息数据类
    
    Codeium 的 RAG 索引存储在 ~/.codeium/windsurf/ 目录
    这是真正的 RAG 索引和对话历史存储位置
    
    主要子目录：
        - cascade/: 对话历史和上下文数据 (.pb, .tmp 文件)
        - implicit/: 隐式上下文数据 (.pb 文件)
        - database/: 嵌入向量数据库 (embedding_database.sqlite)
        - code_tracker/: 代码追踪索引
    
    属性：
        category: 分类名称 (cascade, implicit, database, code_tracker)
        file_path: 文件完整路径
        file_size: 文件大小（字节）
        file_type: 文件类型 (.pb, .tmp, .sqlite 等)
        last_modified: 最后修改时间戳
        conversation_id: 对话ID（如果是从文件名提取的）
    """
    category: str
    file_path: Path
    file_size: int
    file_type: str
    last_modified: float
    conversation_id: Optional[str] = None


# ==================== 核心管理类 ====================

class WindsurfDataManager:
    """
    Windsurf 数据管理器
    
    负责扫描、分析和操作 Windsurf IDE 的本地数据存储
    
    数据存储位置说明：
        - Windows: %APPDATA%\Windsurf\
        - macOS: ~/Library/Application Support/Windsurf/
        - Linux: ~/.config/Windsurf/
    
    核心功能：
        1. 列出所有工作区存储（包含 RAG 索引数据）
        2. 列出所有文件历史记录
        3. 获取缓存信息
        4. 删除/清理数据
    
    关于 RAG 索引：
        Windsurf 使用 RAG (Retrieval-Augmented Generation) 索引代码库
        本地索引存储在两个位置：
        1. ~/.codeium/windsurf/ - 真正的 RAG 索引和对话历史存储
           - cascade/: 对话历史和上下文数据 (.pb, .tmp 文件，可能很大)
           - implicit/: 隐式上下文数据
           - database/: 嵌入向量数据库
        2. state.vscdb 数据库的 ItemTable 表中（工作区状态）
        企业版可以使用远程索引服务，索引存储在云端
    """
    
    def __init__(self):
        """初始化数据管理器，自动检测操作系统和数据路径"""
        self.system = sys.platform
        self.appdata_path = self._get_appdata_path()
        # User 子目录包含用户特定的数据
        self.user_path = self.appdata_path / "User"
        # Codeium RAG 索引路径（真正的 RAG 索引存储位置）
        self.codeium_path = Path.home() / ".codeium" / "windsurf"
        
    def _get_appdata_path(self) -> Path:
        """
        获取 Windsurf 数据路径
        
        根据操作系统返回正确的数据存储路径
        
        Returns:
            Path: Windsurf 数据根目录
        
        路径说明：
            - Windows: 使用 APPDATA 环境变量（Roaming 目录）
            - macOS: 使用用户的 Library/Application Support 目录
            - Linux: 使用 .config 目录
        """
        if self.system == "win32":
            # Windows: C:\Users\<用户名>\AppData\Roaming\Windsurf
            appdata = os.environ.get("APPDATA", "")
            return Path(appdata) / "Windsurf"
        elif self.system == "darwin":
            # macOS: ~/Library/Application Support/Windsurf
            return Path.home() / "Library" / "Application Support" / "Windsurf"
        else:
            # Linux: ~/.config/Windsurf
            return Path.home() / ".config" / "Windsurf"
    
    def list_workspaces(self) -> List[WorkspaceInfo]:
        """
        列出所有工作区存储
        
        Windsurf 为每个打开的项目创建一个独立的工作区存储目录
        目录名是项目路径的 MD5 哈希值
        
        Returns:
            List[WorkspaceInfo]: 工作区信息列表，按最后修改时间降序排列
        
        工作区存储内容：
            - state.vscdb: SQLite 数据库，存储工作区状态
              - 包含 RAG 索引数据（如果启用本地索引）
              - 包含对话历史（conversations）可能存储在此
            - workspace.json: 项目路径映射文件
        """
        workspaces = []
        # workspaceStorage 目录包含所有工作区数据
        storage_path = self.user_path / "workspaceStorage"
        
        if not storage_path.exists():
            return workspaces
        
        # 遍历每个工作区目录
        for ws_dir in storage_path.iterdir():
            if ws_dir.is_dir():
                info = self._analyze_workspace(ws_dir)
                if info:
                    workspaces.append(info)
        
        # 按最后修改时间降序排列（最近的项目在前）
        return sorted(workspaces, key=lambda x: x.last_modified, reverse=True)
    
    def _analyze_workspace(self, ws_path: Path) -> Optional[WorkspaceInfo]:
        """
        分析单个工作区目录
        
        解析工作区存储目录，提取关键信息
        
        Args:
            ws_path: 工作区目录路径
        
        Returns:
            Optional[WorkspaceInfo]: 工作区信息，如果目录无效则返回 None
        
        解析内容：
            1. state.vscdb 数据库文件大小和修改时间
            2. workspace.json 中的项目路径
        """
        ws_id = ws_path.name  # 工作区ID是目录名（哈希值）
        
        # 主要文件路径
        db_path = ws_path / "state.vscdb"      # SQLite 数据库
        json_path = ws_path / "workspace.json"  # 项目路径映射
        
        db_size = 0
        last_modified = 0
        project_path = None
        
        # 检查数据库文件
        # state.vscdb 存储工作区状态，可能包含 RAG 索引数据
        if db_path.exists():
            db_size = db_path.stat().st_size
            last_modified = db_path.stat().st_mtime
        
        # 读取项目路径
        # workspace.json 包含项目文件夹的实际路径
        if json_path.exists():
            try:
                with open(json_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # 'folder' 字段存储项目路径
                    project_path = data.get('folder', '')
                    if last_modified == 0:
                        last_modified = json_path.stat().st_mtime
            except Exception:
                pass
        
        return WorkspaceInfo(
            workspace_id=ws_id,
            workspace_path=ws_path,
            db_path=db_path if db_path.exists() else None,
            db_size=db_size,
            json_path=json_path if json_path.exists() else None,
            last_modified=last_modified,
            project_path=project_path
        )
    
    def list_history(self) -> List[HistoryInfo]:
        """
        列出所有文件历史记录
        
        Windsurf 的 History 目录存储文件级别的编辑历史
        每个子目录对应一个文件的历史版本
        
        Returns:
            List[HistoryInfo]: 历史记录列表，按最后修改时间降序排列
        
        注意：
            - 这是文件编辑历史，不是对话历史
            - 对话历史（conversations）存储在 state.vscdb 数据库中
        """
        histories = []
        history_path = self.user_path / "History"
        
        if not history_path.exists():
            return histories
        
        for hist_dir in history_path.iterdir():
            if hist_dir.is_dir():
                info = self._analyze_history(hist_dir)
                if info:
                    histories.append(info)
        
        return sorted(histories, key=lambda x: x.last_modified, reverse=True)
    
    def _analyze_history(self, hist_path: Path) -> Optional[HistoryInfo]:
        """
        分析单个历史记录目录
        
        Args:
            hist_path: 历史记录目录路径
        
        Returns:
            Optional[HistoryInfo]: 历史记录信息
        
        历史记录目录内容：
            - entries.json: 包含原始文件路径和时间戳
            - 其他文件: 文件的历史版本内容
        """
        hist_id = hist_path.name
        
        file_count = 0
        total_size = 0
        last_modified = 0
        resource = None
        
        # 遍历目录中的所有文件
        for item in hist_path.iterdir():
            if item.is_file():
                file_count += 1
                total_size += item.stat().st_size
                last_modified = max(last_modified, item.stat().st_mtime)
                
                # entries.json 包含原始文件路径信息
                if item.name == "entries.json":
                    try:
                        with open(item, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            # 'resource' 字段存储原始文件路径
                            resource = data.get('resource', '')
                    except Exception:
                        pass
        
        return HistoryInfo(
            history_id=hist_id,
            history_path=hist_path,
            file_count=file_count,
            total_size=total_size,
            last_modified=last_modified,
            resource=resource
        )
    
    def list_codeium_rag(self) -> List[CodeiumRagInfo]:
        """
        列出所有 Codeium RAG 索引文件
        
        这是真正的 RAG 索引存储位置，包含：
            - cascade/: 对话历史和上下文数据 (.pb, .tmp 文件)
            - implicit/: 隐式上下文数据
            - database/: 嵌入向量数据库
            - code_tracker/: 代码追踪索引
            - brain/: 大脑记忆数据 (.pb 文件)
            - memories/: 记忆数据
            - context_state/: 上下文状态
            - rules/: 规则文件
            - recipes/: 配方文件
        
        Returns:
            List[CodeiumRagInfo]: RAG 索引文件列表，按文件大小降序排列
        
        注意：
            这些文件可能非常大（几十MB），是内存占满的主要原因
            .pb 文件是 Protocol Buffer 格式，存储对话历史
            .tmp 文件是临时缓存，可以安全删除
        """
        rag_files = []
        
        if not self.codeium_path.exists():
            return rag_files
        
        # 扫描的子目录和文件类型（完整列表）
        scan_dirs = [
            # 主要数据目录
            ("cascade", [".pb", ".tmp"]),      # 对话历史和临时文件（最大）
            ("implicit", [".pb", ".tmp"]),     # 隐式上下文
            ("brain", [".pb", ".md"]),         # 大脑记忆数据
            ("database", [".sqlite", ".sqlite-wal", ".sqlite-shm"]),  # 嵌入数据库
            
            # 代码追踪和索引
            ("code_tracker", [".md", ".html", ".ts", ".json", ".py"]),  # 代码追踪
            ("codemaps", [".json"]),           # 代码地图
            
            # 配置和规则
            ("rules", [".md", ".json"]),       # 规则文件
            ("recipes", [".md", ".json"]),     # 配方文件
            ("context_state", [".json", ".pb"]),  # 上下文状态
            
            # 记忆和工作流
            ("memories", [".md", ".json", ".pb"]),  # 记忆数据
            ("global_workflows", [".md", ".json"]),  # 全局工作流
            
            # 其他
            ("ask_continue_temp_photo", [".png", ".jpg", ".jpeg"]),  # 临时图片
        ]
        
        for category, extensions in scan_dirs:
            dir_path = self.codeium_path / category
            if not dir_path.exists():
                continue
            
            for ext in extensions:
                for file_path in dir_path.rglob(f"*{ext}"):
                    if file_path.is_file():
                        try:
                            stat = file_path.stat()
                            # 从文件名提取对话ID（如果可能）
                            conversation_id = None
                            if category in ["cascade", "implicit", "brain"]:
                                # 文件名格式: {conversation_id}.{session_id}.{ext}
                                parts = file_path.stem.split(".")
                                if len(parts) >= 1:
                                    conversation_id = parts[0]
                            
                            rag_files.append(CodeiumRagInfo(
                                category=category,
                                file_path=file_path,
                                file_size=stat.st_size,
                                file_type=file_path.suffix,
                                last_modified=stat.st_mtime,
                                conversation_id=conversation_id
                            ))
                        except Exception:
                            pass
        
        # 按文件大小降序排列（最大的文件在前）
        return sorted(rag_files, key=lambda x: x.file_size, reverse=True)
    
    def get_codeium_rag_summary(self) -> Dict[str, Dict]:
        """
        获取 Codeium RAG 索引的摘要统计
        
        Returns:
            Dict[str, Dict]: 各分类的大小和文件数量统计
        """
        summary = {}
        rag_files = self.list_codeium_rag()
        
        for info in rag_files:
            if info.category not in summary:
                summary[info.category] = {
                    "total_size": 0,
                    "file_count": 0,
                    "files": []
                }
            
            summary[info.category]["total_size"] += info.file_size
            summary[info.category]["file_count"] += 1
            # 只保留大文件（>1MB）
            if info.file_size > 1024 * 1024:
                summary[info.category]["files"].append(info)
        
        return summary
    
    def delete_codeium_file(self, file_path: Path) -> bool:
        """
        删除指定的 Codeium RAG 文件
        
        警告：删除 cascade 或 implicit 目录的文件会丢失对话历史
        
        Args:
            file_path: 要删除的文件路径
        
        Returns:
            bool: 删除是否成功
        """
        if not file_path.exists():
            return False
        
        # 安全检查：确保文件在 codeium 目录下
        try:
            file_path.resolve().relative_to(self.codeium_path.resolve())
        except ValueError:
            return False
        
        try:
            file_path.unlink()
            return True
        except Exception:
            return False
    
    def clear_codeium_cache(self, category: str, file_types: List[str] = None) -> tuple:
        """
        清理 Codeium 缓存文件
        
        Args:
            category: 分类名称 (cascade, implicit, database)
            file_types: 要清理的文件类型列表，默认为 [".tmp"]
        
        Returns:
            tuple: (成功数量, 失败数量, 释放空间)
        """
        if file_types is None:
            file_types = [".tmp"]  # 默认只清理临时文件
        
        dir_path = self.codeium_path / category
        if not dir_path.exists():
            return 0, 0, 0
        
        success = 0
        failed = 0
        freed_space = 0
        
        for ext in file_types:
            for file_path in dir_path.rglob(f"*{ext}"):
                if file_path.is_file():
                    size = file_path.stat().st_size
                    if self.delete_codeium_file(file_path):
                        success += 1
                        freed_space += size
                    else:
                        failed += 1
        
        return success, failed, freed_space
    
    def clear_all_codeium_tmp(self) -> tuple:
        """
        清理所有 Codeium 临时文件
        
        Returns:
            tuple: (成功数量, 失败数量, 释放空间)
        """
        total_success = 0
        total_failed = 0
        total_freed = 0
        
        for category in ["cascade", "implicit"]:
            success, failed, freed = self.clear_codeium_cache(category, [".tmp"])
            total_success += success
            total_failed += failed
            total_freed += freed
        
        return total_success, total_failed, total_freed
    
    def get_cache_info(self) -> Dict[str, Dict]:
        """
        获取所有缓存目录信息
        
        Windsurf 使用多个缓存目录存储不同类型的数据
        
        Returns:
            Dict[str, Dict]: 缓存名称到信息的映射
        
        缓存目录说明：
            - Cache: 通用缓存
            - Code Cache: 代码相关缓存
            - GPUCache: GPU 渲染缓存
            - CachedData: 数据缓存
            - CachedExtensionVSIXs: 扩展安装包缓存
            - Local Storage: 浏览器本地存储
            - Session Storage: 浏览器会话存储
            - DawnCache: Dawn 图形库缓存
            - blob_storage: 二进制大对象存储
        """
        caches = {}
        
        # 定义要扫描的缓存目录
        # 格式: (显示名称, 目录路径)
        cache_dirs = [
            ("Cache", self.appdata_path / "Cache"),
            ("Code Cache", self.appdata_path / "Code Cache"),
            ("GPUCache", self.appdata_path / "GPUCache"),
            ("CachedData", self.appdata_path / "CachedData"),
            ("CachedExtensionVSIXs", self.appdata_path / "CachedExtensionVSIXs"),
            ("Local Storage", self.appdata_path / "Local Storage"),
            ("Session Storage", self.appdata_path / "Session Storage"),
            ("DawnCache", self.appdata_path / "DawnCache"),
            ("blob_storage", self.appdata_path / "blob_storage"),
        ]
        
        for name, path in cache_dirs:
            if path.exists():
                size, count = self._calc_dir_size(path)
                caches[name] = {
                    "path": path,
                    "size": size,
                    "count": count
                }
        
        return caches
    
    def _calc_dir_size(self, path: Path) -> tuple:
        """
        计算目录的总大小和文件数量
        
        Args:
            path: 目录路径
        
        Returns:
            tuple: (总大小, 文件数量)
        """
        total_size = 0
        file_count = 0
        
        try:
            # rglob 递归遍历所有子目录
            for item in path.rglob("*"):
                if item.is_file():
                    total_size += item.stat().st_size
                    file_count += 1
        except Exception:
            pass
        
        return total_size, file_count
    
    def get_db_tables(self, db_path: Path) -> List[str]:
        """
        获取 SQLite 数据库中的所有表名
        
        用于分析 state.vscdb 数据库结构
        
        Args:
            db_path: 数据库文件路径
        
        Returns:
            List[str]: 表名列表
        
        已知表：
            - ItemTable: 存储键值对数据，可能包含 RAG 索引和对话历史
        """
        if not db_path or not db_path.exists():
            return []
        
        try:
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            # 查询 sqlite_master 表获取所有表名
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            conn.close()
            return tables
        except Exception:
            return []
    
    def get_conversations_from_db(self, db_path: Path) -> List[Dict]:
        """
        尝试从数据库获取对话数据
        
        注意：此方法尝试查找可能包含对话数据的表
        实际数据结构可能因 Windsurf 版本而异
        
        Args:
            db_path: 数据库文件路径
        
        Returns:
            List[Dict]: 找到的可能包含对话数据的记录
        
        说明：
            conversations（对话历史）可能存储在：
            1. state.vscdb 的 ItemTable 表中（以序列化形式）
            2. 其他专用表中
        """
        if not db_path or not db_path.exists():
            return []
        
        conversations = []
        
        try:
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            
            tables = self.get_db_tables(db_path)
            
            for table in tables:
                try:
                    # 获取表结构
                    cursor.execute(f"SELECT * FROM {table} LIMIT 1")
                    columns = [desc[0] for desc in cursor.description]
                    
                    # 查找可能包含对话数据的列
                    # 关键词: conversation, cascade, chat, message, dialog
                    relevant_cols = [c for c in columns if any(
                        k in c.lower() 
                        for k in ['conversation', 'cascade', 'chat', 'message', 'dialog']
                    )]
                    
                    if relevant_cols:
                        cursor.execute(f"SELECT * FROM {table}")
                        for row in cursor.fetchall():
                            conversations.append({
                                'table': table,
                                'columns': columns,
                                'data': row
                            })
                except Exception:
                    continue
            
            conn.close()
        except Exception:
            pass
        
        return conversations
    
    def delete_workspace(self, ws_id: str) -> bool:
        """
        删除指定工作区的数据
        
        警告：这将删除该项目的所有本地数据，包括：
            - RAG 索引数据
            - 工作区状态
            - 可能的对话历史
        
        Args:
            ws_id: 工作区ID（哈希值）
        
        Returns:
            bool: 删除是否成功
        """
        ws_path = self.user_path / "workspaceStorage" / ws_id
        if not ws_path.exists():
            return False
        
        try:
            shutil.rmtree(ws_path)
            return True
        except Exception:
            return False
    
    def delete_history(self, hist_id: str) -> bool:
        """
        删除指定的文件历史记录
        
        Args:
            hist_id: 历史记录ID
        
        Returns:
            bool: 删除是否成功
        """
        hist_path = self.user_path / "History" / hist_id
        if not hist_path.exists():
            return False
        
        try:
            shutil.rmtree(hist_path)
            return True
        except Exception:
            return False
    
    def clear_cache(self, cache_name: str) -> bool:
        """
        清理指定的缓存目录
        
        删除缓存目录中的所有内容，但保留目录本身
        
        Args:
            cache_name: 缓存名称（如 "Cache", "GPUCache" 等）
        
        Returns:
            bool: 清理是否成功
        """
        cache_info = self.get_cache_info()
        if cache_name not in cache_info:
            return False
        
        cache_path = cache_info[cache_name]["path"]
        
        try:
            # 删除目录内容但保留目录
            for item in cache_path.iterdir():
                if item.is_file():
                    item.unlink()
                elif item.is_dir():
                    shutil.rmtree(item)
            return True
        except Exception:
            return False
    
    def clear_all_caches(self) -> tuple:
        """
        清理所有缓存目录
        
        Returns:
            tuple: (成功数量, 失败数量)
        """
        caches = self.get_cache_info()
        success = 0
        failed = 0
        
        for name in caches:
            if self.clear_cache(name):
                success += 1
            else:
                failed += 1
        
        return success, failed


# ==================== GUI 类 ====================

class DataManagerGUI:
    """
    数据管理器 GUI
    
    使用 tkinter 构建的图形界面，提供：
        - 工作区存储管理
        - 文件历史管理
        - 缓存数据管理
    
    界面结构：
        - 标题栏：显示程序名称和数据路径
        - 标签页：三个主要功能区域
        - 日志面板：显示操作记录
    """
    
    def __init__(self, root: tk.Tk):
        """
        初始化 GUI
        
        Args:
            root: tkinter 根窗口
        """
        self.root = root
        self.root.title("Windsurf 数据管理器")
        self.root.geometry("1000x750")
        self.root.minsize(900, 650)
        
        # 窗口居中显示
        self._center_window()
        
        # 初始化数据管理器
        self.manager = WindsurfDataManager()
        
        # 选择状态跟踪
        self.selected_workspaces: set = set()
        self.selected_histories: set = set()
        self.selected_rag_files: set = set()  # RAG 索引文件选择状态
        self.selected_caches: set = set()      # 缓存选择状态
        
        # 创建界面
        self._create_styles()
        self._create_widgets()
        self._refresh_all()
    
    def _center_window(self):
        """将窗口居中显示在屏幕上"""
        self.root.update_idletasks()
        width = 1000
        height = 750
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def _create_styles(self):
        """创建自定义样式"""
        style = ttk.Style()
        # 使用 clam 主题，提供更现代的外观
        style.theme_use('clam')
        
        # 自定义标签样式
        style.configure('Title.TLabel', font=('Microsoft YaHei', 14, 'bold'))
        style.configure('Tab.TLabel', font=('Microsoft YaHei', 10, 'bold'))
    
    def _create_widgets(self):
        """创建所有界面组件"""
        # 主容器，使用 grid 布局
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置权重，使组件可以随窗口调整大小
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # ===== 标题栏 =====
        title_frame = ttk.Frame(main_frame)
        title_frame.grid(row=0, column=0, pady=(0, 10), sticky=(tk.W, tk.E))
        
        ttk.Label(
            title_frame, 
            text="Windsurf 数据管理器", 
            style='Title.TLabel'
        ).pack(side=tk.LEFT)
        
        # 显示数据路径
        self.path_label = ttk.Label(
            title_frame,
            text=f"数据路径: {self.manager.appdata_path}",
            font=('Microsoft YaHei', 9)
        )
        self.path_label.pack(side=tk.RIGHT)
        
        # ===== 标签页容器 =====
        notebook = ttk.Notebook(main_frame)
        notebook.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # RAG 索引标签页（最重要，放在第一个）
        rag_frame = ttk.Frame(notebook, padding="5")
        notebook.add(rag_frame, text="RAG 索引")
        self._create_rag_tab(rag_frame)
        
        # 工作区存储标签页
        ws_frame = ttk.Frame(notebook, padding="5")
        notebook.add(ws_frame, text="工作区存储")
        self._create_workspace_tab(ws_frame)
        
        # 文件历史标签页
        hist_frame = ttk.Frame(notebook, padding="5")
        notebook.add(hist_frame, text="文件历史")
        self._create_history_tab(hist_frame)
        
        # 缓存数据标签页
        cache_frame = ttk.Frame(notebook, padding="5")
        notebook.add(cache_frame, text="缓存数据")
        self._create_cache_tab(cache_frame)
        
        # ===== 日志面板 =====
        log_frame = ttk.LabelFrame(main_frame, text="操作日志", padding="5")
        log_frame.grid(row=2, column=0, pady=(10, 0), sticky=(tk.W, tk.E))
        log_frame.columnconfigure(0, weight=1)
        
        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            height=6,
            wrap=tk.WORD,
            font=('Consolas', 9)
        )
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 初始日志
        self._log("程序启动完成")
        self._log(f"Windsurf 数据路径: {self.manager.appdata_path}")
        self._log(f"Codeium RAG 路径: {self.manager.codeium_path}")
    
    def _create_rag_tab(self, parent):
        """
        创建 RAG 索引标签页
        
        显示所有 Codeium RAG 索引文件，包括：
            - cascade/: 对话历史和上下文数据 (.pb, .tmp)
            - implicit/: 隐式上下文数据
            - database/: 嵌入向量数据库
            - code_tracker/: 代码追踪索引
        
        这些文件可能非常大（几十MB），是内存占满的主要原因
        """
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(0, weight=1)
        
        # 统计信息栏
        stats_frame = ttk.Frame(parent)
        stats_frame.grid(row=0, column=0, pady=(0, 5), sticky=(tk.W, tk.E))
        
        self.rag_count_label = ttk.Label(stats_frame, text="索引文件: 0")
        self.rag_count_label.pack(side=tk.LEFT, padx=(0, 20))
        
        self.rag_size_label = ttk.Label(stats_frame, text="总大小: 0 B", foreground="red")
        self.rag_size_label.pack(side=tk.LEFT, padx=(0, 20))
        
        self.rag_path_label = ttk.Label(stats_frame, text=f"路径: {self.manager.codeium_path}", font=('Microsoft YaHei', 8))
        self.rag_path_label.pack(side=tk.RIGHT)
        
        # 树形列表
        columns = ('select', 'category', 'file_name', 'size', 'type', 'modified', 'conv_id')
        self.rag_tree = ttk.Treeview(parent, columns=columns, show='headings', selectmode='none')
        
        # 定义列标题
        self.rag_tree.heading('select', text='选')
        self.rag_tree.heading('category', text='分类')
        self.rag_tree.heading('file_name', text='文件名')
        self.rag_tree.heading('size', text='大小')
        self.rag_tree.heading('type', text='类型')
        self.rag_tree.heading('modified', text='最后修改')
        self.rag_tree.heading('conv_id', text='对话ID')
        
        # 定义列宽
        self.rag_tree.column('select', width=40, anchor='center')
        self.rag_tree.column('category', width=80)
        self.rag_tree.column('file_name', width=300)
        self.rag_tree.column('size', width=100)
        self.rag_tree.column('type', width=60)
        self.rag_tree.column('modified', width=150)
        self.rag_tree.column('conv_id', width=150)
        
        # 垂直滚动条
        vsb = ttk.Scrollbar(parent, orient="vertical", command=self.rag_tree.yview)
        self.rag_tree.configure(yscrollcommand=vsb.set)
        
        self.rag_tree.grid(row=1, column=0, sticky=(tk.N, tk.S, tk.E, tk.W))
        vsb.grid(row=1, column=1, sticky=(tk.N, tk.S))
        
        # 绑定点击事件
        self.rag_tree.bind('<Button-1>', self._on_rag_click)
        
        # 按钮栏
        btn_frame = ttk.Frame(parent)
        btn_frame.grid(row=2, column=0, pady=(10, 0), sticky=(tk.W, tk.E))
        
        ttk.Button(btn_frame, text="刷新", command=self._refresh_rag).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(btn_frame, text="全选", command=self._select_all_rag).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(btn_frame, text="取消", command=self._deselect_all_rag).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(btn_frame, text="删除选中", command=self._delete_selected_rag).pack(side=tk.LEFT, padx=(0, 10))
        
        # 清理临时文件按钮（红色警告）
        clear_tmp_btn = ttk.Button(btn_frame, text="清理所有临时文件(.tmp)", command=self._clear_all_rag_tmp)
        clear_tmp_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # 分类统计按钮
        ttk.Button(btn_frame, text="查看统计", command=self._show_rag_summary).pack(side=tk.LEFT)
    
    def _create_workspace_tab(self, parent):
        """
        创建工作区存储标签页
        
        显示所有工作区存储，包括：
            - 工作区ID（哈希值）
            - 项目路径
            - 数据库大小
            - 最后修改时间
        """
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(0, weight=1)
        
        # 统计信息栏
        stats_frame = ttk.Frame(parent)
        stats_frame.grid(row=0, column=0, pady=(0, 5), sticky=(tk.W, tk.E))
        
        self.ws_count_label = ttk.Label(stats_frame, text="工作区数: 0")
        self.ws_count_label.pack(side=tk.LEFT, padx=(0, 20))
        
        self.ws_size_label = ttk.Label(stats_frame, text="总大小: 0 B")
        self.ws_size_label.pack(side=tk.LEFT)
        
        # 树形列表
        columns = ('select', 'ws_id', 'project_path', 'db_size', 'modified')
        self.ws_tree = ttk.Treeview(parent, columns=columns, show='headings', selectmode='none')
        
        # 定义列标题
        self.ws_tree.heading('select', text='选')
        self.ws_tree.heading('ws_id', text='工作区 ID')
        self.ws_tree.heading('project_path', text='项目路径')
        self.ws_tree.heading('db_size', text='数据库大小')
        self.ws_tree.heading('modified', text='最后修改')
        
        # 定义列宽
        self.ws_tree.column('select', width=40, anchor='center')
        self.ws_tree.column('ws_id', width=150)
        self.ws_tree.column('project_path', width=400)
        self.ws_tree.column('db_size', width=100)
        self.ws_tree.column('modified', width=150)
        
        # 垂直滚动条
        vsb = ttk.Scrollbar(parent, orient="vertical", command=self.ws_tree.yview)
        self.ws_tree.configure(yscrollcommand=vsb.set)
        
        self.ws_tree.grid(row=1, column=0, sticky=(tk.N, tk.S, tk.E, tk.W))
        vsb.grid(row=1, column=1, sticky=(tk.N, tk.S))
        
        # 绑定点击事件（用于选择）
        self.ws_tree.bind('<Button-1>', self._on_ws_click)
        
        # 按钮栏
        btn_frame = ttk.Frame(parent)
        btn_frame.grid(row=2, column=0, pady=(10, 0), sticky=(tk.W, tk.E))
        
        ttk.Button(btn_frame, text="刷新", command=self._refresh_workspaces).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(btn_frame, text="全选", command=self._select_all_ws).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(btn_frame, text="取消", command=self._deselect_all_ws).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(btn_frame, text="删除选中", command=self._delete_selected_ws).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(btn_frame, text="查看数据库表", command=self._show_db_tables).pack(side=tk.LEFT)
    
    def _create_history_tab(self, parent):
        """
        创建文件历史标签页
        
        显示所有文件历史记录，包括：
            - 历史ID
            - 原始文件路径
            - 文件数量
            - 总大小
            - 最后修改时间
        """
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(0, weight=1)
        
        # 统计信息栏
        stats_frame = ttk.Frame(parent)
        stats_frame.grid(row=0, column=0, pady=(0, 5), sticky=(tk.W, tk.E))
        
        self.hist_count_label = ttk.Label(stats_frame, text="历史条目: 0")
        self.hist_count_label.pack(side=tk.LEFT, padx=(0, 20))
        
        self.hist_size_label = ttk.Label(stats_frame, text="总大小: 0 B")
        self.hist_size_label.pack(side=tk.LEFT)
        
        # 树形列表
        columns = ('select', 'hist_id', 'resource', 'files', 'size', 'modified')
        self.hist_tree = ttk.Treeview(parent, columns=columns, show='headings', selectmode='none')
        
        self.hist_tree.heading('select', text='选')
        self.hist_tree.heading('hist_id', text='历史 ID')
        self.hist_tree.heading('resource', text='资源路径')
        self.hist_tree.heading('files', text='文件数')
        self.hist_tree.heading('size', text='大小')
        self.hist_tree.heading('modified', text='最后修改')
        
        self.hist_tree.column('select', width=40, anchor='center')
        self.hist_tree.column('hist_id', width=120)
        self.hist_tree.column('resource', width=400)
        self.hist_tree.column('files', width=60, anchor='center')
        self.hist_tree.column('size', width=80)
        self.hist_tree.column('modified', width=150)
        
        vsb = ttk.Scrollbar(parent, orient="vertical", command=self.hist_tree.yview)
        self.hist_tree.configure(yscrollcommand=vsb.set)
        
        self.hist_tree.grid(row=1, column=0, sticky=(tk.N, tk.S, tk.E, tk.W))
        vsb.grid(row=1, column=1, sticky=(tk.N, tk.S))
        
        self.hist_tree.bind('<Button-1>', self._on_hist_click)
        
        # 按钮栏
        btn_frame = ttk.Frame(parent)
        btn_frame.grid(row=2, column=0, pady=(10, 0), sticky=(tk.W, tk.E))
        
        ttk.Button(btn_frame, text="刷新", command=self._refresh_history).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(btn_frame, text="全选", command=self._select_all_hist).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(btn_frame, text="取消", command=self._deselect_all_hist).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(btn_frame, text="删除选中", command=self._delete_selected_hist).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(btn_frame, text="清理全部历史", command=self._delete_all_hist).pack(side=tk.LEFT)
    
    def _create_cache_tab(self, parent):
        """
        创建缓存数据标签页
        
        显示所有缓存目录，包括：
            - 缓存名称
            - 路径
            - 大小
            - 文件数量
        """
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(0, weight=1)
        
        # 统计信息栏
        stats_frame = ttk.Frame(parent)
        stats_frame.grid(row=0, column=0, pady=(0, 5), sticky=(tk.W, tk.E))
        
        self.cache_count_label = ttk.Label(stats_frame, text="缓存目录: 0")
        self.cache_count_label.pack(side=tk.LEFT, padx=(0, 20))
        
        self.cache_size_label = ttk.Label(stats_frame, text="总大小: 0 B")
        self.cache_size_label.pack(side=tk.LEFT)
        
        # 树形列表
        columns = ('select', 'name', 'path', 'size', 'count')
        self.cache_tree = ttk.Treeview(parent, columns=columns, show='headings', selectmode='none')
        
        self.cache_tree.heading('select', text='选')
        self.cache_tree.heading('name', text='缓存名称')
        self.cache_tree.heading('path', text='路径')
        self.cache_tree.heading('size', text='大小')
        self.cache_tree.heading('count', text='文件数')
        
        self.cache_tree.column('select', width=40, anchor='center')
        self.cache_tree.column('name', width=150)
        self.cache_tree.column('path', width=450)
        self.cache_tree.column('size', width=100)
        self.cache_tree.column('count', width=80, anchor='center')
        
        vsb = ttk.Scrollbar(parent, orient="vertical", command=self.cache_tree.yview)
        self.cache_tree.configure(yscrollcommand=vsb.set)
        
        self.cache_tree.grid(row=1, column=0, sticky=(tk.N, tk.S, tk.E, tk.W))
        vsb.grid(row=1, column=1, sticky=(tk.N, tk.S))
        
        # 绑定点击事件
        self.cache_tree.bind('<Button-1>', self._on_cache_click)
        
        # 按钮栏
        btn_frame = ttk.Frame(parent)
        btn_frame.grid(row=2, column=0, pady=(10, 0), sticky=(tk.W, tk.E))
        
        ttk.Button(btn_frame, text="刷新", command=self._refresh_cache).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(btn_frame, text="全选", command=self._select_all_cache).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(btn_frame, text="取消", command=self._deselect_all_cache).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(btn_frame, text="删除选中", command=self._delete_selected_cache).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(btn_frame, text="清理所有缓存", command=self._clear_all_cache).pack(side=tk.LEFT)
    
    # ==================== 数据刷新方法 ====================
    
    def _refresh_all(self):
        """刷新所有标签页数据"""
        self._refresh_workspaces()
        self._refresh_history()
        self._refresh_cache()
        self._refresh_rag()
    
    def _refresh_rag(self):
        """刷新 RAG 索引列表"""
        for item in self.rag_tree.get_children():
            self.rag_tree.delete(item)
        
        self.selected_rag_files: set = set()
        rag_files = self.manager.list_codeium_rag()
        total_size = 0
        
        for info in rag_files:
            total_size += info.file_size
            # 截断文件名
            file_name = info.file_path.name
            if len(file_name) > 50:
                file_name = file_name[:47] + "..."
            
            self.rag_tree.insert('', tk.END, values=(
                '',
                info.category,
                file_name,
                self._format_size(info.file_size),
                info.file_type,
                self._format_time(info.last_modified),
                info.conversation_id or ''
            ))
        
        # 更新统计标签
        self.rag_count_label.config(text=f"索引文件: {len(rag_files)}")
        self.rag_size_label.config(text=f"总大小: {self._format_size(total_size)}")
        self._log(f"加载了 {len(rag_files)} 个 RAG 索引文件，共 {self._format_size(total_size)}")
    
    def _refresh_workspaces(self):
        """刷新工作区列表"""
        # 清空现有数据
        for item in self.ws_tree.get_children():
            self.ws_tree.delete(item)
        
        self.selected_workspaces.clear()
        
        # 获取工作区数据
        workspaces = self.manager.list_workspaces()
        total_size = 0
        
        for ws in workspaces:
            total_size += ws.db_size
            self.ws_tree.insert('', tk.END, values=(
                '',
                ws.workspace_id,
                ws.project_path or '(未知)',
                self._format_size(ws.db_size),
                self._format_time(ws.last_modified)
            ))
        
        # 更新统计标签
        self.ws_count_label.config(text=f"工作区数: {len(workspaces)}")
        self.ws_size_label.config(text=f"总大小: {self._format_size(total_size)}")
        self._log(f"加载了 {len(workspaces)} 个工作区")
    
    def _refresh_history(self):
        """刷新历史记录列表"""
        for item in self.hist_tree.get_children():
            self.hist_tree.delete(item)
        
        self.selected_histories.clear()
        histories = self.manager.list_history()
        total_size = 0
        
        for hist in histories:
            total_size += hist.total_size
            resource = hist.resource or '(未知)'
            # 截断过长的路径
            if len(resource) > 60:
                resource = resource[:57] + "..."
            
            self.hist_tree.insert('', tk.END, values=(
                '',
                hist.history_id,
                resource,
                hist.file_count,
                self._format_size(hist.total_size),
                self._format_time(hist.last_modified)
            ))
        
        self.hist_count_label.config(text=f"历史条目: {len(histories)}")
        self.hist_size_label.config(text=f"总大小: {self._format_size(total_size)}")
        self._log(f"加载了 {len(histories)} 条历史记录")
    
    def _refresh_cache(self):
        """刷新缓存列表"""
        for item in self.cache_tree.get_children():
            self.cache_tree.delete(item)
        
        self.selected_caches.clear()
        caches = self.manager.get_cache_info()
        total_size = 0
        total_count = 0
        
        for name, info in caches.items():
            total_size += info['size']
            total_count += info['count']
            
            self.cache_tree.insert('', tk.END, values=(
                '',  # select 列
                name,
                str(info['path']),
                self._format_size(info['size']),
                info['count']
            ))
        
        self.cache_count_label.config(text=f"缓存目录: {len(caches)}")
        self.cache_size_label.config(text=f"总大小: {self._format_size(total_size)}")
        self._log(f"加载了 {len(caches)} 个缓存目录，共 {self._format_size(total_size)}")
    
    # ==================== 事件处理方法 ====================
    
    def _on_ws_click(self, event):
        """
        工作区列表点击事件处理
        
        点击第一列（选择列）时切换选中状态
        """
        region = self.ws_tree.identify_region(event.x, event.y)
        if region != "cell":
            return
        
        column = self.ws_tree.identify_column(event.x)
        item = self.ws_tree.identify_row(event.y)
        
        # 只处理第一列的点击
        if column == '#1' and item:
            values = self.ws_tree.item(item, 'values')
            ws_id = values[1]
            
            # 切换选中状态
            if ws_id in self.selected_workspaces:
                self.selected_workspaces.remove(ws_id)
                self.ws_tree.set(item, 'select', '')
            else:
                self.selected_workspaces.add(ws_id)
                self.ws_tree.set(item, 'select', '✓')
    
    def _on_hist_click(self, event):
        """历史记录列表点击事件处理"""
        region = self.hist_tree.identify_region(event.x, event.y)
        if region != "cell":
            return
        
        column = self.hist_tree.identify_column(event.x)
        item = self.hist_tree.identify_row(event.y)
        
        if column == '#1' and item:
            values = self.hist_tree.item(item, 'values')
            hist_id = values[1]
            
            if hist_id in self.selected_histories:
                self.selected_histories.remove(hist_id)
                self.hist_tree.set(item, 'select', '')
            else:
                self.selected_histories.add(hist_id)
                self.hist_tree.set(item, 'select', '✓')
    
    def _on_rag_click(self, event):
        """RAG 索引列表点击事件处理"""
        region = self.rag_tree.identify_region(event.x, event.y)
        if region != "cell":
            return
        
        column = self.rag_tree.identify_column(event.x)
        item = self.rag_tree.identify_row(event.y)
        
        if column == '#1' and item:
            values = self.rag_tree.item(item, 'values')
            # 使用文件名作为唯一标识
            file_name = values[2]
            category = values[1]
            key = f"{category}/{file_name}"
            
            if key in self.selected_rag_files:
                self.selected_rag_files.remove(key)
                self.rag_tree.set(item, 'select', '')
            else:
                self.selected_rag_files.add(key)
                self.rag_tree.set(item, 'select', '✓')
    
    def _on_cache_click(self, event):
        """缓存列表点击事件处理"""
        region = self.cache_tree.identify_region(event.x, event.y)
        if region != "cell":
            return
        
        column = self.cache_tree.identify_column(event.x)
        item = self.cache_tree.identify_row(event.y)
        
        if column == '#1' and item:
            values = self.cache_tree.item(item, 'values')
            cache_name = values[1]
            
            if cache_name in self.selected_caches:
                self.selected_caches.remove(cache_name)
                self.cache_tree.set(item, 'select', '')
            else:
                self.selected_caches.add(cache_name)
                self.cache_tree.set(item, 'select', '✓')
    
    # ==================== 选择操作方法 ====================
    
    def _select_all_ws(self):
        """全选所有工作区"""
        self.selected_workspaces.clear()
        for item in self.ws_tree.get_children():
            values = self.ws_tree.item(item, 'values')
            ws_id = values[1]
            self.selected_workspaces.add(ws_id)
            self.ws_tree.set(item, 'select', '✓')
        self._log(f"已选择 {len(self.selected_workspaces)} 个工作区")
    
    def _deselect_all_ws(self):
        """取消选择所有工作区"""
        self.selected_workspaces.clear()
        for item in self.ws_tree.get_children():
            self.ws_tree.set(item, 'select', '')
        self._log("已取消所有选择")
    
    def _select_all_hist(self):
        """全选所有历史记录"""
        self.selected_histories.clear()
        for item in self.hist_tree.get_children():
            values = self.hist_tree.item(item, 'values')
            hist_id = values[1]
            self.selected_histories.add(hist_id)
            self.hist_tree.set(item, 'select', '✓')
        self._log(f"已选择 {len(self.selected_histories)} 条历史")
    
    def _deselect_all_hist(self):
        """取消选择所有历史记录"""
        self.selected_histories.clear()
        for item in self.hist_tree.get_children():
            self.hist_tree.set(item, 'select', '')
        self._log("已取消所有选择")
    
    def _select_all_rag(self):
        """全选所有 RAG 索引文件"""
        self.selected_rag_files.clear()
        for item in self.rag_tree.get_children():
            values = self.rag_tree.item(item, 'values')
            file_name = values[2]
            category = values[1]
            key = f"{category}/{file_name}"
            self.selected_rag_files.add(key)
            self.rag_tree.set(item, 'select', '✓')
        self._log(f"已选择 {len(self.selected_rag_files)} 个 RAG 文件")
    
    def _deselect_all_rag(self):
        """取消选择所有 RAG 索引文件"""
        self.selected_rag_files.clear()
        for item in self.rag_tree.get_children():
            self.rag_tree.set(item, 'select', '')
        self._log("已取消所有选择")
    
    def _select_all_cache(self):
        """全选所有缓存"""
        self.selected_caches.clear()
        for item in self.cache_tree.get_children():
            values = self.cache_tree.item(item, 'values')
            cache_name = values[1]
            self.selected_caches.add(cache_name)
            self.cache_tree.set(item, 'select', '✓')
        self._log(f"已选择 {len(self.selected_caches)} 个缓存")
    
    def _deselect_all_cache(self):
        """取消选择所有缓存"""
        self.selected_caches.clear()
        for item in self.cache_tree.get_children():
            self.cache_tree.set(item, 'select', '')
        self._log("已取消所有选择")
    
    def _delete_selected_cache(self):
        """删除选中的缓存"""
        if not self.selected_caches:
            messagebox.showwarning("警告", "请先选择要删除的缓存")
            return
        
        if not messagebox.askyesno("确认删除", 
            f"确定要删除选中的 {len(self.selected_caches)} 个缓存吗？"):
            return
        
        success = 0
        for cache_name in list(self.selected_caches):
            if self.manager.clear_cache(cache_name):
                success += 1
                self._log(f"已清理缓存: {cache_name}")
            else:
                self._log(f"清理失败: {cache_name}")
        
        self._refresh_cache()
        messagebox.showinfo("完成", f"成功清理 {success} 个缓存")
    
    # ==================== 删除操作方法 ====================
    
    def _delete_selected_ws(self):
        """删除选中的工作区"""
        if not self.selected_workspaces:
            messagebox.showwarning("警告", "请先选择要删除的工作区")
            return
        
        if not messagebox.askyesno("确认删除", 
            f"确定要删除选中的 {len(self.selected_workspaces)} 个工作区数据吗？\n\n"
            "这将删除该项目的本地数据，包括 RAG 索引和工作区状态。"):
            return
        
        success = 0
        for ws_id in list(self.selected_workspaces):
            if self.manager.delete_workspace(ws_id):
                success += 1
                self._log(f"已删除工作区: {ws_id}")
            else:
                self._log(f"删除失败: {ws_id}")
        
        self._refresh_workspaces()
        messagebox.showinfo("完成", f"成功删除 {success} 个工作区")
    
    def _delete_selected_hist(self):
        """删除选中的历史记录"""
        if not self.selected_histories:
            messagebox.showwarning("警告", "请先选择要删除的历史记录")
            return
        
        if not messagebox.askyesno("确认删除", 
            f"确定要删除选中的 {len(self.selected_histories)} 条历史记录吗？"):
            return
        
        success = 0
        for hist_id in list(self.selected_histories):
            if self.manager.delete_history(hist_id):
                success += 1
                self._log(f"已删除历史: {hist_id}")
            else:
                self._log(f"删除失败: {hist_id}")
        
        self._refresh_history()
        messagebox.showinfo("完成", f"成功删除 {success} 条历史记录")
    
    def _delete_all_hist(self):
        """删除所有历史记录"""
        histories = self.manager.list_history()
        if not histories:
            messagebox.showinfo("提示", "没有可删除的历史记录")
            return
        
        if not messagebox.askyesno("确认删除", 
            f"确定要删除所有 {len(histories)} 条历史记录吗？"):
            return
        
        success = 0
        for hist in histories:
            if self.manager.delete_history(hist.history_id):
                success += 1
        
        self._refresh_history()
        messagebox.showinfo("完成", f"成功删除 {success} 条历史记录")
        self._log(f"已清理全部历史记录: {success} 条")
    
    def _delete_selected_rag(self):
        """删除选中的 RAG 索引文件"""
        if not self.selected_rag_files:
            messagebox.showwarning("警告", "请先选择要删除的 RAG 文件")
            return
        
        if not messagebox.askyesno("确认删除", 
            f"确定要删除选中的 {len(self.selected_rag_files)} 个 RAG 文件吗？\n\n"
            "警告：删除 .pb 文件会丢失对话历史！\n"
            "建议只删除 .tmp 临时文件。"):
            return
        
        success = 0
        freed = 0
        rag_files = self.manager.list_codeium_rag()
        
        for key in list(self.selected_rag_files):
            category, file_name = key.split('/', 1)
            # 查找对应的文件
            for info in rag_files:
                if info.category == category and info.file_path.name.startswith(file_name[:30]):
                    size = info.file_size
                    if self.manager.delete_codeium_file(info.file_path):
                        success += 1
                        freed += size
                        self._log(f"已删除: {info.file_path.name}")
                    else:
                        self._log(f"删除失败: {info.file_path.name}")
                    break
        
        self._refresh_rag()
        messagebox.showinfo("完成", f"成功删除 {success} 个文件，释放 {self._format_size(freed)}")
    
    def _clear_all_rag_tmp(self):
        """清理所有 RAG 临时文件"""
        if not messagebox.askyesno("确认清理", 
            "确定要清理所有 .tmp 临时文件吗？\n\n"
            "这些是临时缓存文件，可以安全删除。\n"
            "不会影响对话历史。"):
            return
        
        success, failed, freed = self.manager.clear_all_codeium_tmp()
        self._refresh_rag()
        messagebox.showinfo("完成", 
            f"成功清理 {success} 个临时文件\n"
            f"失败 {failed} 个\n"
            f"释放空间: {self._format_size(freed)}")
        self._log(f"清理 RAG 临时文件: 成功 {success}, 释放 {self._format_size(freed)}")
    
    def _show_rag_summary(self):
        """显示 RAG 索引统计摘要"""
        summary = self.manager.get_codeium_rag_summary()
        
        win = tk.Toplevel(self.root)
        win.title("RAG 索引统计")
        win.geometry("600x500")
        
        text = scrolledtext.ScrolledText(win, wrap=tk.WORD, font=('Consolas', 10))
        text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        text.insert(tk.END, "RAG 索引统计摘要\n")
        text.insert(tk.END, "=" * 50 + "\n\n")
        text.insert(tk.END, f"路径: {self.manager.codeium_path}\n\n")
        
        total_size = 0
        total_count = 0
        
        for category, info in summary.items():
            total_size += info["total_size"]
            total_count += info["file_count"]
            
            text.insert(tk.END, f"【{category}】\n")
            text.insert(tk.END, f"  文件数: {info['file_count']}\n")
            text.insert(tk.END, f"  总大小: {self._format_size(info['total_size'])}\n")
            
            # 显示大文件
            if info["files"]:
                text.insert(tk.END, f"  大文件 (>1MB):\n")
                for f in sorted(info["files"], key=lambda x: x.file_size, reverse=True)[:10]:
                    text.insert(tk.END, f"    - {f.file_path.name}: {self._format_size(f.file_size)}\n")
            text.insert(tk.END, "\n")
        
        text.insert(tk.END, "=" * 50 + "\n")
        text.insert(tk.END, f"总计: {total_count} 个文件, {self._format_size(total_size)}\n\n")
        
        # 添加说明
        text.insert(tk.END, "分类说明:\n")
        text.insert(tk.END, "  - cascade: 对话历史和上下文数据 (.pb 文件可能很大)\n")
        text.insert(tk.END, "  - implicit: 隐式上下文数据\n")
        text.insert(tk.END, "  - database: 嵌入向量数据库\n")
        text.insert(tk.END, "  - code_tracker: 代码追踪索引\n\n")
        
        text.insert(tk.END, "清理建议:\n")
        text.insert(tk.END, "  - .tmp 文件可以安全删除（临时缓存）\n")
        text.insert(tk.END, "  - .pb 文件包含对话历史，删除会丢失历史\n")
        text.insert(tk.END, "  - 定期清理可释放内存占用\n")
        
        text.config(state=tk.DISABLED)
    
    def _show_db_tables(self):
        """
        显示选中工作区的数据库表信息
        
        打开新窗口显示 state.vscdb 数据库中的所有表
        """
        if not self.selected_workspaces:
            messagebox.showwarning("警告", "请先选择一个工作区")
            return
        
        ws_id = list(self.selected_workspaces)[0]
        ws_path = self.manager.user_path / "workspaceStorage" / ws_id
        db_path = ws_path / "state.vscdb"
        
        if not db_path.exists():
            messagebox.showwarning("警告", "该工作区没有数据库文件")
            return
        
        tables = self.manager.get_db_tables(db_path)
        
        # 创建新窗口显示表信息
        win = tk.Toplevel(self.root)
        win.title(f"数据库表 - {ws_id[:16]}...")
        win.geometry("500x400")
        
        text = scrolledtext.ScrolledText(win, wrap=tk.WORD, font=('Consolas', 10))
        text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        text.insert(tk.END, f"数据库: {db_path}\n\n")
        text.insert(tk.END, f"表数量: {len(tables)}\n\n")
        text.insert(tk.END, "表列表:\n")
        
        for i, table in enumerate(tables, 1):
            text.insert(tk.END, f"  {i}. {table}\n")
        
        # 添加说明
        text.insert(tk.END, "\n说明:\n")
        text.insert(tk.END, "  - ItemTable: 存储键值对数据\n")
        text.insert(tk.END, "  - RAG 索引和对话历史可能存储在此表中\n")
        
        text.config(state=tk.DISABLED)
    
    def _clear_all_cache(self):
        """清理所有缓存"""
        caches = self.manager.get_cache_info()
        if not caches:
            messagebox.showinfo("提示", "没有可清理的缓存")
            return
        
        total_size = sum(info['size'] for info in caches.values())
        
        if not messagebox.askyesno("确认清理", 
            f"确定要清理所有缓存吗？\n\n将释放约 {self._format_size(total_size)} 空间"):
            return
        
        success, failed = self.manager.clear_all_caches()
        self._refresh_cache()
        messagebox.showinfo("完成", f"成功清理 {success} 个缓存目录，失败 {failed} 个")
        self._log(f"已清理缓存: 成功 {success}, 失败 {failed}")
    
    # ==================== 工具方法 ====================
    
    def _log(self, message: str):
        """
        添加日志消息
        
        Args:
            message: 日志消息内容
        """
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        # 自动滚动到最新日志
        self.log_text.see(tk.END)
    
    @staticmethod
    def _format_size(size_bytes: int) -> str:
        """
        格式化文件大小为人类可读格式
        
        Args:
            size_bytes: 字节数
        
        Returns:
            str: 格式化后的大小字符串（如 "15.3 MB"）
        """
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f} TB"
    
    @staticmethod
    def _format_time(timestamp: float) -> str:
        """
        格式化时间戳为人类可读格式
        
        Args:
            timestamp: Unix 时间戳
        
        Returns:
            str: 格式化后的时间字符串（如 "2024-03-24 11:30"）
        """
        return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M')


# ==================== 主函数 ====================

def main():
    """
    主函数 - 程序入口
    
    初始化 tkinter 并启动 GUI 主循环
    """
    root = tk.Tk()
    
    # Windows 高 DPI 支持
    # 使程序在高分辨率显示器上显示清晰
    if sys.platform == "win32":
        try:
            from ctypes import windll
            # 设置 DPI 感知级别
            windll.shcore.SetProcessDpiAwareness(1)
        except Exception:
            pass
    
    # 创建应用实例
    app = DataManagerGUI(root)
    
    # 启动主事件循环
    root.mainloop()


if __name__ == "__main__":
    main()
