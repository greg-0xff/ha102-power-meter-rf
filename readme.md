# Decode Mieo HA102 power meter packets

## Overview
Reverse engineering of `Mieo HA102` power meter RF protocol. Not all fields were decoded, but the important ones are there.

## Signal characteristics 
* Frequency: 433.9 MHz
* Modulation: FSK_PCM
* short=120 µs
* long=120 µs
* tolerance=30 µs
* gap=9700 µs
* reset=10000 µs

A few recorded signals can be found in `samples` folder.


## Format description
Packets are sent at 433.9Mhz in bursts, up to 10 equal messages in each burst.
All values seem to be Big-Endian encoded.

* Transmitter - the meter itself, connected to power lines
* Receiver - the display unit

| #  | Field               | Size (bytes)  | Description                                                                                                                              |
|----|---------------------|---------------|------------------------------------------------------------------------------------------------------------------------------------------|
| 0  | 0x55555...          | up to 8 bytes | Preamble                                                                                                                                 |
| 1  | 0x3475              | 2 bytes       | Sync word                                                                                                                                |
| 2  | Device ID ?         | 2 bytes       | Was constant on my device (0xc58c)                                                                                                       |
| 3  | Sender ID ?         | 2 bytes       | Was 0000 for transmitter, FFFF for receiver in 'Search' mode                                                                             |
| 4  | Device Type         | 1 byte        | Was 0x80 for transmitter's packets, 0x10 in Receiver's packets                                                                           |
| 5  | Length ?            | 1 byte        | Observed value was always 0x0d, matching itself + 12 bytes following this field (including CRC). No other packet lengths observed so far |
| 6  | Unknown             | 1 byte        | Unknown, could be part of total consumption counter                                                                                      |
| 7  | Total Consumption   | 3 bytes       | Total consumption (Ah) in steps of 0.01A                                                                                                 |
| 8  | Unknown             | 2 bytes       | Unknown, could be part of current consumption counter                                                                                    |
| 9  | Current Consumption | 2 bytes       | Current consumption (A) in steps of 0.01A                                                                                                |
| 10 | battery status      | 1 byte        | 0x00 = OK, 0x01 = Low battery. Other bits unknown.                                                                                       |
| 11 | Unknown             | 1 byte        | Unknown, was always 00                                                                                                                   |
| 12 | CRC                 | 2 byte        | CRC16/SPI-FUJITSU                                                                                                                        |
| 13 | Unknown             | 1 byte        | Unknown                                                                                                                                  |
 
* Transmitter does not know the voltage, only current. Display unit calculates power using a user-entered voltage value
* No per-phase or per-clamp information is transmitted; all values are aggregate current
* Transmitter sends messages about once in a minute when in normal mode, and about once every 6 seconds when in search mode 
* When display is in search mode: 
  * Sender ID is set to FFFF
  * total and current consumption are always zero
  * battery status is always 00 even if its batteries are low

* Often the preamble is shifted one bit left or right, so if its AAAAA is worth trying to shift it and check if sync word matches
* When current consumption is zero, long runs of identical bits can cause occasional bit misalignment during demodulation. In such cases CRC verification may succeed only after a ±1 bit shift. This is likely a receiver/clock recovery issue, not intentional protocol behavior.
* CRC is calculated over fields [3-11], inclusive

## Examples
* 555555 3475 c58c 0000 80 0d 00 0027b1 0000 008e 01 00 0e24 0 - Transmitter packet
  * Total consumption: 10161 (0x0027b1) => 101.61 Ah
  * Current consumption: 142 (0x008e) => 1.42 A
  * Battery status: 01 => low battery
* 555555 3475 c58c ffff 10 0d 00 000000 0000 0000 00 00 6fd8 0 - Receiver packet in search mode
  * Sender ID: FFFF
  * Total consumption: 0 (0x000000) => 0.00 Ah (always)
  * Current consumption: 0 (0x0000) => 0.00 A (always)
  * Battery status: 00 => OK (always)

## Decoding using rtl_433
`rtl_433 -g 0 -f 433.9M -R 0 -F csv -X "n=meter_fsk,m=FSK_PCM,s=120,l=120,t=30,g=9700,r=10000" | python -u decode.py`

Simple python decoder is in `scripts` folder, it can be used to decode live signals from rtl_433 or from recorded samples.
