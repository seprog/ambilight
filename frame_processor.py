from colorsys import rgb_to_hsv
from dataclasses import dataclass
from functools import lru_cache

import numpy as np
from scipy.ndimage import zoom
import cv2

from lifx_devices import Light


@dataclass
class FrameProcessor:
  lights: list[Light]

  mask: np.ndarray | None = None

  saturation_exp: float = 1
  saturation_factor: float = 1
  saturation_clip_range: tuple[float, float] = (0, 1)
  saturation_lerp_range: tuple[float, float] = (0, 1)

  value_exp: float = 1
  value_factor: float = 1
  value_clip_range: tuple[float, float] = (0, 1)
  value_lerp_range: tuple[float, float] = (0, 1)

  @staticmethod
  @lru_cache
  def _mask(
    mask_bytes: bytes,
    mask_shape: tuple[int, int],
    frame_shape: tuple[int, int],
  ):
    base_mask = np.frombuffer(
      mask_bytes,
      dtype=bool
    ).reshape(mask_shape)
    expanded_mask = np.asarray(
      zoom(
        base_mask,
        (
          frame_shape[0] / mask_shape[0],
          frame_shape[1] / mask_shape[1],
        ),
        order=0,
      ),
      dtype=bool
    )
    flat_mask = expanded_mask.flatten()
    flat_mask_indices = np.nonzero(flat_mask)[0]

    return flat_mask_indices

  def ambilight_color(
    self,
    frame: np.ndarray[tuple[int, int, int]]
  ):
    # flatten and mask (complex variant of cropping) the frame
    frame_flat = frame.reshape(-1,3)
    frame_flat_masked = frame_flat if self.mask is None else frame_flat[
      self._mask(
        self.mask.astype(bool).tobytes(),
        self.mask.shape,
        frame.shape[:2],
      )
    ]
    
    # construct rgb and hsv arrays
    rgb = frame_flat_masked

    hsv = cv2.cvtColor(
      frame_flat_masked.reshape(-1, 1, 3),  # cv2 expects an image (2d by nature)
      cv2.COLOR_RGB2HSV
    ).reshape(-1, 3)  # convert back to 1d

    # normalize
    rgb = rgb.astype(np.float32)
    rgb[:, 0] = rgb[:, 0] / 255
    rgb[:, 1] = rgb[:, 1] / 255
    rgb[:, 2] = rgb[:, 2] / 255

    hsv = hsv.astype(np.float32)
    hsv[:, 0] = hsv[:, 0] / 179  # OpenCV uses 0..179 instead of 0..255
    hsv[:, 1] = hsv[:, 1] / 255
    hsv[:, 2] = hsv[:, 2] / 255

    # derive ambicolor
    hue, saturation = rgb_to_hsv(
      *np.average(
        rgb,
        weights=hsv[:, 2],
        axis=0,
      )
    )[:2] if hsv[:, 2].sum() else (0, 0)
    value = np.mean(hsv, axis=0)[2]

    # lerp, clip and modify saturation and value (brightness)
    ambicolor = (
      hue,
      np.clip(
        saturation ** self.saturation_exp * self.saturation_factor,
        *self.saturation_clip_range
      ) * (self.saturation_lerp_range[1] - self.saturation_lerp_range[0]) + self.saturation_lerp_range[0],
      np.clip(
        value ** self.value_exp * self.value_factor,
        *self.value_clip_range
      ) * (self.value_lerp_range[1] - self.value_lerp_range[0]) + self.value_lerp_range[0],
    )
    
    return ambicolor
