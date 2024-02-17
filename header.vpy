import vapoursynth as vs
import mvsfunc as mvf
import numpy as np
import functools

core = vs.core
core.num_threads = 8
core.max_cache_size = 8192
