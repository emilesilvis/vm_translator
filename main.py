import sys
import re

def parse_vm_instruction(line):
    vm_instruction = {}
    line = line.split(" ")
    if line[0] == "push":
        vm_instruction['command_type'] = "push"
        vm_instruction['arg1'] = line[1]
        vm_instruction['arg2'] = line[2]
    elif line[0] == "pop":
        vm_instruction['command_type'] = "pop"
        vm_instruction['arg1'] = line[1]
        vm_instruction['arg2'] = line[2]
    else:
        vm_instruction['command_type'] = "arithmetic"
        vm_instruction['arg1'] = line[0]
    return vm_instruction

def template_push_constant(constant):
    return ('\n').join([
        f'@{constant}',
        "D=A",
        "@SP",
        "A=M",
        "M=D",
        # move pointer forward
        "@SP",
        "M=M+1"
    ])

def template_arithmetic_add_sub(operation):
    return ('\n').join([
        # pop X
        "@SP",
        "M=M-1",
        "A=M",
        "D=M",
        "@X", 
        "M=D",
        # pop D
        "@SP",
        "M=M-1",
        "A=M",
        "D=M",
        # X + D
        "@X",
        f"D=D{operation}M",
        # push
        "@SP",
        "A=M",
        "M=D",
        # move pointer forward
        "@SP",
        "M=M+1",
    ])

def template_arithmetic_neg():
    return ('\n').join([
        # negate
        "@SP",
        "M=M-1",
        "A=M",
        "M=-M",
        # move pointer forward
        "@SP",
        "M=M+1",
    ])

def template_arithmetic_eq():
    return ('\n').join([
        # pop X
        "@SP",
        "M=M-1",
        "A=M",
        "D=M",
        "@X", 
        "M=D",
        # pop D
        "@SP",
        "M=M-1",
        "A=M",
        "D=M",
        # X - D
        "@X",
        "D=D-M",
        # eq
        "@EQUAL",
        "D;JEQ",
        # push false
        "@SP",
        "A=M",
        "M=0",
        "@END",
        "0;JMP",
        # push true
        "(EQUAL)",
        "@SP",
        "A=M",
        "M=-1",
        # move pointer forward
        "(END)",
        "@SP",
        "M=M+1",
    ])

def translate_to_assembly_instruction(vm_instruction):
    if vm_instruction['command_type'] == "arithmetic":
        if vm_instruction['arg1'] == "add":
            return template_arithmetic_add_sub("+")
        elif vm_instruction['arg1'] == "sub":
            return template_arithmetic_add_sub("-")
        elif vm_instruction['arg1'] == "neg":
            return template_arithmetic_neg()
        elif vm_instruction['arg1'] == "eq":
            return template_arithmetic_eq()
    elif vm_instruction['command_type'] == "push" or vm_instruction['command_type'] == "pop":
        if vm_instruction['arg1'] == "constant":
            constant = vm_instruction['arg2']
            return template_push_constant(constant)

def main():
    if len(sys.argv) != 2:
        print("Usage: python main.py <input_file.vm>")
        sys.exit(1)
    input_file = sys.argv[1]
    output_file = input_file.replace('.vm', '.asm')
    with open(input_file, 'r') as file:
        lines = [re.sub(r'//.*$', '', line) for line in file]
        lines = [line.strip() for line in lines]
        lines = [line for line in lines if line]

        for line in lines:
            parsed_vm_instruction = parse_vm_instruction(line)
            assembly_instruction = translate_to_assembly_instruction(parsed_vm_instruction)
            print(assembly_instruction)

        with open(output_file, 'w') as out_file:
            for line in lines:
                parsed_vm_instruction = parse_vm_instruction(line)
                assembly_instruction = translate_to_assembly_instruction(parsed_vm_instruction)
                out_file.write(assembly_instruction + '\n')

if __name__ == "__main__":
    main()