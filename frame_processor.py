from colorsys import rgb_to_hsv
from dataclasses import dataclass

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

  def ambilight_color(
    self,
    frame: np.ndarray[tuple[int, int, int]]
  ):
    pixels = frame.reshape(-1,3)
    masked = pixels if self.mask is None else pixels[
      np.array(
        zoom(
          self.mask,
          (
            frame.shape[0] / self.mask.shape[0],
            frame.shape[1] / self.mask.shape[1],
          )
        ),
        dtype=bool
      ).flatten()
    ]
    median_rgb = np.median(masked, axis=0)
    median_hsv = rgb_to_hsv(*median_rgb / 255)

    clamped_scaled_median_hsv = (
      median_hsv[0],
      max(
        self.saturation_range[0],
        min(
          self.saturation_range[1],
          median_hsv[1] ** self.saturation_exp * self.saturation_factor,
        )
      ),
      max(
        self.value_range[0],
        min(
          self.value_range[1],
          median_hsv[2] ** self.value_exp * self.value_factor,
        )
      ),
    )
    
    return clamped_scaled_median_hsv
