The sole purpose of this tool is to create texture preview archives for [fxr-playground](https://fxr-playground.pages.dev). It will extract `.dds` textures from FromSoft `.ffxbnd.dcx` binders and convert them to regular lossy image formats, optionally downscaled.

> **NOTE:** before you run it you need to set the path to your [WitchyBND.exe](https://github.com/ividyon/WitchyBND/). Change the path at the top of [fxr_extractor.py](fxr_extractor/fxr_extractor.py) and make sure you replace all backwards slashes '\' with forward slashes '/'.

The most common use case is to point *fxr_extractor* either at a game's `sfx` folder or a specific binder from your mod. For example, the following line will grab and convert all binders from EldenRing and place them in `tmp/eldenring_05` with 50% scale. Passing the `-z` flag also creates a zip-archive with the provided name.

```bash
python ./fxr_extractor/fxr_extractor.py -i 'E:/SteamLibrary/steamapps/common/ELDEN RING/Game/sfx'  -o ./tmp/eldenring_05 -s 0.5 -z eldenring_05
```

Check the source code or run `fxr_extractor.py --help` to see all options.

# Shout-Outs
- This tool uses [texconv](https://github.com/Microsoft/DirectXTex/) for converting `.dds` textures. Sorry, Linux users :/

- [fxr-playground](https://fxr-playground.pages.dev) is just goated - thank you so much, CCC =)
