import re

import constant


class Token:
    def __init__(self, type, lexeme):
        self.type = type
        self.lexeme = lexeme


class Error:
    def __init__(self, value, message):
        self.value = value
        self.message = message


def is_letter_or_digit(input):
    return re.search("[a-zA-Z0-9]", input) is not None


def is_symbol_or_blank(input):
    return input == ' ' or input == ';' or input == ':' or input == ',' \
        or input == '[' or input == ']' or input == '(' or input == ')' \
        or input == '{' or input == '}' or input == '+' or input == '-' \
        or input == '=' or input == '*' or input == '<' or input == '\n'


def is_symbol(input):
    return input == ';' or input == ':' or input == ',' \
        or input == '[' or input == ']' or input == '(' \
        or input == ')' or input == '{' or input == '}' \
        or input == '+' or input == '-' or input == '*' \
        or input == '=' or input == '<' or input == '/'


def is_number(input):
    return re.search("^[0-9]+$", input) is not None


def is_identifier(input):
    return re.search("^[a-zA-Z][a-zA-Z0-9]*$", input) is not None


def is_keyword(input):
    return input == "if" or input == "else" or input == "void" \
        or input == "int" or input == "repeat" or input == "break" \
        or input == "until" or input == "return"


def is_invalid_number(input):
    return re.search("^[0-9]+[a-zA-Z][0-9a-zA-Z]*$", input) is not None


def is_invalid_input(input):
    return re.search("^[a-zA-Z0-9]*[^a-zA-Z0-9\\s]$", input) is not None


def is_unclosed_comment(input):
    return re.search("^[\/\*].*$", input) is not None


def is_unmatched_comment(input):
    return re.search("^[\*\/].*$", input) is not None


def get_next_token(input, right, sub_string):
    if is_symbol(sub_string):
        if sub_string == '=' and input[right + 1] == '=':
            return Token("SYMBOL", "==")
        if sub_string == '/' and input[right + 1] == '*':
            return None
        if sub_string == '*' and input[right + 1] == '/':
            return None
        return Token("SYMBOL", sub_string)

    if is_number(sub_string):
        return Token("NUM", sub_string)

    if is_keyword(sub_string):
        return Token("KEYWORD", sub_string)

    if is_identifier(sub_string):
        return Token("ID", sub_string)

    return None


def get_error(sub_string):
    if is_invalid_number(sub_string):
        return Error(sub_string, constant.INVALID_NUMBER)

    if is_invalid_input(sub_string):
        return Error(sub_string, constant.INVALID_INPUT)

    if is_unclosed_comment(sub_string):
        return Error(sub_string[:7] + "...", constant.UNCLOSED_COMMENT)

    if is_unmatched_comment(sub_string):
        return Error('*/', constant.UNMATCHED_COMMENT)

    return None


def get_sub_string(left, right, input):
    sub_string = input[left: right]
    if len(sub_string) == 0:
        sub_string = input[right]
    else:
        if not (is_symbol_or_blank(input[right])):
            sub_string = f"{sub_string}{input[right]}"
    return sub_string


def add_to_symbol_table(token):
    if token.type == "ID":
        if not (token.lexeme in symbols):
            symbols[token.lexeme] = token.type


def tokenize(input, counter):
    tokens = []
    errors = []
    length = len(input)
    left = 0
    right = 0
    comment = false
    while left <= right <= length:
        if comment and not (input[right] == '*' and input[right + 1] != '/'):
            if right == length:
                sub_string = get_sub_string(left, right, input)
                error = get_error(sub_string)
                if error is not None:
                    errors.append(error)
            right += 1
        elif comment and (input[right] == '*' and input[right + 1] != '/'):
            right += 1
            left = right
        elif right != length and is_letter_or_digit(input[right]):
            right += 1
        else:
            if left == right == length:
                break

            sub_string = get_sub_string(left, right, input)
            token = get_next_token(input, right, sub_string)
            if token is None:
                if input[right] == '/':
                    comment = true
                    continue
                error = get_error(sub_string)
                if error is not None:
                    errors.append(error)
            else:
                tokens.append(token)
                add_to_symbol_table(token)
                if token.lexeme == "==":
                    left += 1
                    right += 1

            if left == right:
                right += 1
            left = right
    if len(tokens) != 0:
        token_file.write(f"{counter}.")
        for token in tokens:
            token_file.write(f"({token.type}, {token.lexeme})")
        token_file.write("\n")
    if len(errors) != 0:
        lexical_error_file.write(f"{counter}.")
        for error in errors:
            lexical_error_file.write(f"({error.value}, {error.message})")
        lexical_error_file.write("\n")


file = open("input.txt", "r")
token_file = open("tokens.txt", "a")
symbol_file = open("symbol_table.txt", "a")
lexical_error_file = open("lexical_errors.txt", "a")
symbols = {"if": "key", "else": "key", "break": "key",
           "until": "key", "void": "key", "int": "key",
           "repeat": "key", "return": "key"}
counter = 1
for line in file:
    tokenize(line, counter)
    counter += 1

counter = 1
for symbol in symbols:
    symbol_file.write(f"{counter}.{symbol}")
    symbol_file.write("\n")
    counter += 1
