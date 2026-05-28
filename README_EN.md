<h1 align="center">
  PeakDeskSprite
</h1>

<p align="center">
  PeakDeskSprite is a PySide6-based Desktop Cyber Pet Framework, providing an App for all desktop pet creators
</p>

<p align="center">
  <a>
    <img src="https://img.shields.io/github/license/VectorPeak/PeakDeskSprite.svg">
  </a>

  <a style="text-decoration:none">
    <img src="https://img.shields.io/badge/python-3.9+-blue.svg" />
  </a>

  <a style="text-decoration:none">
    <img src="https://img.shields.io/badge/PeakDeskSprite-v0.8.5-green.svg"/>
  </a>
</p>

<p align="center">
English | <a href="README.md">简体中文</a>
</p>

:octocat: The project is at the very early stage, and mostly maintained in Chinese. Please leave an issue here if you have any suggestion, question, or trouble using it.  
  
:new: **05-19-2026: v0.8.5** is the current public version tag. GitHub Release assets may be unavailable while the Windows packaging flow is being refreshed. Any feedback is welcome! The LLM module is not fully open-sourced yet
  
:new: **04-06-2024: v0.3.7** has been adapted to PySide6-Fluent-Widgets v1.5.4, Please update PySide6-Fluent-Widgets with pip to run PeakDeskSprite.
  
🆕 **Language changer** is released now, supporting English and Simplified Chinese.    
  
⭐ Please **STAR** if you like it and want to get the update!


## Preview

![Main interface](docs/PeakDeskSprite.png)

| LLM Provider And Bubbles | Chat Panel |
| --- | --- |
| ![LLM provider settings](docs/preview_img/llm-provider.png) | ![LLM chat panel](docs/preview_img/llm-chat.png) |
| Configure an OpenAI-compatible provider, model, API key, and environment-variable fallback | Chat with the selected character, keep local history, and adjust role prompts |

| Bubble Behavior | Role Manager |
| --- | --- |
| ![Bubble behavior settings](docs/preview_img/llm-bubble-settings.png) | ![Role manager](docs/preview_img/role-manager.png) |
| Tune bubble mode, active chat, cooldowns, pat-triggered bubbles, and status-triggered bubbles | Add, switch, and launch desktop pet roles from the control panel |

| Basic Settings |
| --- |
| ![Basic settings](docs/preview_img/basic-settings.png) |
| Adjust pet size, default pet, language, theme color, update links, issue links, and developer docs |


## Quick Start

### Windows Users
If [Releases](https://github.com/VectorPeak/PeakDeskSprite/releases) provides a Windows package, download `PeakDeskSprite-vX.Y.Z-windows-x64.zip`, unzip it, and double-click **``PeakDeskSprite.exe``**. If no release asset is available, run from source. Maintainers can build the Windows package with the [Windows release checklist](docs/release_checklist.md)

### Run From Source

Use Python 3.12 by default. If PySide6 / Qt DLL compatibility is unstable on your machine, Python 3.9 can still be used for source verification

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m PeakDeskSprite
```

The repository now keeps a single [requirements.txt](requirements.txt) for both source runtime and Windows release builds; it is intentionally bounded and is not a `pip freeze`


## Project Structure And Public Docs

- `PeakDeskSprite/__main__.py`: source entry point; the executable in the Release package is named `PeakDeskSprite.exe`
- `PeakDeskSprite/`: PySide6 desktop pet runtime, settings panels, dashboard, notifications, LLM UI, and LLM services
- `res/`: default roles, items, language files, and UI resources
- `docs/`: development, release, and source-structure documentation
- `scripts/`: release build, package audit, and smoke test scripts

Maintenance docs: [asset development](docs/art_dev.md), [HatchPet converter](docs/hatchpet_converter.md), [source architecture](docs/source_architecture.md), [source dependency map](docs/source_dependency_map.md), and [Windows release checklist](docs/release_checklist.md)




## Developer Manual
For feature development, start with the [source architecture](docs/source_architecture.md), [source dependency map](docs/source_dependency_map.md), and [Windows release checklist](docs/release_checklist.md)


## LLM Privacy Note

LLM features are optional. When enabled, PeakDeskSprite sends user input, necessary chat context, role prompts, and event text to the LLM provider configured by the user. API keys are read from an environment variable first and can also be stored in the local runtime configuration directory; chat history is stored in the local runtime data directory. Do not paste API keys, chat history, provider responses, or unredacted local paths into public issues, logs, or screenshots


## Third-Party And Asset Licensing

Project source code follows [LICENSE](LICENSE). Default assets, demo assets, third-party role/item modules, external fonts/icons/audio, and user-imported assets may have separate licensing boundaries. Check the source and license terms before redistribution or derivative asset work



## Acknowledgement
- UI refactoring is based on [Fluent-Widgets](https://github.com/zhiyiYo/PyQt-Fluent-Widgets), with thanks to [zhiyiYo](https://github.com/zhiyiYo)
- Pictures in the Demo partially come from [daywa1kr](https://github.com/daywa1kr/Desktop-Cat)
- Animation module reference: [yanji255](https://toscode.gitee.com/yanji255/desktop_pet/)  
- Dragging and falling reference: [WolfChen1996](https://github.com/WolfChen1996/DesktopPet)
