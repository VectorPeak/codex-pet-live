# PeakDeskSprite Notices

PeakDeskSprite source code is distributed under the license in [LICENSE](LICENSE)

## Python And UI Dependencies

Runtime dependencies are listed in [requirements.txt](requirements.txt). Their upstream licenses are controlled by their respective projects, including PySide6, PySide6-Fluent-Widgets, apscheduler, pynput, tendo, and Pillow

## Bundled And Referenced Assets

The repository includes default demo resources under `res/` and references external desktop-pet projects in the README acknowledgements. These assets and references are not a blanket permission to reuse every character, image, sound, font, or third-party module outside its original license terms

User-imported characters, items, mini-pets, sounds, images, and other MOD packages remain the responsibility of the importer or distributor. Only import or redistribute third-party assets when the source and license allow it

## LLM Providers

PeakDeskSprite can call user-configured OpenAI-compatible LLM providers. The repository does not bundle an LLM model or grant rights to any provider output, model, endpoint, or service brand. Provider use is governed by the provider's own terms and privacy policy

## Packaging Boundary

Release packages should not include local runtime data, logs, API keys, LLM secrets, LLM chat history, `.env` files, or user-specific configuration. Public Windows release artifacts are named `PeakDeskSprite-vX.Y.Z-windows-x64.zip`, and the Windows executable inside the package is `PeakDeskSprite.exe`
