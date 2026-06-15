import yaml
import numpy as np

from ambilight import FrameProcessor
from lifx_devices import Light, Zone


def load_ambilight_config(path: str):
  with open(path, 'r', encoding='utf-8') as file:
    config = yaml.safe_load(file)
  
  ambilight_config = config['ambilight']

  frame_processors = []
  for frame_processor_config in ambilight_config['frame_processors']:
    lights = []
    for light_config in frame_processor_config['lights']:
      if light_config['type'] == 'light':
        lights.append(
          Light(
            light_config['ip'],
            light_config['mac'],
          )
        )
      elif light_config['type'] == 'zone':
        lights.append(
          Zone(
            light_config['ip'],
            light_config['mac'],
            light_config['start_index'],
            light_config.get('end_index'),
          )
        )
      else:
        raise ValueError(f'Unknown light type: {light_config['type']}')

    frame_processors.append(
      FrameProcessor(
        lights=lights,
        mask=None if frame_processor_config.get('mask') is None else np.array(frame_processor_config['mask']),
        saturation_exp=frame_processor_config.get('saturation_exp', 1),
        saturation_factor=frame_processor_config.get('saturation_factor', 1),
        saturation_clip_range=tuple(frame_processor_config.get('saturation_clip_range', (0, 1))),
        saturation_lerp_range=tuple(frame_processor_config.get('saturation_lerp_range', (0, 1))),
        value_exp=frame_processor_config.get('value_exp', 1),
        value_factor=frame_processor_config.get('value_factor', 1),
        value_clip_range=tuple(frame_processor_config.get('value_clip_range', (0, 1))),
        value_lerp_range=tuple(frame_processor_config.get('value_lerp_range', (0, 1))),
      )
    )

  return {
    'frame_processors': frame_processors,
  }
