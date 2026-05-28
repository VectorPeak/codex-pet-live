<h1 align="center">
  CodexPetLive
</h1>

<p align="center">
  A Windows desktop runtime that brings Codex-generated pets to life
</p>

<p align="center">
  <a>
    <img src="https://img.shields.io/github/license/VectorPeak/CodexPetLive.svg">
  </a>
  <a style="text-decoration:none">
    <img src="https://img.shields.io/badge/python-3.9+-blue.svg">
  </a>
  <a style="text-decoration:none">
    <img src="https://img.shields.io/badge/CodexPetLive-v0.8.6-green.svg">
  </a>
</p>

<p align="center">
  English | <a href="README.md">简体中文</a>
</p>

## Project Introduction

Codex-generated Pets should not stay as asset packages

CodexPetLive is a Windows desktop runtime for Codex Pets. It can convert Codex-generated hatch-pet character packages into real desktop pets: they can idle on the desktop, move, switch actions, respond to interactions, and connect to bubbles, status, inventory, role management, settings panels, and optional LLM chat

You can think of Codex as a character incubator and CodexPetLive as the desktop stage. Codex creates the character; CodexPetLive lets that character walk out of a folder and become a companion, an interactive object, and an extensible desktop role

The project is built on top of the CodexPetLive / PySide6 desktop pet framework. It is suitable for showcasing AI-generated characters, building desktop companion apps, validating character assets, developing desktop pet interactions, or extending a simple Pet package into a complete desktop experience

If you like this desktop pet program, please click the ⭐ Star button in the upper-right corner. It means a lot to us

## Why CodexPetLive

Because there is still a desktop runtime gap between “generating a character” and “actually having a character”

Codex Pet can hatch a character, but an asset package does not move by itself, handle clicks or dragging, show bubbles, maintain status, manage inventory, expose settings, or chat. CodexPetLive fills this last mile: it brings AI-generated Pets from folders, preview images, and asset sheets onto the real desktop

It is more like a stage than another asset repository. Characters can be switched, interacted with, and extended; developers can also use the same PySide6 desktop pet framework to connect Codex Pets to a richer desktop experience

If Codex lets a character be born, CodexPetLive lets that character start working beside you

## Preview

The pet can stay near the bottom of the desktop and work together with the settings panel, role manager, LLM bubbles, and chat interface. The screenshots below show the current desktop runtime and control-panel experience

![Main interface](docs/PeakDeskSprite.png)

<table>
  <tr>
    <th width="50%">LLM Provider And Bubbles</th>
    <th width="50%">Chat Panel</th>
  </tr>
  <tr>
    <td><img src="docs/preview_img/llm-provider.png" alt="LLM provider settings" width="100%"></td>
    <td><img src="docs/preview_img/llm-chat.png" alt="LLM chat panel" width="100%"></td>
  </tr>
  <tr>
    <td>Configure an OpenAI-compatible provider, endpoint URL, model name, API Key, and environment-variable fallback</td>
    <td>The role chat interface supports contextual messages, role prompt entry, chat history saving, and AI-content notices</td>
  </tr>
  <tr>
    <th>Bubble Behavior</th>
    <th>Role Manager</th>
  </tr>
  <tr>
    <td><img src="docs/preview_img/llm-bubble-settings.png" alt="Bubble behavior settings" width="100%"></td>
    <td><img src="docs/preview_img/role-manager.png" alt="Role manager" width="100%"></td>
  </tr>
  <tr>
    <td>Tune bubble mode, active chat, cooldown time, pat-triggered bubble probability, and status-triggered bubble probability</td>
    <td>Add, switch, and launch different roles. Role assets can be extended through the resource directory or import flow</td>
  </tr>
</table>

| Basic Settings |
| --- |
| ![Basic settings](docs/preview_img/basic-settings.png) |
| Adjust pet size, default pet, interface language, theme color, and access update, issue, and developer-documentation entries |

## How to use CodexPetLive

If you only want to run the desktop pet first, download the Windows package, unzip it, and double-click `CodexPetLive.exe`. The pet will appear on your desktop. You can switch roles, adjust size, change bubble behavior, configure LLM services, or use it as a daily desktop companion app from the settings panel

