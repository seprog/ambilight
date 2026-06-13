from colorsys import rgb_to_hsv
from dataclasses import dataclass
from functools import lru_cache

import numpy as np
from scipy.ndimage import zoom

from lifx_devices import Light


@dataclass
class FrameProcessor:
  lights: list[Light]

  mask: np.ndarray | None = None

  saturation_exp: float = 1
  saturation_factor: float = 1
  saturation_range: tuple[float, float] = (0, 1)

  value_exp: float = 1
  value_factor: float = 1
  value_range: tuple[float, float] = (0, 1)

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
    pixels = frame.reshape(-1,3)
    masked = pixels if self.mask is None else pixels[
      self._mask(
        self.mask.astype(bool).tobytes(),
        self.mask.shape,
        frame.shape[:2],
      )
    ]
    median_rgb = np.median(masked, axis=0)
    median_hsv = rgb_to_hsv(*median_rgb / 255)

    clamped_scaled_median_hsv = (
      median_hsv[0],
      np.clip(
        median_hsv[1] ** self.saturation_exp * self.saturation_factor,
        *self.saturation_range
      ),
      np.clip(
        median_hsv[2] ** self.value_exp * self.value_factor,
        *self.value_range
      ),
    )
    
    return clamped_scaled_median_hsv
