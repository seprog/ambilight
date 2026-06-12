from argparse import ArgumentParser

import numpy as np
import ffmpeg

from capture import Capture
from ambilight import Ambilight, FrameProcessor
from lifx_devices import Light, Zone


def main():
  parser = ArgumentParser()

  # Input Mode Selection
  input_group = parser.add_mutually_exclusive_group(required=True)
  input_group.add_argument(
    '--stream', type=str,
    help='RTMP stream URL (e.g., rtmp://localhost/live/my_stream)'
  )
  input_group.add_argument(
    '--linux-wayland', action='store_true',
    help='Capture Linux Wayland display via PipeWire (requires system dialog permission).'
  )
  input_group.add_argument(
    '--linux-x11', type=str, nargs='?', const=':0.0',
    help='Capture Linux X11 display. Provide display ID (e.g., :0.0), or leave empty for default.'
  )
  input_group.add_argument(
    '--windows-screen', type=str, nargs='?', const='desktop',
    help='Capture Windows screen. Provide window title, or leave empty for "desktop".'
  )

  # Specific Input Arguments (depending on mode)
  parser.add_argument(
    '--input-width', type=int,
    help='Input resolution (width) for screen grabs (e.g., for 1920x1080 use 1920). Required for --windows-screen, --linux-x11 if not capturing full screen.'
  )
  parser.add_argument(
    '--input-height', type=int,
    help='Input resolution (height) for screen grabs (e.g., for 1920x1080 use 1080). Required for --windows-screen, --linux-x11 if not capturing full screen.'
  )
  parser.add_argument(
    '--input-offset-x', type=int, default=0,
    help='X-offset for screen capture regions (Windows/X11).'
  )
  parser.add_argument(
    '--input-offset-y', type=int, default=0,
    help='Y-offset for screen capture regions (Windows/X11).'
  )

  # General Output Arguments
  parser.add_argument(
    '--output-width', type=int, default=640,
    help=f'Output width for pixel data processing (downscaled from source).'
  )
  parser.add_argument(
    '--output-height', type=int, default=360,
    help=f'Output height for pixel data processing (downscaled from source).'
  )
  parser.add_argument(
    '--output-fps', type=int,
    help=f'Output frames per second for pixel data processing.'
  )

  # Other Arguments
  parser.add_argument(
    '--identify-lights', type=float, default=0,
    help='Identify lights by turning them on and cycling through colors. Disable if set to 0.'
  )

  args = parser.parse_args()

  stream: ffmpeg.nodes.FilterableStream
  if args.stream:
    stream = ffmpeg.input(
      args.stream
    )
  elif args.linux_wayland:
    stream = ffmpeg.input(
      '0',
      f='pipewire'
    )
  elif args.linux_x11:
    if not args.input_width or not args.input_height:
      raise ValueError('input_width and input_height are required for "linux-x11"')
    stream = ffmpeg.input(
      f'{args.linux_x11}+{args.input_offset_x},{args.input_offset_y}',
      f='x11grab',
      video_size=(args.input_width, args.input_height)
    )
  elif args.windows_screen:
    if not args.input_width or not args.input_height:
      raise ValueError('input_width and input_height are required for "windows-screen"')
    stream = ffmpeg.input(
      args.windows_screen,
      f='gdigrab',
      video_size=(args.input_width, args.input_height),
      offset_x=args.input_offset_x,
      offset_y=args.input_offset_y
    )
  else:
    raise ValueError('No source was selected.')

  with (
    Ambilight(
      frame_processors=[
        FrameProcessor(
          lights=[
            Light('192.168.178.31', 'D0:73:D5:2E:14:A7'),
            Light('192.168.178.32', 'D0:73:D5:2E:95:B1'),
            # Light('192.168.178.30', 'D0:73:D5:2E:85:58'),
            # Light('192.168.178.33', 'D0:73:D5:2E:12:B7'),
          ]
        ),
        FrameProcessor(
          lights=[
            Zone('192.168.178.29', 'D0:73:D5:43:96:16', 0),
            # Zone('192.168.178.39', 'D0:73:D5:43:84:82', 0, 1),
            # Zone('192.168.178.38', 'D0:73:D5:43:E0:90', 0, 1),
          ],
          mask=np.array([ [ 1, 0, 0, 0, 0, 0, 0 ] ])
        ),
        FrameProcessor(
          lights=[
            Zone('192.168.178.29', 'D0:73:D5:43:96:16', 1),
            # Zone('192.168.178.39', 'D0:73:D5:43:84:82', 2, 3),
            # Zone('192.168.178.38', 'D0:73:D5:43:E0:90', 2, 3),
          ],
          mask=np.array([ [ 0, 1, 0, 0, 0, 0, 0 ] ])
        ),
        FrameProcessor(
          lights=[
            Zone('192.168.178.29', 'D0:73:D5:43:96:16', 2),
            # Zone('192.168.178.39', 'D0:73:D5:43:84:82', 4, 5),
            # Zone('192.168.178.38', 'D0:73:D5:43:E0:90', 4, 5),
          ],
          mask=np.array([ [ 0, 0, 1, 0, 0, 0, 0 ] ])
        ),
        FrameProcessor(
          lights=[
            Zone('192.168.178.29', 'D0:73:D5:43:96:16', 3),
            # Zone('192.168.178.39', 'D0:73:D5:43:84:82', 6, 9),
            # Zone('192.168.178.38', 'D0:73:D5:43:E0:90', 6, 9),
          ],
          mask=np.array([ [ 0, 0, 0, 1, 0, 0, 0 ] ])
        ),
        FrameProcessor(
          lights=[
            Zone('192.168.178.29', 'D0:73:D5:43:96:16', 4),
            # Zone('192.168.178.39', 'D0:73:D5:43:84:82', 10, 11),
            # Zone('192.168.178.38', 'D0:73:D5:43:E0:90', 10, 11),
          ],
          mask=np.array([ [ 0, 0, 0, 0, 1, 0, 0 ] ])
        ),
        FrameProcessor(
          lights=[
            Zone('192.168.178.29', 'D0:73:D5:43:96:16', 5),
            # Zone('192.168.178.39', 'D0:73:D5:43:84:82', 12, 13),
            # Zone('192.168.178.38', 'D0:73:D5:43:E0:90', 12, 13),
          ],
          mask=np.array([ [ 0, 0, 0, 0, 0, 1, 0 ] ])
        ),
        FrameProcessor(
          lights=[
            Zone('192.168.178.29', 'D0:73:D5:43:96:16', 6),
            # Zone('192.168.178.39', 'D0:73:D5:43:84:82', 14, 15),
            # Zone('192.168.178.38', 'D0:73:D5:43:E0:90', 14, 15),
          ],
          mask=np.array([ [ 0, 0, 0, 0, 0, 0, 1 ] ])
        ),
      ]
    ) as ambilight,
    Capture(
      stream=stream,
      resolution=(args.output_width, args.output_height),
      fps=args.output_fps
    ) as frame_generator
  ):
    if args.identify_lights:
      ambilight.identify_lights(args.identify_lights)
    ambilight.sync_lights(
      frame_generator=frame_generator,
      fps=args.output_fps
    )

if __name__ == '__main__':
  main()
