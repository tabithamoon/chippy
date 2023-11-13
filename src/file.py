def load_rom(path, mem):
    try:
        with open(path, "rb") as f:
            rom = bytearray(f.read())             # Read file bytes into variable
            first_byte = 0x200                    # Establish beginning of ROM in memory space (0x200 by default in CHIP-8)
            last_byte = 0x200 + len(rom)          # Calculate end of bytestream 
            mem[first_byte:last_byte] = rom       # Replace bytes in memory with ROM file
        return True                               # Return True if success
    except IOError:
        return False                              # Return False if we ran into a problem