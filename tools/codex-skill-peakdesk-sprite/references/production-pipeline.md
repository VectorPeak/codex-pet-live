# Production Pipeline

## What To Reuse From hatch-pet

Reuse the discipline, not the final package format.

hatch-pet separates generation from deterministic processing:

```text
visual generation -> decoded rows -> deterministic frames -> QA -> package
```

CodexPetLive should use the same separation:

```text
concept/reference -> action frame sets -> pet_conf/act_conf -> validation -> app import/run
```

## Recommended Run Artifacts

For non-trivial generated roles, create a work folder under `build/peakdesk-sprite/<role-id>/`:

```text
role_request.json
jobs.json
prompts/
source/
frames/
qa/
role/
```

`role_request.json` should record role name, display name, description, style notes, target canvas size, action list, and source references.

`jobs.json` should record each action job, dependencies, selected source path, output prefix, expected frame count, and status.

## Action Set

Start with a robust role set:

- `default`: calm idle.
- `drag`: safe held/drag pose; may reuse idle if no dedicated art exists.
- `fall`: falling or jump/fall fallback.
- `left_walk`: left movement.
- `right_walk`: right movement.
- `patpat`: clicked interaction.
- `focus`: focus/timer state.
- `onfloor`: landing/failure floor fallback.

Add richer random actions only after the minimal set passes runtime tests.

## Deterministic QA

Script checks should verify:

- JSON files parse as UTF-8 objects.
- Required keys exist.
- All referenced action names exist.
- Every `images` prefix has continuous frames.
- PNG files are readable and transparent-capable.
- Frame sizes are consistent.
- `info.author` is an object.

Framework checks should verify:

```powershell
from CodexPetLive.conf import CheckCharFiles
```

PySide6 smoke tests should load each frame into `QPixmap`.

## Visual QA

Generate a contact sheet and optional GIF previews for generated assets. Reject:

- different character identity across actions;
- opaque or white rectangular backgrounds;
- cropped frames;
- baseline or size jumps;
- wrong movement direction;
- jitter from inconsistent anchors;
- tiny unreadable details;
- effects that are detached from the character and should have been part of the sprite.

## Runtime QA

When the user asks for proof, set `data/settings.json` default role to the generated role, launch `python -X faulthandler -u -m CodexPetLive`, redirect stdout/stderr into `logs/`, then inspect:

- process state;
- stdout and stderr;
- Windows Event Log or platform crash logs;
- single-instance exit messages.

Do not treat a successful config check as a successful runtime test.
