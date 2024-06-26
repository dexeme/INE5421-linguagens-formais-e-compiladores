from dataclasses import dataclass, field, replace
from typing import List

@dataclass
class Rule:
    symbol: str = field(default=None, repr=False)
    productions: List[str] = field(default_factory=list, repr=False)
    
    @property
    def nullable(self):
        return "&" in self.productions  
    
@dataclass
class Grammar:
    rules: List[Rule] = field(default_factory=list, repr=False)
    start_symbol: str = field(default=None, repr=False)
    _nullables: set = field(default_factory=set, repr=False)

    @property
    def non_terminals(self):
        return {rule.symbol 
                for rule in self.rules}
    
    @property
    def terminals(self):
        return {symbol for rule in self.rules 
                for production in rule.productions 
                    for symbol in production
                        if symbol not in self.non_terminals 
                            and symbol != ""}
    
    def direct_nullables(self):
            for rule in self.rules:
                if rule.nullable:
                    self._nullables.add(rule.symbol)
            return self._nullables
        
    def indirect_nullables(self):
        while True:
            new_nullables = set()
            for rule in self.rules:
                if rule.symbol not in self._nullables:
                    for production in rule.productions:
                        if all(symbol in self._nullables for symbol in production):
                            new_nullables.add(rule.symbol)
                            break
            if not new_nullables:
                break
            self._nullables.update(new_nullables)
        return self._nullables
    
    @property
    def nullables(self):
        # Atualiza os nulos diretos e indiretos
        self.direct_nullables()
        self.indirect_nullables()
        return self._nullables
    
    @property
    def create_prods_combinations(self):
        new_rules = []
        for rule in self.rules:
            for production in rule.productions:
                new_productions = []
                new_productions.append(production)
                is_nullable = all(symbol in self._nullables for symbol in production)
                if is_nullable:
                    new_productions.append("&")
                for i, symbol in enumerate(production):
                    if symbol in self._nullables:
                        new_production = production[:i] + production[i+1:]
                        new_productions.append(new_production)
                        print(new_productions)
            new_rules.append(replace(rule, productions=new_productions))

        return new_rules


def parse(input_str: str) -> Grammar:
    rules = []
    start_symbol = None
    for line in input_str.strip().split('\n'):
        symbol, productions = line.strip().split(' -> ')
        if not start_symbol:
            start_symbol = symbol
        rules.append(Rule(symbol, productions.split(' | ')))
    return Grammar(rules, start_symbol)


# Test if the grammar is correct
def test_parse():
    input_str = """
    S -> ABC
    A -> aAA | aAB | BC
    B -> bBS | bBC | &
    C -> cC | &
    """
    grammar = parse(input_str)
    print(grammar)
    print(grammar.non_terminals)
    print(grammar.terminals)
    print(grammar.nullables)   
    print(grammar.create_prods_combinations)

test_parse()

