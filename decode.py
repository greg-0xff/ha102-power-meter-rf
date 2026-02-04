import re
import sys
from dataclasses import dataclass
from typing import Optional

from payload import Message

@dataclass
class RawString:
    date: str
    length: int
    nibbles: str


regex = re.compile(r"{(?P<len>\d+?)}(?P<nibbles>.+?),")


def decode_csv_string(string: str) -> Optional[RawString]:
    try:
        fields = string.split(",")
        date = fields[0]
        result = regex.search(string)
        if result is None:
            return None

        length = int(result.group("len"))
        nibbles = result.group("nibbles")
        return RawString(date=date, length=length, nibbles=nibbles)
    except Exception as e:
        print(f"!{e} for string '{string}'")
        return None


def decode_message(raw: RawString) -> Optional[Message]:
    if 190 < raw.length < 220:
        return Message.from_str(raw.nibbles)
    return None


prev_output_string = ""


def print_measurement_if_valid(msg: Message, date: str) -> None:
    global prev_output_string

    if msg.crc_result is False:
        return

    output_string = f"{date}: {msg.to_string()}"
    if output_string != prev_output_string:
        print(output_string)

    prev_output_string = output_string


if __name__ == "__main__":
    for line in sys.stdin:
        line = line.strip()
        try:
            raw_string = decode_csv_string(line)
            if raw_string is None:
                continue
            m = decoded_message = decode_message(raw_string)
            if decoded_message:
                print_measurement_if_valid(decoded_message, raw_string.date)

        except Exception as e:
            print(f"! {e} on string '{line}'")
