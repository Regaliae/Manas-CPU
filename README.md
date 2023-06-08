# Manas-CPU
Files for the 16-bit Manas-CPU architecture. Made with Logisim-Evolution { https://github.com/logisim-evolution/logisim-evolution/releases } 
<br/>
# Registers: 16-bit
 - A (Accumulator)
 - B 
 - C
 - Mem Address Register
 - Instruction Register : Holds the instruction currently being executed
 - Program Counter : Stores addr of next instruction, incremented by one after loaded
                     or changed by a jump instruction
 - Zero flag : Indicates if A register equals 0, 1 if yes | 1-bit register
#16 bit word instructions | First 5 bits instruction opcode
#Data and address bus
<br/>

#Microprogram ROM as lookup table for instructions
#Add fetch to the end of every instruction instead of EI
# Instructions:
 - LDA <addr>    00001 : Load data from memory to A register
   - 1: IR, AW | 2: RM, WA | 3: EI  #Microcode for LDA
 - LDB <addr>    00010 : Load data from memory to B register
 - LDC <addr>    00011 : Load data from memory to C register
<br/>
 - LDIA <value>  00100 : Immediatly load value into register A  
   - 1: IR, WA | 2: EI  
 - LDIB <value>  00101 : Immediatly load value into register B  
 - LDIC <value>  00110 : Immediatly load value into register CIN  

 - STA <addr>	 00111 : Store A into memory <addr> 
   - 1: IR, AW | 2: RA, WM | 3: EI
 - STB <addr>    01000 : Store B into memory <addr>
 - STC <addr>	 01001 : Store C into memory <addr>

 - ADD			 01010 : Add register B to A, and store result in register A
   - 1: EO, WA | 2: EI
 - SUB			 01011 : Subtract register B from A, and store result in A
   - 1: SU, EO, WA | 2: EI
 - MULT			 01100 : Multiply register B with A, store result in A
   - 1: MU, EO, WA | 2: EI
 - SHL			 01101 : Shift value in A register by value in B amount to the left
   - 1: SL, EO, WA | 2: EI
 - SHR			 01110 : Shift value in A register by value in B amount to the right
   - 1: SR, EO, WA | 2: EI

 - JMP <addr>	 01111 : Change program counter to <addr>, changes next instruction
   - 1: IR, CW | 2: EI
 - JMPZ <addr>   10000 : Jump if zero flag set
   - 1: IR, JZ | 2: EI
 
#LDAIN and STAOUT allows for 16-bit mem addresses
 - LDAIN 		 10001 : Use A as mem addr then load from mem to A register
   - 1: RA, AW | 2: RM, WA | 3: EI
 - STAOUT		 10010 : Use register A as mem addr, then load B to memory address
   - 1: RA, AW | 2: RB, WM | 3: EI
   
 - SWP			 10011 : Swap contents in register A and B, overwrites C
   - 1: RA, WC | 2: RB, WA | 3: RC, WB | 4: EI
 - SWPC 		 10100 : Swap reg A and C, overwrites B
   - 1: RA, WB | 2: RC, WA | 3: RB, WC | 4: EI
 
 - HLT			 10101 : Stop the clock
   - 1: ST, EI
 - NOP		     10110 : No operation | just fetch next instruction
   - 0: FETCH
 - FETCH 	           : Fetch next instruction
   - 0: CR, AW | 1: RM, IW | 2: CI, EI
 - Copy program ROM	   : Copy program rom to memory until End program discovered.
   - 0: Copy_ROM, Check_prg_end | 1: Copy_ROM, AW | 2: CI, WM | 3: EI
     4: FETCH to get instructions started, jumps here if prg_end detected
 - Program_END	 11111 : Signifies end of program in ROM, stops copying here; f800 | Won't be included in normal code, gets added by assembler
 
 # Microinstructions: | Constituent parts of the different instructions
 #ALU in addition mode by default
 - SU : Enable subtraction mode
 - MU : Enable multiplication mode
 - DI : Division | NOT IMPLEMENTED
 - SR : Enable shift right | Floor divide by 2
 - SL : Enable shift left | Multiply by 2
 - AND : Enable logical AND operation in ALU | NOT IMPLEMENTED
 
 - RA : Read from register A to bus
 - RB : Read from register B to bus
 - RC : Read from register C to bus
 - RM : Read from memory to bus, from adress specified in address register
 - IR : Read from lowest 11 bits of instruction register to bus
 - CR : Read value from program counter to bus
 
 - WA : Write from bus to register A
 - WB : Write from bus to register B
 - WC : Write from bus to register C
 - WM : Write from bus to memory, at location specified in address register
 - AW : Write from bus to address register
 - IW : Write from bus to instruction register
 - CW : Write from bus to program counter
 
 - EI : End instruction
 - CI : Program counter increment
 - EO : Evaluate operation, write result to bus
 - ST : Stop clock
 - JZ : Jump if zero flag set; writes to program counter from data bus if zero flag
 - Cpy_ROM: Copies the program ROM to RAM, changes a few things to fit this purpose.
 - Chk_Prg_End: Checks for the end of the program in ROM and stops copying if found.
 
# Microinstruction setup:
 - 5-ALU operations; 3-bits; EO 1-bit | 4b
 - 6-Read operations; 				  | 3b
 - 7-Write operations; 				  | 3b
 - 3-Special operations; EI, CI, ST	  | 3b
 - Plus: Copy_ROM, Check_prg_end, jz  | 3b
 - 16-bits total\

 0000000000000000: 16b												                                      # 16 bits \
  0---------------: Copy_ROM 											                                 | bit 15 \
  -0--------------: Check_prg_end										                              | bit 14 \
  --0-------------: Jump if zero (JZ)									                           | bit 13 \
  ---000----------: ALU operations; SU, MU, SL, SR, addition when all 0  | bit 10-12 \
  ------0---------: ALU; EO											                                   | bit 9 \
  -------000------: Read instructions									                           | bit 6-8 \
  ----------000---: Write instructions									                          | bit 3-5 \
  -------------0--: Counter Increment/Enable (CI)						                  | bit 2 \
  --------------0-: End Instruction (EI)								                         | bit 1 \
  ---------------0: ST													                                      | bit 0 \
 
 
# Microprogram Address:
 - 11111222 |  1=Instruction code; 5b | 2 = Counter; 3b | 8b addr
