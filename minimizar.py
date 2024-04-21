from typing import Dict, FrozenSet, Set, List

State = FrozenSet[str]

class FDA:
    def __init__(self, string: str="") -> None:
        self.string: str = string
        self.initial_state: State = None
        self.transitions: Dict[State, Dict[str, FrozenSet[State]]] = {}
        self.final_states: FrozenSet[State] = frozenset()
        self.current_state: State = None
        self.states: FrozenSet[State] = frozenset((frozenset(("qm",)),))
        self.num_states: int = 0
        self.alphabet: Set[chr] = set()
        if self.string: self.parse()
    
    def compute(self, symbol: chr) -> None:
        if self.current_state is None: self.current_state = self.initial_state
        if self.current_state == 'qm': return
        if self.current_state not in self.transitions or symbol not in self.transitions[self.current_state]:
            self.current_state = 'qm'
            return
        self.current_state = self.transitions[self.current_state][symbol]

    def extended_compute(self, string: str) -> bool:
        for symbol in string: self.compute(symbol)
        return self.current_state in self.final_states

    def parse(self) -> None:
        temp_states = set()
        num_states, initial_state, final_states, alphabet, *transitions = self.string.split(';')
        self.num_states = int(num_states)
        self.initial_state = frozenset(initial_state)
        self.final_states = frozenset(frozenset(state) for state in final_states[1:-1].split(','))
        self.alphabet = frozenset(alphabet[1:-1].split(','))
        transitions = [transition for transition in transitions if transition]
        for transition in transitions:
            state, symbol, next_state = transition.split(',')
            if symbol == "": symbol = "&"
            state = frozenset((state,))
            next_state = frozenset((next_state,))
            if state not in self.transitions: self.transitions[state] = {}
            if symbol not in self.transitions[state]: self.transitions[state][symbol] = frozenset()
            self.transitions[state][symbol] = self.transitions[state][symbol].union(frozenset((next_state,)))
            temp_states.add(state)
            temp_states.update(self.transitions[state][symbol])
        self.states = frozenset(temp_states)

    @staticmethod
    def state_to_string(state: State) -> str:
        '''Une as partes de um estado em uma string.'''
        '''Exemplo: um estado {"A", "B"} vira "AB"'''
        string = ""
        for state_part in sorted(state):
            string += state_part
        return string

    def __str__(self) -> str:
        num_states = str(self.num_states)
        initial_state = "{" + ''.join(sorted(self.initial_state)) + "}"
        alphabet = "{" + ','.join(sorted(self.alphabet)) + "};"
        final_states = "{"
        for state in sorted(self.final_states_as_tuple()):
            final_states += "{" + self.state_to_string(state) + "},"
        final_states = final_states[:-1] + "}"

        base = f"{num_states};{initial_state};{final_states};{alphabet}"
        trans = ""
        for state, symbol, next_state in self.transitions_as_tuples():
            string_state = "{" + self.state_to_string(state) + "}"
            string_next_state = "{" + self.state_to_string(next_state) + "}"
            trans += f"{string_state},{symbol},{string_next_state};"

        return base + trans
