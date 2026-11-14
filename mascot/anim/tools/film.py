"""FILM frame interpolation on CPU (TorchScript model from dajes/frame-interpolation-pytorch, v1.0.2).

interpolate(a, b, n) returns n in-between RGB frames (uint8 HxWx3 arrays) between images a and b, made by recursive
midpoint splitting (the way the model was trained). Sizes are padded to a multiple of 64.
Model file: /home/user/models/film_net_fp32.pt (download: see mascot/anim/README.md).
"""
import bisect
import numpy as np
import torch

MODEL = "/home/user/models/film_net_fp32.pt"
_m = None


def _model():
    global _m
    if _m is None:
        torch.set_num_threads(4)
        _m = torch.jit.load(MODEL, map_location="cpu").eval()
    return _m


def _t(a):
    h, w = a.shape[:2]
    ph, pw = (64 - h % 64) % 64, (64 - w % 64) % 64
    x = torch.from_numpy(np.pad(a, ((0, ph), (0, pw), (0, 0)), mode="edge")).permute(2, 0, 1)[None].float() / 255
    return x, (h, w)


def interpolate(a, b, n):
    x0, (h, w) = _t(a)
    x1, _ = _t(b)
    res, idx = [x0, x1], [0, n + 1]
    remains = list(range(1, n + 1))
    splits = torch.linspace(0, 1, n + 2)
    m = _model()
    with torch.no_grad():
        while remains:
            starts = torch.tensor(idx[:-1]); ends = torch.tensor(idx[1:])
            d = (splits[None, remains] - splits[starts, None]) / (splits[ends, None] - splits[starts, None]) - .5
            mi = torch.argmin(d.abs())
            si, step = int(mi // d.shape[1]), int(mi % d.shape[1])
            ei = si + 1
            dt = x0.new_full((1, 1), float((splits[remains[step]] - splits[idx[si]]) / (splits[idx[ei]] - splits[idx[si]])))
            p = m(res[si], res[ei], dt).clamp(0, 1)
            pos = bisect.bisect_left(idx, remains[step])
            idx.insert(pos, remains[step]); res.insert(pos, p)
            del remains[step]
    return [(r[0, :, :h, :w].permute(1, 2, 0).numpy() * 255 + .5).astype(np.uint8) for r in res[1:-1]]
