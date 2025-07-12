import sys
import re

def parse_vm_instruction(line):
    vm_instruction = {}
    line = line.split(" ")
    if (line[0] == "push" or line[0] == "pop" or line[0] == "function"):
        vm_instruction['command_type'] = line[0]
        vm_instruction['arg1'] = line[1]
        vm_instruction['arg2'] = line[2]
    elif (line[0] == "goto" or line[0] == "if-goto" or line[0] == "label"):
        vm_instruction['command_type'] = line[0]
        vm_instruction['arg1'] = line[1]
    elif (line[0] == "return"):
        vm_instruction['command_type'] = line[0]
    else:
        vm_instruction['command_type'] = "arithmetic"
        vm_instruction['arg1'] = line[0]
    return vm_instruction

def template_push_constant(constant):
    if int(constant) < 0:
        return ('\n').join([
            f'@{abs(int(constant))}',
            "D=A",
            "D=-D", #negate
            "@SP",
            "A=M",
            "M=D",
            # move pointer forward
            "@SP",
            "M=M+1"
    ])
    else:
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

def base_address_pointer(segment):
    if segment == "local":
        return 1
    elif segment == "argument":
        return 2
    elif segment == "this":
        return 3
    elif segment == "that":
        return 4

def template_pop(segment, i):
    if segment == "temp":
        return ('\n').join([
                # pop to D
                "@SP",
                "M=M-1",
                "A=M",
                "D=M",
                # write D to temp address (temp uses direct addressing (R5-R12))
                f"@{5 + int(i)}",
                "M=D"
            ])
    else:
        return ('\n').join([
                # store segment address in R13
                f"@{base_address_pointer(segment)}",
                "D=M",
                f"@{i}",
                "D=D+A",
                "@13",
                "M=D",
                # pop to D
                "@SP",
                "M=M-1",
                "A=M",
                "D=M",
                # write D to segment address
                "@13",
                "A=M",
                "M=D"
            ])

def template_push(segment, i):
    if segment == "temp":
        return ('\n').join([
                # temp uses direct addressing (R5-R12)
                f"@{5 + int(i)}",
                "D=M",
                # push D to stack
                "@SP",
                "A=M",
                "M=D",
                # move pointer forward
                "@SP",
                "M=M+1"
            ])
    else:
        return ('\n').join([
                # store segment address in D
                f"@{base_address_pointer(segment)}",
                "D=M",
                f"@{i}",
                "D=D+A",
                # read contents of segment address to D
                "A=D",
                "D=M",
                # push D to stack
                "@SP",
                "A=M",
                "M=D",
                # move pointer forward
                "@SP",
                "M=M+1"
            ])

def template_pop_static(filename, i):
    return ('\n').join([
        "@SP",
        "M=M-1",
        "A=M",
        "D=M",
        f"@{filename}.{i}",
        "M=D"
    ])

def template_push_static(filename, i):
    return ('\n').join([
        f"@{filename}.{i}",
        "D=M",
        "@SP",
        "A=M", 
        "M=D",
        "@SP",
        "M=M+1"
    ])

def template_pop_pointer(i):
    return ('\n').join([
        "@SP",
        "M=M-1",
        "A=M",
        "D=M",
        f"@R{int(i)+3}",
        "M=D"
    ])

def template_push_pointer(i):
    return ('\n').join([
        f"@R{int(i)+3}",
        "D=M",
        "@SP",
        "A=M",
        "M=D",
        # move pointer forward
        "@SP",
        "M=M+1"
    ])

