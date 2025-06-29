// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.

// Tests and illustrates SimoleLoop.vm on the VM emulator.
// Before executing the code, initializes the stack pointer
// and the base addresses of the local and argument segments,
// and sets argument[0].

load SimpleLoop.vm,
output-file SimpleLoop.out,
compare-to SimpleLoop.cmp,

set sp 256,

repeat 10 {
 	vmstep;
}

// Outputs the stack pointer and the value at the stack's base
output-list RAM[0]%D1.6.1 RAM[256]%D1.6.1;
output;
