# Mohammad Mahdi Mirzaei 99171022
# Alireza Farshi 99101976

import re

import constant
from dfa import dfa
from Token import Token
from Error import Error


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


def is_slash(character):
    return character == '/'


def is_star(character):
    return character == '*'


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
    if type == "ID" and not lexeme in keywords_and_identifiers:
        keywords_and_identifiers.append(lexeme)
    return Token(type, lexeme)


def append_error(text, lexeme):
    reset_dfa()
    errors_in_a_line.append(Error(text, lexeme))


def get_lexeme(input, start_index, end_index):
    return input[start_index: end_index]


def is_invalid_character(character):
    return not is_digit(character) and not is_letter(character) and not is_symbol(character) and not is_white_space(
        character)


def get_next_token(input):
    global current_index, comment_string, line_counter
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
                append_error("Invalid number", get_lexeme(input, start_index, current_index + 1))
                start_index = current_index + 1
            if complete_dfa.type == "comment":
                comment_string += input[current_index]
            current_index += 1

        elif is_symbol(input[current_index]):
            if is_in_initial_state():
                copy_current_index = current_index
                current_index += 1
                if input[copy_current_index] == '/':
                    if current_index != len(input) and input[current_index] == '*':
                        start("comment")
                        comment_string += "/"
                    elif is_in_special_state(3, "comment"):
                        reset_dfa()
                        start_index = current_index
                        comment_string = ""
                        line_counter = None
                    elif input[current_index] == " " or input[current_index] == "\n":
                        append_error("Invalid input", "/")
                        start_index = current_index
                    elif not is_symbol(input[current_index]):
                        continue
                    else:
                        append_error("Invalid input", "/")
                        start_index = current_index
                elif input[copy_current_index] == '=':
                    if input[current_index] == '=':
                        current_index += 1
                        return get_token("SYMBOL", "==")
                    elif is_invalid_character(input[current_index]):
                        current_index += 1
                        append_error("Invalid input", get_lexeme(input, start_index, current_index))
                        start_index = current_index
                    else:
                        return get_token("SYMBOL", "=")

                elif (input[copy_current_index] == "*" and not is_white_space(input[current_index])):
                    append_error(constant.UNMATCHED_COMMENT, get_lexeme(input, start_index, current_index + 1))
                    current_index += 1
                    start_index = current_index
                else:
                    token = input[copy_current_index]
                    return get_token("SYMBOL", token)

            elif is_in_special_state(1, "number"):
                return get_token("NUM", get_lexeme(input, start_index, current_index))
            elif is_in_special_state(1, "identifier"):
                return get_token("ID", get_lexeme(input, start_index, current_index))
            elif is_in_special_state(1, "comment") and is_star(input[current_index]):
                complete_dfa.current_state += 1
                comment_string += "*"
                current_index += 1

            elif is_in_special_state(2, "comment") and is_star(input[current_index]):
                complete_dfa.current_state += 1
                current_index += 1
            elif is_in_special_state(3, "comment") and is_slash(input[current_index]):
                reset_dfa()
                comment_string = ""
                line_counter = None
                current_index += 1
                start_index = current_index
            else:
                current_index += 1
        elif is_white_space(input[current_index]):
            if is_in_special_state(1, "number"):
                return get_token("NUM", get_lexeme(input, start_index, current_index))
            if is_in_special_state(1, "identifier"):
                return get_token("ID", get_lexeme(input, start_index, current_index))
            current_index += 1
            if is_in_special_state(2, "comment"):
                comment_string += " "
                continue
            start_index = current_index
        elif input[current_index] == '\n':
            copy_current_index = current_index
            current_index += 1
            if is_in_special_state(1, "number"):
                token = get_token("NUM", get_lexeme(input, start_index, copy_current_index))
                return token
            if is_in_special_state(1, "identifier"):
                token = get_token("ID", get_lexeme(input, start_index, copy_current_index))
                return token
            return None
        elif input[current_index] == '\t':
            current_index += 1
            start_index = current_index;
        else:
            if is_in_special_state(2, "comment"):
                current_index += 1
                continue
            append_error("Invalid input", get_lexeme(input, start_index, current_index + 1))
            current_index += 1
            start_index = current_index
    # these codes ore for handling last line in a file
    if current_index - 1 != '\n':
        if is_in_special_state(1, "number"):
            token = get_token("NUM", get_lexeme(input, start_index, current_index))
            return token
        if is_in_special_state(1, "identifier"):
            token = get_token("ID", get_lexeme(input, start_index, current_index))
            return token


file = open("input.txt", "r")
token_file = open("tokens.txt", "a")
symbol_file = open("symbol_table.txt", "a")
lexical_error_file = open("lexical_errors.txt", "a")
complete_dfa = dfa("", 0)
symbols = {';', ':', ',', '[', ']', '(', ')', '{', '}', '+', '-', '*', '=', '<', '/'}
total_errors = []
keywords = {"break", "else", "if", "int", "repeat", "return", "until", "void"}
keywords_and_identifiers = ["break", "else", "if", "int", "repeat", "return", "until", "void"]
current_index = 0
lexical_error = False
counter = 1
comment_string = ""
line_counter = None
for line in file:
    tokens_in_a_line = []
    errors_in_a_line = []
    while current_index != len(line):
        result = get_next_token(line)
        if result != None:
            tokens_in_a_line.append(result)
            print(f"lexeme is :{result.lexeme}")
    if len(tokens_in_a_line) != 0:
        token_file.write(f"{counter}.\t")
        for token in tokens_in_a_line:
            token_file.write(f"({token.type}, {token.lexeme}) ")
        token_file.write("\n")
    if len(errors_in_a_line) != 0:
        if not lexical_error:
            lexical_error = True
        lexical_error_file.write(f"{counter}.\t")
        for error in errors_in_a_line:
            lexical_error_file.write(f"({error.lexeme}, {error.text}) ")
        lexical_error_file.write("\n")
    if (line_counter == None and complete_dfa.type == "comment"):
        line_counter = counter
    counter += 1
    current_index = 0

if complete_dfa.type == "comment":
    error = Error(constant.UNCLOSED_COMMENT, comment_string[:7] + "...")
    lexical_error_file.write(f"{line_counter}.\t({error.lexeme}, {error.text}) ")
    lexical_error_file.write("\n")
    total_errors.append(error)
if not lexical_error:
    lexical_error_file.write("There is no lexical error.")

counter = 1
for symbol in keywords_and_identifiers:
    symbol_file.write(f"{counter}.\t{symbol}")
    symbol_file.write("\n")
    counter += 1
