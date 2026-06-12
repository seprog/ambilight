from dataclasses import dataclass

import numpy as np
from scipy.ndimage import zoom

from lifx_devices import Light


@dataclass
class FrameProcessor:
  lights: list[Light]
  mask: np.ndarray | None = None

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
            frame.shape[1] / self.mask.shape[1]
          )
        ),
        dtype=bool
      ).flatten()
    ]
    median = np.median(masked, axis=0)
    
    return median