If you want to try Codex Pets, first download a pet package you like from [Codex Pets](https://codex-pets.net/). A standard hatch-pet package usually contains `pet.json` and `spritesheet.webp`; they describe pet metadata and the animation spritesheet

After getting a pet package, use the CodexPetLive conversion tool to turn it into a desktop role module:

```powershell
python tools\hatchpet_to_peakdesk.py convert `
  --input C:\Path\To\codex-pet-package `
  --out-dir res\role\YourPetName `
  --role-name YourPetName `
  --overwrite
```

After conversion, restart CodexPetLive and select the new role in Role Manager. For the full conversion flow, spritesheet requirements, and action mapping, see [HatchPet Converter Guide](docs/hatchpet_converter.md)

## Quick Start

### Windows Users

The latest version is [CodexPetLive v0.8.6](https://github.com/VectorPeak/CodexPetLive/releases/tag/v0.8.6), and the Windows package is `CodexPetLive-v0.8.6-windows-x64.zip`

Download the zip, unzip it, and double-click `CodexPetLive.exe`. `v0.8.5` is a historical version published before the rename, so the old package name and old exe name still appear in historical Release assets

Maintainers who need to build the Windows zip package can refer to the [Windows Release Checklist](docs/release_checklist.md)

### Run From Source

Use Python 3.12 by default. If PySide6 / Qt DLL compatibility is unstable on your machine, Python 3.9 can still be used for source verification. The project now keeps only one [requirements.txt](requirements.txt), serving both source runtime and Windows release builds:

```txt
apscheduler
pynput
PyInstaller>=6.19,<7.0
PySide6>=6.10,<6.12
PySide6-Fluent-Widgets>=1.10,<2.0
tendo
Pillow>=11.0,<13.0
```

Install and run with conda:

```powershell
conda create --name CodexPetLive_pyside python=3.12 -y
conda activate CodexPetLive_pyside
python -m pip install -r requirements.txt
python -m CodexPetLive
```

If you already have a compatible Python 3.12 installation, you can also use a virtual environment:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m CodexPetLive
```

`Pillow>=11.0,<13.0` means Pillow 11.x or 12.x. It is not pinned to a single exact version; pip will choose a compatible version in that range

## Project Architecture

CodexPetLive can be understood in three layers: the outer layer is the transparent Qt window and control panels visible to users; the middle layer is runtime features such as actions, notifications, inventory, tasks, and LLM; the inner layer is role assets, configuration files, and local runtime data

A desktop pet can be understood as a “state machine on a transparent window”: users see a character moving, jumping, and interacting on the desktop, while the program is continuously processing states, events, timers, and resource configuration. In engineering terms, it is roughly `desktop pet = Qt window + animation frames + behavior state machine + user data + event responses`

<table>
  <thead>
    <tr>
      <th width="180" nowrap>Category</th>
      <th width="260">Module</th>
      <th>Description</th>
    </tr>
  </thead>
  <tbody>
    <tr><td width="180" nowrap>Startup And Lifecycle</td><td><code>CodexPetLive/__main__.py</code></td><td>Creates <code>QApplication</code>, loads pet, notification, accessory, system panel, and dashboard objects, and wires them through Qt Signals</td></tr>
    <tr><td width="180" nowrap>Startup And Lifecycle</td><td>Single-instance control</td><td>Uses <code>tendo.singleton.SingleInstance()</code> to prevent duplicate launches; a later process exits silently if an instance already exists</td></tr>
    <tr><td width="180" nowrap>Startup And Lifecycle</td><td>Multi-screen and midnight timer</td><td>Reads screen list at startup, prefers the primary screen, and sets cross-day timers for daily state or event refreshes</td></tr>
    <tr><td width="180" nowrap>Desktop Pet Runtime</td><td><code>CodexPetLive/CodexPetLive.py</code></td><td>Main pet window and runtime coordinator, responsible for character display, action switching, state changes, mouse interaction, and signal dispatch</td></tr>
    <tr><td width="180" nowrap>Desktop Pet Runtime</td><td>Animation action system</td><td>Role actions are configured through <code>act_conf.json</code> and <code>pet_conf.json</code>; PNG frame sequences provide the actual visual output</td></tr>
    <tr><td width="180" nowrap>Desktop Pet Runtime</td><td>Interaction behavior</td><td>Supports common desktop pet behavior such as clicking, dragging, following, falling, patting, and focus actions</td></tr>
    <tr><td width="180" nowrap>Role And Asset System</td><td><code>res/role</code></td><td>Main role directory. Each role usually contains <code>pet_conf.json</code>, <code>act_conf.json</code>, <code>action/*.png</code>, <code>info</code>, and related assets</td></tr>
    <tr><td width="180" nowrap>Role And Asset System</td><td><code>res/pet</code></td><td>Legacy mini-pet structure, kept for compatibility and reflecting the project's evolution from pet assets to role modules</td></tr>
    <tr><td width="180" nowrap>Role And Asset System</td><td><code>CodexPetLive/conf.py</code></td><td>Reads role, action, item, and save configuration; this is the core domain-configuration layer</td></tr>
    <tr><td width="180" nowrap>Notifications And Bubbles</td><td><code>CodexPetLive/Notification.py</code></td><td>Manages pop-up notifications, bubbles, and log forwarding</td></tr>
    <tr><td width="180" nowrap>Notifications And Bubbles</td><td><code>CodexPetLive/bubbleManager.py</code></td><td>Manages dialogue bubbles triggered by events such as hunger, favorability, clicks, and focus</td></tr>
    <tr><td width="180" nowrap>Notifications And Bubbles</td><td>LLM bubble integration</td><td>The bubble system can request short text from an LLM for specific events and display it back as a pet bubble</td></tr>
    <tr><td width="180" nowrap>Accessories And Sub-pets</td><td><code>CodexPetLive/Accessory.py</code></td><td>Manages accessory, drop, sub-pet, mouse-decoration, and related window objects</td></tr>
    <tr><td width="180" nowrap>Accessories And Sub-pets</td><td>Sub-pet following</td><td>Sub-pets can follow the main pet, stop following, be recycled, or appear independently as an extension of “main role + attached objects”</td></tr>
    <tr><td width="180" nowrap>Dashboard</td><td><code>CodexPetLive/Dashboard/DashboardUI.py</code></td><td>Provides tabs for status, inventory, shop, daily tasks, and animation management</td></tr>
    <tr><td width="180" nowrap>Dashboard</td><td>Status And Buff</td><td>The status page displays HP, FV, coins, Buffs, and related pet values; inventory items can affect these states</td></tr>
    <tr><td width="180" nowrap>Dashboard</td><td>Inventory And Shop</td><td>The inventory manages items; the shop handles buying and selling. Signals keep coins and item counts synchronized</td></tr>
    <tr><td width="180" nowrap>Dashboard</td><td>Tasks And Focus</td><td>The task page includes Pomodoro, focus time, progress tasks, and daily tasks, and can grant coin rewards</td></tr>
    <tr><td width="180" nowrap>System Settings Panel</td><td><code>CodexPetLive/SpriteSettings/SpriteControlPanel.py</code></td><td>Main system settings window, including settings, chat, LLM provider, saves, roles, item MODs, and mini-pet tabs</td></tr>
    <tr><td width="180" nowrap>System Settings Panel</td><td><code>CharCardUI.py</code></td><td>Handles role import, switching, and card display</td></tr>
    <tr><td width="180" nowrap>System Settings Panel</td><td><code>ItemCardUI.py</code></td><td>Handles item MOD management</td></tr>
    <tr><td width="180" nowrap>System Settings Panel</td><td><code>GameSaveUI.py</code></td><td>Supports save, load, rollback, and deletion operations</td></tr>
    <tr><td width="180" nowrap>LLM Features</td><td><code>CodexPetLive/llm_client.py</code></td><td>Includes OpenAI, DeepSeek, Ollama, and Custom OpenAI-compatible provider presets</td></tr>
    <tr><td width="180" nowrap>LLM Features</td><td><code>LLMChatUI.py</code></td><td>Provides the pet chat interface and supports chat-history saving</td></tr>
    <tr><td width="180" nowrap>LLM Features</td><td>Safety boundary</td><td>API Keys are read from environment variables first, and can also be saved to <code>llm_secrets.json</code> in the runtime data directory</td></tr>
    <tr><td width="180" nowrap>Packaging And Tools</td><td><code>tools/</code></td><td>Contains HatchPet conversion helpers for turning other pet assets into the CodexPetLive structure</td></tr>
    <tr><td width="180" nowrap>Packaging And Tools</td><td><code>docs/</code></td><td>Contains source architecture, dependency map, asset development, and release checklist documents</td></tr>
  </tbody>
</table>

For more detail on source structure and dependencies, read [Source Architecture](docs/source_architecture.md) and [Dependency Map](docs/source_dependency_map.md)

## Configuration

Project configuration falls into three broad groups: repository default resource configuration, local runtime configuration, and optional LLM service configuration

| Type | Location | Description |
| --- | --- | --- |
| Default roles and assets | `res/role`, `res/pet`, `res/icons` | Distributed with the project, including role actions, avatars, bubbles, icons, items, and default resources |
| Role action configuration | `pet_conf.json`, `act_conf.json` | Describes role base attributes, action sets, frame refresh, movement, anchors, and trigger conditions |
| Runtime config | `%APPDATA%\CodexPetLive` on Windows | Stores user settings and runtime data; can be overridden with `CODEXPETLIVE_CONFIG_DIR` |
| Runtime data | `%APPDATA%\CodexPetLive\data` | Stores user data such as `settings.json`, `pet_data.json`, `act_data.json`, and `task_data.json` |
| LLM API Key | Environment variable `CODEXPETLIVE_LLM_API_KEY` or `llm_secrets.json` | Environment variable takes priority; otherwise the local runtime secret file is read |
| LLM chat history | `llm_chat_history.json` | Stored in the local runtime data directory and should not be posted to public repositories or issues |

If you want to develop new pet characters, actions, props, or mini-pets, read [Asset Development](docs/art_dev.md) and [HatchPet Converter Guide](docs/hatchpet_converter.md) first

If you want to modify the runtime, settings panel, notifications, inventory, LLM, or release flow, read [Source Architecture](docs/source_architecture.md), [Dependency Map](docs/source_dependency_map.md), and the [Windows Release Checklist](docs/release_checklist.md) first

## FAQ

### Is this a web project

No. CodexPetLive is a PySide6 desktop GUI application. It shows desktop windows, system panels, and tray-related interactions after launch. It does not provide a localhost web page

### Why does the example recommend Python 3.12

The current `requirements.txt` has consolidated dependencies for both source runtime and Windows release builds, and constrains PySide6 to the 6.10 series. The release checklist also uses an isolated Python 3.12 virtual environment by default. Qt desktop apps are sensitive to Python, PySide6, and native DLL compatibility; if Python 3.12 hits QtCore or similar dynamic-library loading issues on a specific machine, Python 3.9 can still be used for source verification

### What does `Pillow>=11.0,<13.0` mean

It means Pillow 11.0.0 or later, but lower than 13.0. It is a version range, not an exact pin, and it does not require manually installing one fixed version. Pillow is mainly used for image reading, processing, and asset-related flows

### Why does launching a second time do nothing

The project uses `tendo.singleton.SingleInstance()` for single-instance protection. If a CodexPetLive process is already running, a later launch exits to avoid multiple desktop pets competing for the same configuration and resources

### What does LLM send to the provider

LLM is optional. When enabled, the pet sends user input, required chat context, role prompts, and event text to the LLM provider configured by the user. API Keys are read from environment variables first and can also be saved in the local runtime configuration directory. Chat history is stored in the local runtime data directory

Do not paste API Keys, chat history, provider responses, or unredacted local paths into public issues, logs, screenshots, or PRs

### What should I know about asset licensing

Project code follows the repository [LICENSE](LICENSE). Default assets, sample assets, third-party role/item modules, external fonts/icons/audio, and user-imported assets may have independent licensing boundaries. Confirm the asset source and license terms before redistribution or derivative work

## Developer Docs And Contribution Boundaries

The public repository welcomes these types of contributions:

- Feedback on pet startup, resource loading, role import, inventory, notifications, or settings panels
- Additional roles, item MODs, mini-pets, document examples, or screenshot explanations
- Fixes for path compatibility, release package auditing, resource location, UI behavior, and smoke tests
- Discussion of LLM chat, role bubbles, context management, and local privacy boundaries

Before submitting code, keep each PR focused and solve one clear problem at a time. If API Keys, chat history, provider responses, local absolute paths, or other private information are involved, redact them first. Security or privacy issues should preferably be reported privately to maintainers

CodexPetLive is not a small program bound to one fixed character. It is a desktop pet foundation that can keep changing clothes, actions, props, and personality. Users can treat it as a desktop companion app, asset creators can use it as a character asset lab, and developers can use it as a starting point for interaction demos or lightweight desktop tools

## Acknowledgements

- Based on [ChaozhongLiu/DyberPet](https://github.com/ChaozhongLiu/DyberPet)
- UI refactoring is based on [Fluent-Widgets](https://github.com/zhiyiYo/PyQt-Fluent-Widgets), with thanks to [zhiyiYo](https://github.com/zhiyiYo)
- Some demo assets come from [daywa1kr](https://github.com/daywa1kr/Desktop-Cat)
- Early animation module logic references [yanji255](https://toscode.gitee.com/yanji255/desktop_pet/)
- Dragging and falling calculation logic references [WolfChen1996](https://github.com/WolfChen1996/DesktopPet)
