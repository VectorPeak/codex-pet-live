# Contributing / 参与贡献

感谢关注 PeakDeskSprite。这个项目面向 Windows 桌宠、PySide6 界面和角色素材开发，欢迎提交 bug 修复、功能改进、文档补充和素材配置示例。

## 提交 Issue

- Bug 请尽量提供 Windows 版本、Python 版本、运行方式、复现步骤和关键日志
- 功能建议请说明使用场景、期望行为、是否影响现有角色素材或配置
- 公开 issue 中不要粘贴 API key、聊天记录、账号信息、完整本机路径或未脱敏日志

## 本地开发

```powershell
python -m pip install -r requirements.txt
python run_PeakDeskSprite.py
```

建议在 Windows 环境验证改动。涉及 UI、动画、托盘、开机自启、通知、文件路径的改动，最好说明手动验证过的场景。

## Pull Request

- PR 保持聚焦，一次解决一个明确问题
- 不要混入格式化、依赖升级、发布脚本调整等无关改动
- 修改角色配置、资源目录或默认行为时，请说明兼容性影响
- 新增依赖时，请解释用途，并同步更新 `requirements.txt`
- 文档和中文内容请默认使用 UTF-8 编码

## 代码风格

- 优先沿用现有 PySide6、PySide6-Fluent-Widgets 和项目目录结构
- UI 文案中文优先，必要时保留清晰英文术语
- 避免在界面线程中放入耗时逻辑，涉及文件、网络或模型调用时注意用户体验
