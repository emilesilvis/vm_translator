// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.

// Tests and illustrates SimpleGt.vm on the VM simulator.

load SimpleGt.vm,
output-file SimpleGt.out,
compare-to SimpleGt.cmp,

set RAM[0] 256,  // initializes the stack pointer

repeat 3 {       // SimpleGt.vm has 6 VM commands
  vmstep;
}

// Outputs the stack pointer and the value at the stack's base
output-list RAM[0]%D2.6.2 RAM[256]%D2.6.2;
output;
