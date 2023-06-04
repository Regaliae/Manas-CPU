""" 
Manas-CPU microassembler for assembling the microprogram 
    - Microinstruction 16-bits 
    - For custom 16-bit Manas-CPU architecture
"""
"""
Copyright (C) 2023 David Jøssang

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

NOTHING = 0b0000000000000000

Special_Instructions = {
    "Cpy_ROM":     0b1000000000000000, # Copy rom and enable direct access from counter to address register | bit 16
    "Chk_Prg_End": 0b0100000000000000, # Check for program end in ROM, jump to 3 in microinstruction counter | bit 15
    "JZ":          0b0010000000000000, # Jump to address if zero flag set | bit 14
    "EO":          0b1000000000,       # Evaluate ALU operation, addition if not specified otherwise | bit 10
    "CI":          0b100,              # Increment/Enable program counter | bit 3
    "EI":          0b010,              # End instruction                  | bit 2
    "ST":          0b001               # Stop clock                       | bit 1
}

ALU_Instructions = { # bits 13-11
    "SU":0b0010000000000, # Enable subtract mode
    "MU":0b0100000000000, # Enable multiplication mode
    "SL":0b0110000000000, # Enable bitshift left mode
    "SR":0b1000000000000  # Enable bitshift right mode
}

Read_Instructions = { # bits 9-7
    "RA":0b001000000, #Read A register to bus
    "RB":0b010000000, #Read B register to bus
    "RC":0b011000000, #Read C register to bus
    "RM":0b100000000, #Read from memory at address specified in address register to bus
    "IR":0b101000000, #Read lowest 11bits of instruction register to bus
    "CR":0b110000000  #Read program counter to bus
}

Write_Instructions = { # bits 6-4
    "WA":0b001000, # Write from bus to A register
    "WB":0b010000, # Write from bus to B register
    "WC":0b011000, # Write from bus to C register
    "WM":0b100000, # Write from bus to memory at address specified in address register
    "AW":0b101000, # Write from bus to address register
    "IW":0b110000, # Write from bus to instruction register
    "CW":0b111000  # Write from bus to program counter | acts as a jump instruction
}

Microprogram = [[hex(0x0000) for i in range(16)] for i in range(0x1f)]
# Have them 8 bits for each list, because address and counter just look
FETCH = (f'{(Read_Instructions["CR"] | Write_Instructions["AW"]):04x}', 
         f'{(Read_Instructions["RM"] | Write_Instructions["IW"] | Special_Instructions["CI"]):04x}', 
         f'{(Special_Instructions["EI"]):04x}')
Assembly_Instructions = {
    "Copy Program ROM": [
        f'{(Special_Instructions["Cpy_ROM"] | Write_Instructions["AW"]):04x}',
        f'{(Special_Instructions["Cpy_ROM"] | Special_Instructions["Chk_Prg_End"]):04x}',
        f'{(Special_Instructions["Cpy_ROM"] | Special_Instructions["CI"] | Write_Instructions["WM"]):04x}',
        f'{(Special_Instructions["EI"]):04x}',
        FETCH[0], FETCH[1], FETCH[2]
    ],
    "LDA": [ # Load data from memory to A register | 00001 | LDA <addr> 11-bits
        f'{(Read_Instructions["IR"] | Write_Instructions["AW"]):04x}',
        f'{(Read_Instructions["RM"] | Write_Instructions["WA"]):04x}',
        FETCH[0], FETCH[1], FETCH[2]
    ],
    "LDB": [ # Load data from memory to B register | 00010 | LDB <addr> 11-bits
        f'{(Read_Instructions["IR"] | Write_Instructions["AW"]):04x}',
        f'{(Read_Instructions["RM"] | Write_Instructions["WB"]):04x}',
        FETCH[0], FETCH[1], FETCH[2]
    ],
    "LDC": [ # Load data from memory to C register | 00011 | LDC <addr> 11-bits
        f'{(Read_Instructions["IR"] | Write_Instructions["AW"]):04x}',
        f'{(Read_Instructions["RM"] | Write_Instructions["WC"]):04x}',
        FETCH[0], FETCH[1], FETCH[2]
    ],
    "LDIA": [ # Load data immediately from instruction to A register | 00100 | LDIA <value> 11-bits
        f'{(Read_Instructions["IR"] | Write_Instructions["WA"]):04x}',
        FETCH[0], FETCH[1], FETCH[2]
    ],
    "LDIB": [ # Load data immediately from instruction to B register | 00101 | LDIB <value> 11-bits
        f'{(Read_Instructions["IR"] | Write_Instructions["WB"]):04x}',
        FETCH[0], FETCH[1], FETCH[2]
    ],
    "LDIC": [ # Load data immediately from instruction to C register | 00110 | LDIC <value> 11-bits
        f'{(Read_Instructions["IR"] | Write_Instructions["WC"]):04x}',
        FETCH[0], FETCH[1], FETCH[2]
    ],
    "STA": [ # Store A reg into <addr> in memory | 00111
        f'{(Read_Instructions["IR"] | Write_Instructions["AW"]):04x}',
        f'{(Read_Instructions["RA"] | Write_Instructions["WM"]):04x}',
        FETCH[0], FETCH[1], FETCH[2]
    ],
    "STB": [ # Store B reg into <addr> in memory | 01000
        f'{(Read_Instructions["IR"] | Write_Instructions["AW"]):04x}',
        f'{(Read_Instructions["RB"] | Write_Instructions["WM"]):04x}',
        FETCH[0], FETCH[1], FETCH[2]
    ],
    "STC": [ # Store C reg into <addr> in memory | 01001
        f'{(Read_Instructions["IR"] | Write_Instructions["AW"]):04x}',
        f'{(Read_Instructions["RC"] | Write_Instructions["WM"]):04x}',
        FETCH[0], FETCH[1], FETCH[2]
    ],

    "ADD": [ # Add register B to A, and store result in register A | 01010
        f'{(Special_Instructions["EO"] | Write_Instructions["WA"]):04x}',
        FETCH[0], FETCH[1], FETCH[2]
    ],
    "SUB": [ # 01011 : Subtract register B from A, and store result in A
        f'{(ALU_Instructions["SU"] | Special_Instructions["EO"] | Write_Instructions["WA"]):04x}',
        FETCH[0], FETCH[1], FETCH[2]
    ],
    "MULT": [ # 01100 : Multiply register B with A, store result in A
        f'{(ALU_Instructions["MU"] | Special_Instructions["EO"] | Write_Instructions["WA"]):04x}',
        FETCH[0], FETCH[1], FETCH[2]
    ],
    "SHL": [ # 01101 : Shift value in A register by value in B amount to the left
        f'{(ALU_Instructions["SL"] | Special_Instructions["EO"] | Write_Instructions["WA"]):04x}',
        FETCH[0], FETCH[1], FETCH[2]
    ],
    "SHR": [ # 01110 : Shift value in A register by value in B amount to the right
        f'{(ALU_Instructions["SR"] | Special_Instructions["EO"] | Write_Instructions["WA"]):04x}',
        FETCH[0], FETCH[1], FETCH[2]
    ],

    "JMP": [ # JMP <addr>	 01111 : Change program counter to <addr>, changes next instruction
        f'{(Read_Instructions["IR"]):04x}',
        f'{(Read_Instructions["IR"] | Write_Instructions["CW"]):04x}',
        FETCH[0], FETCH[1], FETCH[2]
    ],
    "JMPZ": [ # JMPZ <addr>   10000 : Jump if zero flag set
        f'{(Read_Instructions["IR"]):04x}',
        f'{(Read_Instructions["IR"] | Special_Instructions["JZ"]):04x}',
        FETCH[0], FETCH[1], FETCH[2]
    ],

    #LDAIN and STAOUT allows for 16-bit mem address
    "LDAIN": [ # LDAIN 		 10001 : Use A as mem addr then load from memory to A register
        f'{(Read_Instructions["RA"] | Write_Instructions["AW"]):04x}',
        f'{(Read_Instructions["RM"] | Write_Instructions["WA"]):04x}',
        FETCH[0], FETCH[1], FETCH[2]
    ],
    "STAOUT": [ # STAOUT	 10010 : Use register A as mem addr, then load B to memory address
        f'{(Read_Instructions["RA"] | Write_Instructions["AW"]):04x}',
        f'{(Read_Instructions["RB"] | Write_Instructions["WM"]):04x}',
        FETCH[0], FETCH[1], FETCH[2]
    ],

    "SWP": [ # SWP			 10011 : Swap contents in register A and B, overwrites C
        f'{(Read_Instructions["RA"] | Write_Instructions["WC"]):04x}',
        f'{(Read_Instructions["RB"] | Write_Instructions["WA"]):04x}',
        f'{(Read_Instructions["RC"] | Write_Instructions["WB"]):04x}',
        FETCH[0], FETCH[1], FETCH[2]
    ],
    "SWPC": [ # SWPC		 10100 : Swap contents in register A and C, overwrites B
        f'{(Read_Instructions["RA"] | Write_Instructions["WB"]):04x}',
        f'{(Read_Instructions["RC"] | Write_Instructions["WA"]):04x}',
        f'{(Read_Instructions["RB"] | Write_Instructions["WC"]):04x}',
        FETCH[0], FETCH[1], FETCH[2]
    ],

    "HLT": [ # HLT			 10101 : Stop the clock
        f'{(Special_Instructions["ST"]):04x}',
        FETCH[0], FETCH[1], FETCH[2] #just add in case something goes wrong
    ],
    "NOP": [ # NOP		     10110 : No operation | just fetch next instruction
        FETCH[0], FETCH[1], FETCH[2]
    ]
    
}

def printInstructions():
    lineLength = 8
    line = 0
    with open("microprogram.txt", "w") as f:
        print("v3.0 hex words addressed", file=f)
        for instruction in Assembly_Instructions.values():
            remainingInsLength = lineLength - len(instruction)
            for y in range(remainingInsLength):
                instruction.append(f"{0:04x}")
            print(f"{line*8:02x}:", *instruction, file=f)
            line = line + 1

printInstructions()