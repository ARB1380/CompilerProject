import re



def is_symbol_or_blank(input):
    return input == ' ' or input == ';' or input == ':' or input == ',' \
        or input == '[' or input == ']' or input == '(' or input == ')'\
        or input == '{' or input == '}' or input == '+' or input == '-' \
        or input == '=' or input == '*' or input == '<'

def is_symbol(input):
    return input == ';' or input == ':' or input == ',' \
        or input == '[' or input == ']' or input == '(' \
        or input == ')' or input == '{' or input == '}' \
        or input == '+' or input == '-' or input == '*' \
        or input == '=' or input == '<'

def is_number(input):
    return re.search("^[0-9]+$", input) is not None

def is_identifier(input):
    return re.search("[a-zA-Z][a-zA-Z0-9]*",input) is not None

def is_keyword(input):
    return input == "if" or input == "else" or input == "void"\
        or input == "int" or input == "repeat" or input == "break" \
        or input == "until" or input == "return"

def is_invalid_number(input):
    return re.search("[0-9]+[a-zA-Z][0-9a-zA-Z]*", input) is not None

def is_invalid_input(input):
    return re.search("[a-zA-Z0-9]*[^a-zA-Z0-9\s]", input) is not None

def get_next_token(input, right, subString):
    if is_symbol(subString):
        if subString == '=' and input[right + 1] == '=':
            return "(SYMBOL, ==)"
        return f"(SYMBOL,{subString})"
    if is_number(subString):
        return f"(NUM,{subString})"
    if is_invalid_number(subString):
        return f"({subString}, invalid number)"
    if is_keyword(subString):
        return f"(KEYWORD,{subString})"
    if is_identifier(subString):
        return f"(ID,{subString})"
    if is_invalid_input(subString):
        return f"({subString}, invalid input)"
    return None


def get_sub_string(left, right, input):
    subString = input[left: right]
    if len(subString) == 0:
        subString = input[right]
    return subString




def tokenize(input):
    length = len(input)
    left = 0
    right = 0
    while left <= right and right <= length:
        if right != length and not (is_symbol_or_blank(input[right])):
            right = right + 1
        else:
            if left == right == length:
                break

            subString = get_sub_string(left, right, input)
            token = get_next_token(input, right, subString)
            if token == "(SYMBOL,==)":
                left = left + 1
                right = right + 1

            print(token)
            if left == right:
                right = right + 1
            left = right





input ="cde = a;"
tokenize(input)


# file = open("input.txt","r")
# counter = 1
# for line in file:
#     get_next_token(line)
