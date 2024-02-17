# Video Quality Assurance (VQA) Tool

The Video Quality Assurance (VQA) tool is designed to batch assess the quality of video files, specifically to identify corrupted frames. Run `python vqa.py -h` for available command-line options.

## Requirements

[VapourSynth](https://www.vapoursynth.com/) must be installed and linked with Python on the system. Only the latest versions of the dependencies are tested and supported.

### Required Python Packages

- [numpy](https://numpy.org/)
- [matplotlib](https://matplotlib.org/)

### Required VapourSynth Plugins

- [VMAF](https://github.com/HomeOfVapourSynthEvolution/VapourSynth-VMAF)
- [fmtconv](https://gitlab.com/EleonoreMizo/fmtconv)
- [mvsfunc](https://github.com/HomeOfVapourSynthEvolution/mvsfunc)
- [subtext](https://github.com/vapoursynth/subtext)
- [ImageMagick](https://github.com/vapoursynth/vs-imwri)

## Configuration File

The configuration JSON file should contain an array of objects. Each object specifies a video file to process. See `config_sample.json` for all the available options and their descriptions. Paths in the configuration file may be specified as either absolute or relative to the config file's directory.

## Video Processing Script

A segment of a VapourSynth script must be provided via the `script` option in the configuration file for processing video files. The expected format and specifications for this script segment are outlined in `script_sample.vpy`.

## Temporary files

The following temporary files will be generated and subsequently overwritten in the output directory during script execution. If the script is interrupted, these files may not be deleted and should be removed manually.

- `__vqa__.vpy`
- `__vqa_low_psnr__.npy`
- `__vqa_low_ssim__.npy`

## Output

Upon completion, the tool produces the following files in the output directory:

- `vqa_metrics.csv`: A CSV file containing the PSNR and SSIM metrics for all frames in the video file.
- `vqa_plot.png`: A plot of the PSNR and SSIM metrics across all frames.
- `vqa_hist.png`: A histogram of PSNR and SSIM values for all frames.
- Images of the frames with the lowest PSNR and SSIM values. The filenames are in the format `{metric}{i}_f{frame_num}_psnr{psnr}_ssim{ssim}`, where `{metric}{i}` indicates the `i`-th lowest `metric` value, `frame_num` denotes the frame number, and `psnr` and `ssim` represent their respective values. `i` and `frame_num` are indexed from 0.