## 3;{ABC};{{ABC},{BC},{C}};{1,2,3};{ABC},1,{ABC};{ABC},2,{BC};{ABC},3,{C};{BC},2,{BC};{BC},3,{C};{C},3,{C}
    def equivalent_states(self) -> Dict[State, State]:
        def are_equivalent(state: State, other_state: State, previous_classes: List[FrozenSet[State]]) -> bool:
            '''Verifica se dois estados são n_equivalentes, ou seja, se para toda transição, o estado destino pertence à mesma classe de equivalência n-1.'''
            # Para cada símbolo do alfabeto, verifica se o estado destino da transição pertence à mesma classe de equivalência n
            for symbol in self.alphabet:
                # Calcula o destino de cada estado
                if state not in self.transitions or symbol not in self.transitions[state]:
                    next_state = frozenset()
                else:
                    next_state = min(self.transitions[state][symbol])
                
                if other_state not in self.transitions or symbol not in self.transitions[other_state]:
                    other_next_state = frozenset()
                else:
                    other_next_state = min(self.transitions[other_state][symbol])

                # Busca a qual classe de equivalencia n cada estado pertence
                next_state_class = None
                other_next_state_class = None
                for previous_class in previous_classes:
                    if next_state in previous_class:
                        next_state_class = previous_class
                    if other_next_state in previous_class:
                        other_next_state_class = previous_class
                
                # Se para algum símbolo as classes dos destinos forem diferentes, então os estados não são n+1 equivalentes
                if next_state_class != other_next_state_class:
                    return False
            # Se nenhum símbolo encontrar umas classe destino diferente, então os estados são n+1 equivalentes
            return True

        def belong(state: State, equivalence_class: FrozenSet[State], previous_classes: List[FrozenSet[State]]) -> bool:
            '''Verifica se um estado pertence a uma classe de equivalência.'''
            # Compara o estado com um estado qualquer da classe de equivalência
            for present_state in equivalence_class:
                return are_equivalent(state, present_state, previous_classes)

        current_equivalence: List[FrozenSet[State]] = [self.final_states, self.states.difference(self.final_states)]
        next_equivalence: List[FrozenSet[State]] = []
        while True:
            for equivalence_class in current_equivalence:
                temp_equivalence: List[FrozenSet[State]] = []
                for state in equivalence_class:
                    state_placed = False
                    # Coloca o estado na classe que ele pertence
                    for i, possible_equivalence_class in enumerate(temp_equivalence):
                        if belong(state, possible_equivalence_class, current_equivalence):
                            temp_equivalence[i] = temp_equivalence[i].union(frozenset((state,)))
                            state_placed = True
                            break
                    # Se o estado não pertencer a nenhuma classe, cria-se uma nova classe para ele
                    if not state_placed:
                        temp_equivalence.append(frozenset((state,)))
                for new_class in temp_equivalence:
                    next_equivalence.append(new_class)
            
            # Se o cálculo de n+1 equivalência dos estados for igual à n equivalência, encerra a conta
            if current_equivalence == next_equivalence:
                break
            # Se não, esquece a equivalência atual e passa a calcular a próxima da próxima, para comparar n+1 com n+2
            else:
                current_equivalence, next_equivalence = next_equivalence, []

        equivalent = {}
        for state in self.states:
            find = None
            for equivalence_class in current_equivalence:
                if state in equivalence_class: find = sorted([self.state_to_string(x) for x in equivalence_class])[0]
            equivalent[state] = find        
        return equivalent
    
    def minimal_equivalent(self) -> 'FDA':
        # Determiniza, remove estados inalcançáveis e mortos
        clean = self.deterministic_equivalent().remove_unreachable_states().remove_dead_states()

        # Calcula os estados equivalentes
        equivalent_states = clean.equivalent_states()
        minimal = FDA()

        minimal.alphabet = clean.alphabet.copy()
        minimal.initial_state = frozenset([equivalent_states[clean.initial_state]])
        minimal.final_states = frozenset([equivalent_states[state] for state in clean.final_states])

        # Substitui os estados pelos equivalentes na tabela de transições
        minimal.transitions = {}
        for state in clean.states:
            for symbol in clean.transitions[state]:
                next_state = min(clean.transitions[state][symbol])
                if equivalent_states[state] not in minimal.transitions:
                    minimal.transitions[equivalent_states[state]] = {}
                if symbol not in minimal.transitions[equivalent_states[state]]:
                    minimal.transitions[equivalent_states[state]][symbol] = frozenset()
                minimal.transitions[equivalent_states[state]][symbol] = minimal.transitions[equivalent_states[state]][symbol].union(frozenset([equivalent_states[next_state]]))
        
        minimal.states = frozenset(equivalent_states.values())
        minimal.num_states = len(minimal.states)
        minimal.string = str(minimal)
        return minimal

    def is_deterministic(self):
        '''Busca por transições por ε ou por um estado que tenha mais de um destino para um mesmo símbolo.'''
        for state in self.transitions:
            if "&" in self.transitions[state]: return False
            for symbol in self.alphabet:
                if symbol not in self.transitions[state]: continue
                if len(self.transitions[state][symbol]) > 1: return False
        return True
    def transitions_as_tuples(self) -> list:
        '''Retorna as transições do autômato como uma lista de tuplas (estado, símbolo, próximo estado) para facilitar a ordenação da saída do programa.'''
        transitions = []
        for state in self.transitions:
            for symbol in self.transitions[state]:
                for next_state in self.transitions[state][symbol]:
                    transitions.append((self.state_to_string(state), symbol, self.state_to_string(next_state)))
        transitions.sort(key=lambda x: sorted(x[0]))
        return transitions

    def final_states_as_tuple(self) -> tuple:
        '''Mesma ideia da função transitions_as_tuples, mas para os estados finais.'''
        final_states = []
        for state in self.final_states:
            final_states.append(tuple(sorted(state)))
        final_states.sort()
        return tuple(final_states)
    def deterministic_equivalent(self) -> 'FDA':
        def epsilon_closure(state: State, closure: set=None) -> State:
            '''Retorna o ε* de um estado, realizando uma busca em profundidade.'''
            if closure is None: closure = set(state)
            if state not in self.transitions or "&" not in self.transitions[state]: return frozenset(closure)

            for reachable_state in self.transitions[state]["&"]:
                if reachable_state not in closure:
                    reachable_state_closure: State = epsilon_closure(reachable_state)
                    closure.update(reachable_state_closure)

            return frozenset(closure)

        # Se o autômato já é determinístico, retorna uma cópia dele mesmo
        if self.is_deterministic(): return self.copy()

        deterministic = FDA()
        # Trata todo autômato não determinístico como se tivesse transições por ε
        # Caso não tenha, ε* de cada estado é ele mesmo, não influenciando no resultado
        states_epsilon_closure: Dict[State, State] = {}
        for state in self.states.difference({'qm'}): states_epsilon_closure[state] = epsilon_closure(state)

        # Construir o autômato determinístico equivalente

        # Conjunto temporário para armaenar os estados a serem incluídos no autômato determinístico
        temp_states: set[State] = set()

        # O estado inicial do autômato determinístico é o ε* do estado inicial do autômato não determinístico
        deterministic.initial_state = states_epsilon_closure[self.initial_state]
        
        # O alfabeto do autômato determinístico é o mesmo do autômato não determinístico, sem o símbolo ε
        deterministic.alphabet = self.alphabet.copy().difference({"&"})
        
        # Começa a construir as transições do autômato determinístico, partindo do estado inicial
        deterministic.transitions = {}
        stack = [deterministic.initial_state]
        while stack:
            # Adiciona o estado visitado ao conjunto de estados do autômato determinístico
            current_state = stack.pop()
            temp_states.add(current_state)

            # Prepara a tabela de transições para receber o novo estado
            if current_state not in deterministic.transitions:
                deterministic.num_states += 1
                deterministic.transitions[current_state] = {}

            # Para cada símbolo do alfabeto, visita os estados alcançáveis a partir do estado atual
            for symbol in sorted(deterministic.alphabet.difference({"&"})):
                next_state: Set[str] = set()
                for state in sorted(current_state):
                    state = frozenset((state,))
                    if state not in self.transitions or symbol not in self.transitions[state]: continue
                    next_state.update({states_epsilon_closure[huh] for huh in self.transitions[state][symbol]})
                if not next_state: continue
                next_state = frozenset([state_part for x in next_state for state_part in x])
                deterministic.transitions[current_state][symbol] = frozenset([next_state])
                if next_state not in temp_states:
                    stack.append(next_state)

        # Agora que todos os estados foram calculados, o conjunto temporário pode ser transformado em um conjunto imutável
        deterministic.states = frozenset(temp_states)
        # Adiciona ao conjunto de estados finais do autômato determinístico os estados que contém algum estado final do autômato não determinístico
        for state in deterministic.states:
            for final_state in self.final_states:
                if final_state.intersection(state):
                    deterministic.final_states = deterministic.final_states.union(frozenset((state,)))
                    break

        deterministic.string = str(deterministic)
        return deterministic

    
    def remove_unreachable_states(self) -> 'FDA':
        '''Busca em profundidade a partir do estado inicial, estados não alcançados são inalcançáveis'''
        reachable_states = set()
        stack = [self.initial_state]
        
        while stack:
            current_state = stack.pop()
            reachable_states.add(current_state)
            for symbol in self.alphabet:
                if symbol not in self.transitions[current_state]: continue
                for next_state in self.transitions[current_state][symbol]:
                    if next_state not in reachable_states:
                        stack.append(next_state)
        unreachable_states = self.states.difference(reachable_states)

        # Remove as transições que envolvem os estados inalcançáveis
        self.remove_states_transitions(unreachable_states)

        self.states = reachable_states
        self.num_states = len(self.states)
        self.string = str(self)
        return self
    
    def remove_dead_states(self) -> 'FDA':
        '''Busca reversa a partir dos estados de aceitação, estados que não são alcançados são considerados mortos.'''
        dead_states = set(self.states.difference(self.final_states))
        stack = [state for state in self.final_states]

        while stack:
            current_state = stack.pop()
            dead_states.discard(current_state)
            for other_state in self.transitions:
                for symbol in self.transitions[other_state]:
                    if current_state in self.transitions[other_state][symbol] and other_state in dead_states:
                        stack.append(other_state)
                        break
        
        self.remove_states_transitions(dead_states)

        self.states = self.states.difference(dead_states)
        self.num_states = len(self.states)
        self.string = str(self)
        return self

    def remove_states_transitions(self, states: Set[State]) -> None:
        '''Remove as entradas da tabela de transições que envolvem os estados passados como argumento.'''
        transitions_to_remove = []
        # Remove todas as transições que partem dos estados removidos
        for state_to_remove in states:
            if state_to_remove in self.transitions: del self.transitions[state_to_remove]

        # Remove os estados removidos dos destinos das transições partidas de outros estados
        for state in self.transitions:
            for symbol in self.transitions[state]:
                self.transitions[state][symbol] = self.transitions[state][symbol].difference(states)
                # Se a transição não leva a outro estado, removê-la depois
                if not self.transitions[state][symbol]: transitions_to_remove.append((state, symbol))

        # Remove transições que agora não levam a lugar nenhum, pois seus destinos foram removidos
        for state, symbol in transitions_to_remove:
            del self.transitions[state][symbol]

    def copy(self) -> 'FDA':
        copy = FDA()
        copy.string = self.string
        copy.initial_state = self.initial_state
        copy.final_states = self.final_states.copy()
        copy.current_state = self.current_state
        copy.states = self.states.copy()
        copy.num_states = self.num_states
        copy.alphabet = self.alphabet.copy()
        copy.transitions = {state: {symbol: next_state.copy() for symbol, next_state in self.transitions[state].items()} for state in self.transitions}
        return copy

