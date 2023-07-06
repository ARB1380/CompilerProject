# Mohammad Mahdi Mirzaei 99171022
# Alireza Farshi 99101976

import string
from anytree import Node, RenderTree
import json

import constant
from SymbolTable import SymbolTable
from cede_generator import cede_generator
from dfa import dfa
from Token import Token


def is_digit(character):
    return (character == '0' or
            character == '1' or
            character == '2' or
            character == '3' or
            character == '4' or
            character == '5' or
            character == '6' or
            character == '7' or
            character == '8' or
            character == '9')


def is_letter(character):
    small_alphabet = list(string.ascii_lowercase)
    big_alphabet = list(string.ascii_uppercase)
    return character in small_alphabet or character in big_alphabet


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
        if lexeme not in sym.symbol_table:
            sym.symbol_table[lexeme] = get_free_address()
        return Token("KEYWORD", lexeme)
    if type == "ID" and not lexeme in sym.symbol_table and not lexeme == 'main':
        sym.symbol_table[lexeme] = get_free_address()
    return Token(type, lexeme)


def append_error(text, lexeme):
    reset_dfa()
    # errors_in_a_line.append(Error(text, lexeme))


def get_lexeme(input, start_index, end_index):
    return input[start_index: end_index]


def is_invalid_character(character):
    return not is_digit(character) and not is_letter(character) and not is_symbol(character) and not is_white_space(
        character)


def get_next_token(input):
    global current_index, comment_string, line_counter, next_line, line_count
    start_index = current_index
    line_counter = next_line
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

                # elif (input[copy_current_index] == "*" and not is_white_space(input[current_index])):
                #     append_error(constant.UNMATCHED_COMMENT, get_lexeme(input, start_index, current_index + 1))
                #     current_index += 1
                #     start_index = current_index
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
            if (current_index == start_index):
                line_counter += 1
                next_line += 1
                if (input[current_index - 1] == '\n'):
                    line_count += 1
            else:
                next_line += 1
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
    return get_token("X", "$")


action_symbols = ['#p_id', '#declare_id', '#assign', '#p_num', '#add', '#cal', '#mul', '#sub', '#less_than',
                  '#declare_arr', '#test', '#label', '#until', '#save', '#save_jpf', '#jp', '#print', '#equal',
                  '#break_save', '#test2', '#test3', '#test5', '#start_get_var', '#end_get_var', '#add_empty_block']


def is_action_symbol(action):
    return action in action_symbols


def call_action_symbol_routine(action_symbol):
    global free_address
    if action_symbol == '#p_id':
        if look_ahead.lexeme == 'main':
            code_generator.line_counter = line_counter
            code_generator.line_count = line_count
            code_generator.add_call()
            return
        code_generator.token = look_ahead.lexeme
        code_generator.push_id()
    if action_symbol == '#declare_id':
        code_generator.declare_id()
    if action_symbol == '#assign':
        if len(code_generator.stack) < 2:
            return
        code_generator.assign()
    if action_symbol == '#p_num':
        code_generator.token = look_ahead.lexeme
        code_generator.push_num()
    if action_symbol == '#add':
        code_generator.plus()
    if action_symbol == '#mul':
        code_generator.mul()
    if action_symbol == '#sub':
        code_generator.minus()
    if action_symbol == '#less_than':
        code_generator.less_than()
    if action_symbol == '#cal':
        code_generator.calc(get_free_address())
    if action_symbol == '#declare_arr':
        code_generator.variable = free_address
        code_generator.arr_declare()
        free_address = code_generator.variable
    if action_symbol == '#test':
        code_generator.variable = free_address
        code_generator.arr_access()
        free_address = code_generator.variable
    if action_symbol == '#test2':
        code_generator.number_of_assign_var += 1
        # for declare a simple param
    if action_symbol == '#test3':
        code_generator.number_of_assign_var += 1
        # for declare param list
    if action_symbol == '#test5':
        # this action for count number of var pass to func
        code_generator.number_of_input_var += 1
    if action_symbol == '#label':
        code_generator.label()
    if action_symbol == '#until':
        code_generator.until()
    if action_symbol == '#save':
        code_generator.save()
    if action_symbol == '#save_jpf':
        code_generator.save_jpf()
    if action_symbol == '#jp':
        code_generator.endif()
    if action_symbol == '#print':
        code_generator.print_out()
    if action_symbol == '#equal':
        code_generator.equal()
    if action_symbol == '#break_save':
        code_generator.break_save()
    if action_symbol == '#start_get_var':
        code_generator.is_input_var = True
    if action_symbol == '#end_get_var':
        code_generator.is_input_var = False
    if action_symbol == '#add_empty_block':
        code_generator.add_empty_block()


