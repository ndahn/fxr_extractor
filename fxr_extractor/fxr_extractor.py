import os
import shutil
import argparse
from pathlib import Path
import subprocess
from PIL import Image


WITCHY_BND = Path(
    "E:/Games/Elden Ring/Modding/Tools/WitchyBND-v3.0.0.0-win-x64/WitchyBND.exe"
)


def unpack(ffxbnds: Path | list[Path], output_dir: Path) -> Path:
    if not WITCHY_BND.is_file():
        raise FileNotFoundError("Cannot find WitchyBND.exe")

    if isinstance(ffxbnds, Path):
        ffxbnds = [ffxbnds]

    for offset in range(0, len(ffxbnds), 128):
        batch = ffxbnds[offset : offset + 128]
        args = [
            "--passive",
            *("--location", str(output_dir)),
            *[str(p) for p in batch],
        ]

        subprocess.call([WITCHY_BND, *args], stdout=open(os.devnull, "wb"))

    return output_dir


def texconv(
    inputs: Path | list[Path], output_dir: Path, format: str = "png"
) -> list[Path]:
    texconv_path = Path(__file__).parent / "texconv.exe"
    if not texconv_path.is_file():
        raise FileNotFoundError("Cannot find texconv.exe")

    if isinstance(inputs, Path):
        if inputs.is_file():
            inputs = [inputs]
        else:
            # We can only pass so many arguments to a subprocess,
            # but luckily texconv supports wildcards
            inputs = [inputs / "*.dds"]

    # Resizing with texconv will not keep aspect ratios, so we do it with pillow later instead
    args = [
        *("-o", str(output_dir)),
        *("-ft", format),
        "-r:flatten",
        "-nologo",
        "-y",
        *[str(p) for p in inputs],
    ]

    subprocess.check_call([texconv_path, *args], stdout=open(os.devnull, "wb"))

    res = []
    for f in inputs:
        if "*" in f.name:
            for dds in f.parent.glob(f.name):
                res.append(output_dir / f"{dds.stem}.{format}")
        else:
            res.append(output_dir / f"{f.stem}.{format}")

    return res


def convert_to_webp(inputs: list[Path], output_dir: Path, scale: float = 1.0) -> Path:
    for f in inputs:
        with Image.open(f) as img:
            if scale != 1.0:
                img = img.resize(
                    (int(img.size[0] * scale), int(img.size[1] * scale)),
                    Image.Resampling.LANCZOS,
                )

            img.save(
                output_dir / f"{f.stem}.webp",
                "WEBP",
                quality=90,
                alpha_quality=100,
                lossless=False,
                method=4,
                exact=False,
            )

    return output_dir


def convert(ffxbnd: Path, tmp_path: Path, output_path: Path, scale: float = 1.0) -> int:
    print(f"  => {ffxbnd.stem}... ", flush=True, end="")
    unpack(ffxbnd, tmp_path)

    bnd_dir = ffxbnd.name.replace(".", "-") + "-wffxbnd"
    my_tmp_dir = tmp_path / bnd_dir

    num_dds = len(list(my_tmp_dir.glob("tex/*.dds")))
    if num_dds == 0:
        print("empty")
        shutil.rmtree(my_tmp_dir)
        return 0

    img_files = texconv(my_tmp_dir / "tex", my_tmp_dir, format="tga")
    convert_to_webp(img_files, output_path, scale=scale)
    print(f"converted {num_dds} textures")

    try:
        shutil.rmtree(my_tmp_dir)
    except Exception:
        # This sometimes fails, probably because witchy is still active, 
        # but we can remove it later
        pass

    return num_dds


def main(
    input_paths: list[Path],
    output_path: Path,
    scale: float = 1.0,
    clear_output: bool = False,
) -> None:
    if clear_output:
        for f in output_path.glob("*"):
            if f.is_file():
                f.unlink()

    ffxbnds: list[Path] = []
    for p in input_paths:
        if p.is_dir():
            ffxbnds.extend(p.glob("*.ffxbnd.dcx"))
        else:
            ffxbnds.append(p)

    for p in ffxbnds:
        if not p.is_file():
            raise FileNotFoundError(f"Could not find ffxbnd {p}")

    print(f"=> Found {len(ffxbnds)} binders")

    tmp_path = output_path / "tmp"
    tmp_path.mkdir(parents=True, exist_ok=True)
    total = 0

    for bnd in ffxbnds:
        total += convert(bnd, tmp_path, output_path, scale=scale)

    try:
        shutil.rmtree(tmp_path)
    except Exception:
        print(f"WARNING: failed to remove tmp directory {tmp_path}, you can do it manually")

    print("=> Done!\n")
    print(f"Converted {total} dds files from {len(ffxbnds)} binders")
    print(f"All files have been written to {output_path.absolute()}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i",
        "--input",
        nargs="+",
        type=Path,
        help="One or more ffxbnd.dcx files. If folders are specified they will be searched for ffxbnd.dcx files without recursion.",
    )
    parser.add_argument("-o", "--output", type=Path, help="Output directory.")
    parser.add_argument(
        "-c",
        "--clear",
        action="store_true",
        default=True,
        help="Remove all files from the targegt directory before extracting.",
    )
    parser.add_argument(
        "-s",
        "--scale",
        type=float,
        default=1.0,
        help="Scale converted images by this factor.",
    )
    parser.add_argument(
        "-f",
        "--format",
        type=str,
        default="tga",
        help="Format of the intermediary image format.",
    )
    args = parser.parse_args()

    main(args.input, args.output, scale=args.scale, clear_output=args.clear)


# Example: python .\fxr_extractor\fxr_extractor.py -i 'E:\SteamLibrary\steamapps\common\ELDEN RING\Game\sfx\'  -o .\tmp\eldenring_0 -s 0