if __name__ == "__main__":
    input1 = "17;A;{A,D,F,M,N,P};{a,b,c,d};A,a,B;A,b,E;A,c,K;A,d,G;B,a,C;B,b,H;B,c,L;B,d,Q;C,a,D;C,b,I;C,c,M;C,d,Q;D,a,B;D,b,J;D,c,K;D,d,O;E,a,Q;E,b,F;E,c,H;E,d,N;F,a,Q;F,b,E;F,c,K;F,d,G;G,a,Q;G,b,Q;G,c,Q;G,d,N;H,a,Q;H,b,K;H,c,I;H,d,Q;I,a,Q;I,b,L;I,c,J;I,d,Q;J,a,Q;J,b,M;J,c,H;J,d,P;K,a,Q;K,b,H;K,c,L;K,d,Q;L,a,Q;L,b,I;L,c,M;L,d,Q;M,a,Q;M,b,J;M,c,K;M,d,O;N,a,R;N,b,R;N,c,R;N,d,G;O,a,R;O,b,R;O,c,R;O,d,P;P,a,R;P,b,R;P,c,Q;P,d,O;Q,a,R;Q,b,Q;Q,c,R;Q,d,Q;R,a,Q;R,b,R;R,c,Q;R,d,R"
    fda = FDA(input1)
    print(fda.minimal_equivalent())