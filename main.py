import re



def isSymbolOrBlank(input):
    return input == ' ' or input == ';' or input == ':' or input == ',' \
        or input == '[' or input == ']' or input == '(' or input == ')'\
        or input == '{' or input == '}' or input == '+' or input == '-' \
        or input == '=' or input == '*' or input == '<'

def isSymbol(input):
    return input == ';' or input == ':' or input == ',' \
        or input == '[' or input == ']' or input == '(' \
        or input == ')' or input == '{' or input == '}' \
        or input == '+' or input == '-' or input == '*' \
        or input == '=' or input == '<'

def isNumber(input):
    return re.search("^[0-9]+$", input) is not None

def isIdentifier(input):
    return re.search("[a-zA-Z][a-zA-Z0-9]*",input) is not None

def isKeyWord(input):
    return input == "if" or input == "else" or input == "void"\
        or input == "int" or input == "repeat" or input == "break" \
        or input == "until" or input == "return"

def isInvalidNumber(input):
    return re.search("[0-9]+[a-zA-Z][0-9a-zA-Z]*", input) is not None

def isInvalidInput(input):
    return re.search("[a-zA-Z0-9]*[^a-zA-Z0-9\s]", input) is not None

def get_token(input,right,subString):
    if isSymbol(subString):
        if subString == '=' and input[right + 1] == '=':
            return "(SYMBOL, ==)"
        return f"(SYMBOL,{subString})"
    if isNumber(subString):
        return f"(NUM,{subString})"
    if isInvalidNumber(subString):
        return f"({subString}, invalid number)"
    if isKeyWord(subString):
        return f"(KEYWORD,{subString})"
    if isIdentifier(subString):
        return f"(ID,{subString})"
    if isInvalidInput(subString):
        return f"({subString}, invalid input)"
    return None


def get_sub_string(left, right, input):
    subString = input[left: right]
    if len(subString) == 0:
        subString = input[right]
    return subString




def get_next_token(input):
    length = len(input)
    left = 0
    right = 0
    while left <= right and right <= length:
        if right != length and not (isSymbolOrBlank(input[right])):
            right = right + 1
        else:
            if left == right == length:
                break

            subString = get_sub_string(left, right, input)
            token = get_token(input,right,subString)
            if token == "(SYMBOL,==)":
                left = left + 1
                right = right + 1

            print(token)
            if left == right:
                right = right + 1
            left = right





input ="cde = a;"
get_next_token(input)


# file = open("input.txt","r")
# counter = 1
# for line in file:
#     get_next_token(line)
