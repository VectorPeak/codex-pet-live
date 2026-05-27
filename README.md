<h1 align="center">
  PeakDeskSprite
</h1>

<p align="center">
  基于 PySide6 的桌面宠物框架，用于构建可换装、可扩展、可陪伴的桌面角色
</p>

<p align="center">
  <a>
    <img src="https://img.shields.io/github/license/VectorPeak/PeakDeskSprite.svg">
  </a>

  <a style="text-decoration:none">
    <img src="https://img.shields.io/github/downloads/VectorPeak/PeakDeskSprite/total.svg"/>
  </a>

  <a style="text-decoration:none">
    <img src="https://img.shields.io/badge/python-3.9+-blue.svg" />
  </a>

  <a style="text-decoration:none">
    <img src="https://img.shields.io/badge/PeakDeskSprite-v0.8.5-green.svg"/>
  </a>
</p>

<p align="center">
简体中文 | <a href="README_EN.md">English</a>
</p>

![Interface](https://raw.githubusercontent.com/VectorPeak/PeakDeskSprite/main/docs/PeakDeskSprite.png)

## 项目简介

PeakDeskSprite 是一只可以住在桌面上的小伙伴，也是一套面向开发者的桌宠框架。它把角色素材、动作状态、交互事件、背包物品、系统通知和可选 LLM 聊天能力组织在同一个 PySide6 桌面运行时里，让桌宠既能被直接使用，也能被继续改造成新的角色和玩法

它不是只绑定某一个形象的小程序，而是一个可以不断换衣服、换动作、换道具、换性格的桌宠底座。你可以把它当作桌面陪伴应用，也可以把它当作角色素材实验室、互动 Demo 原型或轻量桌面工具的起点

## 它能做什么

- 在桌面上显示可拖拽、可互动、会切换状态的角色
- 通过素材包扩展新角色、新动作、物品模组和迷你宠物
- 用背包、数值、通知和设置面板承载更完整的桌宠体验
- 为后续的角色聊天、AI 气泡和 LLM 互动保留清晰的扩展位置

## Quick Start

### Windows 用户

1. 打开 [GitHub Releases](https://github.com/VectorPeak/PeakDeskSprite/releases)
2. 下载当前版本的 Windows 发布包，文件名通常为 `PeakDeskSprite-vX.Y.Z-windows-x64.zip`
3. 解压后双击 `PeakDeskSprite.exe` 启动桌宠

## 功能概览

- 桌面角色运行时：支持角色动作、状态切换、拖拽、交互和桌面常驻
- 素材与模组：支持角色、物品模组和迷你宠物的导入与管理
- 背包与数值系统：包含物品格子、自动喂食、HP / FV / 好感度等桌宠状态
- 通知与设置面板：提供通知合并、界面设置、运行时配置和桌宠行为开关
- 可选 LLM 聊天：预留角色聊天、上下文、提示词与服务商配置相关能力

## 项目结构与公开文档

- `PeakDeskSprite/__main__.py`：源码运行入口；Release 包中的可执行文件统一命名为 `PeakDeskSprite.exe`
- `PeakDeskSprite/`：PySide6 桌宠运行时代码、设置面板、仪表盘、通知、LLM 相关界面和服务
- `res/`：默认角色、物品、语言和 UI 资源
- `docs/`：开发、发布和源码结构文档
- `scripts/`：发布构建、发布包审计和 smoke test 脚本
- `tools/`：面向 Codex / HatchPet 等辅助流程的工具与技能说明
- `.github/`：Issue 模板、PR 模板和 GitHub Actions 工作流


## 开发者文档

### 素材开发

如果你想开发新的宠物形象、动作、道具或迷你宠物，请先阅读 [素材开发文档](docs/art_dev.md) 和 [HatchPet 转换说明](docs/hatchpet_converter.md)

### 功能开发

如果你想修改运行时、设置面板、通知、背包、LLM 或发布流程，请先阅读这些文档：

- [源码结构说明](docs/source_architecture.md)
- [依赖结构图](docs/source_dependency_map.md)
- [参与贡献](CONTRIBUTING.md)
- [Windows 发布清单](docs/release_checklist.md)
- [安全报告](SECURITY.md)
- [第三方与素材授权说明](NOTICE.md)

## 贡献与反馈

公开仓库欢迎以下类型的贡献：

- 反馈桌宠启动、资源加载、角色导入、背包、通知或设置面板问题
- 补充角色、物品模组、迷你宠物、文档示例或截图说明
- 修复路径兼容、发布包审计、资源定位、UI 行为和 smoke test 问题
- 讨论 LLM 聊天、角色气泡、上下文管理和本地隐私边界

提交代码前请先阅读 [CONTRIBUTING.md](CONTRIBUTING.md)。如果你发现安全或隐私相关问题，请优先按照 [SECURITY.md](SECURITY.md) 的说明私下报告


## LLM 隐私说明

LLM 功能是可选功能。启用后，桌宠会把用户输入、必要的聊天上下文、角色提示词和事件文本发送到用户配置的 LLM 服务商。API Key 优先从环境变量读取，也可保存在本机运行态配置目录，聊天记录保存在本机运行态数据目录

请不要在公开 issue、日志、截图或 PR 中粘贴 API Key、聊天记录、服务商返回体或未脱敏的本机路径


## 第三方与素材授权

项目代码遵循仓库内的 [LICENSE](LICENSE)。默认素材、示例素材、第三方角色/物品模组、外部字体/图标/音频和用户自行导入的素材可能有独立授权边界。分发或二次创作前请阅读 [NOTICE.md](NOTICE.md)


## 致谢
- 基于 [ChaozhongLiu/DyberPet](https://github.com/ChaozhongLiu/DyberPet) 基座进行二次开发
- UI 重构基于 [Fluent-Widgets](https://github.com/zhiyiYo/PyQt-Fluent-Widgets)，感谢作者 [zhiyiYo](https://github.com/zhiyiYo) 的指导和帮助
- Demo 中的部分素材来自 [daywa1kr](https://github.com/daywa1kr/Desktop-Cat)
- 框架早期的动画模块的逻辑参考了 [yanji255](https://toscode.gitee.com/yanji255/desktop_pet/)
- 框架拖拽掉落的计算逻辑参考了 [WolfChen1996](https://github.com/WolfChen1996/DesktopPet)
