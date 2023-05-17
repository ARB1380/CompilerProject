# Mohammad Mahdi Mirzaei 99171022
# Alireza Farshi 99101976

import re
import json
from anytree import Node, RenderTree

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
    if character in symbols_x:
        return True
    return False


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
    #errors_in_a_line.append(Error(text, lexeme))


def get_lexeme(input, start_index, end_index):
    return input[start_index: end_index]


def is_invalid_character(character):
    return not is_digit(character) and not is_letter(character) and not is_symbol(character) and not is_white_space(
        character)


def get_next_token(input):
    global current_index, comment_string, line_counter
    start_index = current_index
    while current_index != len(input):
        temp = input[current_index]
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
            start_index = current_index
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
    # if current_index - 1 != '\n':
    #     if is_in_special_state(1, "number"):
    #         token = get_token("NUM", get_lexeme(input, start_index, current_index))
    #         return token
    #     if is_in_special_state(1, "identifier"):
    #         token = get_token("ID", get_lexeme(input, start_index, current_index))
    #         return token


file = open("input.txt", "r")
input1 = file.read()
# token_file = open("tokens.txt", "a")
# symbol_file = open("symbol_table.txt", "a")
# lexical_error_file = open("lexical_errors.txt", "a")
complete_dfa = dfa("", 0)
symbols_x = {';', ':', ',', '[', ']', '(', ')', '{', '}', '+', '-', '*', '=', '<', '/'}

# total_errors = []
keywords = {"break", "else", "if", "int", "repeat", "return", "until", "void"}
keywords_and_identifiers = ["break", "else", "if", "int", "repeat", "return", "until", "void"]
current_index = 0
# lexical_error = False
# counter = 1
comment_string = ""
# line_counter = None
# for line in file:
#     tokens_in_a_line = []
#     errors_in_a_line = []
#     while current_index != len(line):
#         result = get_next_token(line)
#         if result != None:
#             tokens_in_a_line.append(result)
#             print(f"lexeme is :{result.lexeme}")
#     if len(tokens_in_a_line) != 0:
#         token_file.write(f"{counter}.\t")
#         for token in tokens_in_a_line:
#             token_file.write(f"({token.type}, {token.lexeme}) ")
#         token_file.write("\n")
#     if len(errors_in_a_line) != 0:
#         if not lexical_error:
#             lexical_error = True
#         lexical_error_file.write(f"{counter}.\t")
#         for error in errors_in_a_line:
#             lexical_error_file.write(f"({error.lexeme}, {error.text}) ")
#         lexical_error_file.write("\n")
#     if (line_counter == None and complete_dfa.type == "comment"):
#         line_counter = counter
#     counter += 1
#     current_index = 0
#
# if complete_dfa.type == "comment":
#     error = Error(constant.UNCLOSED_COMMENT, comment_string[:7] + "...")
#     lexical_error_file.write(f"{line_counter}.\t({error.lexeme}, {error.text}) ")
#     lexical_error_file.write("\n")
#     total_errors.append(error)
# if not lexical_error:
#     lexical_error_file.write("There is no lexical error.")
#
# counter = 1
# for symbol in keywords_and_identifiers:
#     symbol_file.write(f"{counter}.\t{symbol}")
#     symbol_file.write("\n")
#     counter += 1



# parser code
f = open('data.json')
data = json.load(f)
terminals = data['terminals']
non_terminals = data['non-terminal']
first_dict = data['first']
follow_dict = data['follow']
parse_table = {}
rule_file = open('rules.txt')
lines = rule_file.readlines()
rules = {}
for line in lines:
    line = line.strip()
    rule = line.split('->')
    rules[rule[0]] = rule[1]
parse_table = {}
for non_terminal, productions in rules.items():
    non_terminal = non_terminal.strip()
    productions = productions.strip()

    for production in productions.split('|'):
        production = production.strip()
        symbols = production.split(' ')
        if symbols[0] in terminals:
            parse_table[(non_terminal, symbols[0])] = production
        else:
            if symbols[0] == "EPSILON":
                for terminal in follow_dict[non_terminal]:
                    parse_table[(non_terminal, terminal)] = "EPSILON"
            else:
                for terminal in first_dict[symbols[0]]:
                    if terminal != "EPSILON":
                        parse_table[(non_terminal, terminal)] = production
                if "EPSILON" in first_dict[symbols[0]]:
                    for i in range(1, len(symbols)):
                        for terminal in first_dict[symbols[i]]:
                            if terminal != 'EPSILON' and (non_terminal,terminal) not in parse_table:
                                parse_table[(non_terminal, terminal)] = production
                        if "EPSILON" not in symbols[i]:
                            break

                    moves_to_epsilon = True
                    for symbol in symbols:
                        if symbol in terminals or "EPSILON" not in first_dict[symbols[0]]:
                            moves_to_epsilon = False
                            break
                    if moves_to_epsilon:
                        for terminal in follow_dict[non_terminal]:
                            parse_table[(non_terminal, terminal)] = production
