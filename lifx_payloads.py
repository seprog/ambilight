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
    (round(0x10000 * hsv_color[0]) % 0x10000).to_bytes(2, byteorder='little'),
    round(0xFFFF * hsv_color[1]).to_bytes(2, byteorder='little'),
    round(0xFFFF * hsv_color[2]).to_bytes(2, byteorder='little'),
    kelvin.to_bytes(2, byteorder='little'),
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
