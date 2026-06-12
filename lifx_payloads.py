'''
Documentation:
  - https://lan.developer.lifx.com/docs
'''

from binascii import unhexlify


def add_header(
  payload: bytes,
  mac: str,
  sequence: int = 0,
  source: int = 2,
  ack_required: bool = False,
  res_required: bool = False,
  tagged: bool = False
):
  return b''.join((
    (36 + len(payload)).to_bytes(2, byteorder='little'),
    (5120 + (tagged << 13)).to_bytes(2, byteorder='little'),
    source.to_bytes(4, byteorder='little'),
    unhexlify(mac.replace(':', '')),
    b'\x00' * 8,
    (res_required + (ack_required << 1)).to_bytes(1),
    (sequence % 0x100).to_bytes(1),
    b'\x00' * 8,
    payload
  ))

def _hsbk_struct(
  hue: float,
  saturation: float,
  value: float,
  kelvin: int,
): 
  return b''.join((
    (round(0x10000 * hue) % 0x10000).to_bytes(2, byteorder='little'),
    round(0xFFFF * saturation).to_bytes(2, byteorder='little'),
    round(0xFFFF * value).to_bytes(2, byteorder='little'),
    kelvin.to_bytes(2, byteorder='little')
  ))


# https://lan.developer.lifx.com/docs/changing-a-device#setpower---packet-21
def payload_21(
  level: bool
):
  return b''.join((
    (21).to_bytes(2, byteorder='little'),
    b'\x00' * 2,
    b'\xFF\xFF' if level else b'\x00\x00'
  ))

# https://lan.developer.lifx.com/docs/changing-a-device#setreboot---packet-38
def payload_38():
  return b''.join((
    (38).to_bytes(2, byteorder='little'),
    b'\x00' * 2
  ))

# https://lan.developer.lifx.com/docs/changing-a-device#setcolor---packet-102
def payload_102(
  hsv_color: tuple[float, float, float],
  kelvin: int,
  duration: float
):
  return b''.join((
    (102).to_bytes(2, byteorder='little'),
    b'\x00' * 3,
    _hsbk_struct(*hsv_color, kelvin),
    round(duration * 1_000).to_bytes(4, byteorder='little')
  ))

# https://lan.developer.lifx.com/docs/changing-a-device#setlightpower---packet-117
def payload_117(
  level: bool,
  duration: float
):
  return b''.join((
    (21).to_bytes(2, byteorder='little'),
    b'\x00' * 2,
    b'\xFF\xFF' if level else b'\x00\x00',
    round(duration * 1_000).to_bytes(4, byteorder='little')
  ))

# https://lan.developer.lifx.com/docs/changing-a-device#setcolorzones---packet-501
def payload_501(
  hsv_color: tuple[float, float, float],
  kelvin: int,
  duration: float,
  start_index: int,
  end_index: int,
  apply: int = 1
):
  return b''.join((
    (501).to_bytes(2, byteorder='little'),
    b'\x00' * 2,
    start_index.to_bytes(2, byteorder='little'),
    end_index.to_bytes(2, byteorder='little'),
    _hsbk_struct(*hsv_color, kelvin),
    round(duration * 1_000).to_bytes(4, byteorder='little'),
    apply.to_bytes(1, byteorder='little')
  ))

# https://lan.developer.lifx.com/docs/changing-a-device#setextendedcolorzones---packet-510
def payload_510(
  start_index: int,
  hsvk_colors: list[tuple[float, float, float, int]],
  duration: float,
  apply: int = 1,
):
  return b''.join((
    (510).to_bytes(2, byteorder='little'),
    b'\x00' * 2,
    round(duration * 1_000).to_bytes(4, byteorder='little'),
    apply.to_bytes(1, byteorder='little'),
    start_index.to_bytes(2, byteorder='little'),
    len(hsvk_colors).to_bytes(1, byteorder='little'),
    b''.join(
      _hsbk_struct(*hsvk_color)
      for hsvk_color in hsvk_colors
   )
  ))
