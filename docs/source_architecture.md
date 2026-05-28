# CodexPetLive Source Architecture

This document records the current source dependency map and the proposed naming boundaries for future refactors. It is intentionally conservative: do not move runtime modules until the import graph, resource paths, Qt lifetime rules, and packaging path are covered by tests.

## Current Layers

```text
CodexPetLive/__main__.py
  -> CodexPetLive.CodexPetLive.PetWidget
  -> CodexPetLive.Notification.SpriteNote
  -> CodexPetLive.Accessory.SpriteAccessory
  -> CodexPetLive.SpriteSettings.SpriteControlPanel.ControlMainWindow
  -> CodexPetLive.Dashboard.DashboardUI.DashboardMainWindow

CodexPetLive.settings
  -> runtime paths, global user preferences, role list, runtime data objects
  -> conf.PetData / TaskData / ActData / ItemData

CodexPetLive.conf
  -> role config, action config, item config, save data, validation
  -> res/role, res/pet, res/items

UI layers
  -> SpriteSettings/* for system settings and role/item/save/LLM panels
  -> Dashboard/* for status, inventory, shop, tasks, and animation management

LLM feature
  -> llm_client.py for provider requests and secret storage
  -> llm_chat_store.py for chat history and role prompts
  -> bubbleManager.py and SpriteSettings/LLM*.py as UI/runtime integration points
```

## Dependency Hotspots

The high-coupling files are not necessarily wrong, but they are the first places to protect before changing names or paths.

| File | Current role | Coupling signal | Better long-term name |
| --- | --- | --- | --- |
| `CodexPetLive/CodexPetLive.py` | Pet window and runtime coordinator | Imports runtime objects, widgets, settings, config, bubbles, and resource helpers | `ui/pet_window.py` plus `runtime/pet_controller.py` |
| `CodexPetLive/settings.py` | Global settings plus runtime state bootstrap | Many modules read and mutate `settings.*` directly | `config/app_settings.py` plus `runtime/app_state.py` |
| `CodexPetLive/conf.py` | Role/action/item/save models and validators | Mixes config parsing, save data, role validation, and item data | `domain/role_config.py`, `domain/save_data.py`, `domain/item_config.py` |
| `CodexPetLive/modules.py` | Worker and animation helpers | Generic name hides scheduling and interaction responsibilities | `runtime/workers.py` or `animation/workers.py` |
| `CodexPetLive/Accessory.py` | Accessory and companion pet runtime | Large UI/runtime module with direct settings/config access | `runtime/accessories.py` |
| `CodexPetLive/Notification.py` | Notification and bubble display widgets | Name is broad; includes bubble display behavior | `ui/notifications.py` and `ui/bubbles.py` |
| `CodexPetLive/bubbleManager.py` | Bubble scheduling and LLM bubble integration | Mixes policy, Qt timers, and LLM requests | `services/bubble_policy.py` plus `ui/bubble_manager.py` |
| `CodexPetLive/extra_windows.py` | Multiple legacy/extra windows | Generic bucket, hard to infer ownership | split by feature before renaming |
| `CodexPetLive/SpriteSettings/custom_utils.py` | Settings UI helper widgets and role cards | Large mixed helper module | `ui/settings/widgets.py`, `ui/settings/role_cards.py` |
| `CodexPetLive/Dashboard/dashboard_widgets.py` | Dashboard shared widgets and logic | Large mixed UI plus business behavior | `ui/dashboard/widgets.py`, then split by feature |
| `tools/codex-skill-peakdesk-sprite/` | Codex skill and role production references | Non-runtime development tooling | keep under `tools/` |

## Recommended Target Names

These names describe responsibility rather than implementation detail.

```text
CodexPetLive/
  app_identity.py              # app name, repository URLs, env var names
  runtime_paths.py             # AppData and package/resource path helpers
  config/
    app_settings.py            # settings schema, defaults, migration
  domain/
    role_config.py             # pet_conf/act_conf parsing and validation
    save_data.py               # PetData, ActData, TaskData
    item_config.py             # item metadata and item data
  services/
    llm_client.py              # OpenAI-compatible provider calls
    llm_chat_store.py          # chat history and role prompt store
    bubble_policy.py           # cooldowns, probability, active chat policy
  runtime/
    pet_controller.py          # runtime state transitions and signal wiring
    workers.py                 # background workers and timers
    accessories.py             # accessory and companion runtime
  ui/
    pet_window.py
    notifications.py
    bubbles.py
    settings/
    dashboard/
```

The target structure should be reached through compatibility shims, not a single large move. For example, keep `CodexPetLive/settings.py` as a facade while new code imports `CodexPetLive.config.app_settings`.

## Safe Refactor Order

1. Move non-runtime tooling out of the package.
   - Done: `CodexPetLive/peakdesk-sprite` is now `tools/codex-skill-peakdesk-sprite`.
   - Reason: skill references are not application runtime code and should not be bundled with `--add-data CodexPetLive`.

2. Add explicit path boundaries.
   - Keep `runtime_paths.py` as the only place that knows AppData layout.
   - Add a future `resource_paths.py` before moving `res/`.

3. Split configuration from runtime state.
   - `settings.py` should keep compatibility globals.
   - New code should move toward a repository/service API instead of direct global mutation.

4. Split role and save data from `conf.py`.
   - Start with tests around `CheckCharFiles`, `PetData`, `ActData`, and `TaskData`.
   - Keep import shims until all UI modules are migrated.

5. Split UI by domain.
   - Dashboard and settings panels can move only after their dependency on global `settings` is reduced.
   - Do not rename `CodexPetLive.py`, `Accessory.py`, or `Notification.py` until launch, tray, bubble, and packaging smoke tests are stable.

## Minimum Regression For Any Move

```powershell
D:\ZXY\Dev\Miniconda3\envs\Dyber_pyside\python.exe -m compileall CodexPetLive

@'
from CodexPetLive.conf import CheckCharFiles
for role in ["BestFriendsCodex", "frierencodex", "jige-kunkun", "lajiaoquan", "hu-tao-1-pet", "shogun-dango", "genshin-ayaka"]:
    code, errors = CheckCharFiles(rf"D:\ZXY\Codex\DyberPet\res\role\{role}")
    print(role, code, errors)
'@ | D:\ZXY\Dev\Miniconda3\envs\Dyber_pyside\python.exe -
```

For any move that touches Qt UI or resource paths, also run the packaged app and verify the packaged app does not create a data directory inside `dist/CodexPetLive`.
