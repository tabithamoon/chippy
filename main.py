from src import display
import pygame
import sys

running = False

def load_rom(path, mem):
    try:
        with open(path, "rb") as f:
            rom = bytearray(f.read())           # Read file bytes into variable
            first_byte = 0x200                    # Establish beginning of ROM in memory space (0x200 by default in CHIP-8)
            last_byte = 0x200 + len(rom)          # Calculate end of bytestream 
            mem[first_byte:last_byte] = rom     # Replace bytes in memory with ROM file

        return True                 # Return True if success
    except IOError:
        return False                # Return False if we ran into a problem

def main():
    # Feel like the first thing to do is initialize memory, so let's do that
    main_memory = bytearray(4096)
    
    # Let's also get the registers out of the way
    vx_registers = bytearray(16)
    stack_pointer = bytes(1)
    i_register = bytes(2)
    pcounter = bytes(2)

    # Initializing the stack
    stack = [bytes(2)]*16

    # Try to load ROM into main memory at 0x200
    load_rom(sys.argv[1], main_memory)

    # Fire up our display
    screen = display.initialize()

    # Set up our clock
    clock = pygame.time.Clock()
    clock.tick(10) #TODO: check ideal framerate

    # Set the program counter to the default entry point
    pcounter = bytes(main_memory[0x200:0x202]) #TODO: why do i need to use 0x202 here to read the first two bytes? theoretically this would return 3 bytes but it doesn't...

    print(pcounter)

    # The interpreter is now running!
    # This variable keeps track if we're supposed to stop.
    running = True

    # The main logic loop
    while running:
        # Allow the user to quit by pressing the close button
        # Kind of important
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        # Main interpreter logic goes here!

        # Flip and display at end of execution loop
        display.flip(screen)

if __name__ == "__main__":
    main()