// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.

// Tests SimpleEq.asm on the CPU emulator.

load SimpleEq.asm,
output-file SimpleEq.out,
compare-to SimpleEq.cmp,

set RAM[0] 256,  // initializes the stack pointer 

repeat 150 {      // enough cycles to complete the execution
  ticktock;
}

// Outputs the stack pointer and the value at the stack's base
output-list RAM[0]%D2.6.2 RAM[256]%D2.6.2 RAM[257]%D2.6.2 RAM[258]%D2.6.2;
output;
