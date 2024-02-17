reference_bits = reference.format.bits_per_sample
distorted_bits = distorted.format.bits_per_sample
if reference_bits < distorted_bits:
    reference = core.fmtc.bitdepth(reference, bits=distorted_bits)
elif reference_bits > distorted_bits:
    distorted = core.fmtc.bitdepth(distorted, bits=reference_bits)
res = core.vmaf.Metric(reference, distorted, [0, 2])
metrics = {}
total_frames = res.num_frames


def get_metrics(n, f, clip):
    metrics[n] = (
        (f.props["psnr_y"] + f.props["psnr_cr"] + f.props["psnr_cb"]) / 3,
        f.props["float_ssim"],
    )
    if len(metrics) == total_frames:
        with open("vqa_metrics.csv", "w") as f:
            f.write("frame,psnr,ssim\n")
            for i in range(total_frames):
                f.write(f"{i},{metrics[i][0]},{metrics[i][1]}\n")
    return clip


res = core.std.FrameEval(res, functools.partial(get_metrics, clip=res), prop_src=[res])
res.set_output()
