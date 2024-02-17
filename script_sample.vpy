"""
The following variables are available to the script:
- vs: The VapourSynth module
- mvf: The mvsfunc module
- np: The numpy module
- functools: The functools module
- core (vs.core): A VapourSynth core
- reference_path (str): absolute path to the reference file
- distorted_path (str): absolute path to the distorted file
- subtitle_path (str | None): absolute path to the subtitle file, or None if no subtitle file is provided
The following variables must be set in the script:
- reference (vs.VideoNode): the reference clip, should be in the same resolution as `distorted`
- distorted (vs.VideoNode): the distorted clip, should be in the same resolution as `reference`
"""

reference = core.lsmas.LWLibavSource(reference_path, threads=1)
if subtitle_path:
    reference = core.sub.TextFile(reference, subtitle_path)
distorted = core.lsmas.LWLibavSource(distorted_path, threads=1)
