import sys
from dataclasses import dataclass

import numpy as np
import ffmpeg


@dataclass
class Capture:
  stream: ffmpeg.nodes.FilterableStream
  resolution: tuple[int, int]
  fps: int | None = None

  @property
  def bytes_per_frame(self):
    return self.resolution[0] * self.resolution[1] * 3

  def __enter__(self):
    if self.fps:
      self.stream = self.stream.video.filter('fps', fps=self.fps)

    out = ffmpeg.output(
      self.stream,
      'pipe:',
      format='rawvideo',
      pix_fmt='rgb24',
      s=f'{self.resolution[0]}x{self.resolution[1]}',
      an=None
    )

    print(' '.join(ffmpeg.compile(out, overwrite_output=True)), file=sys.stderr)
    self.process = ffmpeg.run_async(out, pipe_stdout=True, pipe_stderr=True)

    print(f'Starting screen capture loop ({self.resolution[0]}x{self.resolution[1]} @ {self.fps} FPS)...', file=sys.stderr)
    while True:
      if self.process.stdout:
        yield np \
          .frombuffer(self.process.stdout.read(self.bytes_per_frame), dtype=np.uint8) \
          .reshape((self.resolution[1], self.resolution[0], 3))

  def __exit__(self, type, value, traceback):
    self.process.terminate()
    try:
      self.process.wait(timeout=5)
    except ffmpeg.Error as e:
      print(f'FFmpeg process termination timed out or failed: {e}', file=sys.stderr)
      if self.process.poll() is None:
        print('Forcing FFmpeg process kill.', file=sys.stderr)
        self.process.kill()
    print('FFmpeg process terminated.', file=sys.stderr)
