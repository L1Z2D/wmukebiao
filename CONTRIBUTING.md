# 贡献指南 (Contributing Guide)

👋 欢迎来到 **课程表生成器 (Zhengfang Schedule to iCal)** 项目！

首先，感谢你愿意抽出时间来参与贡献。无论你是修复了一个拼写错误、改进了文档，还是添加了一个全新的功能，你的每一次提交都能让这个项目变得更好。

这份文档旨在帮助你快速了解项目结构，并顺利完成第一次贡献。

## 🚀 快速上手 (Getting Started)

### 1. 环境准备
在开始之前，请确保你的开发环境满足以下要求：
- **操作系统**: Windows, macOS, 或 Linux
- **Python**: 3.8 或更高版本
- **Git**: 版本控制工具

### 2. 获取代码
1. 点击右上角的 **Fork** 按钮，将本仓库复刻到你的 GitHub 账号下。
2. 将你的 Fork 克隆到本地：
   ```bash
   git clone https://github.com/pkx07/wmukebiao.git
   cd wmukebiao
   ```

### 3. 本地开发环境搭建
为了避免依赖冲突，强烈建议使用 Python 虚拟环境。

```bash
# 1. 创建虚拟环境
python -m venv venv

# 2. 激活虚拟环境
# Windows (CMD/PowerShell):
venv\Scripts\activate
# macOS / Linux:
source venv/bin/activate

# 3. 安装项目依赖
pip install -r requirements.txt
```

### 4. 运行项目
安装完成后，你可以通过以下命令启动本地服务器：

```bash
python app.py
```

终端显示 `Running on http://127.0.0.1:5001` 后，在浏览器中访问该地址即可看到应用界面。

## 📂 项目结构概览

了解项目结构有助于你快速定位代码：

| 文件/目录 | 说明 |
| :--- | :--- |
| `app.py` | **核心入口**。Flask 后端主程序，处理路由、文件上传和 API 响应。 |
| `generate_ics.py` | **业务逻辑**。负责解析 Excel/HTML 数据并生成 iCal (`.ics`) 文件的核心逻辑。 |
| `templates/` | Flask 渲染的 HTML 模板文件（主要用于后端直出模式）。 |
| `static/` | Flask 使用的静态资源（CSS, JS, 图片等）。 |
| `frontend/` | **独立前端**。用于 Vercel 部署的静态前端版本，通过 CORS 调用后端 API。 |
| `requirements.txt`| Python 依赖列表。 |

> **💡 开发提示**：
> - 如果你主要修改后端逻辑（如解析算法），请关注 `generate_ics.py`。
> - 如果你修改 UI/UX，请注意本项目支持两种部署模式（Flask 直出和 Vercel 静态托管），修改前端时最好同时兼顾 `templates/index.html` 和 `frontend/index.html` 的一致性。

## 🤝 贡献流程 (Workflow)

### 1. 分支管理
请不要直接在 `main` 分支上进行修改。根据你的修改类型创建新的分支：

- **功能开发**: `feature/功能名称` (例如: `feature/dark-mode`)
- **Bug 修复**: `fix/问题描述` (例如: `fix/parse-error`)
- **文档改进**: `docs/修改内容` (例如: `docs/update-readme`)

```bash
git checkout -b feature/my-new-feature
```

### 2. 代码规范
- **Python**: 请遵循 [PEP 8](https://peps.python.org/pep-0008/) 编码规范。保持代码简洁、可读。
- **注释**: 关键逻辑请添加中文注释，方便他人理解。
- **提交信息 (Commit Message)**: 请使用清晰的描述性语言。
  - ✅ `fix: 修复了实验课程解析时间错误的问题`
  - ❌ `update code`

### 3. 提交 Pull Request (PR)
1. 将修改推送到你的 GitHub 仓库：`git push origin feature/my-new-feature`
2. 在 GitHub 上发起 Pull Request 到本仓库的 `main` 分支。
3. 在 PR 描述中详细说明你的修改内容、解决了什么问题，以及如何测试你的修改。

## 🐛 反馈问题

如果你发现了 Bug 或有好的建议，但暂时无法通过代码贡献，欢迎提交 [Issue](https://github.com/pkx07/wmukebiao/issues)。

提交 Issue 时请提供：
- **问题描述**: 发生了什么错误？
- **复现步骤**: 如何重现这个错误？
- **环境信息**: 操作系统、浏览器版本等。
- **附件 (可选)**: 如果是解析失败，可以提供脱敏后的课表文件帮助排查。

## 📜 许可证

参与本项目贡献即表示你同意你的代码将遵循项目的 [MIT License](LICENSE)。

---

再次感谢你的热心贡献！让我们一起打造更好用的校园工具！ ❤️
