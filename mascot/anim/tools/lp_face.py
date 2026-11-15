"""Animated face for the master character with LivePortrait (https://github.com/KlingAIResearch/LivePortrait, MIT).

One source image (raw/master.png). Every face frame is that same face re-posed by the model from a parameter set
(mouth shapes, smile, brows, eye openness, eyeball direction, small head turn), so identity, hair and glasses stay
the master's. Used as a library: Face(master).render(**params) -> RGB uint8 image the size of the master.
"""
import os, sys
import numpy as np, torch, cv2

LP = os.environ.get("LIVEPORTRAIT", "/home/user/LivePortrait")
sys.path.insert(0, LP)
from src.config.inference_config import InferenceConfig
from src.config.crop_config import CropConfig
from src.live_portrait_wrapper import LivePortraitWrapper
from src.utils.cropper import Cropper
from src.utils.camera import get_rotation_matrix
from src.utils.crop import prepare_paste_back, paste_back
from src.utils.retargeting_utils import calc_eye_close_ratio, calc_lip_close_ratio

P0 = dict(aaa=0, eee=0, woo=0, pout=0, smile=0, brow=0, eye=None, lip=None, gx=0, gy=0, wink=0,
          pitch=0, yaw=0, roll=0)


class Face:
    def __init__(self, path, scale=2.3):
        torch.set_num_threads(int(os.environ.get("LP_THREADS", os.cpu_count())))
        icfg = InferenceConfig(flag_force_cpu=True, flag_use_half_precision=False)
        ccfg = CropConfig(flag_force_cpu=True, scale=scale)
        self.w = LivePortraitWrapper(inference_cfg=icfg)
        self.cropper = Cropper(crop_cfg=ccfg)
        self.img = cv2.cvtColor(cv2.imread(path), cv2.COLOR_BGR2RGB)
        ci = self.cropper.crop_source_image(self.img, ccfg)
        self.lmk = ci['lmk_crop']
        self.M = ci['M_c2o']
        self.mask = prepare_paste_back(icfg.mask_crop, self.M, dsize=(self.img.shape[1], self.img.shape[0]))
        I_s = self.w.prepare_source(ci['img_crop_256x256'])
        self.info = self.w.get_kp_info(I_s)
        self.R_s = get_rotation_matrix(self.info['pitch'], self.info['yaw'], self.info['roll'])
        self.f_s = self.w.extract_feature_3d(I_s)
        self.x_s = self.w.transform_keypoint(self.info)
        self.eye0 = float(calc_eye_close_ratio(self.lmk[None]).mean())
        self.lip0 = float(calc_lip_close_ratio(self.lmk[None])[0][0])

    @torch.no_grad()
    def render(self, crop_only=False, **p):
        q = dict(P0); q.update(p)
        i = self.info
        d = i['exp'].clone()
        s = q['smile']
        d[0, 20, 1] += s * -0.01; d[0, 14, 1] += s * -0.02; d[0, 17, 1] += s * 0.0065; d[0, 17, 2] += s * 0.003
        d[0, 13, 1] += s * -0.00275; d[0, 16, 1] += s * -0.00275; d[0, 3, 1] += s * -0.0035; d[0, 7, 1] += s * -0.0035
        b = q['brow']
        if b > 0:
            d[0, 1, 1] += b * 0.001; d[0, 2, 1] += b * -0.001
        else:
            d[0, 1, 0] += b * -0.001; d[0, 2, 0] += b * 0.001; d[0, 1, 1] += b * 0.0003; d[0, 2, 1] += b * -0.0003
        gx, gy = q['gx'], q['gy']
        if gx > 0:
            d[0, 11, 0] += gx * 0.0007; d[0, 15, 0] += gx * 0.001
        else:
            d[0, 11, 0] += gx * 0.001; d[0, 15, 0] += gx * 0.0007
        d[0, 11, 1] += gy * -0.001; d[0, 15, 1] += gy * -0.001
        k = q['wink']
        d[0, 11, 1] += k * 0.001; d[0, 13, 1] += k * -0.0003; d[0, 17, 0] += k * 0.0003; d[0, 17, 1] += k * 0.0003
        d[0, 3, 1] += k * -0.0003
        d[0, 19, 0] += q['pout']
        o = q['woo']
        d[0, 14, 1] += o * 0.001; d[0, 3, 1] += o * -0.0005; d[0, 7, 1] += o * -0.0005; d[0, 17, 2] += o * -0.0005
        a = q['aaa']
        d[0, 20, 2] += a * -0.001; d[0, 20, 1] += a * -0.001; d[0, 14, 1] += a * -0.001
        e = q['eee']
        d[0, 19, 1] += e * 0.001; d[0, 19, 2] += e * 0.0001; d[0, 17, 1] += e * -0.0001
        R_d = get_rotation_matrix(i['pitch'] + q['pitch'], i['yaw'] + q['yaw'], i['roll'] + q['roll'])
        x_d = i['scale'] * (i['kp'] @ R_d + d) + i['t']
        if q['eye'] is not None:
            r = self.w.calc_combined_eye_ratio([[float(q['eye'])]], self.lmk)
            x_d = x_d + self.w.retarget_eye(self.x_s, r)
        if q['lip'] is not None:
            r = self.w.calc_combined_lip_ratio([[float(q['lip'])]], self.lmk)
            x_d = x_d + self.w.retarget_lip(self.x_s, r)
        x_d = self.w.stitching(self.x_s, x_d)
        out = self.w.parse_output(self.w.warp_decode(self.f_s, self.x_s, x_d)['out'])[0]
        if crop_only:
            return out
        return paste_back(out, self.M, self.img, self.mask)
