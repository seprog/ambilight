import math
from time import time, sleep
from random import randint
from socket import socket, AF_INET, SOCK_DGRAM
from colorsys import rgb_to_hsv
from itertools import count, chain
from dataclasses import dataclass
from collections.abc import Generator
from concurrent.futures import ThreadPoolExecutor
from queue import Queue, Empty
from threading import Thread

import numpy as np
from scipy.ndimage import zoom

from lifx_devices import Light, Device, LIFX_PORT
from lifx_payloads import add_header


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

@dataclass
class Ambilight:
  frame_processors: list[FrameProcessor]
  lifx_sequence: int = 0
  lifx_source: int = randint(2, 2**32-1)

  @property
  def lights(self):
    return list(chain(*(
      frame_processor.lights
      for frame_processor
      in self.frame_processors
    )))

  def _send_payload(self,
    light: Device,
    payload: bytes
  ):
    self.sock.sendto(
      add_header(
        payload=payload,
        mac=light.mac,
        sequence=self.lifx_sequence,
        source=self.lifx_source
      ),
      (light.ip, LIFX_PORT)
    )
    self.lifx_sequence += 1

  def identify_lights(self,
    delay: float = 2
  ):
    print('Identifying lights...')
    for light in self.lights:
      light.set_power()
      light.set_color()

    for frame_processor, hue in zip(self.frame_processors, count(step=len(self.frame_processors)**-1)):
      print(frame_processor)
      for light in frame_processor.lights:
        light.set_color((hue,1,.1))
      sleep(delay)

      for light in frame_processor.lights:
        print(light)
        light.set_color((hue,1,1))
        sleep(delay)
        light.set_color((hue,1,.1))
      print()
      sleep(delay)

    for light in self.lights:
      light.set_color()

  def sync_lights(self,
    frame_generator: Generator[np.ndarray[tuple[int, int, int]]],
    fps: int | None = None,
    warn_threshold: float = 0.1,
    timeout: float = 10,
  ):
    with ThreadPoolExecutor() as executor:
      t, t0 = (time(), ) * 2

      for frame_id in count():
        result_queue = Queue(maxsize=1)

        def fetch_next_frame() -> None:
          try:
            result_queue.put(('value', next(frame_generator)))
          except StopIteration as stop:
            result_queue.put(('stop', stop))
          except BaseException as error:
            result_queue.put(('error', error))

        thread = Thread(target=fetch_next_frame, daemon=True)
        thread.start()

        try:
          status, payload = result_queue.get(timeout=timeout)
        except Empty:
          print(f'Frame generator did not yield for {timeout:.1f} seconds, stopping.')
          break

        thread.join(timeout=0)

        if status == 'stop':
          break
        if status == 'error':
          raise payload

        frame = payload
        sleep(max(0, (fps ** -1 - (time() - t)) * (1-warn_threshold)) if fps else 0)
        elapsed, t = time() - t, time()
        freq = elapsed ** -1 if elapsed else math.inf

        print(
          f'{t-t0:>6.0f}',
          f'{frame_id:>6d}',
          f'{freq:>5.2f}hz',
          f'({elapsed:.3f}s{elapsed - (fps ** -1 if fps else 0):+.3f}s)',
          end='\n' if fps and abs(freq / fps - 1) > warn_threshold else '\r'
        )

        for lights, hsv_color in executor.map(
          lambda fp: (fp.lights, rgb_to_hsv(*fp.ambilight_color(frame) / 255)),
          self.frame_processors
        ):
          for light in lights:
            light.set_color(
              hsv_color=hsv_color,
              transition_duration=fps ** -1 if fps else elapsed
            )

  def __enter__(self):
    self.sock = socket(AF_INET, SOCK_DGRAM)
    for light in self.lights:
      light._ambilight = self
      light.set_power()
    return self

  def __exit__(self,
    type,
    value,
    traceback
  ):
    for light in self.lights:
      light._ambilight = None
    self.sock.close()
