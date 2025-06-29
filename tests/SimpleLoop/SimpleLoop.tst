// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.

// Tests SimpleLoop.asm on the CPU emulator.
// Before executing the code, initializes the stack pointer.

load SimpleLoop.asm,
output-file SimpleLoop.out,
compare-to SimpleLoop.cmp,

set RAM[0] 256,  // SP

repeat 30 {
	ticktock;
}

// Outputs the stack pointer and the value at the stack's base
output-list RAM[0]%D1.6.1 RAM[256]%D1.6.1;
output;
