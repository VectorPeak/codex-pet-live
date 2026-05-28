# Source Dependency Map

This file records the current import-level dependency map. It is a working reference for future renaming and directory refactors.

## Layer Topology

```text
entry/bootstrap
  CodexPetLive/__main__.py
    -> CodexPetLive.CodexPetLive
    -> CodexPetLive.Notification
    -> CodexPetLive.Accessory
    -> CodexPetLive.SpriteSettings.SpriteControlPanel
    -> CodexPetLive.Dashboard.DashboardUI

core runtime
  CodexPetLive.CodexPetLive
    -> settings, conf, modules, bubbleManager, Accessory, runtime_paths, widgets
  Accessory
    -> settings, conf, utils, custom_widgets
  Notification
    -> settings, conf, utils
  modules
    -> settings, conf, utils
  bubbleManager
    -> settings, llm_client

domain/config
  settings
    -> conf.PetData / TaskData / ActData / ItemData
    -> runtime_paths, app_identity
  conf
    -> runtime_paths, utils
  runtime_paths
    -> app_identity

ui/settings
  SpriteSettings.SpriteControlPanel
    -> BasicSettingUI, CharCardUI, ItemCardUI, PetCardUI, GameSaveUI, LLMProviderUI, LLMChatUI
  SpriteSettings/*
    -> settings, conf, utils, llm_client

ui/dashboard
  Dashboard.DashboardUI
    -> statusUI, inventoryUI, shopUI, taskUI, animationUI
  Dashboard/*
    -> settings, dashboard_widgets, conf, utils

services/llm
  llm_client
    -> settings, runtime_paths, app_identity
  llm_chat_store
    -> settings, runtime_paths
  LLMProviderUI / LLMChatUI / bubbleManager
    -> llm_client

resources/tools
  res/*
    -> loaded by conf, SpriteSettings, Dashboard, Accessory, Notification
  tools/*
    -> development and conversion tooling, not app runtime
```

## Current Direction Risks

- `settings.py -> conf.py` is a configuration layer depending on domain data classes. Keep it as a compatibility facade for now, but new code should move toward a `settings_store` plus explicit runtime state object.
- `Dashboard/dashboard_widgets.py -> SpriteSettings/custom_utils.py` is a UI subpackage depending on another UI subpackage. Shared widgets should eventually move to a common UI package.
- `llm_client.py -> settings.py` makes the service layer depend on global state. A future client should accept explicit config and path arguments.
- Multiple modules directly compose `res/...` paths. A future `resource_paths.py` should become the only resource path API.
- `CodexPetLive.py`, `Accessory.py`, `Notification.py`, and `modules.py` mix Qt presentation, runtime state, and animation behavior. Rename only after tests are stable.

## High Fan-In Global Modules

These modules are widely imported or referenced and should remain compatibility shims during migration:

- `CodexPetLive.settings`
- `CodexPetLive.conf`
- `CodexPetLive.utils`
- `CodexPetLive.runtime_paths`

## Refactor Rule

Do not move a runtime module and change behavior in the same commit. Use this sequence:

1. Add the new target module.
2. Keep the old module as a re-export compatibility shim.
3. Move one consumer group at a time.
4. Run compile, role validation, source launch, and packaged launch tests.
5. Remove the compatibility shim only after all imports are migrated.
