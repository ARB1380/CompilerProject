# Mohammad Mahdi Mirzaei 99171022
# Alireza Farshi 99101976

import re

import constant
from dfa import dfa
from Token import Token


def is_digit(character):
    return re.match("[0-9]", character)


def is_letter(character):
    return re.match("[a-zA-Z]", character)


def is_in_special_state(state, type):
    return complete_dfa.current_state == state and complete_dfa.type == type


def is_in_initial_state():
    return complete_dfa.current_state == 0


def reset_dfa():
    complete_dfa.current_state = 0
    complete_dfa.type = ""


def is_symbol(character):
    return character in symbols


def is_white_space(character):
    return character == ' '


def is_keyword(input):
    return input in keywords


def start(type):
    complete_dfa.current_state += 1
    complete_dfa.type = type


def get_token(type, lexeme):
    reset_dfa()
    if type == "ID" and is_keyword(lexeme):
        return Token("KEYWORD", lexeme)
    return Token(type, lexeme)


def get_next_token(input):
    global current_index
    start_index = current_index
    while current_index != len(input):
        if is_digit(input[current_index]):
            if is_in_initial_state():
                start("number")
            elif is_in_special_state(3, "comment"):
                complete_dfa.current_state -= 1
            current_index += 1
        elif is_letter(input[current_index]):
            if is_in_initial_state():
                start("identifier")
            elif is_in_special_state(3, "comment"):
                complete_dfa.current_state -= 1
            elif is_in_special_state(1, "number"):
                return get_token("NUM", input[start_index: current_index])
            current_index += 1
        elif is_symbol(input[current_index]):
            if is_in_initial_state():
                copy_current_index = current_index
                current_index += 1
                if input[copy_current_index] == '/':
                    start("comment")
                else:
                    token = input[copy_current_index]
                    return get_token("SYMBOL", token)

            elif is_in_special_state(1, "number"):
                return get_token("NUM", input[start_index: current_index])
            elif is_in_special_state(1, "identifier"):
                return get_token("ID", input[start_index: current_index])
        elif is_white_space(input[current_index]):
            if is_in_special_state(1, "number"):
                return get_token("NUM", input[start_index: current_index])
            if is_in_special_state(1, "identifier"):
                return get_token("ID", input[start_index: current_index])
            current_index += 1
            start_index = current_index
        elif input[current_index] == '\n':
            copy_current_index = current_index
            current_index += 1
            if is_in_special_state(1, "number"):
                token = get_token("NUM", input[start_index: copy_current_index])
                return token
            if is_in_special_state(1, "identifier"):
                token = get_token("ID", input[start_index: copy_current_index])
                return token
            return None


file = open("input.txt", "r")
token_file = open("tokens.txt", "a")
symbol_file = open("symbol_table.txt", "a")
lexical_error_file = open("lexical_errors.txt", "a")
complete_dfa = dfa("", 0)
symbols = {';', ':', ',', '[', ']', '(', ')', '{', '}', '+', '-', '*', '=', '<', '/'}
# total_errors = []
keywords = {"break", "else", "if",
            "int", "repeat", "return",
            "until", "void"}
current_index = 0
# s = "int x = 2"
# while current_index != len(s):
#     print(f"lemxeme is : {get_next_token(s).lexeme}")

for line in file:
    while current_index != len(line):
        result = get_next_token(line)
        if result != None:
            print(f"lexeme is :{result.lexeme}")
    current_index = 0

# if comment:
#     error = Error(comment_string[:7] + "...", constant.UNCLOSED_COMMENT)
#     lexical_error_file.write(f"{comment_line}.\t({error.value}, {error.message}) ")
#     lexical_error_file.write("\n")
#     total_errors.append(error)
# if len(total_errors) == 0:
#     lexical_error_file.write("There is no lexical error.")
#
# counter = 1
# for symbol in symbols:
#     symbol_file.write(f"{counter}.\t{symbol}")
#     symbol_file.write("\n")
#     counter += 1