def start_parse(node):
    global look_ahead
    global has_eof_error
    global free_address
    if node.name in terminals:
        if node.name == 'NUM' or node.name == 'ID':
            if look_ahead.type != node.name:
                errors.append(f"#{line_counter} : syntax error, missing {node.name}")
                node.parent = None
            else:
                node.name = f'({look_ahead.type}, {look_ahead.lexeme})'
                look_ahead = get_next_token(input1)
                print(look_ahead.lexeme)
                if look_ahead.lexeme == '=':
                    code_generator.return_size += 1
        else:
            if look_ahead.lexeme != node.name:
                errors.append(f"#{line_counter} : syntax error, missing {node.name}")
                node.parent = None
            else:
                node.name = f'({look_ahead.type}, {look_ahead.lexeme})'
                look_ahead = get_next_token(input1)
                print(look_ahead.lexeme)
                if look_ahead.lexeme == '=':
                    code_generator.return_size += 1
        return
    if node.name == "epsilon":
        return
    rule = get_rule(node.name, look_ahead)
    # panic mode to be added
    while rule == None:
        if look_ahead.type == 'NUM' or look_ahead.type == 'ID':
            if look_ahead.type not in follow_dict[node.name]:
                errors.append(f"#{line_counter} : syntax error, illegal {look_ahead.type}")
                look_ahead = get_next_token(input1)
                rule = get_rule(node.name, look_ahead)
                print(look_ahead.lexeme)
                if look_ahead.lexeme == '=':
                    code_generator.return_size += 1
            else:
                errors.append(f"#{line_counter} : syntax error, missing {node.name}")
                node.parent = None
                return
        else:
            if look_ahead.lexeme not in follow_dict[node.name]:
                if look_ahead.lexeme == '$' and node.name != '$':
                    errors.append(f"#{line_counter} : syntax error, Unexpected EOF")
                    has_eof_error = True
                    node.parent = None
                    return
                else:
                    errors.append(f"#{line_counter} : syntax error, illegal {look_ahead.lexeme}")
                    look_ahead = get_next_token(input1)
                    print(look_ahead.lexeme)
                    if look_ahead.lexeme == '=':
                        code_generator.return_size += 1
                    rule = get_rule(node.name, look_ahead)
            else:
                errors.append(f"#{line_counter} : syntax error, missing {node.name}")
                node.parent = None
                return

    for action in rule.split(' '):
        if is_action_symbol(action):
            call_action_symbol_routine(action)
            continue

        if look_ahead.lexeme == '$' and has_eof_error:
            return

        new_node = Node(action, parent=node)
        if action == 'EPSILON':
            new_node.name = 'epsilon'

        start_parse(new_node)
    return


def get_rule(non_terminal, token):
    productions = rules[non_terminal]
    symbols = productions.split('|')
    symbols = [item for item in symbols if not item.startswith('#')]
    for production in symbols:
        production = production.strip()
        if production != "EPSILON" and is_in_first_of_production(token, production):
            return production
        if is_in_follow_of_production(token, non_terminal, production):
            return production

    return None


def is_in_first_of_production(token, production):
    symbols = production.split(' ')
    symbols = [item for item in symbols if not item.startswith('#')]
    for symbol in symbols:
        if symbol in terminals:
            if token.type == "ID" or token.type == "NUM":
                return symbol == token.type
            return symbol == token.lexeme

        else:
            if token.type == "ID" or token.type == "NUM":
                if token.type in first_dict[symbol]:
                    return True
            if token.lexeme in first_dict[symbol]:
                return True
            if "EPSILON" not in first_dict[symbol]:
                return False


def is_in_follow_of_production(token, non_terminal, production):
    if moves_to_epsilon(production):
        if token.type == "ID" or token.type == "NUM":
            return token.type in follow_dict[non_terminal]
        return token.lexeme in follow_dict[non_terminal]
    return False


def moves_to_epsilon(production):
    if production == "EPSILON":
        return True
    symbols = production.split(' ')
    symbols = [item for item in symbols if not item.startswith('#')]
    for symbol in symbols:
        if symbol in terminals:
            return False
        if "EPSILON" not in first_dict[symbol]:
            return False
    return True


def get_free_address():
    global free_address
    result1 = free_address
    free_address += 4
    return result1


file = open("input.txt", "r")
input1 = file.read()
line_counter = 1
line_count = 0
next_line = 1
# token_file = open("tokens.txt", "a")
# symbol_file = open("symbol_table.txt", "a")
# lexical_error_file = open("lexical_errors.txt", "a")
complete_dfa = dfa("", 0)
symbols_x = {';', ':', ',', '[', ']', '(', ')', '{', '}', '+', '-', '*', '=', '<', '/'}

# total_errors = []
keywords = {"break", "else", "if", "int", "repeat", "return", "until", "void"}
sym = SymbolTable()
free_address = 500
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
    rules[rule[0].strip()] = rule[1].strip()

start_node = Node('Program')
look_ahead = ""
look_ahead = get_next_token(input1)
errors = []
has_eof_error = False
code_generator = cede_generator(sym.symbol_table)  # todo : fix
start_parse(start_node)
if not has_eof_error:
    end_node = Node("$", parent=start_node)

