low_psnr = np.load("__vqa_low_psnr__.npy")
low_ssim = np.load("__vqa_low_ssim__.npy")

if distorted.format.bits_per_sample != 16:
    distorted = core.fmtc.bitdepth(distorted, bits=16)
if reference.format.bits_per_sample != 16:
    reference = core.fmtc.bitdepth(reference, bits=16)
diff = core.std.MakeDiff(reference, distorted)
style_string = "sans-serif,50,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,2,0,9,10,10,10,1"
distorted = core.sub.Subtitle(distorted, "Distorted", style=style_string)
reference = core.sub.Subtitle(reference, "Reference", style=style_string)
res = core.std.StackVertical([reference, distorted, diff])
res = mvf.ToRGB(res, depth=8)

res_trim = None
for j in range(2):
    if j == 0:
        metrics_arr = low_psnr
        metric_name = "psnr"
    else:
        metrics_arr = low_ssim
        metric_name = "ssim"
    for i in range(len(metrics_arr)):
        metrics = metrics_arr[i]
        frame_num = round(metrics[0])
        psnr = metrics[1]
        ssim = metrics[2]
        frame = res[frame_num]
        frame = core.imwri.Write(
            frame,
            "PNG",
            filename=f"{metric_name}{i}_f{frame_num}_psnr{psnr}_ssim{ssim}.png",
            overwrite=True,
        )
        if res_trim is None:
            res_trim = frame
        else:
            res_trim += frame
core.std.ShufflePlanes(
    [res_trim, res_trim, res_trim], planes=[0, 1, 2], colorfamily=vs.YUV
).set_output()
