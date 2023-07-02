class SymbolTable:
    def __init__(self):
        self.symbol_table = {}

    def add_to_symbol_table(self, lexeme, address):
        self.symbol_table[lexeme] = address

    def get_address(self, lexeme):
        return self.symbol_table[lexeme]