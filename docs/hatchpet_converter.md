# Hatch-Pet Converter

This project can convert a Codex hatch-pet package into a PeakDeskSprite role module.

## Input

A Codex pet package contains:

```text
pet.json
spritesheet.webp
```

The spritesheet must follow the Codex atlas contract:

- 1536 x 1872 pixels
- 8 columns x 9 rows
- 192 x 208 pixels per cell
- transparent background

## Convert A Local Package

```powershell
python tools\hatchpet_to_peakdesk.py convert `
  --input C:\Users\You\.codex\pets\best-friends `
  --out-dir res\role\BestFriendsCodex `
  --role-name BestFriendsCodex `
  --overwrite
```

Then validate the generated PeakDeskSprite role:

```powershell
python tools\hatchpet_to_peakdesk.py validate res\role\BestFriendsCodex
```

## Convert A Codex Pets Download

For pets on Codex Pets, download the package zip and unzip it first:

```powershell
$pet = "best-friends"
$root = "build\codex-pets\$pet"
New-Item -ItemType Directory -Force -Path $root | Out-Null
Invoke-WebRequest "https://codex-pets.net/api/pets/$pet/download" -OutFile "$root\$pet.codex-pet.zip"
Expand-Archive "$root\$pet.codex-pet.zip" -DestinationPath "$root\package" -Force

python tools\hatchpet_to_peakdesk.py convert `
  --input "$root\package" `
  --out-dir "res\role\BestFriendsCodex" `
  --role-name "BestFriendsCodex" `
  --overwrite
```

## Output

The converter writes a PeakDeskSprite role folder:

```text
res/role/BestFriendsCodex/
  pet_conf.json
  act_conf.json
  action/
    stand_0.png
    rightwalk_0.png
    leftwalk_0.png
    ...
  info/
    info.json
    pfp.png
  conversion-report.json
```

The default mapping is:

| Hatch-pet state | PeakDeskSprite action |
| --- | --- |
| idle | default / stand |
| running-right | right_walk |
| running-left | left_walk |
| waving | patpat |
| jumping | fall |
| failed | onfloor / failed |
| waiting | waiting |
| running | focus |
| review | review |

