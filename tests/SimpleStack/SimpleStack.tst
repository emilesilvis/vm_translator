// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.

// Tests SimpleStack.asm on the CPU emulator.

load SimpleStack.asm,
output-file SimpleStack.out,
compare-to SimpleStack.cmp,

set RAM[0] 256,   // stack pointer
set RAM[1] 300,   // base address of the local segment
set RAM[2] 400,   // base address of the argument segment
set RAM[3] 3000,  // base address of the this segment
set RAM[4] 3010,  // base address of the that segment

repeat 200 {      // enough cycles to complete the execution
  ticktock;
}

// Outputs the value at the stack's base and some values from the tested memory segments
output-list RAM[256]%D1.6.1 RAM[300]%D1.6.1 RAM[400]%D1.6.1 RAM[3000]%D1.6.1 RAM[3010]%D1.6.1;
output;
