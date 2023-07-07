def get_str_val(item: list) -> str:
    return ('' if not item[1] else '#' if item[1] == 1 else '@') + str(item[0])


class cede_generator:
    def __init__(self, symbol_table) -> None:
        self.symbol_table = symbol_table
        self.program_block = [[None, None, None, None] for _ in range(100)]  # program block
        self.stack = []  # semantic stack
        self.breaks_link = []  # linked list used for implementation of breaks
        self.current_scope = 0  # scope counter
        self.program_counter = 2  # index of the current line of program block
        self.temp_id = 996  # temp ID
        self.funcs = {}  # code generator functions
        self.token = ''  # next input called as current token
        self.line_counter = 0
        self.line_count = 0
        self.variable = 500
        self.has_break = False
        self.return_size = 0

    # pops an element from stack (used for balancing the statements)
    # returns a temp register
    def get_temp(self) -> int:
        self.temp_id += 4
        return self.temp_id

    def pop(self) -> None:
        self.stack.pop()

    # add a break address to the linked list
    def save_break(self) -> None:
        self.breaks_link.append((self.program_counter, self.current_scope))
        self.program_counter += 1

    # jump if false implementation
    def jpf(self) -> None:
        x = get_str_val(self.stack[-2])
        self.program_block[self.stack.pop()[0]] = ['JPF', x, self.program_counter, None]
        self.stack.pop()

    # used for jumping before entering the else
    def endif(self) -> None:
        x = self.stack.pop()
        if x[1] != 0:
            x = self.stack.pop()

        self.program_block[x[0]] = ['JP', self.program_counter, None, None]

    # handles the while jumps
    def handle_while(self) -> None:
        while self.breaks_link and self.breaks_link[-1][1] == self.current_scope:
            self.program_block[self.breaks_link.pop()[0]] = ['JP', self.program_counter + 1, None, None]
        x = get_str_val(self.stack[-2])
        self.program_block[self.stack.pop()[0]] = ['JPF', x, self.program_counter + 1, None]
        self.stack.pop()
        x = get_str_val(self.stack.pop())
        self.program_block[self.program_counter] = ['JP', x, None, None]
        self.program_counter += 1
        self.current_scope -= 1

    # print the value of top of the stack
    def print_out(self, function_name):
        if function_name != '':
            return
        x = get_str_val(self.stack.pop())
        self.program_block[self.program_counter] = ['PRINT', x, None, None]
        self.program_counter += 1
        self.stack.pop()

    # assign implementation
    def assign(self):
        while (self.return_size != 0):
            x = get_str_val(self.stack.pop())
            y = get_str_val(self.stack[-1])
            self.program_block[self.program_counter] = ['ASSIGN', x, y, None]
            self.program_counter += 1
            self.return_size -= 1
        self.return_size = 0
        self.stack.pop()

    # calculates an operational command (+, -, *, /, <, ==)
    def calc(self, free_address):
        op = self.stack[-2][0]
        t = free_address
        x = get_str_val(self.stack[-3])
        y = get_str_val(self.stack[-1])
        self.program_block[self.program_counter] = [op, x, y, t]
        self.program_counter += 1
        for i in range(3):
            self.stack.pop()
        self.stack.append((t, 0))

    # the next 6 functions push the used operand to the stack
    def less_than(self):
        self.stack.append(('LT', 0))

    def equal(self):
        self.stack.append(('EQ', 0))

    def plus(self):
        self.stack.append(('ADD', 0))

    def minus(self):
        self.stack.append(('SUB', 0))

    def mul(self):
        self.stack.append(('MULT', 0))

    def div(self):
        self.stack.append(('DIV', 0))

    def get_index(self):
        return self.symbol_table[self.token]

    # pushes the ID of the next input (token) to the stack
    def push_id(self):
        self.stack.append((self.get_index(), 0))

    # push a number to the stack
    def push_num(self):
        self.stack.append((int(self.token), 1))

    # indicates that we have entered a new scope
    def push_size(self):
        self.current_scope += 1

    # push the index and go to the next index
    def save(self):
        self.stack.append((self.program_counter, 0))
        self.program_counter += 1

    # just push the index
    def label(self):
        self.stack.append((self.program_counter, 0))

    # push the index and than jpf (used for if-else)
    def save_jpf(self):
        if self.has_break:
            x = get_str_val(self.stack[-3])
            self.program_block[self.stack[-2][0]] = ['JPF', x, self.program_counter + 1, None]
            self.stack.append((self.program_counter, 0))
            self.program_counter += 1
            self.stack.remove(self.stack[-3])
            self.stack.remove(self.stack[-3])
            return

        x = get_str_val(self.stack[-2])
        self.program_block[self.stack.pop()[0]] = ['JPF', x, self.program_counter + 1, None]
        self.stack.pop()
        self.stack.append((self.program_counter, 0))
        self.program_counter += 1

    # push a comparing value of switch expression and case value to the stack
    def case_save(self):
        x = get_str_val(self.stack.pop())
        y = get_str_val(self.stack[-1])
        self.program_block[self.program_counter] = ['EQ', x, y, self.get_temp()]
        self.stack.append((self.program_block[self.program_counter][-1], 0))
        self.program_counter += 1
        self.save()

    # set size of the array
    def arr_declare(self):
        size = self.stack[-1][0]
        # self.symbol_table[self.token] = ((self.stack[-2]), size)
        self.program_block[self.program_counter] = ['ASSIGN', '#0', get_str_val(self.stack[-2]), None]
        self.variable += (size - 1) * 4
        self.program_counter += 1
        self.stack.pop()
        self.stack.pop()

    # we should play with addresses, and we did that in this function
    def arr_access(self):
        t = self.variable
        address = self.stack[-2][0]
        num = self.stack[-1]
        x = ('' if not num[1] else '#' if num[1] == 1 else '@') + str(num[0])
        self.program_block[self.program_counter] = ['MULT', x, '#4', t]
        x = self.stack.pop()
        x = ('' if not x[1] else '#' if x[1] == 1 else '@') + str(x[0])
        self.program_block[self.program_counter + 1] = ['ADD', f'#{address}', t, t]
        self.stack.pop()
        self.variable += 4
        self.stack.append((t, 2))
        self.program_counter += 2

    # filling out breaks which has occurred in the switch statements
    def switch_jump(self):
        while self.breaks_link and self.breaks_link[-1][1] == self.current_scope:
            self.program_block[self.breaks_link.pop()[0]] = ['JP', self.program_counter, None, None]

    def declare_id(self):
        id = self.stack[-1]
        self.program_block[self.program_counter] = ['ASSIGN', '#0', get_str_val(id), None]
        # self.symbol_table[self.token] = ((self.stack[-1]), 1)
        self.stack.pop()
        self.program_counter += 1

    # use for repeat if condition false
    def until(self):
        if self.has_break:
            self.program_block[self.stack[-2][0]] = ['JP', self.program_counter + 1, None, None]
            self.stack.remove(self.stack[-2])

        top = self.stack[-1]
        top2 = self.stack[-2]
        self.program_block[self.program_counter] = ['JPF', get_str_val(top), get_str_val(top2), None]
        self.program_counter += 1
        for i in range(2):
            self.stack.pop()

    def add_call(self):
        self.program_block[0] = ['ASSIGN', '#4', 0, None]
        self.program_block[1] = ['JP', self.program_counter, None, None]
        # befor_list = self.program_block[:]
        # self.program_block = []
        # self.program_block.append(['ASSIGN', '#4', 0, None])
        # # self.program_block.append(['JP', self.line_counter - self.line_count, None, None])
        # self.program_block.append(['JP', self.program_counter, None, None])
        # self.program_block += befor_list
        # self.program_counter += 2


    def break_save(self):
        self.stack.append((self.program_counter, 0))
        self.program_counter += 1
        self.has_break = True

    def save_return(self, address, function_name):
        if function_name == 'main':
            return
        self.program_block[self.program_counter] = ['JP', get_str_val(address), None, None]
        self.program_counter += 1

    def save_return_value(self,address_to_return_value,function_to_information, function_name):
        #address_to_return_value[function_to_information[function_name]['return_value_address']] = self.stack.pop()[0]
        self.program_block[self.program_counter] = ['ASSIGN', get_str_val(self.stack.pop()), function_to_information[function_name]['return_value_address'], None]
        self.program_counter += 1

    def save_params(self, function_to_information, function_name):
        result = []
        while len(self.stack) != 0:
            result.append(self.stack.pop(0))

        result.reverse()
        function_to_information[function_name]['params'] = result
        self.stack = []
        function_to_information[function_name]['start_address'] = self.program_counter

        print(function_to_information[function_name]['params'])

    def call_function(self, function_to_information, function_name):
        if function_name == '':
            return
        parameters = function_to_information[function_name]['params']
        for i in range(len(parameters)):
            x = self.stack.pop()
            self.program_block[self.program_counter] = ['ASSIGN', get_str_val(x), get_str_val(parameters[len(parameters) - 1 - i]), None]
            self.program_counter += 1
        return_address = function_to_information[function_name]['return_address']
        y = (self.program_counter + 2, 1)
        self.program_block[self.program_counter] = ['ASSIGN', get_str_val(y), return_address[0], None]
        self.program_counter += 1
        start_address = function_to_information[function_name]['start_address']
        self.program_block[self.program_counter] = ['JP', start_address, None, None]
        self.program_counter += 1
        if 'return_value_address' in function_to_information[function_name]:
            self.stack.append((function_to_information[function_name]['return_value_address'], 0))



    def remove_function_name_from_stack(self):
        self.stack.pop()














