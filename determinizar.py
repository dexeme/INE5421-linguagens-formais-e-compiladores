from typing import List

determinizar1 = "4;A;{D};{a,b};A,a,A;A,a,B;A,b,A;B,b,C;C,b,D"
determinizar2 = "3;A;{C};{1,2,3,&};A,1,A;A,&,B;B,2,B;B,&,C;C,3,C"
determinizar3 = "4;P;{S};{0,1};P,0,P;P,0,Q;P,1,P;Q,0,R;Q,1,R;R,0,S;S,0,S;S,1,S"

inputs = [determinizar1, determinizar2, determinizar3]

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
    def __init__(self, num_states: int, initial_state: State, final_states: List[State], alphabet: set[str], transitions: List[str]):
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

    def determinize(self):
        pass

    def process_transitions(self):
        adjacency_list = {}
        for src, symbol, dest in self.transitions:
            print(src, symbol, dest)
            if src not in adjacency_list:
                adjacency_list[src] = {}
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





# Testar a função parse

# print(parse(inputs[0]))
# print(parse(inputs[1]))
# print(parse(inputs[2]))

# Testar função is_deterministic

# automaton = parse(inputs[0])
# print(automaton.is_deterministic())

# Testar funções process_transitions e compute_epsilon_closure

automaton = parse(inputs[1])
transitions_str = automaton.formatted_transitions()
print(transitions_str)
adjacency_list = automaton.process_transitions()
epsilon_closures = automaton.compute_epsilon_closure(adjacency_list=adjacency_list)
print(adjacency_list)
print(epsilon_closures)
