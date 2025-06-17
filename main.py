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

def template_arithmetic_add_sub(operation, label_id):
    return ('\n').join([
        # pop first operand to D
        "@SP",
        "M=M-1",
        "A=M",
        "D=M",
        # pop second operand and perform operation
        "@SP",
        "M=M-1",
        "A=M",
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

def template_arithmetic_eq(label_id):
    return ('\n').join([
        # pop first operand to D
        "@SP",
        "M=M-1",
        "A=M",
        "D=M",
        # pop second operand and perform operation
        "@SP",
        "M=M-1",
        "A=M",
        "D=D-M",
        # eq
        f"@EQUAL_{label_id}",
        "D;JEQ",
        # push false
        "@SP",
        "A=M",
        "M=0",
        f"@END_{label_id}",
        "0;JMP",
        # push true
        f"(EQUAL_{label_id})",
        "@SP",
        "A=M",
        "M=-1",
        # move pointer forward
        f"(END_{label_id})",
        "@SP",
        "M=M+1",
    ])

def template_arithmetic_gt(label_id):
    return ('\n').join([
        # pop first operand to D
        "@SP",
        "M=M-1",
        "A=M",
        "D=M",
        # pop second operand and perform operation
        "@SP",
        "M=M-1",
        "A=M",
        "D=M-D",
        # gt
        f"@GT_{label_id}",
        "D;JGT",
        # push false
        "@SP",
        "A=M",
        "M=0",
        f"@END_{label_id}",
        "0;JMP",
        # push true
        f"(GT_{label_id})",
        "@SP",
        "A=M",
        "M=-1",
        # move pointer forward
        f"(END_{label_id})",
        "@SP",
        "M=M+1",
    ])

def translate_to_assembly_instruction(vm_instruction, vm_instruction_index):
    if vm_instruction['command_type'] == "arithmetic":
        if vm_instruction['arg1'] == "add":
            return template_arithmetic_add_sub("+", vm_instruction_index)
        elif vm_instruction['arg1'] == "sub":
            return template_arithmetic_add_sub("-", vm_instruction_index)
        elif vm_instruction['arg1'] == "neg":
            return template_arithmetic_neg()
        elif vm_instruction['arg1'] == "eq":
            return template_arithmetic_eq(vm_instruction_index)
        elif vm_instruction['arg1'] == "gt":
            return template_arithmetic_gt(vm_instruction_index)
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

        with open(output_file, 'w') as out_file:
            for index, line in enumerate(lines):
                parsed_vm_instruction = parse_vm_instruction(line)
                assembly_instruction = translate_to_assembly_instruction(parsed_vm_instruction, index)
                print(assembly_instruction)
                out_file.write(assembly_instruction + '\n')

if __name__ == "__main__":
    main()