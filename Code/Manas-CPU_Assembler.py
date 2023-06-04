"""
Assembler for the 16-bit Manas-CPU
    - Highest value of instruction argument is 11-bits, 5 bits for instruction code, so 0x7FF.
    - Provide .manas assembly file name or path.
    - Can also include output file name or path as third argument, 
      however this is optional, it will default to "output.manasbin".

Functions:
    - strToInt(number:str) -> int
    - ReadInstructions(file: str) -> list[list]
    - Assemble(instructionList: list[list], outfile: str) -> None
    - run() -> None

Constants:
    - PRG_END

Dictionaries:
    - Instruction_codes -> Contains all the instruction opcodes for the assembly instructions.
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

import sys

#Explanations are in the microassembler
PRG_END = 0b1111100000000000
Instruction_codes = {
    "LDA":      0b0000100000000000,
    "LDB":      0b0001000000000000,
    "LDC":      0b0001100000000000,
    "LDIA":     0b0010000000000000,
    "LDIB":     0b0010100000000000,
    "LDIC":     0b0011000000000000,
    "STA":      0b0011100000000000,
    "STB":      0b0100000000000000,
    "STC":      0b0100100000000000,

    "ADD":      0b0101000000000000,
    "SUB":      0b0101100000000000,
    "MULT":     0b0110000000000000,
    "SHL":      0b0110100000000000,
    "SHR":      0b0111000000000000,

    "JMP":      0b0111100000000000,
    "JMPZ":     0b1000000000000000,

    "LDAIN":    0b1000100000000000,
    "STAOUT":   0b1001000000000000,

    "SWP":      0b1001100000000000,
    "SWPC":     0b1010000000000000,

    "HLT":      0b1010100000000000,
    "NOP":      0b1011000000000000
}

def strToInt(number: str) -> int:
    "Checks if number in str form is appended by 0x or 0b and converts it into appropriate base integer"
    if (len(number) > 1):
        if (number[0:2] == "0x"):
            return int(number[2:],base=16)
        elif (number[0:2] == "0b"):
            return int(number[2:],base=2)
        else:
            return int(number)
    else:
        return int(number)

def ReadInstructions(file: str) -> list[list]:
    """
    Reads provided .manas assembly file, removes unnecessary whitespace characters and returns list of 
    instructions and labels.

    Attributes:
        - file: Name or path to .manas assembly file to read.
    """
    readInstructions = []
    with open(file, "r") as f:
        for line in f:
            instructions = line.rstrip()
            instructions = " ".join(instructions.split()) # Remove all whitespace characters and seperate instructions by only one space
            instructions = instructions.split(" ")
            if (instructions[0] != "" and instructions[0][0] != ";"):
                readInstructions.append(instructions)
    return readInstructions

def Assemble(instructionList: list[list], outfile: str) -> None:
    """
    Reads provided list of instructions and labels and assembles it into hex addressed machine code for the
    Manas-CPU.

    Attributes:
        - instructionList: List of instructions and labels to assemble.
        - outfile: Name or path to file the function will write to.
    """
    assembledInstructions = []
    lineLength = 16
    labels = {}
    currentPosition = -1
    adjustment = 0
    #print(instructionList)
    for instruction in instructionList:
        currentPosition += 1
        if (instruction[0][-1] == ":"): # do labels and define bytes
            if (len(instruction) > 1 and instruction[1][0] != ";"): # if there is a value after label, then treat label as a variable
                labels[instruction[0][0:-1]] = strToInt(instruction[1])
            else: # If label only by itself, treat as address
                labels[instruction[0][0:-1]] = currentPosition - adjustment # Adjust address for amount of labels
            adjustment += 1
    #print(labels)
    currentPosition = -1
    for instruction in instructionList:
        currentPosition += 1
        if (instruction[0][0:-1] in labels): continue
        elif (instruction[0] == "db"): # Define one word of data, placed at current position in program memory
            assembledInstructions.append(f'{strToInt(instruction[1]):04x}')
        elif (instruction[0] in Instruction_codes): # Check if current instruction in opcodes
            if (len(instruction) == 1 or instruction[1][0] == ";"): 
                assembledInstructions.append(f'{Instruction_codes[instruction[0]]:04x}')
            elif (instruction[1] in labels): # Check if argument is label, can be address or variable
                assembledInstructions.append(f'{Instruction_codes[instruction[0]] | labels[instruction[1]]:04x}')
            else:
                assembledInstructions.append(f'{Instruction_codes[instruction[0]] | strToInt(instruction[1]):04x}')
        else: 
            print(f"Error, cannot assemble instruction: {instruction}!")
    assembledInstructions.append(f'{PRG_END:04x}')
    with open(outfile, "w") as f:
        line = 0
        currentPosition = 0
        print("v3.0 hex words addressed", file=f)
        for i in range(len(assembledInstructions) // lineLength + 1):
            print(f'{(line*lineLength):04x}:', file=f, end=" ")
            for y in range(lineLength):
                if (currentPosition > len(assembledInstructions)-1):
                    break
                print(assembledInstructions[currentPosition], file=f, end=" ")
                currentPosition += 1
    #print(assembledInstructions)

def run() -> None:
    if (len(sys.argv) < 2):
        print(__doc__)
    elif (len(sys.argv) == 2):
        manasAssemblyfile = sys.argv[1]
        outputfile = "output.manasbin"
        insList = ReadInstructions(manasAssemblyfile)
        Assemble(insList, outputfile)
    else:
        manasAssemblyfile = sys.argv[1]
        outputfile = sys.argv[2]
        insList = ReadInstructions(manasAssemblyfile)
        Assemble(insList, outputfile)

if __name__ == "__main__":
    run()