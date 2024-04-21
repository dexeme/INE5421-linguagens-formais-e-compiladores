from typing import List, Set

def parse(input_str: str):
    parts = input_str.split(';')
    num_states = int(parts[0])
    initial_state_name = parts[1]
    final_states_names = set(parts[2].strip('{}').split(','))
    alphabet = set(parts[3].strip('{}').split(','))

    states_dict = {name: State(name, name in final_states_names) for name in set(parts[1]) | final_states_names}
    
    for transition in parts[4:]:
        src_name, symbol, dst_name = map(str.strip, transition.split(','))
        if src_name not in states_dict:
            states_dict[src_name] = State(src_name)
        if dst_name not in states_dict:
            states_dict[dst_name] = State(dst_name)
        states_dict[src_name].add_transition(symbol, states_dict[dst_name].name)

    initial_state = states_dict[initial_state_name]
    final_states = [state for name, state in states_dict.items() if state.final]

    transitions = [transition.split(',') for transition in parts[4:]]

    automaton = Automaton(num_states, initial_state, final_states, alphabet, transitions)
    for state in states_dict.values():
        automaton.add_state(state)
    return automaton


# --------------------------------------------

class State:
    def __init__(self, name: str, final: bool = False):
        self.name = name
        self.final = final
        self.transitions = {}

    def add_transition(self, symbol: str, state: 'State'):
        if symbol not in self.transitions:
            self.transitions[symbol] = []
        self.transitions[symbol].append(state)
    
    def __str__(self):
        return ''.join(f"{self.name},{symbol},{state};" for symbol, states in self.transitions.items() for state in states)
    
class Automaton:
    def __init__(self, num_states: int, initial_state: State, final_states: List[State], alphabet: Set[str], transitions: List[str]):
        self.num_states = num_states
        self.initial_state = initial_state
        self.final_states = final_states
        self.alphabet = alphabet
        self.states = {}
        self.transitions = transitions

    def add_state(self, state: State):
        self.states[state.name] = state

    def formatted_transitions(self):
        transitions_str = ''
        for state in self.states.values():
            transitions_str += str(state)
        return transitions_str
    
    def __str__(self):
        return f"{self.num_states};{self.initial_state.name};{{{','.join(state.name for state in self.final_states)}}};{{{','.join(sorted(self.alphabet))}}};{self.formatted_transitions()}"

    def is_deterministic(self):
        for state in self.states.values():
            for symbol in self.alphabet:
                if symbol not in state.transitions:
                    return False
                if len(state.transitions[symbol]) > 1:
                    return False
        return True


    def process_transitions(self):
        adjacency_list = {}
        for state in self.states:
            adjacency_list[state] = {}
        for src, symbol, dest in self.transitions:

            if symbol not in adjacency_list[src]:
                adjacency_list[src][symbol] = []
            adjacency_list[src][symbol].append(dest)
        return adjacency_list

    def compute_epsilon_closure(self, adjacency_list, epsilon_symbol='&'):
        epsilon_closures = {}
        def dfs(state):
            stack = [state]
            closure = set()
            while stack:
                current = stack.pop()
                if current not in closure:
                    closure.add(current)
                    if current in adjacency_list and epsilon_symbol in adjacency_list[current]:
                        stack.extend(adjacency_list[current][epsilon_symbol])
            return closure

        for state in adjacency_list:
            epsilon_closures[state] = dfs(state)
        return epsilon_closures

    def verify_if_group_is_final(self, group, final_states):
        for state in group:
            if state in final_states:
                return True
        return False
    

    def get_reachable_states(self, adjacency_list, state, symbol):
        reachable_states = []
        if state in adjacency_list and symbol in adjacency_list[state]:
            reachable_states.extend(adjacency_list[state][symbol])
        return reachable_states
    

    def determinize(self):
        if self.is_deterministic(): return self

        adjacency_list = self.process_transitions()
        epsilon_closures = self.compute_epsilon_closure(adjacency_list)
        new_alphabet = self.alphabet - {'&'}

        new_states = {}

        new_initial_state = ''.join(sorted(epsilon_closures[self.initial_state.name]))
        
        transicoes = []
        lista = [new_initial_state]
        while lista:
            state = lista.pop(0)
            new_states[state] = State(state, self.verify_if_group_is_final(state, [final.name for final in self.final_states]))
            for symbol in new_alphabet:
                reachable_states = []
                for old_state in state:
                    for new_state in self.get_reachable_states(adjacency_list, old_state, symbol):
                        reachable_states = list(set(reachable_states + list(epsilon_closures[new_state])))
                if reachable_states:
                    new_state = ''.join(sorted(reachable_states))
                    if (state, symbol, new_state) not in transicoes:
                        transicoes.append((state, symbol, new_state))

                        if new_state not in new_states:
                            new_states[new_state] = State(new_state, self.verify_if_group_is_final(new_state, [final.name for final in self.final_states]))
                            lista.append(new_state)
                            
                    # cria transição
                        new_states[state].add_transition(symbol, new_states[new_state])

        formatted_string = ''
        formatted_string += f"{len(new_states)};"
        formatted_string += "{" + str(new_initial_state) + "};"
        formatted_string += "{" + ','.join(sorted(["{"+ str(state) + "}" for state in new_states if new_states[state].final])) + "};"
        formatted_string += "{" + ','.join(sorted(new_alphabet)) + "};"
        # Organizando e formatando as transições
        sorted_transitions = sorted(
            transicoes, 
            key=lambda x: (x[0], x[1])
        )

        # Concatenando transições formatadas
        for transition in sorted_transitions:
            formatted_string += "{" + transition[0] + "}," + transition[1] + ",{" + transition[2] + "};"

        return formatted_string

print(parse(input()).determinize())

# 3;A;{C};{1,2,3,&};A,1,A;A,&,B;B,2,B;B,&,C;C,3,C
# 4;P;{S};{0,1};P,0,P;P,0,Q;P,1,P;Q,0,R;Q,1,R;R,0,S;S,0,S;S,1,S
# 4;A;{D};{a,b};A,a,A;A,a,B;A,b,A;B,b,C;C,b,D

