// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.

// Tests and illustrates SimpleLt.vm on the VM simulator.

load SimpleLt.vm,
output-file SimpleLt.out,
compare-to SimpleLt.cmp,

set RAM[0] 256,  // initializes the stack pointer

repeat 9 {       // SimpleLt.vm has 9 VM commands
  vmstep;
}

// Outputs the stack pointer and the value at the stack's base
output-list RAM[0]%D2.6.2 RAM[256]%D2.6.2;
output;
