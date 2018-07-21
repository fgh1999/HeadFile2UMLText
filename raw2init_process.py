 #!/usr/bin/env python3 
 # -*- coding: utf-8 -*-

import glob
import os
import re
import shutil
import sys


def pop_n_upAndDown(list):
    def pop_n_Behind(list):
        """
        Parameter:
            list:list contains strings
        Function:
            recursively pop the last element which equal to '\n'
        """
        if list[-1] == '\n':
            list.pop()
            return pop_n_Behind(list)
        else:
            return list

    def pop_n_Front(list):
        """
        Parameter:
            list:list contains strings
        Function:
            recursively pop the first element which equal to '\n'
        """
        if list[0] == '\n':
            list.pop(0)
            return pop_n_Front(list)
        else:
            return list

    pop_n_Front(list)
    pop_n_Behind(list)

def field_level(level_statement):
    if level_statement.startswith("public:"):
        return 1
    if level_statement.startswith("protected:"):
        return 2
    if level_statement.startswith("private:"):
        return 3
    return 0

def dropNote(line):
    return re.sub(r"/\*.*\*/", "", line.split("//")[0])

def dropBody(line):
    """
    Parameter:
        line:string
    Function:
        drop the function body in the string "line".
    """
    return re.sub(r"(\{?.*\}$)|(\{.*\}?$)", "", line)

def null_process(line):
    """
    Parameter:
        line: string
    Function: 
        if line is empty, return "\n" ; else, return itself
    """
    return line if line else "\n"

def sig_var_process(pattern, line):
    """
    Parameter:
        pattern: a compiled regEx Object that matces variable
        line: string contains a function statement like "func(string a, int b)const" Attention: NoReturn
    Function:
        return a string which contains variables statement processed
        like this, "func(a:string, b:int)const"
    """
    m = re.search(r"\(.*\)", line)
    if m != None:
        parameters = line[m.start():m.end()].rstrip(')').lstrip('(').split(',')
    else:
        return "NONE : SIG_VAR_PROCESS : no match " # For Debug
    if len(parameters) == 0:
        return ""
    parameters_pro = []
    for parameter in parameters:
        parameters_pro.append(parameter.split('=')[0].strip())
    parameters_new = []
    for parameter in parameters_pro:
        if len(parameter) == 0:
            continue
        m = re.search(pattern, parameter)
        if m != None:
            para_new = parameter[m.start():m.end()] + ':' + parameter[:m.start()].strip()
        else:
            para_new = "NONE : SIG_VAR_PROCESS : miss var " + parameter # For Debug
        parameters_new.append(para_new)
    para_str = '(' + ', '.join(parameters_new) + ')'
    return re.sub(r"\(.*\)", para_str, line)

def process2text(document_name):
    """
    Parameter:
        document_name: string, indicates the address of the HEAD File
    Function:
        change the input HEAD File "abc.h" into a class-picture-friendly format Text "abc_sub.txt"
    """
    state_map = {0:"", 1:"+ ", 2:"# ", 3:"- "}
    variable_pattern = re.compile(r"_*[a-zA-a]+[0-9a-zA-z,]*$")
    function_pattern = re.compile(r"(~?\s*[a-zA-a]+[0-9a-zA-z]*\s*\(.*\))|(~?_+[0-9a-zA-z]*\s*\(.*\))")
    symbol_pattern_map = {0:re.compile(r".*"), 1:variable_pattern, 2:function_pattern}
    """
    0:None    1:variable    2:function signature
    """

    with open(document_name, mode="r", encoding= "utf-8") as document:
        lines = document.readlines()
        lines_new = []
        lines_new_class = []
        lines_new_var = ["VAR：\n"]
        lines_new_func = ["FUNC:\n"]

        field_level_state = 0
        """
        0:None    1:public    2:protected    3:private
        """
        var_or_func = 0

        continuous_null_lines_number = 0
        for line in lines:
            line = null_process(line.strip())
            if line.startswith("#"):
                line = "\n"
            if line == "\n":
                # to avoid too many continuous null lines
                continuous_null_lines_number += 1
                if continuous_null_lines_number <= 2:
                    lines_new.append("\n")
                    if continuous_null_lines_number == 2:
                        continuous_null_lines_number = 0
                    continue
            line = null_process(dropBody(dropNote(line))).replace(";", "").strip()

            field_level_state_temp = field_level(line)
            field_level_state = field_level_state_temp if field_level_state_temp != 0 else field_level_state
            
            if not line.startswith("class"):
                if line.endswith(")") or line.endswith("const") or line.endswith("override") or line.endswith("default"):
                    var_or_func = 2
                else:
                    var_or_func = 1

                m = re.search(symbol_pattern_map[var_or_func], line)
                if m != None:
                    if var_or_func == 2:# Function
                        line = sig_var_process(variable_pattern, line[m.start():]).strip() + ":" + line[:m.start()].strip()
                        if field_level_state_temp != 0:
                            lines_new.append("\n")
                            continue
                        line = state_map[field_level_state] + line + "\n"
                        lines_new_func.append(line)
                    if var_or_func == 1:# Variable
                        line = line[m.start():].strip() + ":" + line[:m.start()].strip()
                        if field_level_state_temp != 0:
                            lines_new.append("\n")
                            continue
                        line = state_map[field_level_state] + line + "\n"
                        lines_new_var.append(line)
                else:
                    if null_process(line) == "\n":
                        continue
                    line = "NONE VAR_OR_FUNC: " + str(var_or_func) + " " + line # For Debug
                    if field_level_state_temp != 0:
                        lines_new.append("\n")
                        continue
                    line = state_map[field_level_state] + line + "\n"
                    lines_new.append(line)
            else:
                lines_new_class.append(line)    
    
    for i in range(len(lines_new)):
        if lines_new[i].endswith("}\n"):
            lines_new[i] = '\n'
    for i in range(len(lines_new_class)):
        lines_new_class[i] += '\n'
    lines_new = lines_new + lines_new_class + lines_new_var + lines_new_func
    pop_n_upAndDown(lines_new)

    name_words = document_name.split('.')        
    new_document_name = ''.join(name_words[:-1]) + "_sub.txt"
    with open(new_document_name, mode="w", encoding="utf-8") as document:
        document.writelines(lines_new)

def print_help():
    print("enter a .h document or enter a directory name to generate class text")

if __name__ == "__main__":
    try:
        para_1 = sys.argv[1]
    except IndexError as e:
        print(e)
        print("Please enter a directory or a HEAD File after the python script name.")
        exit(1)

    if para_1 == "--help" or para_1 == "-h":
        print_help()
        exit(0)

    address = para_1
    failed = False
    if address.endswith(".h") or address.endswith(".hpp"):
        process2text(address)
        exit(0)
    else: # address maybe a directory
        try:
            os.chdir(address)
        except Exception as e:
            print(e)
            print("Address invalid!")
            failed = True
    if not failed:
        HEAD_FILES_H = glob.glob("*.h")
        HEAD_FILES_HPP = glob.glob("*.hpp")
        HEAD_FILES = HEAD_FILES_H + HEAD_FILES_HPP
        for FILE in HEAD_FILES:
            process2text(FILE)
        results = glob.glob("*_sub.txt")
        try:
            os.mkdir("processed_sub_text")
        except FileExistsError as e:
            print(e)
            print("delete the existed directory, and make a new directory.")
            shutil.rmtree("processed_sub_text")
            os.mkdir("processed_sub_text")
            
        for result in results:
            shutil.move(result, "processed_sub_text")
    else:
        print("Program has stopped!")
