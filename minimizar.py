from dataclasses import dataclass
from typing import List, Set

State = str

def parse(input_str: str):
    parts = input_str.split(';')
    num_states = int(parts[0])
    initial_state_name = parts[1]
    final_states = set(parts[2].strip('{}').split(','))
    alphabet = set(parts[3].strip('{}').split(','))
    states = set()

    print(states)
    for transition in parts[4:]:
        src_name, symbol, dst_name = map(str.strip, transition.split(','))
        if src_name not in states:
            states.add(src_name)
        if dst_name not in states:
            states.add(dst_name)

    initial_state = initial_state_name
    print(initial_state)
    transitions = [transition.split(',') for transition in parts[4:]]
    automaton = AFD(states, initial_state, final_states, alphabet, transitions)

        
    return automaton
@dataclass(init=False)
class AFD:
    states: set[State]
    initial_state: State
    final_states: Set[str]
    alphabet: Set[str]
    transitions: List[str]

    def __init__(self, states: set[State], initial_state: State, final_states: Set[str], alphabet: Set[str], transitions: List[str]) -> 'AFD':
        self.initial_state = initial_state
        self.final_states = final_states
        self.alphabet = alphabet
        self.states = states
        self.transitions = transitions

    @property
    def transition_map(self):
        return {(source, symbol): {dest} for source, symbol, dest in self.transitions}

    @property
    def reverse_transition_map(self):
        map = {}
        for source, symbol, dest in self.transitions:
            dests = map.setdefault((dest, symbol), set())
            dests.add(source)
        return map

    def get_reachable_states(self, transition_map, state, symbols):
        reachable_states = set()
        not_visited_states = {state}
        while not_visited_states:
            selected = not_visited_states.pop()
            for symbol in symbols:
                for neighbour in transition_map.get((selected,symbol), set()):
                    if neighbour not in reachable_states:
                        not_visited_states.add(neighbour)              
                    reachable_states.add(neighbour)
        return reachable_states
        
    def remove_dead_states(self):
        pass

    def remove_unreachable_states(self):
        pass

    def compute_equivalence_classes(self):
        pass

    def minimize(self):
        pass


if __name__ == "__main__":
    input1 = "17;A;{A,D,F,M,N,P};{a,b,c,d};A,a,B;A,b,E;A,c,K;A,d,G;B,a,C;B,b,H;B,c,L;B,d,Q;C,a,D;C,b,I;C,c,M;C,d,Q;D,a,B;D,b,J;D,c,K;D,d,O;E,a,Q;E,b,F;E,c,H;E,d,N;F,a,Q;F,b,E;F,c,K;F,d,G;G,a,Q;G,b,Q;G,c,Q;G,d,N;H,a,Q;H,b,K;H,c,I;H,d,Q;I,a,Q;I,b,L;I,c,J;I,d,Q;J,a,Q;J,b,M;J,c,H;J,d,P;K,a,Q;K,b,H;K,c,L;K,d,Q;L,a,Q;L,b,I;L,c,M;L,d,Q;M,a,Q;M,b,J;M,c,K;M,d,O;N,a,R;N,b,R;N,c,R;N,d,G;O,a,R;O,b,R;O,c,R;O,d,P;P,a,R;P,b,R;P,c,Q;P,d,O;Q,a,R;Q,b,Q;Q,c,R;Q,d,Q;R,a,Q;R,b,R;R,c,Q;R,d,R"
    afd = ((parse(input1)))
    bucetil = (afd.transition_map)
    print('\n\n')
    reverse = (afd.reverse_transition_map)
    print(afd.get_reachable_states(bucetil, 'A', afd.alphabet))