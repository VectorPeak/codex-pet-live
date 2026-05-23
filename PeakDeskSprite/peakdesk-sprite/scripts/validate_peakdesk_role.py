#!/usr/bin/env python
"""Validate a PeakDeskSprite role module more strictly than the app import check."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

from PIL import Image


REQUIRED_PET_ACTIONS = ("default", "drag", "fall")
PET_ACTION_KEYS = (
    "default",
    "up",
    "down",
    "left",
    "right",
    "drag",
    "prefall",
    "fall",
    "on_floor",
    "focus",
    "patpat",
)


def read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"missing JSON file: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid JSON file: {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"JSON root must be an object: {path}")
    return value


def collect_references(pet_conf: dict[str, Any]) -> list[str]:
    refs: list[str] = []
    for key in PET_ACTION_KEYS:
        value = pet_conf.get(key)
        if isinstance(value, str):
            refs.append(value)
        elif isinstance(value, dict):
            refs.extend(str(item) for item in value.values())

    for group_key in ("random_act", "accessory_act"):
        groups = pet_conf.get(group_key, [])
        if not isinstance(groups, list):
            continue
        for group in groups:
            if not isinstance(group, dict):
                continue
            for action in group.get("act_list", []):
                refs.append(str(action))
            for action in group.get("acc_list", []):
                refs.append(str(action))
    return refs


def validate(role_dir: Path) -> list[str]:
    errors: list[str] = []
    role_dir = role_dir.resolve()
    action_dir = role_dir / "action"

    try:
        pet_conf = read_json(role_dir / "pet_conf.json")
    except ValueError as exc:
        return [str(exc)]

    try:
        act_conf = read_json(role_dir / "act_conf.json")
    except ValueError as exc:
        return [str(exc)]

    if not action_dir.is_dir():
        errors.append(f"missing action directory: {action_dir}")

    for key in REQUIRED_PET_ACTIONS:
        if key not in pet_conf:
            errors.append(f"pet_conf.json missing required key: {key}")

    random_act = pet_conf.get("random_act")
    if not isinstance(random_act, list) or not random_act:
        errors.append("pet_conf.json random_act must be a non-empty list")

    for action_name in collect_references(pet_conf):
        if action_name not in act_conf:
            errors.append(f"pet_conf.json references missing act_conf action: {action_name}")

    frame_sizes: set[tuple[int, int]] = set()
    for action_name, conf in act_conf.items():
        if not isinstance(conf, dict):
            errors.append(f"act_conf action must be an object: {action_name}")
            continue

        prefix = conf.get("images")
        if not isinstance(prefix, str) or not prefix:
            errors.append(f"act_conf action missing non-empty images prefix: {action_name}")
            continue

        files = sorted(action_dir.glob(f"{prefix}_*.png"))
        pattern = re.compile(rf"^{re.escape(prefix)}_(\d+)\.png$")
        indices: list[int] = []
        for file in files:
            match = pattern.match(file.name)
            if match:
                indices.append(int(match.group(1)))

        if not indices:
            errors.append(f"no frames found for action {action_name}: {prefix}_*.png")
            continue

        expected = set(range(0, max(indices) + 1))
        missing = sorted(expected.difference(indices))
        if missing:
            errors.append(f"non-continuous frames for prefix {prefix}: missing {missing}")

        for file in files:
            try:
                with Image.open(file) as image:
                    frame_sizes.add(image.size)
                    if image.format != "PNG":
                        errors.append(f"frame is not PNG: {file}")
                    if image.mode not in ("RGBA", "LA", "P"):
                        errors.append(f"frame is not transparent-capable mode {image.mode}: {file}")
                    image.verify()
            except Exception as exc:
                errors.append(f"invalid frame {file}: {exc}")

    if len(frame_sizes) > 1:
        errors.append(f"role frames use multiple canvas sizes: {sorted(frame_sizes)}")

    info_path = role_dir / "info" / "info.json"
    if info_path.exists():
        try:
            info_conf = read_json(info_path)
        except ValueError as exc:
            errors.append(str(exc))
        else:
            author = info_conf.get("author", {})
            if author is not None and not isinstance(author, dict):
                errors.append("info/info.json author must be an object")

    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("role_dir", help="Path to res/role/<RoleName>")
    args = parser.parse_args(argv)

    errors = validate(Path(args.role_dir))
    if errors:
        print("validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(f"validation ok: {Path(args.role_dir).resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