stack = []
start_node = Node("Program")
end_node = Node("$", parent=start_node)
stack.append(end_node)
stack.append(start_node)
token = get_next_token(input1)
while len(stack) != 0:
    node = stack[len(stack) - 1]
    if node.name in non_terminals:
        action = ""
        if token.type == "NUM" or token.type == "ID":
            action = parse_table[(node.name, token.type)]
        else:
            action = parse_table[(node.name, token.lexeme)]
        action = action.split(' ')
        removed_node = stack.pop()
        for i in range(len(action)):
            if action[len(action) -1 - i] != "EPSILON":
                stack.append(Node(action[len(action) - 1 - i], parent=removed_node))
            else:
                epsilon_node = Node("epsilon", parent=removed_node)

    elif node.name in terminals:
        removed_token = stack.pop()
        removed_token.name = token
        print(f'removed token is :{removed_token.name.lexeme}')
        token = get_next_token(input1)
    else:
        stack.pop()

for pre, fill, node in RenderTree(start_node):
    print("%s%s" % (pre, node.name))











# first_set = {
#     'Type': ['id', 'array', 'integer', 'char', 'num'],
#     'Simple': ['integer', 'char', 'num']
# }
#
# follow_set = {
#     'Type': ['$'],
#     'Simple': ['$', ']']
# }
# nodes = []
# nodes_value = []
#
#
# def Type():
#     if lookahead in first_set['Simple']:
#         nodes.append(Node("simple", parent= nodes[get_parent("type")]))
#         nodes_value.append("simple")
#         Simple()
#     elif lookahead == 'id':
#         nodes.append(Node("id", parent=nodes[get_parent("type")]))
#         nodes_value.append("id")
#         Match('id')
#     elif lookahead == 'array':
#         nodes.append(Node("array", parent= nodes[get_parent("type")]))
#         nodes_value.append("array")
#         Match('array')
#         nodes.append(Node("[", parent=nodes[get_parent("type")]))
#         nodes_value.append("[")
#         Match('[')
#         nodes.append(Node("simple", parent=nodes[get_parent("type")]))
#         nodes_value.append("simple")
#         Simple()
#         nodes.append(Node("]", parent=nodes[get_parent("type")]))
#         nodes_value.append("]")
#         Match(']')
#         nodes.append(Node("of", parent=nodes[get_parent("type")]))
#         nodes_value.append("of")
#         Match('of')
#         nodes.append(Node("type", parent=nodes[get_parent("type")]))
#         nodes_value.append("type")
#         Type()
#
#
#
#
#
# def Simple():
#     if lookahead == 'integer':
#         nodes.append(Node("integer", parent=nodes[get_parent("simple")]))
#         nodes_value.append("integer")
#         Match('integer')
#     elif lookahead == 'char':
#         nodes.append(Node("char", parent=nodes[get_parent("simple")]))
#         nodes_value.append("char")
#         Match('char')
#     elif lookahead == 'num':
#         nodes.append(Node("num", parent=nodes[get_parent("simple")]))
#         nodes_value.append("num")
#         Match('num')
#         nodes.append(Node("dotdot", parent=nodes[get_parent("simple")]))
#         nodes_value.append("dotdot")
#         Match('dotdot')
#         nodes.append(Node("num", parent=nodes[get_parent("simple")]))
#         nodes_value.append("num")
#         Match('num')
#
# def Match(expected_token):
#     global lookahead
#     if lookahead == expected_token:
#         token = get_next_token(input)
#         if token != None:
#             lookahead = token.lexeme
#
#
#
# def get_parent(value):
#     for i in range(len(nodes_value) - 1, -1, -1):
#         if nodes_value[i] == value:
#             return i
#         continue
#
#
# input = "array [ num dotdot num ] of integer"
# lookahead = "array"
# start_node = Node("type")
# nodes.append(start_node)
# nodes_value.append("type")
# Type()
