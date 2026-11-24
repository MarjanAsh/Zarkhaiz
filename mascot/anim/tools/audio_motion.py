"""Audio-driven face motion for the whole voiceover (the premium lip-sync, from reel v020).

The first lip-sync test (visemes.py: mouth shapes picked per letter) looked mechanical; the user rejected it. Here the
mouth, jaw and cheeks are generated from the voice itself by JoyVASA's motion generator (MIT,
https://github.com/jdh-algo/JoyVASA): a diffusion model that turns speech audio (HuBERT features) into a sequence of
LivePortrait expression keypoints and head rotations, 25 per second. LivePortrait then renders those on the master
face (lp_face.Face.render(exp_delta=...)), so the identity stays the master's.

The voice lines are laid on one track at their reel times (timeline.json), so frame i of the result is reel time i/25.
Usage: python3 audio_motion.py [--seed 7] [--cfg 2.8]
Output: out/speech/motion.npz  exp (N,21,3) expression offsets relative to the resting face, pitch/yaw/roll (N,)
        relative to rest, fps, speaking (N,) 0..1 (voice loudness, for gating)
Install: git clone https://github.com/jdh-algo/JoyVASA /home/user/JoyVASA; weights in its pretrained_weights/
  (JoyVASA/motion_generator/motion_generator_hubert_chinese.pt, JoyVASA/motion_template/motion_template.pkl from
  huggingface.co/jdh-algo/JoyVASA; "TencentGameMate:chinese-hubert-base"/ from
  huggingface.co/TencentGameMate/chinese-hubert-base); pip install transformers einops.
"""
import json, math, os, pickle, sys, wave
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F

JV = os.environ.get("JOYVASA", "/home/user/JoyVASA")
ROOT = Path(__file__).resolve().parents[1]
REEL = ROOT.parents[1] / "video" / "outputdm-reel"


def voice_track(sr=16000):
    """All lines on one mono track at their reel times."""
    import torchaudio
    TL = json.loads((REEL / "timeline.json").read_text())
    buf = torch.zeros(int(TL["dur"] * sr) + sr)
    for l in TL["lines"]:
        w = wave.open(str(REEL / "vo" / f"{l['id']}.wav"))
        a = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
        if w.getnchannels() > 1:
            a = a.reshape(-1, w.getnchannels()).mean(1)
        a = torchaudio.functional.resample(torch.from_numpy(a.copy()), w.getframerate(), sr)
        i = int(l["t0"] * sr)
        buf[i:i + len(a)] += a
    return buf, TL


def main():
    args = sys.argv[1:]
    seed = int(args[args.index("--seed") + 1]) if "--seed" in args else 7
    cfg = float(args[args.index("--cfg") + 1]) if "--cfg" in args else 2.8
    sys.path.insert(0, JV)
    import src.modules.common as jc
    jc.enc_dec_mask.__defaults__ = (2, 0, 'cpu')     # the model's default device is cuda; this machine has no GPU
    import src.modules.hubert as jh
    _fp = jh.HubertModel.from_pretrained.__func__     # newer transformers: the model asks for attention outputs, which needs the eager attention
    jh.HubertModel.from_pretrained = classmethod(lambda cls, path, **k: _fp(cls, path, attn_implementation="eager", **k))
    from src.modules.dit_talking_head import DitTalkingHead
    torch.manual_seed(seed); np.random.seed(seed)
    data = torch.load(f"{JV}/pretrained_weights/JoyVASA/motion_generator/motion_generator_hubert_chinese.pt",
                      map_location="cpu", weights_only=False)
    A = data["args"] if isinstance(data["args"], dict) else vars(data["args"])
    model = DitTalkingHead(device='cpu', motion_feat_dim=A["motion_feat_dim"], n_motions=A["n_motions"], n_prev_motions=A["n_prev_motions"],
                           feature_dim=A["feature_dim"], audio_model=A["audio_model"], n_diff_steps=A["n_diff_steps"])
    data["model"].pop("denoising_net.TE.pe")
    model.load_state_dict(data["model"], strict=False)
    model.eval()
    T = pickle.load(open(f"{JV}/pretrained_weights/JoyVASA/motion_template/motion_template.pkl", "rb"))
    n_m, n_prev, fps = A["n_motions"], A["n_prev_motions"], A["fps"]
    unit = 16000. / fps
    audio, TL = voice_track()
    n_frames = int(TL["dur"] * fps) + 1
    audio = F.pad(audio, (1280, 640))
    nsub = math.ceil(len(audio) / 16000 * fps / n_m)
    audio = F.pad(audio, (0, max(0, round(unit * n_m) * nsub - len(audio))))
    coefs = []
    prev_m = prev_a = noise = None
    with torch.no_grad():
        for i in range(nsub):
            a_in = audio[round(i * n_m * unit):round((i + 1) * n_m * unit)][None]
            ind = torch.ones((1, n_m)) if A.get("use_indicator") else None
            kw = dict(indicator=ind, cfg_mode="incremental", cfg_cond=None, cfg_scale=cfg, dynamic_threshold=0)
            if i == 0:
                m, noise, prev_a = model.sample(a_in, **kw)
            else:
                m, noise, prev_a = model.sample(a_in, prev_m, prev_a, noise, **kw)
            prev_m = m[:, -n_prev:].clone(); prev_a = prev_a[:, -n_prev:]
            coefs.append(m[0])
            print("window", i + 1, "/", nsub, flush=True)
    c = torch.cat(coefs)[:n_frames].cpu().numpy()
    g = lambda k: np.asarray(T[k], np.float32)
    exp = (c[:, :63] * g("std_exp") + g("mean_exp")).reshape(-1, 21, 3)
    f1 = lambda k: float(np.asarray(T[k]).reshape(-1)[0])
    rot = {k: c[:, j] * (f1(f"max_{k}") - f1(f"min_{k}")) + f1(f"min_{k}")
           for j, k in ((67, "pitch"), (68, "yaw"), (69, "roll"))}
    # loudness per frame, and the resting face = the median of the frames in silence
    a = audio[1280:].numpy()
    hop = int(unit)
    rms = np.array([np.sqrt(np.mean(a[i * hop:i * hop + 2 * hop] ** 2) + 1e-9) for i in range(len(exp))])
    speaking = np.clip(rms / (np.percentile(rms, 90) + 1e-6), 0, 1)
    quiet = speaking < .03
    rest = np.median(exp[quiet], 0)
    out = ROOT / "out" / "speech"; out.mkdir(parents=True, exist_ok=True)
    np.savez(out / "motion.npz", exp=(exp - rest).astype(np.float32), rest=rest.astype(np.float32), fps=fps, speaking=speaking.astype(np.float32),
             **{k: (v - np.median(v[quiet])).astype(np.float32) for k, v in rot.items()})
    print("frames", len(exp), "fps", fps, "quiet", int(quiet.sum()))


if __name__ == "__main__":
    main()
