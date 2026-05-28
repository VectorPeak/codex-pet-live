# CodexPetLive Windows Release Checklist

## 目标

第一阶段 release 只解决三件事：可复现构建、发布包内容可审计、发布元数据可复核。

项目只保留一个 `requirements.txt`。它同时服务源码运行和 Windows release 构建，并且是经过发布流程接受的版本范围，不是 `pip freeze`，因此不假造某台机器上的精确安装结果。

输出位置固定为 `release-work\dist`，最终压缩包按版本命名为 `release-work\CodexPetLive-$Version-windows-x64.zip`。`release-work/` 是构建产物目录，不进入 Git。

## Release Python 环境

不要依赖脚本里的私人路径默认值。发布者应显式指定 `-PythonPath`，推荐使用独立虚拟环境：

```powershell
py -3.12 -m venv .venv-release
$PythonPath = (Resolve-Path .\.venv-release\Scripts\python.exe).Path
& $PythonPath -m pip install --upgrade pip
& $PythonPath -m pip install -r .\requirements.txt
& $PythonPath -m pip check
```

如果使用 conda 或已有 Python，也必须把解释器路径赋给 `$PythonPath` 并在后续命令里显式传入：

```powershell
$PythonPath = 'C:\Path\To\Python\python.exe'
& $PythonPath -m pip install -r .\requirements.txt
& $PythonPath -m pip check
```

## 构建命令

在仓库根目录执行：

```powershell
.\scripts\build_release.ps1 -PythonPath $PythonPath
```

脚本会执行：

1. 清理 `release-work\dist`、`release-work\build`、`release-work\spec`。
2. 使用 `python -m PyInstaller --clean --noconfirm` 构建 `CodexPetLive/__main__.py`。
3. 将 PyInstaller 输出写入 `release-work\dist\CodexPetLive`。
4. 审计未压缩发布目录。
5. 压缩为 `release-work\CodexPetLive-$Version-windows-x64.zip`。
6. 审计 zip 包。

如只想重新审计已有包：

```powershell
.\scripts\audit_release_package.ps1 -PackagePath .\release-work\dist\CodexPetLive
.\scripts\audit_release_package.ps1 -PackagePath .\release-work\CodexPetLive-$Version-windows-x64.zip
```

如只想复用已有 PyInstaller 输出并重新打包，可先确认 `release-work\dist\CodexPetLive` 存在，再执行：

```powershell
.\scripts\build_release.ps1 -PythonPath $PythonPath -SkipBuild
```

## 内容黑名单

release 包不允许包含：

- `data`
- `logs`
- `build`
- `dist`
- `llm_secrets.json`
- `llm_chat_history.json`
- `.env`、`*.env`
- `__pycache__`
- `*.pyc`
- 旧工具目录 `peakdesk-sprite`

审计脚本只报告命中的相对路径，不读取或输出敏感文件内容。

## 预期产物

- `release-work\dist\CodexPetLive\CodexPetLive.exe`
- `release-work\CodexPetLive-$Version-windows-x64.zip`

`data` 属于用户运行态配置目录，不应进入发布包。LLM 服务商地址、模型名、API Key 和聊天记录也不应进入发布包。

## 发布前检查

```powershell
git status --short --branch
git check-ignore -v data logs dist build release-work **/llm_secrets.json **/llm_chat_history.json
git ls-files data logs dist build release-work
& $PythonPath -m pip check
& $PythonPath -m compileall CodexPetLive tools scripts
$env:QT_QPA_PLATFORM = 'offscreen'
& $PythonPath .\scripts\smoke_resource_paths.py
& $PythonPath .\scripts\smoke_ui_llm_bugs.py
Remove-Item Env:\QT_QPA_PLATFORM -ErrorAction SilentlyContinue
.\scripts\build_release.ps1 -PythonPath $PythonPath
```

## 版本、Tag、Zip 和 SHA256

发布前确认应用内版本、README 发布说明和 Git tag 指向同一个版本。当前仓库没有独立 `VERSION` 文件，应用版本源是 `CodexPetLive\settings.py` 里的 `VERSION`。

```powershell
$Version = & $PythonPath -c "import pathlib,re; text=pathlib.Path('CodexPetLive/settings.py').read_text(encoding='utf-8'); print(re.search(r'^VERSION\\s*=\\s*[\"'']([^\"'']+)[\"'']', text, re.M).group(1))"
git grep -n $Version -- README.md README_EN.md CodexPetLive/settings.py
git tag --list $Version
git rev-parse --verify "refs/tags/$Version"
git rev-parse HEAD
git rev-parse "$Version^{commit}"
```

`git rev-parse HEAD` 与 `git rev-parse "$Version^{commit}"` 必须一致；如果 tag 还未创建，应在最终提交确定后再创建并推送：

```powershell
git tag -a $Version -m "CodexPetLive $Version"
git push origin $Version
```

构建完成后复核 zip 存在、内容可审计，并生成 SHA256 摘要：

```powershell
$ZipPath = ".\release-work\CodexPetLive-$Version-windows-x64.zip"
Test-Path $ZipPath
.\scripts\audit_release_package.ps1 -PackagePath $ZipPath
Get-FileHash -Algorithm SHA256 $ZipPath
```

把 SHA256 值写入 GitHub Release 说明，避免用户下载后只能“相信文件名”。校验和的作用类似包裹封签：它不证明程序没有 bug，但能证明用户拿到的 zip 与发布者上传的 zip 是同一个字节序列。

## Release 冒烟检查

先用 release 环境跑脚本级 smoke，再启动打包后的 exe。脚本级 smoke 负责检查资源路径、配置目录隔离、通知队列和 LLM 错误脱敏等低成本回归点：

```powershell
$env:QT_QPA_PLATFORM = 'offscreen'
& $PythonPath .\scripts\smoke_resource_paths.py
& $PythonPath .\scripts\smoke_ui_llm_bugs.py
Remove-Item Env:\QT_QPA_PLATFORM -ErrorAction SilentlyContinue
```

然后用临时配置目录启动发布产物，避免读写本机真实用户配置：

```powershell
$env:CODEXPETLIVE_CONFIG_DIR = (Resolve-Path .\release-work).Path + '\smoke-config'
$Process = Start-Process -FilePath '.\release-work\dist\CodexPetLive\CodexPetLive.exe' -PassThru
Start-Sleep -Seconds 10
if ($Process.HasExited) { throw "CodexPetLive exited during release smoke with code $($Process.ExitCode)" }
Stop-Process -Id $Process.Id
Remove-Item Env:\CODEXPETLIVE_CONFIG_DIR -ErrorAction SilentlyContinue
```

人工确认程序能保持运行、设置面板可打开，并且发布目录没有携带 `data`、`logs`、LLM secrets 或聊天记录。
