from collections import defaultdict

EPSILON = "&"

class GrammarParser:
    def __init__(self):
        self.alphabet = []
        self.nonterminals = []
        self.terminals = []
        self.rules = []
        self.firsts = defaultdict(list)
        self.follows = defaultdict(list)
        self.rule_table = defaultdict(lambda: defaultdict(str))
        
    def grammar_changed(self, grammar_text):
        self.rules = [line.strip() for line in grammar_text.strip().split('\n') if line.strip()]
        self.alphabet = []
        self.nonterminals = []
        self.terminals = []
        
        self.collect_alphabet_and_nonterminals_and_terminals()
        self.collect_firsts()
        self.collect_follows()
        self.make_rule_table()
        
        return self.display_table()

    def display_table(self):
        headers = ["NT", "FIRST", "FOLLOW"] + self.terminals + ["$"]
        table = [headers]
        
        for nonterminal in self.nonterminals:
            row = [
                nonterminal,
                "{" + ', '.join(self.firsts[nonterminal]) + "}",
                "{" + ', '.join(self.follows[nonterminal]) + "}"
            ]
            for terminal in self.terminals:
                production_number = self.rule_table[nonterminal][terminal]
                row.append(production_number)
            production_number = self.rule_table[nonterminal]['$']
            row.append(production_number)
            table.append(row)
        
        return self.format_table(table)

    def format_table(self, table):
        col_widths = [max(len(cell) for cell in col) for col in zip(*table)]
        row_format = " | ".join("{:<" + str(width) + "}" for width in col_widths)
        
        lines = [row_format.format(*table[0])]
        lines.append("-+-".join('-' * width for width in col_widths))
        for row in table[1:]:
            lines.append(row_format.format(*row))
        
        return "\n".join(lines)

    def make_rule_table(self):
        self.rule_table = defaultdict(lambda: defaultdict(str))
        
        for idx, rule in enumerate(self.rules):
            nonterminal, development = map(str.strip, rule.split('->'))
            development = self.trim_elements(development.split())
            development_firsts = self.collect_firsts3(development)
            rule_number = str(idx + 1)
            
            for symbol in development_firsts:
                if symbol != EPSILON:
                    self.rule_table[nonterminal][symbol] = rule_number
                else:
                    for symbol2 in self.follows[nonterminal]:
                        self.rule_table[nonterminal][symbol2] = rule_number

    def collect_firsts(self):
        not_done = True
        
        while not_done:
            not_done = False
            
            for rule in self.rules:
                nonterminal, development = map(str.strip, rule.split('->'))
                development = self.trim_elements(development.split())
                
                if development == [EPSILON]:
                    not_done |= self.add_unique(EPSILON, self.firsts[nonterminal])
                else:
                    not_done |= self.collect_firsts4(development, nonterminal)

    def collect_firsts4(self, development, nonterminal_firsts):
        result = False
        epsilon_in_symbol_firsts = True
        
        for symbol in development:
            epsilon_in_symbol_firsts = False

            if symbol in self.terminals:
                result |= self.add_unique(symbol, self.firsts[nonterminal_firsts])
                break
            
            for first in self.firsts[symbol]:
                epsilon_in_symbol_firsts |= first == EPSILON
                result |= self.add_unique(first, self.firsts[nonterminal_firsts])
            
            if not epsilon_in_symbol_firsts:
                break
        
        if epsilon_in_symbol_firsts:
            result |= self.add_unique(EPSILON, self.firsts[nonterminal_firsts])
        
        return result

    def collect_firsts3(self, sequence):
        result = []
        epsilon_in_symbol_firsts = True
        
        for symbol in sequence:
            epsilon_in_symbol_firsts = False
            
            if symbol in self.terminals:
                self.add_unique(symbol, result)
                break
            
            for first in self.firsts[symbol]:
                epsilon_in_symbol_firsts |= first == EPSILON
                self.add_unique(first, result)
            
            epsilon_in_symbol_firsts |= not self.firsts[symbol]
            
            if not epsilon_in_symbol_firsts:
                break
        
        if epsilon_in_symbol_firsts:
            self.add_unique(EPSILON, result)
        
        return result

    def collect_follows(self):
        not_done = True
        
        while not_done:
            not_done = False
            
            for i, rule in enumerate(self.rules):
                nonterminal, development = map(str.strip, rule.split('->'))
                development = self.trim_elements(development.split())
                
                if i == 0:
                    not_done |= self.add_unique('$', self.follows[nonterminal])
                
                for j, symbol in enumerate(development):
                    if symbol in self.nonterminals:
                        after_symbol_firsts = self.collect_firsts3(development[j + 1:])
                        
                        for first in after_symbol_firsts:
                            if first == EPSILON:
                                for follow in self.follows[nonterminal]:
                                    not_done |= self.add_unique(follow, self.follows[symbol])
                            else:
                                not_done |= self.add_unique(first, self.follows[symbol])

    def collect_alphabet_and_nonterminals_and_terminals(self):
        for rule in self.rules:
            nonterminal, development = map(str.strip, rule.split('->'))
            development = self.trim_elements(development.split())
            
            self.add_unique(nonterminal, self.alphabet)
            self.add_unique(nonterminal, self.nonterminals)
            
            for symbol in development:
                if symbol != EPSILON:
                    self.add_unique(symbol, self.alphabet)
        
        terminals_set = set(self.nonterminals)
        self.terminals = [symbol for symbol in self.alphabet if symbol not in terminals_set]

    def trim_elements(self, array):
        return [x.strip() for x in array]

    def is_element(self, element, array):
        return element in array

    def add_unique(self, element, array):
        if element not in array:
            array.append(element)
            return True
        return False

    def print_formatted_output(self):
        sorted_nonterminals = sorted(self.nonterminals)
        sorted_terminals = sorted(self.terminals) + ['$']
        
        nt_set = "{" + ','.join(sorted_nonterminals) + "}"
        epsilon_nonterminals = "E" if EPSILON in self.nonterminals else ""
        term_set = "{" + ','.join(sorted_terminals) + "}"
        
        rule_mappings = []
        for nonterminal in sorted_nonterminals:
            for terminal in sorted_terminals:
                production_number = self.rule_table[nonterminal][terminal]
                if production_number:
                    rule_mappings.append(f"[{nonterminal},{terminal},{production_number}]")
        
        initial_nonterminal = self.rules[0].split('->')[0].strip()
        
        formatted_output = f"{nt_set};{initial_nonterminal};{term_set};" + ''.join(rule_mappings)
        print(formatted_output)

def parse_grammar(input_text):
    rules = [rule.strip() for rule in input_text.split(';') if rule.strip()]
    
    grammar_text = []
    
    for rule in rules:
        if '=' not in rule:
            continue
        
        left_side, right_side = rule.split('=')
        left_side = left_side.strip()
        right_side = right_side.strip()
        
        right_side = ' '.join(right_side)
        
        grammar_text.append(f"{left_side} -> {right_side}")
    
    return "\n".join(grammar_text)

def print_parsed_grammar(parsed_grammar):
    print("Gramática de entrada:")
    for i, rule in enumerate(parsed_grammar.split('\n'), 1):
        print(f"{i}. {rule}")

def main():
    parser = GrammarParser()
    input_text = input()
    parsed_grammar = parse_grammar(input_text)
    print_parsed_grammar(parsed_grammar)
    print("\nLL(1) Parsing Table:")
    table = parser.grammar_changed(parsed_grammar)
    print(table)
    print("\nResposta final:")
    parser.print_formatted_output()

if __name__ == "__main__":
    main()