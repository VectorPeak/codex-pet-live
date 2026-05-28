#!/usr/bin/env python
"""Convert Codex hatch-pet packages into CodexPetLive role modules."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from PIL import Image


ATLAS_COLUMNS = 8
ATLAS_ROWS = 9
CELL_WIDTH = 192
CELL_HEIGHT = 208
ATLAS_SIZE = (ATLAS_COLUMNS * CELL_WIDTH, ATLAS_ROWS * CELL_HEIGHT)

HATCH_ROWS: tuple[tuple[str, int, int], ...] = (
    ("idle", 0, 6),
    ("running-right", 1, 8),
    ("running-left", 2, 8),
    ("waving", 3, 4),
    ("jumping", 4, 5),
    ("failed", 5, 8),
    ("waiting", 6, 6),
    ("running", 7, 6),
    ("review", 8, 6),
)

STATE_TO_PREFIX = {
    "idle": "stand",
    "running-right": "rightwalk",
    "running-left": "leftwalk",
    "waving": "wave",
    "jumping": "jump",
    "failed": "failed",
    "waiting": "waiting",
    "running": "focus",
    "review": "review",
}


@dataclass(frozen=True)
class ConversionPlan:
    input_dir: Path
    pet_json: Path
    spritesheet: Path
    out_dir: Path
    role_name: str
    display_name: str
    description: str
    overwrite: bool


def _read_json(path: Path) -> dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as file:
            value = json.load(file)
    except FileNotFoundError as exc:
        raise SystemExit(f"missing JSON file: {path}") from exc
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid JSON file: {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise SystemExit(f"JSON root must be an object: {path}")
    return value


def _write_json(path: Path, value: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def slugify(value: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9_.-]+", "-", value.strip())
    slug = re.sub(r"-{2,}", "-", slug).strip("-._")
    return slug or "codex-pet"


def resolve_plan(args: argparse.Namespace) -> ConversionPlan:
    input_dir = Path(args.input).expanduser().resolve()
    pet_json = Path(args.pet_json).expanduser().resolve() if args.pet_json else input_dir / "pet.json"
    manifest = _read_json(pet_json)

    sheet_arg = args.spritesheet or manifest.get("spritesheetPath") or "spritesheet.webp"
    spritesheet = Path(sheet_arg).expanduser()
    if not spritesheet.is_absolute():
        spritesheet = pet_json.parent / spritesheet
    spritesheet = spritesheet.resolve()

    display_name = args.display_name or str(manifest.get("displayName") or manifest.get("id") or input_dir.name)
    role_name = slugify(args.role_name or str(manifest.get("id") or display_name))
    description = args.description or str(manifest.get("description") or "Converted from a Codex hatch-pet package.")

    if args.out_dir:
        out_dir = Path(args.out_dir).expanduser().resolve()
    else:
        out_root = Path(args.out_root).expanduser().resolve()
        out_dir = out_root / role_name

    return ConversionPlan(
        input_dir=input_dir,
        pet_json=pet_json,
        spritesheet=spritesheet,
        out_dir=out_dir,
        role_name=role_name,
        display_name=display_name,
        description=description,
        overwrite=args.overwrite,
    )


def load_atlas(path: Path) -> Image.Image:
    if not path.exists():
        raise SystemExit(f"missing spritesheet: {path}")
    try:
        with Image.open(path) as opened:
            atlas = opened.convert("RGBA")
    except Exception as exc:  # Pillow exposes format-specific exceptions.
        raise SystemExit(f"could not open spritesheet {path}: {exc}") from exc

    if atlas.size != ATLAS_SIZE:
        raise SystemExit(
            f"spritesheet must be {ATLAS_SIZE[0]}x{ATLAS_SIZE[1]}, got {atlas.width}x{atlas.height}: {path}"
        )
    return atlas


def extract_frames(atlas: Image.Image, action_dir: Path) -> dict[str, int]:
    action_dir.mkdir(parents=True, exist_ok=True)
    frame_counts: dict[str, int] = {}

    for state, row, count in HATCH_ROWS:
        prefix = STATE_TO_PREFIX[state]
        frame_counts[prefix] = count
        for col in range(count):
            box = (
                col * CELL_WIDTH,
                row * CELL_HEIGHT,
                (col + 1) * CELL_WIDTH,
                (row + 1) * CELL_HEIGHT,
            )
            frame = atlas.crop(box)
            frame.save(action_dir / f"{prefix}_{col}.png")

    return frame_counts


def build_pet_conf(display_name: str) -> dict[str, Any]:
    return {
        "width": CELL_WIDTH,
        "height": CELL_HEIGHT,
        "scale": 0.75,
        "refresh": 5,
        "interact_speed": 0.02,
        "default": "default",
        "up": "default",
        "down": "default",
        "left": "left_walk",
        "right": "right_walk",
        "drag": "drag",
        "fall": "fall",
        "on_floor": "onfloor",
        "focus": "focus",
        "patpat": "patpat",
        "random_act": [
            {"name": "Stand", "act_list": ["default"], "act_prob": 1.0, "act_type": [2, 0]},
            {
                "name": "Walk",
                "act_list": ["left_walk", "right_walk", "default"],
                "act_prob": 0.25,
                "act_type": [2, 0],
            },
            {"name": "Wave", "act_list": ["patpat"], "act_prob": 0.2, "act_type": [2, 0]},
            {"name": "Waiting", "act_list": ["waiting"], "act_prob": 0.1, "act_type": [2, 0]},
            {"name": "Focus", "act_list": ["focus"], "act_prob": 0.1, "act_type": [2, 0]},
            {"name": "Review", "act_list": ["review"], "act_prob": 0.1, "act_type": [2, 0]},
            {"name": "onfloor", "act_list": ["onfloor"], "act_prob": 0, "act_type": [0, 10000]},
        ],
        "metadata": {
            "display_name": display_name,
            "source": "codex-hatch-pet",
        },
    }


def build_act_conf() -> dict[str, dict[str, Any]]:
    return {
        "default": {"images": "stand", "act_num": 1, "frame_refresh": 0.16},
        "left_walk": {
            "images": "leftwalk",
            "act_num": 2,
            "need_move": True,
            "direction": "left",
            "frame_move": 8,
            "frame_refresh": 0.12,
        },
        "right_walk": {
            "images": "rightwalk",
            "act_num": 2,
            "need_move": True,
            "direction": "right",
            "frame_move": 8,
            "frame_refresh": 0.12,
        },
        "drag": {"images": "stand", "act_num": 1, "frame_refresh": 0.16},
        "fall": {"images": "jump", "act_num": 1, "frame_refresh": 0.14},
        "onfloor": {"images": "failed", "act_num": 1, "frame_refresh": 0.16},
        "patpat": {"images": "wave", "act_num": 1, "frame_refresh": 0.14},
        "waiting": {"images": "waiting", "act_num": 1, "frame_refresh": 0.15},
        "focus": {"images": "focus", "act_num": 1, "frame_refresh": 0.12},
        "review": {"images": "review", "act_num": 1, "frame_refresh": 0.15},
        "failed": {"images": "failed", "act_num": 1, "frame_refresh": 0.16},
    }


def build_info(plan: ConversionPlan) -> dict[str, Any]:
    return {
        "petName": plan.display_name,
        "intro": plan.description,
        "coverImages": ["pfp.png"],
        "author": {
            "name": "Codex hatch-pet",
            "pfp": "pfp.png",
            "frameColor": "#4f91ff",
            "infos": "Converted from a Codex hatch-pet package.",
            "links": {},
        },
        "tages": {
            "Codex": "#b7df8a",
            "Converted": "#9fd3ff",
        },
    }


def validate_role_dir(role_dir: Path) -> list[str]:
    errors: list[str] = []
    pet_path = role_dir / "pet_conf.json"
    act_path = role_dir / "act_conf.json"
    action_dir = role_dir / "action"

    if not pet_path.exists():
        errors.append(f"missing {pet_path}")
        return errors
    if not act_path.exists():
        errors.append(f"missing {act_path}")
        return errors
    if not action_dir.is_dir():
        errors.append(f"missing action directory: {action_dir}")
        return errors

    pet_conf = _read_json(pet_path)
    act_conf = _read_json(act_path)

    for key in ("default", "drag", "fall"):
        if key not in pet_conf:
            errors.append(f"pet_conf.json missing required action key: {key}")

    referenced: list[str] = []
    for key in ("default", "up", "down", "left", "right", "drag", "fall", "on_floor", "focus", "patpat"):
        value = pet_conf.get(key)
        if isinstance(value, str):
            referenced.append(value)
        elif isinstance(value, dict):
            referenced.extend(str(item) for item in value.values())

    for item in pet_conf.get("random_act", []):
        if isinstance(item, dict):
            referenced.extend(str(action) for action in item.get("act_list", []))

    for action_name in referenced:
        if action_name not in act_conf:
            errors.append(f"pet_conf.json references missing act_conf action: {action_name}")

    for action_name, conf in act_conf.items():
        if not isinstance(conf, dict):
            errors.append(f"act_conf action must be an object: {action_name}")
            continue
        prefix = conf.get("images")
        if not isinstance(prefix, str) or not prefix:
            errors.append(f"act_conf action missing non-empty images prefix: {action_name}")
            continue
        files = sorted(action_dir.glob(f"{prefix}_*.png"))
        indices = []
        pattern = re.compile(rf"^{re.escape(prefix)}_(\d+)\.png$")
        for file in files:
            match = pattern.match(file.name)
            if match:
                indices.append(int(match.group(1)))
        if not indices:
            errors.append(f"no PNG frames found for action {action_name}: {prefix}_*.png")
            continue
        expected = set(range(min(indices), max(indices) + 1))
        missing = sorted(expected.difference(indices))
        if missing:
            errors.append(f"non-continuous frames for prefix {prefix}: missing {missing}")

        for file in files:
            try:
                with Image.open(file) as image:
                    image.verify()
            except Exception as exc:
                errors.append(f"invalid PNG frame {file}: {exc}")

    return errors


def convert(plan: ConversionPlan) -> None:
    atlas = load_atlas(plan.spritesheet)

    if plan.out_dir.exists():
        if not plan.overwrite:
            raise SystemExit(f"output directory already exists; pass --overwrite to replace it: {plan.out_dir}")
        shutil.rmtree(plan.out_dir)

    action_dir = plan.out_dir / "action"
    info_dir = plan.out_dir / "info"
    plan.out_dir.mkdir(parents=True, exist_ok=True)
    info_dir.mkdir(parents=True, exist_ok=True)

    frame_counts = extract_frames(atlas, action_dir)
    _write_json(plan.out_dir / "pet_conf.json", build_pet_conf(plan.display_name))
    _write_json(plan.out_dir / "act_conf.json", build_act_conf())
    _write_json(info_dir / "info.json", build_info(plan))

    first_frame = action_dir / "stand_0.png"
    if first_frame.exists():
        shutil.copy2(first_frame, info_dir / "pfp.png")

    report = {
        "ok": True,
        "role_name": plan.role_name,
        "display_name": plan.display_name,
        "source": {
            "input_dir": str(plan.input_dir),
            "pet_json": str(plan.pet_json),
            "spritesheet": str(plan.spritesheet),
        },
        "output_dir": str(plan.out_dir),
        "cell_size": [CELL_WIDTH, CELL_HEIGHT],
        "atlas_size": [ATLAS_SIZE[0], ATLAS_SIZE[1]],
        "frame_counts": frame_counts,
    }
    _write_json(plan.out_dir / "conversion-report.json", report)

    errors = validate_role_dir(plan.out_dir)
    if errors:
        raise SystemExit("conversion output failed validation:\n" + "\n".join(f"- {error}" for error in errors))


def cmd_convert(args: argparse.Namespace) -> int:
    plan = resolve_plan(args)
    convert(plan)
    print(f"converted {plan.display_name} -> {plan.out_dir}")
    return 0


def cmd_validate(args: argparse.Namespace) -> int:
    role_dir = Path(args.role_dir).expanduser().resolve()
    errors = validate_role_dir(role_dir)
    if errors:
        print("validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print(f"validation ok: {role_dir}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Convert a Codex hatch-pet package into a CodexPetLive role module.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    convert_parser = subparsers.add_parser("convert", help="convert a pet.json + spritesheet package")
    convert_parser.add_argument("--input", required=True, help="Codex pet package directory")
    convert_parser.add_argument("--pet-json", help="Path to pet.json; defaults to <input>/pet.json")
    convert_parser.add_argument("--spritesheet", help="Path to spritesheet; defaults to pet.json spritesheetPath")
    convert_parser.add_argument("--out-root", default="res/role", help="Output root; ignored when --out-dir is set")
    convert_parser.add_argument("--out-dir", help="Exact CodexPetLive role output directory")
    convert_parser.add_argument("--role-name", help="Output role folder name; defaults to pet id")
    convert_parser.add_argument("--display-name", help="Display name stored in metadata")
    convert_parser.add_argument("--description", help="Description stored in metadata")
    convert_parser.add_argument("--overwrite", action="store_true", help="Replace output directory if it exists")
    convert_parser.set_defaults(func=cmd_convert)

    validate_parser = subparsers.add_parser("validate", help="validate a generated CodexPetLive role directory")
    validate_parser.add_argument("role_dir")
    validate_parser.set_defaults(func=cmd_validate)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