# for non_terminal, productions in rules.items():
#     non_terminal = non_terminal.strip()
#     productions = productions.strip()
#
#     for production in productions.split('|'):
#         production = production.strip()
#         symbols = production.split(' ')
#         if symbols[0] in terminals:
#             parse_table[(non_terminal, symbols[0])] = production
#         else:
#             if symbols[0] == "EPSILON":
#                 for terminal in follow_dict[non_terminal]:
#                     parse_table[(non_terminal, terminal)] = "EPSILON"
#             else:
#                 for terminal in first_dict[symbols[0]]:
#                     if terminal != "EPSILON":
#                         parse_table[(non_terminal, terminal)] = production
#                 if "EPSILON" in first_dict[symbols[0]]:
#                     for i in range(1, len(symbols)):
#                         if non_terminal == 'H':
#                             w = 0
#                         for terminal in first_dict[symbols[i]]:
#                             if terminal != 'EPSILON' and (non_terminal, terminal) not in parse_table:
#                                 parse_table[(non_terminal, terminal)] = production
#                         if "EPSILON" not in first_dict[symbols[i]]:
#                             break
#
#                     moves_to_epsilon = True
#                     for symbol in symbols:
#                         if symbol in terminals or "EPSILON" not in first_dict[symbols[0]]:
#                             moves_to_epsilon = False
#                             break
#                     if moves_to_epsilon:
#                         for terminal in follow_dict[non_terminal]:
#                             parse_table[(non_terminal, terminal)] = production
# for i in non_terminals:
#     for j in follow_dict.get(i):
#         if (i, j) not in parse_table:
#             parse_table[(i, j)] = 'SYNCH'
#
#
# error_text = []
# stack = []
# start_node = Node("Program")
# end_node = Node("$")
# stack.append(start_node)
# stack.append(end_node)
# stack.reverse()
# token = get_next_token(input1)
# while len(stack) != 0:
#     node = stack[len(stack) - 1]
#     if node.name in non_terminals:
#         action = ""
#         if (token.type == "ID" or token.type == "NUM"):
#             if (node.name, token.type) not in parse_table:
#                 error_text.append(f"#{line_counter} : syntax error, illegal {token.type}")
#                 token = get_next_token(input1)
#                 continue
#             if parse_table[(node.name, token.type)] == "SYNCH":
#                 error_text.append(f"#{line_counter} : syntax error, missing {node.name}")
#                 removed_token = stack.pop()
#                 removed_token.parent = None
#                 continue
#             action = parse_table[(node.name, token.type)]
#
#         else:
#             if (node.name, token.lexeme) not in parse_table:
#                 if token.lexeme == '$' and node.name != '$':
#                     error_text.append(f"#{line_counter} : syntax error, Unexpected EOF")
#                     break
#                 error_text.append(f"#{line_counter} : syntax error, illegal {token.lexeme}")
#                 token = get_next_token(input1)
#                 continue
#             if parse_table[(node.name, token.lexeme)] == "SYNCH":
#                 error_text.append(f"#{line_counter} : syntax error, missing {node.name}")
#                 removed_token = stack.pop()
#                 removed_token.parent = None
#                 continue
#             action = parse_table[(node.name, token.lexeme)]
#         action = action.split(' ')
#         removed_node = stack.pop()
#         nodes_to_add = []
#         for i in range(len(action)):
#             if action[i] != "EPSILON":
#                 nodes_to_add.append(Node(action[i], parent=removed_node))
#             else:
#                 epsilon_node = Node("epsilon", parent=removed_node)
#         for i in range(len(nodes_to_add)):
#             stack.append(nodes_to_add[len(nodes_to_add) - 1 - i])
#
#     elif node.name in terminals:
#         removed_token = stack.pop()
#         if (removed_token.name == 'NUM' or removed_token.name == "ID"):
#             if (removed_token.name != token.type):
#                 removed_token.parent = None
#                 error_text.append(f"#{line_counter} : syntax error, missing {removed_token.name}")
#                 continue
#         elif (removed_token.name != token.lexeme):
#             removed_token.parent = None
#             error_text.append(f"#{line_counter} : syntax error, missing {removed_token.name}")
#             continue
#         removed_token.name = f'({token.type}, {token.lexeme})'
#         token = get_next_token(input1)
#
#     else:
#         stack.pop()
# end_node.parent = start_node
# for i in stack:
#     i.parent = None

file = open("parse_tree.txt", "w", encoding="utf-8")
result = ""
for pre, _, node in RenderTree(start_node):
    result += ("%s%s" % (pre, node.name)) + "\n"
result = result[:-1]
file.write(result)
file.close()
file = open("output.txt", "w", encoding="utf-8")
for i in range(len(code_generator.program_block)):
    var0 = code_generator.program_block[i][0]
    if var0 is None:
        break
    var1 = code_generator.program_block[i][1]
    var2 = code_generator.program_block[i][2] if code_generator.program_block[i][2] is not None else ' '
    var3 = code_generator.program_block[i][3] if code_generator.program_block[i][3] is not None else ' '
    file.write(f"{i}\t({var0}, {var1}, {var2}, {var3} )\n")
file.close()
file = open("syntax_errors.txt", "w")
if len(errors) == 0:
    file.write("There is no syntax error.")
else:
    for i in range(len(errors)):
        # if (i == len(errors) - 1):
        #     file.write(f"{errors[i]}")
        # else:
        file.write(f"{errors[i]}\n")
