from socket import socket, AF_INET, SOCK_DGRAM
from dataclasses import dataclass

from lifx_payloads import add_header, payload_21, payload_38, payload_102, payload_117


@dataclass
class Device:
  ip: str
  mac: str
  port: int = 56700

  def _send_payload(self,
    payload: bytes
  ):
    if self.ambilight:
      self.ambilight._send_payload(self, payload)
    else:
      socket(AF_INET, SOCK_DGRAM).sendto(
        add_header(
          payload=payload,
          mac=self.mac,
        ),
        (self.ip, self.port)
      )

  def set_power(self,
    on: bool = True
  ):
    self._send_payload(
      payload=payload_21(
        level=on
      )
    )

  def reboot(self):
    self._send_payload(
      payload=payload_38()
    )

@dataclass
class Light(Device):
  def set_color(self,
    hsv_color: tuple[float, float, float] = (0, 0, 1),
    kelvin: int = 3500,
    transition_duration: float = 0
  ):
    self._send_payload(
      payload=payload_102(
        hsv_color=hsv_color,
        kelvin=kelvin,
        duration=transition_duration
      )
    )

  def set_light_power(self,
    on: bool = True,
    transition_duration: float = 0
  ):
    self._send_payload(
      payload=payload_117(
        level=on,
        duration=transition_duration
      )
    )
