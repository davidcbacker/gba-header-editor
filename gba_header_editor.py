#!/usr/bin/env python3
#
# Modify header values of a GBA ROM

import sys
import shutil
from pathlib import Path

if len(sys.argv) != 4:
    print(f"Usage: {sys.argv[0]} ROM_FILE TITLE GAME_CODE")
    sys.exit(1)

rom = Path(sys.argv[1])
title = sys.argv[2]
game_code = sys.argv[3]
game_code = game_code.upper()

if not rom.is_file():
    sys.exit("Error: ROM file not found")

data = bytearray(rom.read_bytes())

if len(data) < 0xC0:
    sys.exit("Error: File is too small to contain a GBA header")

if len(title.encode("ascii")) > 12:
    sys.exit("Error: Game title must be at most 12 ASCII characters")

if len(game_code) != 4 or not game_code.isascii():
    sys.exit("Error: Game code must be exactly 4 ASCII characters")

region_char = game_code[3].upper()

match region_char:
    case "E":
        region_code = "USA"
    case "P":
        region_code = "Europe"
    case "J":
        region_code = "Japan"
    case "D":
        region_code = "Germany"
    case "F":
        region_code = "France"
    case "I":
        region_code = "Italy"
    case "S":
        region_code = "Spain"
    case _:
        region_code = "UNKNOWN"

print(f"Game code {game_code} implies region {region_code}.")

# Backup original ROM
backup = rom.with_suffix(rom.suffix + ".bak")
shutil.copy2(rom, backup)

# Field	ROM offset	Length
#Game title       0xA0    12 bytes
#Game code        0xAC     4 bytes
#Maker code       0xB0     2 bytes
#Fixed value      0xB2     1 byte
#Unit code        0xB3     1 byte
#Device type      0xB4     1 byte
#Header checksum  0xBDi    1 byte

# Write title (offset 0xA0, 12 bytes)
data[0xA0:0xAC] = title.encode("ascii").ljust(12, b"\x00")

# Write game code (offset 0xAC, 4 bytes)
data[0xAC:0xB0] = game_code.encode("ascii")

# Recalculate header checksum
checksum = (-(sum(data[0xA0:0xBD]) + 0x19)) & 0xFF
data[0xBD] = checksum

# Save patched ROM
rom.write_bytes(data)

print(f"ROM patched: {rom}")
print(f"Backup:      {backup}")
print(f"Title:       {title}")
print(f"Game code:   {game_code}")
print(f"Checksum:    {checksum:02X}")
