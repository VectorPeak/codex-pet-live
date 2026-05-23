---
name: peakdesk-sprite
description: Create, convert, validate, import, smoke-test, and package PeakDeskSprite desktop pet role modules. Use when Codex needs to build PeakDeskSprite or DyberPet character resources, transform Codex hatch-pet packages into PeakDeskSprite role folders, inspect or repair role module structure, generate role metadata, verify assets with Pillow/PySide6, or run the desktop app with a generated character.
---

# PeakDeskSprite

## Overview

Build PeakDeskSprite desktop pet role modules end to end. The target artifact is a role folder under `res/role/<RoleName>/`, not a Codex custom pet package. Keep Chinese JSON and Markdown files UTF-8.

If the user asks to generate a new Codex pet first, use `$hatch-pet` for visual generation and Codex atlas packaging, then return to this skill to convert and verify the PeakDeskSprite module.

## Mental Model

PeakDeskSprite role creation is a three-layer contract:

```text
pet_conf.json  -> schedule: default, drag, fall, random action groups
act_conf.json  -> action definitions: image prefixes, timing, movement, anchors
action/*.png   -> animation frames: prefix_0.png, prefix_1.png, ...
```

The native app check proves the files are connected. It does not prove transparent pixels, baseline stability, action semantics, or visual identity. Always add stronger deterministic and visual QA when generating assets.

## Workflow

1. Find the repo root. It must contain `run_PeakDeskSprite.py`, `PeakDeskSprite/`, and `res/role/`.
2. Inspect the active Python environment. Install `Pillow` only if image conversion or validation needs it and it is missing.
3. Choose a path:
   - Native role creation or repair: read `references/role-contract.md`.
   - Codex hatch-pet conversion: read `references/hatchpet-mapping.md`.
   - Generation pipeline design: read `references/production-pipeline.md`.
4. Generate or convert into `res/role/<RoleName>/`.
5. Run deterministic validation:
   - this skill's validator script;
   - `PeakDeskSprite.conf.CheckCharFiles`;
   - PySide6 pixmap smoke test.
6. When the user asks whether it really works, launch the app with logs and inspect process state plus logs. A second launch may exit with `Another instance is already running, quitting.`; do not confuse that with a crash.
7. Report exact absolute paths for role output, logs, contact sheets, previews, and any modified config.

## Codex Hatch-Pet Conversion

Input:

```text
pet.json
spritesheet.webp
```

Command from the repo root:

```powershell
$Skill = ".\PeakDeskSprite\peakdesk-sprite"
python "$Skill\scripts\hatchpet_to_peakdesk.py" convert `
  --input "D:\path\to\codex-pet-package" `
  --out-dir "res\role\BestFriendsCodex" `
  --role-name "BestFriendsCodex" `
  --overwrite
```

Validate:

```powershell
python "$Skill\scripts\validate_peakdesk_role.py" "res\role\BestFriendsCodex"
python "$Skill\scripts\hatchpet_to_peakdesk.py" validate "res\role\BestFriendsCodex"
```

Then run framework validation:

```powershell
@'
from PeakDeskSprite.conf import CheckCharFiles
code, errors = CheckCharFiles(r"D:\absolute\path\to\res\role\BestFriendsCodex")
print(code, errors)
'@ | python -
```

## Runtime Smoke Test

PySide6 frame-load smoke test:

```powershell
@'
from pathlib import Path
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QPixmap
import sys

app = QApplication.instance() or QApplication(sys.argv)
root = Path(r"D:\absolute\path\to\res\role\RoleName\action")
files = sorted(root.glob("*.png"))
bad = [str(p) for p in files if QPixmap(str(p)).isNull()]
print("frames", len(files), "bad", bad[:5])
'@ | python -
```

Launch app with logs:

```powershell
$Stamp = Get-Date -Format "yyyyMMdd-HHmmss"
New-Item -ItemType Directory -Force -Path ".\logs" | Out-Null
$Out = ".\logs\run_$Stamp.out.log"
$Err = ".\logs\run_$Stamp.err.log"
Start-Process -FilePath "python" `
  -ArgumentList "-X","faulthandler","-u","run_PeakDeskSprite.py" `
  -WorkingDirectory (Get-Location) `
  -RedirectStandardOutput $Out `
  -RedirectStandardError $Err `
  -PassThru
```

If the app exits, inspect `logs/*.err.log` and the platform crash log before changing assets.

## Acceptance Criteria

- `pet_conf.json`, `act_conf.json`, and `info/info.json` parse as UTF-8 JSON objects.
- `default`, `drag`, and `fall` exist and resolve to actions.
- `random_act` is non-empty.
- Every action has a non-empty `images` prefix.
- Every prefix has continuous `prefix_0.png...prefix_N.png` frames.
- PNG frames are readable and have consistent role dimensions.
- `info.author` is an object, not a string.
- The role passes this skill's validator and `CheckCharFiles`.
- A PySide6 pixmap smoke test loads all frames.
- For generated art, contact sheet or GIF review confirms stable identity, transparent background, no baseline jumps, and action semantics that match the config.
