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

    automaton = Automaton(num_states, initial_state, final_states, alphabet)
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

    # def __str__(self):
    #     # Formato: A,a,A;A,a,B;A,b,A;B,b,C;C,b,D
    #     transitions_str = ';'.join(f"{self.name},{symbol},{state}" for symbol, states in self.transitions.items() for state in states)
    #     print(self.transitions)
    #     return transitions_str
    
    def formatted_transitions(self):
        return ''.join(f"{self.name},{symbol},{state};" for symbol, states in self.transitions.items() for state in states)
    
class Automaton:
    def __init__(self, num_states: int, initial_state: State, final_states: List[State], alphabet: set[str]):
        self.num_states = num_states
        self.initial_state = initial_state
        self.final_states = final_states
        self.alphabet = alphabet
        self.states = {}

    def add_state(self, state: State):
        self.states[state.name] = state

    def __str__(self):
        transitions_str = ''
        for state in self.states.values():
            transitions_str += state.formatted_transitions()
        return transitions_str

automaton = parse(determinizar1)
print(automaton)

# Testar a função parse

# print(parse(inputs[0]))
# print(parse(inputs[1]))
# print(parse(inputs[2]))