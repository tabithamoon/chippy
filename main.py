from src import display
from src import file
import pygame
import sys

running = False

def main():
    # Feel like the first thing to do is initialize memory, so let's do that
    main_memory = [0]*4096
    
    # Let's also get the registers out of the way
    vx_registers = [0]*16
    stack_pointer = 0
    i_register = 0
    pcounter = 0

    # Initializing the stack
    stack = [0]*16

    # Try to load ROM into main memory at 0x200
    file.load_rom(sys.argv[1], main_memory)

    # Fire up our display
    screen = display.initialize()

    # Set up our clock
    clock = pygame.time.Clock()
    clock.tick(10) #TODO: check ideal framerate

    # Set the program counter to the default entry point
    pcounter = 0x200

    # The interpreter is now running!
    # This variable keeps track if we're supposed to stop.
    running = True

    # The main logic loop
    while running:

        # Main interpreter logic goes here!
        # Get current instruction at program counter
        curr_instr = (main_memory[pcounter] << 8) + main_memory[pcounter + 1]
        print(curr_instr)

        match curr_instr:
            # CLS - Clear the display
            case 0x00E0:
                display.cls(screen)
                pcounter += 2
            
            # RET - Return from a subroutine
            case 0x00EE:
                pcounter = stack[stack_pointer]
                stack_pointer -= 1
            
            # JP addr - Jump to location 0x1nnn
            case _ if curr_instr & 0xF000 == 0x1000:
                pcounter = curr_instr & 0x0FFF

            # CALL addr - Call subroutine at 0x2nnn
            case _ if curr_instr & 0xF000 == 0x2000:
                stack[stack_pointer] = pcounter
                stack_pointer += 1
                pcounter = curr_instr & 0x0FFF

            # SE Vx, byte - (0x3xkk) Skip next instruction if Vx = kk
            case _ if curr_instr & 0xF000 == 0x3000:
                reg = (curr_instr & 0x0F00) >> 8
                val = curr_instr & 0x00FF
                if (vx_registers[reg] == val):
                    pcounter += 4
                else:
                    pcounter += 2

            # SNE Vx, byte - (0x4xkk) Skip next instruction if Vx != kk
            case _ if curr_instr & 0xF000 == 0x4000:
                reg = (curr_instr & 0x0F00) >> 8
                if (vx_registers[reg] != (curr_instr & 0x00FF)):
                    pcounter += 4
                else:
                    pcounter += 2

            # SE Vx, Vy - (0x5xy0) Skip next instruction if Vx = Vy
            case _ if curr_instr & 0xF000 == 0x5000:
                vx = (curr_instr & 0x0F00) >> 8
                vy = (curr_instr & 0x00F0) >> 4
                if (vx_registers[vx] == vx_registers[vy]):
                    pcounter += 4
                else:
                    pcounter += 2

            # LD Vx, byte - (0x6xkk) Set Vx = kk
            case _ if curr_instr & 0xF000 == 0x6000:
                reg = (curr_instr & 0x0F00) >> 8
                vx_registers[reg] = (curr_instr & 0x00FF)
                pcounter += 2

            # ADD Vx, byte - (0x7xkk) Adds the value kk to the value of register Vx, then stores the result in Vx
            case _ if curr_instr & 0xF000 == 0x7000:
                reg = (curr_instr & 0x0F00) >> 8
                add = curr_instr & 0x00FF
                res = vx_registers[reg] + add

                # Overflow and roll back around if > 0xFF
                if (res > 0xFF): res -= 0xFF

                vx_registers[reg] = res
                pcounter += 2

            # OR Vx, Vy - (0x8xy1) Set Vx = Vx OR Vy
            case _ if curr_instr & 0xF00F == 0x8001:
                vx = (curr_instr & 0x0F00) >> 8
                vy = (curr_instr & 0x00F0) >> 4

                vx_registers[vx] = vx_registers[vx] | vx_registers[vy]
                pcounter += 2

            # AND Vx, Vy - (0x8xy2) Set Vx = Vx AND Vy
            case _ if curr_instr & 0xF00F == 0x8002:
                vx = (curr_instr & 0x0F00) >> 8
                vy = (curr_instr & 0x00F0) >> 4

                vx_registers[vx] = vx_registers[vx] & vx_registers[vy]
                pcounter += 2

            # XOR Vx, Vy - (0x8xy3) Set Vx = Vx XOR Vy
            case _ if curr_instr & 0xF00F == 0x8003:
                vx = (curr_instr & 0x0F00) >> 8
                vy = (curr_instr & 0x00F0) >> 4

                vx_registers[vx] = vx_registers[vx] ^ vx_registers[vy]
                pcounter += 2
            
            # ADD Vx, Vy - (0x8xy4) Set Vx = Vx + Vy, set VF = carry
            case _ if curr_instr & 0xF00F == 0x8004:
                vx = (curr_instr & 0x0F00) >> 8
                vy = (curr_instr & 0x00F0) >> 4

                res = vx_registers[vx] + vx_registers[vy]

                if (res > 0xFF):
                    vx_registers[0xF] = 1
                    vx_registers[vx] = (res & 0x00FF)
                else:
                    vx_registers[vx] = res

            # SUB Vx, Vy - (0x8xy5) Set Vx = Vx - Vy, set VF = NOT borrow
            case _ if curr_instr & 0xF00F == 0x8005:
                vx = (curr_instr & 0x0F00) >> 8
                vy = (curr_instr & 0x00F0) >> 4
                if (vx_registers[vx] > vx_registers[vy]):
                    # No underflow, subtract normally
                    vx_registers[0xF] = 1
                    vx_registers[vx] = vx_registers[vx] - vx_registers[vy]
                else:
                    # Underflow, do a little cheaty cheat >:3
                    vx_registers[0xF] = 0
                    vx_registers[vx] = (vx_registers[vx] + 0xFF) - vx_registers[vy]
                    
                pcounter += 2

            # SHR Vx{, Vy} - (0x8xy6) Set Vx = Vx SHR 1
            case _ if curr_instr & 0xF00F == 0x8006:
                vx = (curr_instr & 0x0F00) >> 8

                if ((vx_registers[vx] & 0x01) == 0x01):
                    vx_registers[0xF] = 1
                else:
                    vx_registers[0xF] = 0
                
                res = vx_registers[vx] // 2
                vx_registers[vx] = res
                pcounter += 2

            # SUBN Vx, Vy - (0x8xy7) Set Vx = Vy - Vx, set VF = NOT borrow
            case _ if curr_instr & 0xF00F == 0x8007:
                vx = (curr_instr & 0x0F00) >> 8
                vy = (curr_instr & 0x00F0) >> 4

                if (vx_registers[vy] > vx_registers[vx]):
                    vx_registers[0xF] = 1
                    vx_registers[vx] = vx_registers[vy] - vx_registers[vx]
                else:
                    vx_registers[0xF] = 0
                    vx_registers[vx] = (vx_registers[vy] + 0xFF) - vx_registers[vx]

                pcounter += 2
            
            # SHL Vx{, Vy} - (0x8xyE) Set Vx = Vx SHL 1
            case _ if curr_instr & 0xF00F == 0x800E:
                vx = (curr_instr & 0x0F00) >> 8

                if ((vx_registers[vx] & 0x80) == 0x80):
                    vx_registers[0xF] = 1
                else:
                    vx_registers[0xF] = 0
                
                res = vx_registers[vx] * 2
                if (res > 0xFF): res -= 0xFF
                vx_registers[vx] = res
                pcounter += 2

            # LD I, addr - Set I = 0xAnnn
            case _ if curr_instr & 0xF000 == 0xA000:
                i_register = curr_instr & 0x0FFF
                pcounter += 2

            # LD B, Vx - (0xFx33) Store BCD representation of Vx in memory locations I, I+1, and I+2
            case _ if curr_instr & 0xF0FF == 0xF033:
                vx = ((curr_instr & 0x0F00) >> 8)
                val = vx_registers[vx]
                start = i_register
                curr = start

                for num in map(int, val):
                    main_memory[curr] = num
                    curr += curr
                
                pcounter += 2

            # LD [I], Vx - (0xFx55) Store registers V0 through Vx in memory starting at location I
            case _ if curr_instr & 0xF0FF == 0xF055:
                vx = ((curr_instr & 0x0F00) >> 8) + 1 # Working around strange python behavior
                start = i_register
                end = start + vx 

                main_memory[start:end] = vx_registers[0x0:vx]
                pcounter += 2

            # LD Vx, [I] - (0xFx65) Read registers V0 through Vx from memory starting at location I
            case _ if curr_instr & 0xF0FF == 0xF065:
                vx = ((curr_instr & 0x0F00) >> 8) + 1 # Working around strange python behavior
                start = i_register
                end = start + vx

                vx_registers[0x0:vx] = main_memory[start:end]
                pcounter += 2

        # Allow the user to quit by pressing the close button, kind of important
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False


        # Flip and display at end of execution loop
        display.flip(screen)

if __name__ == "__main__":
    main()