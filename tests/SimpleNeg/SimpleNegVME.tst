// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.

// Tests and illustrates SimpleSubtract.vm on the VM simulator.

load SimpleNeg.vm,
output-file SimpleNeg.out,
compare-to SimpleNeg.cmp,

set RAM[0] 256,  // initializes the stack pointer

repeat 2 {       // SimpleNeg.vm has 2 VM commands
  vmstep;
}

// Outputs the stack pointer and the value at the stack's base
output-list RAM[0]%D2.6.2 RAM[256]%D2.6.2;
output;