def template_arithmetic_add_sub(operation, label_id):
    if operation == "+":
        assembly_operation = "D=D+M"
    else:
        assembly_operation = "D=M-D"

    return ('\n').join([
        # pop second operand to D
        "@SP",
        "M=M-1",
        "A=M",
        "D=M",
        # pop first operand and perform operation
        "@SP",
        "M=M-1",
        "A=M",
        assembly_operation, # D = first operand - second operand
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
        "D=M-D",
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

def template_arithmetic_comparison(operation, label_id):
    return ('\n').join([
        # pop second operand to D
        "@SP",
        "M=M-1",
        "A=M",
        "D=M",
        # pop first operand and compare
        "@SP",
        "M=M-1",
        "A=M",
        "D=M-D", # D = firist operand - second operand
        # jump based on comparison
        f"@TRUE_{label_id}",
        f"D;J{operation}",
        # push false (0)
        "@SP",
        "A=M",
        "M=0",
        f"@END_{label_id}",
        "0;JMP",
        # push true (-1)
        f"(TRUE_{label_id})",
        "@SP",
        "A=M",
        "M=-1",
        # move pointer forward
        f"(END_{label_id})",
        "@SP",
        "M=M+1",
    ])

def template_logical_operation(operation):
    return ('\n').join([
        # pop first operand to D
        "@SP",
        "M=M-1",
        "A=M",
        "D=M",
        # pop second operand and perform logical operation
        "@SP",
        "M=M-1",
        "A=M",
        f"D=D{operation}M",
        "M=D",
        # move pointer forward
        "@SP",
        "M=M+1",
    ])

def template_logical_not():
    return ('\n').join([
        # pop first operand to D
        "@SP",
        "M=M-1",
        "A=M",
        "D=M",
        # not
        "D=!D",
        # push
        "M=D",
        # move pointer forward
        "@SP",
        "M=M+1",
    ])

def template_goto(label):
    return ('\n').join([
        f"@{label}",
        "0;JMP"
    ])

def template_if_goto(label):
            return ('\n').join([
                # pop to D
                "@SP",
                "M=M-1",
                "A=M",
                "D=M",
                # jmp
                f"@{label}",
                "D;JNE"
            ])

def template_label(label):
    return f"({label})"

def tempalte_call(function_name, n_args):
    return "call"

def template_function(function_name, n_vars):
    lines = []

    function_name_label = template_label(function_name)
    lines.append(f"{function_name_label}")

    for n in range(int(n_vars)):
        lines.append(template_push_constant(0))
        lines.append(template_pop('local', n))

    return ('\n').join(lines)

def template_return():
    # 1. Freeze a pointer to the current (callee) frame.
    # FRAME = LCL (e.g. store in R13)
    frame_pointer = ('\n').join([
        "@LCL",
        "D=M",
        "@R13",
        "M=D"
    ])

    # 2. Fetch the address the caller expects to jump to. 
    # RET = *(FRAME-5) (e.g. R14)
    ret = ('\n').join([
        "@R13", # Get FRAME (see #1)
        "D=M", # Read value of FRAME pointer
        "@5", 
        "D=D-A", # Minus 5 from FRAME pointer to get to return address
        "A=D", # Set A to point to return address location
        "D=M", # Read the return address pointer
        "@R14",
        "M=D" # Save it to RET/@R14
    ])

    # 3. Place the function’s return value where the caller expects it. 
    # *ARG = pop()
    arg_pop = ('\n').join([
        "@SP",
        "AM=M-1", # Move SP back one (because this is where the returned value is)
        "D=M", # Popped value in D
        "@ARG", # Address @ARG pointer
        "A=M",
        "M=D" # Write popped value to ARG
    ])

    # 4. Restore the caller’s view of the stack pointer.
    # SP = ARG + 1
    restore_sp = ('\n').join([
        "@ARG",
        "D=M+1",
        "@SP",
        "M=D"
    ])

    # 5. Reinstall the caller’s segment pointers. 
    # THAT = *(FRAME-1)
    # THIS = *(FRAME-2)
    # ARG  = *(FRAME-3)
    # LCL  = *(FRAME-4)

    reinstall_frame = ('\n').join([
        "@R13", # Get FRAME
        "AM=M-1", # Decrement FRAME
        "D=M", # Read FRAME
        "@THAT", # Address segment to be restore
        "M=D", # Restore segment

        "@R13", # Get FRAME
        "AM=M-1", # Decrement FRAME
        "D=M", # Read FRAME
        "@THIS", # Address segment to be restore
        "M=D", # Restore segment

        "@R13", # Get FRAME
        "AM=M-1", # Decrement FRAME
        "D=M", # Read FRAME
        "@ARG", # Address segment to be restore
        "M=D", # Restore segment


        "@R13", # Get FRAME
        "AM=M-1", # Decrement FRAME
        "D=M", # Read FRAME
        "@LCL", # Address segment to be restore
        "M=D", # Restore segment
    ])

    # 6. Resume the caller’s code. 
    # goto RET
    goto_ret = ('\n').join([
        "@R14",
        "A=M",
        "0;JMP"
    ])

    return ('\n').join([
        frame_pointer,
        ret,         
        arg_pop,      
        restore_sp, 
        reinstall_frame,
        goto_ret
    ])

def translate_to_assembly_instruction(vm_instruction, vm_instruction_index, filename):
    class_name = filename.split("/")[-1].replace(".vm", "")
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
            return template_arithmetic_comparison("GT", vm_instruction_index)
        elif vm_instruction['arg1'] == "lt":
            return template_arithmetic_comparison("LT", vm_instruction_index)
        elif vm_instruction['arg1'] == "and":
            return template_logical_operation("&")
        elif vm_instruction['arg1'] == "or":
            return template_logical_operation("|")
        elif vm_instruction['arg1'] == "not":
            return template_logical_not()
    elif vm_instruction['command_type'] == "push" or vm_instruction['command_type'] == "pop":
        if vm_instruction['arg1'] == "constant":
            constant = vm_instruction['arg2']
            return template_push_constant(constant)
        elif vm_instruction['command_type'] == "pop":
            if vm_instruction['arg1'] == "static":
                return template_pop_static(class_name, vm_instruction['arg2'])
            elif vm_instruction['arg1'] == "pointer":
                return template_pop_pointer(vm_instruction['arg2'])
            else:
                return template_pop(vm_instruction['arg1'], vm_instruction['arg2'])
        elif vm_instruction['command_type'] == "push":
            if vm_instruction['arg1'] == "static":
                return template_push_static(class_name, vm_instruction['arg2'])
            elif vm_instruction['arg1'] == "pointer":
                return template_push_pointer(vm_instruction['arg2'])
            else:
                return template_push(vm_instruction['arg1'], vm_instruction['arg2'])
    elif vm_instruction['command_type'] == "goto":
        return template_goto(vm_instruction['arg1'])
    elif vm_instruction['command_type'] == "if-goto":
        return template_if_goto(vm_instruction['arg1'])
    elif vm_instruction['command_type'] == "label":
        return template_label(vm_instruction['arg1'])
    elif vm_instruction['command_type'] == "function":
        return template_function(vm_instruction['arg1'], vm_instruction['arg2'])
    elif vm_instruction['command_type'] == "return":
        return template_return()

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
                assembly_instruction = translate_to_assembly_instruction(parsed_vm_instruction, index, input_file)
                print(assembly_instruction)
                out_file.write(assembly_instruction + '\n')

if __name__ == "__main__":
    main()