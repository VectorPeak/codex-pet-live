# CodexPetLive Role Contract

## Directory Shape

Role modules live under `res/role/<RoleName>/`.

```text
pet_conf.json
act_conf.json
action/
info/
note/
items/
msg_conf.json
```

Only `pet_conf.json`, `act_conf.json`, and `action/` are required for a minimal role. `info/` is strongly recommended because the role manager and dashboard use it for names, avatars, tags, author data, and cover images.

Use English-safe folder and file names for role folders, PNG prefixes, and bundled resources. The upstream art guide warns that non-English filenames can become garbled after extraction in some locales and may crash the app.

## pet_conf.json

`pet_conf.json` schedules behavior. Important fields:

- `width`, `height`: maximum PNG frame width and height.
- `scale`: display scale; also affects movement distance.
- `refresh`: animation module refresh factor.
- `interact_speed`: interaction loop interval in seconds; `0.02` is the normal baseline.
- `default`: idle action name.
- `drag`: mouse drag action name.
- `fall`: free-fall action name.
- `prefall`: optional pre-fall action; falls back to `fall`.
- `left`, `right`: directional movement actions.
- `on_floor`: landing or floor action.
- `focus`: focus/timer action.
- `patpat`: click action; may be a string or HP-tier dict.
- `random_act`: non-empty list of action groups.
- `accessory_act`: optional component/effect actions.
- `item_favorite`, `item_dislike`, `coin_config`, `msg_dict`: optional extended systems.

Minimal robust action keys:

```json
{
  "default": "default",
  "drag": "drag",
  "fall": "fall",
  "random_act": [
    {"name": "Stand", "act_list": ["default"], "act_prob": 1.0, "act_type": [2, 0]}
  ]
}
```

`random_act` group shape:

```json
{
  "name": "Walk",
  "act_list": ["left_walk", "right_walk", "default"],
  "act_prob": 0.25,
  "act_type": [2, 0],
  "sound": []
}
```

`act_type` is `[hp_tier, fv_lock]`. HP tiers act like a probability center: a tier-2 action is most likely when the pet is in normal satiety. A lock above 100 is treated as a special hidden action by runtime act-data generation.

## act_conf.json

`act_conf.json` defines each action. Every action object must include `images`.

```json
{
  "left_walk": {
    "images": "leftwalk",
    "act_num": 2,
    "need_move": true,
    "direction": "left",
    "frame_move": 8,
    "frame_refresh": 0.12,
    "anchor": [0, 0]
  }
}
```

Fields:

- `images`: PNG prefix in `action/`.
- `act_num`: number of loops.
- `need_move`: whether the whole sprite window moves during playback.
- `direction`: `left`, `right`, `up`, or `down` when moving.
- `frame_move`: movement per frame interval.
- `frame_refresh`: seconds per frame.
- `anchor`: offset from the image bottom-center to the character bottom-center.

The anchor can be understood as:

```text
anchor = [character_bottom_center_x - image_bottom_center_x,
          character_bottom_center_y - image_bottom_center_y]
```

Positive `x` means move right. Positive `y` means move down.

## action/

Frames are transparent-background PNG files named with a shared prefix and zero-based continuous indices:

```text
stand_0.png
stand_1.png
leftwalk_0.png
leftwalk_1.png
```

All frames for one role should use consistent canvas dimensions. Character scale and bottom-center should stay stable across actions, or the desktop pet will visually jump when changing actions.

## info/info.json

Recommended shape:

```json
{
  "coverImages": ["pfp.png"],
  "pfp": "pfp.png",
  "petName": "Display Name",
  "tages": {
    "Converted": "#9fd3ff"
  },
  "intro": "Short description.",
  "author": {
    "name": "Author",
    "pfp": "pfp.png",
    "frameColor": "#4f91ff",
    "links": {},
    "infos": "Optional tooltip."
  }
}
```

`author` must be an object. Do not write it as a string.

Allowed link keys are controlled by `CodexPetLive.settings.LINK_PERMIT`: `BiliBili`, `微博`, `抖音`, `GitHub`, `爱发电`, `TikTok`, and `YouTube`.

## Failure Risks

- Missing `images` in an action.
- A prefix with no matching `prefix_*.png` frames.
- Non-continuous frame indices.
- `pet_conf.json` references an action absent from `act_conf.json`.
- Empty `random_act`.
- Non-object `info.author`.
- Non-UTF-8 or malformed JSON.
- Mixed frame sizes or unstable bottom-center anchors.
- Chinese or special-character filenames in distributed archives.
