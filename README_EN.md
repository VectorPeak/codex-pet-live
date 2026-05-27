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
English | <a href="README.md">简体中文</a>
</p>

:octocat: The project is at the very early stage, and mostly maintained in Chinese. Please leave an issue here if you have any suggestion, question, or trouble using it.  
  
:new: **05-19-2026: v0.8.5** Release entry is available from [Releases](https://github.com/VectorPeak/PeakDeskSprite/releases). Any feedback is welcome! The LLM module is not fully open-sourced yet
  
:new: **04-06-2024: v0.3.7** has been adapted to PySide6-Fluent-Widgets v1.5.4, Please update PySide6-Fluent-Widgets with pip to run PeakDeskSprite.
  
🆕 **Language changer** is released now, supporting English and Simplified Chinese.    
  
⭐ Please **STAR** if you like it and want to get the update!


## Quick Start

### Windows Users
  Download the [Release](https://github.com/VectorPeak/PeakDeskSprite/releases), unzip it, and double-click **``PeakDeskSprite.exe``**. Windows release artifacts are named **``PeakDeskSprite-vX.Y.Z-windows-x64.zip``**


## Project Structure And Public Docs

- `PeakDeskSprite/__main__.py`: source entry point; the executable in the Release package is named `PeakDeskSprite.exe`
- `PeakDeskSprite/`: PySide6 desktop pet runtime, settings panels, dashboard, notifications, LLM UI, and LLM services
- `res/`: default roles, items, language files, and UI resources
- `docs/`: development, release, and source-structure documentation
- `scripts/`: release build, package audit, and smoke test scripts

Maintenance docs: [asset development](docs/art_dev.md), [HatchPet converter](docs/hatchpet_converter.md), [source architecture](docs/source_architecture.md), [source dependency map](docs/source_dependency_map.md), [Windows release checklist](docs/release_checklist.md), [contributing](CONTRIBUTING.md), and [security reporting](SECURITY.md)




## Developer Manual
For feature development, start with the [source architecture](docs/source_architecture.md), [source dependency map](docs/source_dependency_map.md), and [contributing guide](CONTRIBUTING.md)


## LLM Privacy Note

LLM features are optional. When enabled, PeakDeskSprite sends user input, necessary chat context, role prompts, and event text to the LLM provider configured by the user. API keys are read from an environment variable first and can also be stored in the local runtime configuration directory; chat history is stored in the local runtime data directory. Do not paste API keys, chat history, provider responses, or unredacted local paths into public issues, logs, or screenshots


## Third-Party And Asset Licensing

Project source code follows [LICENSE](LICENSE). Default assets, demo assets, third-party role/item modules, external fonts/icons/audio, and user-imported assets may have separate licensing boundaries. Read [NOTICE.md](NOTICE.md) before redistribution or derivative asset work



## Acknowledgement
- UI refactoring is based on [Fluent-Widgets](https://github.com/zhiyiYo/PyQt-Fluent-Widgets), with thanks to [zhiyiYo](https://github.com/zhiyiYo)
- Pictures in the Demo partially come from [daywa1kr](https://github.com/daywa1kr/Desktop-Cat)
- Animation module reference: [yanji255](https://toscode.gitee.com/yanji255/desktop_pet/)  
- Dragging and falling reference: [WolfChen1996](https://github.com/WolfChen1996/DesktopPet)
