import re




def isSymbolOrBlank(input):
    return input == ' ' or input == ';' or input == ':' \
        or input == ',' or input == '[' or input == ']' \
        or input == '(' or input == ')' or input == '{' \
        or input == '}' or input == '+' or input == '-' \
        or input == '*' or input == '=' or input == '<'

def isSymbol(input):
    return input == ';' or input == ':' or input == ',' \
        or input == '[' or input == ']' or input == '(' \
        or input == ')' or input == '{' or input == '}' \
        or input == '+' or input == '-' or input == '*' \
        or input == '=' or input == '<'

def isNumber(input):
    return re.search("[0-9]+", input) is not None

def isIdentifier(input):
    return re.search("[a-zA-Z][a-zA-Z0-9]*",input) is not None


def get_token(left,right,input):
    subString = input[left: right]
    if isNumber(subString):
        return f"(NUM,{subString})"
    if isIdentifier(subString):
        return f"(ID,{subString})"




def get_next_token(input):
    length = len(input)
    left = 0
    right = 0
    while left <= right and right <= length:
        if right != length and not(isSymbolOrBlank(input[right])):
            right = right + 1
        else:
            if left == right:
                if left == length:
                    break
                if isSymbolOrBlank(input[right]):
                    print(f"symbol recognized!{input[right]}")
                right = right + 1
                left = right
            else:
                token = get_token(left,right,input)
                print(token)
                left = right





input ="+="
get_next_token(input)


# file = open("input.txt","r")
# counter = 1
# for line in file:
#     get_next_token(line)
