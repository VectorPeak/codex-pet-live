# Codex Hatch-Pet To PeakDeskSprite Mapping

## Source Contract

A Codex hatch-pet package contains:

```text
pet.json
spritesheet.webp
```

Atlas contract:

- `1536x1872`
- 8 columns x 9 rows
- `192x208` cells
- transparent background

Rows:

| Row | Hatch state | Frames | PeakDeskSprite prefix |
| --- | --- | ---: | --- |
| 0 | `idle` | 6 | `stand` |
| 1 | `running-right` | 8 | `rightwalk` |
| 2 | `running-left` | 8 | `leftwalk` |
| 3 | `waving` | 4 | `wave` |
| 4 | `jumping` | 5 | `jump` |
| 5 | `failed` | 8 | `failed` |
| 6 | `waiting` | 6 | `waiting` |
| 7 | `running` | 6 | `focus` |
| 8 | `review` | 6 | `review` |

## Generated PeakDeskSprite Actions

| PeakDeskSprite action | Source prefix | Purpose |
| --- | --- | --- |
| `default` | `stand` | idle/default |
| `left_walk` | `leftwalk` | left movement |
| `right_walk` | `rightwalk` | right movement |
| `drag` | `stand` | drag fallback |
| `fall` | `jump` | fall/jump fallback |
| `onfloor` | `failed` | floor/failure fallback |
| `patpat` | `wave` | click interaction |
| `waiting` | `waiting` | waiting/blocked state |
| `focus` | `focus` | active work or focus state |
| `review` | `review` | focused inspection |
| `failed` | `failed` | failure state |

The mapping is intentionally conservative. It favors a stable import over perfect semantic richness because Codex hatch-pet rows and PeakDeskSprite native interactions are not the same product contract.

## Metadata

Use `pet.json.displayName` or `pet.json.id` for `info.petName`. Use `pet.json.description` for `info.intro`.

Create:

```text
info/info.json
info/pfp.png
conversion-report.json
```

Copy `stand_0.png` to `info/pfp.png` as the default avatar.

## QA

After conversion:

```powershell
python ".\PeakDeskSprite\peakdesk-sprite\scripts\validate_peakdesk_role.py" "res\role\RoleName"
python ".\PeakDeskSprite\peakdesk-sprite\scripts\hatchpet_to_peakdesk.py" validate "res\role\RoleName"
```

Then run `PeakDeskSprite.conf.CheckCharFiles`. Treat all three checks as necessary: the first is stronger on assets, the second is converter-local compatibility, and the third verifies the current app code path.
