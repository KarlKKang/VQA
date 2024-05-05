import argparse
import os
import json
import subprocess
import pathlib
import numpy as np
import matplotlib.pyplot as plt
from typing import List

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def run_command(command: List[str]):
    subprocess.run(command, check=True)


def delete_file(relative_path: str):
    pathlib.Path(os.path.abspath(relative_path)).unlink()


def vspipe():
    run_command(
        [
            "vspipe",
            "-p",
            "-c",
            "y4m",
            "__vqa__.vpy",
            ".",
        ]
    )


def create_temp_script(
    distorted_path: str,
    reference_path: str,
    subtitle_path: str | None,
    script_path: str,
    output_script_name: str,
):
    with open(os.path.join(SCRIPT_DIR, "header.vpy"), "r", encoding="utf-8") as f:
        script = f.read()
    if subtitle_path is None:
        subtitle_path = "None"
    else:
        subtitle_path = subtitle_path.replace("\\", "\\\\")
        subtitle_path = f"'{subtitle_path}'"
    reference_path = reference_path.replace("\\", "\\\\")
    distorted_path = distorted_path.replace("\\", "\\\\")
    script += (
        f"\nreference_path = '{reference_path}'\n"
        + f"distorted_path = '{distorted_path}'\n"
        + f"subtitle_path = {subtitle_path}\n"
    )
    with open(script_path, "r", encoding="utf-8") as f:
        script += f.read()
    with open(os.path.join(SCRIPT_DIR, output_script_name), "r", encoding="utf-8") as f:
        script += "\n" + f.read()
    with open("__vqa__.vpy", "w", encoding="utf-8") as f:
        f.write(script)


def cd_output_folder(output_path: str):
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    os.chdir(output_path)


def compute_metrics(
    distorted_path: str,
    reference_path: str,
    subtitle_path: str | None,
    script_path: str,
):
    create_temp_script(
        distorted_path, reference_path, subtitle_path, script_path, "metrics_out.vpy"
    )
    vspipe()
    delete_file("__vqa__.vpy")


def parse_metrics() -> np.ndarray:
    data = np.genfromtxt("vqa_metrics.csv", delimiter=",", skip_header=1)
    data = data[data[:, 0].argsort()]
    frames = data[:, 0]
    psnr = data[:, 1]
    ssim = data[:, 2]

    fig, ax = plt.subplots(2, figsize=(10, 10))
    ax[0].plot(frames, psnr)
    ax[0].sharex(ax[1])
    plt.setp(ax[0].get_xticklabels(), visible=False)
    ax[0].set_ylabel("PSNR (dB)")
    ax[0].axhline(
        y=np.min(psnr), color="r", linestyle="--", label=f"min: {np.min(psnr):.2f}dB"
    )
    ax[0].legend()
    ax[1].plot(frames, ssim)
    ax[1].set_xlabel("Frame number")
    ax[1].set_ylabel("SSIM")
    ax[1].axhline(
        y=np.min(ssim), color="r", linestyle="--", label=f"min: {np.min(ssim):.4f}"
    )
    ax[1].legend()
    plt.tight_layout()
    plt.savefig("vqa_plot.png")
    plt.close(fig)

    fig, ax = plt.subplots(2, figsize=(10, 10))
    ax[0].hist(psnr, bins=20)
    ax[0].set_xlabel("PSNR (dB)")
    ax[0].set_ylabel("Count")
    ax[0].text(
        0.95,
        0.95,
        f"mean: {np.mean(psnr):.2f}dB\nstd: {np.std(psnr):.2f}dB",
        ha="right",
        va="top",
        transform=ax[0].transAxes,
    )
    ax[1].hist(ssim, bins=20)
    ax[1].set_xlabel("SSIM")
    ax[1].set_ylabel("Count")
    ax[1].text(
        0.95,
        0.95,
        f"mean: {np.mean(ssim):.4f}\nstd: {np.std(ssim):.4f}",
        ha="right",
        va="top",
        transform=ax[1].transAxes,
    )
    plt.tight_layout()
    plt.savefig("vqa_hist.png")
    plt.close(fig)

    return data


def save_frames(
    distorted_path: str,
    reference_path: str,
    subtitle_path: str | None,
    script_path: str,
):
    create_temp_script(
        distorted_path, reference_path, subtitle_path, script_path, "frames_out.vpy"
    )
    vspipe()
    delete_file("__vqa__.vpy")


def check_video(
    distorted_path: str,
    reference_path: str,
    output_path: str,
    script_path: str,
    subtitle_path: str | None,
    num_frames: int,
):
    cd_output_folder(output_path)
    compute_metrics(distorted_path, reference_path, subtitle_path, script_path)
    data = parse_metrics()
    if num_frames > 0:
        np.save("__vqa_low_psnr__.npy", data[data[:, 1].argsort()[:num_frames]])
        np.save("__vqa_low_ssim__.npy", data[data[:, 2].argsort()[:num_frames]])
        save_frames(distorted_path, reference_path, subtitle_path, script_path)
        delete_file("__vqa_low_psnr__.npy")
        delete_file("__vqa_low_ssim__.npy")


def main():
    parser = argparse.ArgumentParser(description="VQA - Video Quality Assurance tool")
    parser.add_argument(
        "-c",
        "--config",
        type=str,
        default="config.json",
        help="Path to the configuration file",
    )
    parser.add_argument(
        "-n",
        "--num-frames",
        type=int,
        default=20,
        help="Save the n frames with the lowest quality by each metric",
    )
    args = parser.parse_args()

    config_path = os.path.abspath(args.config)
    wd = os.path.dirname(config_path)
    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    if not isinstance(config, list):
        raise TypeError("config.json should be a list of objects")

    for i in config:
        os.chdir(
            wd
        )  # change working directory to the directory of config.json as the paths may be relative
        if not isinstance(i, dict):
            raise TypeError("config.json should be a list of objects")
        distorted_path = i.get("distorted")
        reference_path = i.get("reference")
        output_path = i.get("output")
        script_path = i.get("script")
        subtitle_path = i.get("subtitle")
        if (
            distorted_path is None
            or reference_path is None
            or output_path is None
            or script_path is None
        ):
            raise AttributeError("Missing required fields in config.json")
        distorted_path = os.path.abspath(distorted_path)
        reference_path = os.path.abspath(reference_path)
        output_path = os.path.abspath(output_path)
        script_path = os.path.abspath(script_path)
        if subtitle_path is not None:
            subtitle_path = os.path.abspath(subtitle_path)
        check_video(
            distorted_path,
            reference_path,
            output_path,
            script_path,
            subtitle_path,
            args.num_frames,
        )


if __name__ == "__main__":
    main()
