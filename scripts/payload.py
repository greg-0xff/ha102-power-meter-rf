import binascii
from dataclasses import dataclass
from typing import Optional, Union

SYNCWORD = '3475'
POWER_FACTOR = 0.01
VOLTS = 239  # nominal voltage for power calculation

@dataclass(repr=True)
class Message:
    raw: str  # the raw string as it was received
    adjusted: str  # with preamble fixed by shifting

    syncword: str  # first 4 nibbles
    receiver_id: str  # 4 nibbles
    sender_id: str  # 4 nibbles, FFFF when sent by display in search mode
    u1: str  # 2 nibbles, (80 when sent by TX, 10 when RX in search mode)
    u2: str  # 2 nibbles , looks like len (0d -> 13 -> 26 nibbles after 0d)
    u3: str  # 2 nibbles

    total_Ah: float  # 6 nibbles
    raw_total_Ah: str
    u4: str  # 4 nibbles
    current_A: float  # 4 nibbles
    raw_current_A: str
    battery: str  # 2 nibble
    u5: str  # 2 nibbles
    crc: str  # 4 nibbles
    u6: str  # 1 nibble, probably end

    crc_result: Union[bool, int]

    @staticmethod
    def from_str(raw: str) -> Optional["Message"]:
        adjusted = _adjust_preamble(raw)
        if adjusted is None:
            return None

        receiver_id = adjusted[4:8]
        sender_id = adjusted[8:12]
        u1 = adjusted[12:14]
        u2 = adjusted[14:16]
        u3 = adjusted[16:18]

        raw_total_Ah = adjusted[18:24]
        total_Ah = int(raw_total_Ah, 16) * POWER_FACTOR
        u4 = adjusted[24:28]
        raw_current_A = adjusted[28:32]
        current_A = int(raw_current_A, 16) * POWER_FACTOR
        battery_flag = adjusted[32:34]
        u5 = adjusted[34:36]
        crc = adjusted[36:40]
        u6 = adjusted[40]

        crc_check = Message.calc_crc(adjusted[8:36])
        crc_received = int(crc, 16)

        crc_result = False
        if crc_check == crc_received:
            crc_result = True
        elif crc_check == (crc_received << 1):
            crc_result = -1
        elif crc_check == (crc_received >> 1):
            crc_result = 1

        return Message(
            raw=raw,
            adjusted=adjusted,
            syncword=SYNCWORD,
            receiver_id=receiver_id,
            sender_id=sender_id,
            u1=u1,
            u2=u2,
            u3=u3,
            u4=u4,
            u5=u5,
            u6=u6,
            total_Ah=total_Ah,
            raw_total_Ah=raw_total_Ah,
            current_A=current_A,
            raw_current_A=raw_current_A,
            battery=battery_flag,
            crc=crc,
            crc_result=crc_result
        )

    def to_string(self) -> str:
        total_kWh = self.total_Ah * VOLTS / 1000
        current_kW = self.current_A * VOLTS / 1000
        return f"DS:{self.receiver_id} PM:{self.sender_id} " \
               f"u1:{self.u1} u2:{self.u2} u3:{self.u3} " \
               f"total:{self.raw_total_Ah}={total_kWh:.3f}, " \
               f"u4:{self.u4} " \
               f"current:{self.raw_current_A}={current_kW:.3f}, BAT_LOW: {self.battery} " \
               f"u5: {self.u5} crc:{self.crc} " \
               f"CRC: {self.crc_result}"

    @staticmethod
    def calc_crc(hex_string: str) -> int:
        # width=16  poly=0x1021  init=0x1d0f  refin=false  refout=false  xorout=0x0000  check=0xe5cc  residue=0x0000  name="CRC-16/SPI-FUJITSU"
        data = bytes.fromhex(hex_string)
        return binascii.crc_hqx(data, 0x1D0F)


def _shift_left(msg: str, bits: int = 1) -> str:
    n = int(msg, 16)
    n2 = (n << bits)
    width = len(msg)
    return f"{n2:0{width}x}"[1:]


def _shift_right(msg: str, bits: int = 1) -> str:
    n = int(msg, 16)
    n2 = (n >> bits)
    width = len(msg)
    return f"{n2:0{width}x}"[1:]


def _adjust_preamble(message: str) -> Optional[str]:
    if message.startswith(SYNCWORD):
        return message

    message = message[4:]  # first nibbles of preamble are often garbled

    if message.startswith('55'):
        stripped = message.lstrip('55')
        if stripped.startswith(SYNCWORD):
            return stripped

    if message.startswith('aa'):
        shifted_left = _shift_left(message).lstrip('55')
        if shifted_left.startswith(SYNCWORD):
            return shifted_left

        shifted_right = _shift_right(message).lstrip('55')
        if shifted_right.startswith(SYNCWORD):
            return shifted_right

    return None


