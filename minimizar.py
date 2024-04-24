from typing import List, Set, Dict, Tuple

State = str

def parse(input_str: str):
    parts = input_str.split(';')
    num_states = int(parts[0])
    initial_state_name = parts[1]
    final_states = set(parts[2].strip('{}').split(','))
    alphabet = set(parts[3].strip('{}').split(','))
    states = set()

    for transition in parts[4:]:
        src_name, symbol, dst_name = map(str.strip, transition.split(','))
        if src_name not in states:
            states.add(src_name)
        if dst_name not in states:
            states.add(dst_name)

    initial_state = initial_state_name
    transitions = [transition.split(',') for transition in parts[4:]]
    automaton = AFD(states, initial_state, final_states, alphabet, transitions)
    return automaton
class AFD:
    states: Set[State]
    initial_state: State
    final_states: Set[str]
    alphabet: Set[str]
    transitions: List[str]
    transition_map: Dict[Tuple[State, str], Set[State]]
    reverse_transition_map: Dict[Tuple[State, str], Set[State]]
    num_states: int

    def __init__(self, states: Set[State], initial_state: State, final_states: Set[str], alphabet: Set[str], transitions: List[str]) -> 'AFD':
        self.initial_state = initial_state
        self.final_states = {*final_states}
        self.alphabet = {*alphabet}
        self.states = {*states}
        self.transitions = [*transitions]
        self.num_states = len(states)
        self.transition_map = self.get_transition_map()
        self.reverse_transition_map = self.get_reverse_transition_map()

    def get_transition_map(self):
        return {(source, symbol): {dest} for source, symbol, dest in self.transitions}

    def get_reverse_transition_map(self):
        map = {}
        for source, symbol, dest in self.transitions:
            dests = map.setdefault((dest, symbol), set())
            dests.add(source)
        return map

    def get_reachable_states(self, transition_map, state, symbols):
        reachable_states = {state}
        not_visited_states = {state}
        while not_visited_states:
            selected = not_visited_states.pop()
            for symbol in symbols:
                for neighbour in transition_map.get((selected,symbol), set()):
                    if neighbour not in reachable_states:
                        not_visited_states.add(neighbour)              
                    reachable_states.add(neighbour)
        return reachable_states
        
    def get_unreachable_states(self):
        reachable_states = self.get_reachable_states(self.transition_map, self.initial_state, self.alphabet)
        return self.states - reachable_states
    
    def get_dead_states(self):
        reached = set()
        for final_state in self.final_states:
            states = self.get_reachable_states(self.reverse_transition_map, final_state, self.alphabet)
            reached.update(states)
        return self.states - reached
    
    def compute_equivalence_classes(self):
        p = {frozenset(self.final_states), frozenset(self.states - self.final_states)}
        q = {frozenset(self.final_states)}

        while q:
            sel = q.pop()

            for symbol in self.alphabet:
                x = set()

                for state in sel:
                    x.update(self.reverse_transition_map.get((state, symbol), set()))

                x = frozenset(x)

                for y in [*p]:
                    if not(x & y) or not y - x:
                        continue

                    p.remove(y)
                    p.add(x & y)
                    p.add(y - x)

                    if y in q:
                        q.remove(y)
                        q.add(x & y)
                        q.add(y - x)
                        continue
                
                    if len(x & y) <= len(y - x):
                        q.add(x & y)
                    else:
                        q.add(y - x)
        return p
    
    def minimize(self):
        states = self.states - self.get_unreachable_states() - self.get_dead_states()
        final_states = self.final_states & states
        transitions = [t for t in self.transitions if t[0] in states and t[2] in states]
        new_afd = AFD(states, self.initial_state, final_states, self.alphabet, transitions)

        equivalence_classes = new_afd.compute_equivalence_classes()
        merged_states = [sorted(clss)[0] for clss in equivalence_classes]
        merged_states_map = {
            state: merged_states[i]
            for i, clss in enumerate(equivalence_classes)
            for state in clss
        }

        new_transitions = {
            (merged_states_map[source], symbol, merged_states_map[dest]) 
            for source, symbol, dest in transitions
        }
        new_initial_state = merged_states_map[self.initial_state]
        new_final_states = {merged_states_map[state] for state in final_states}
        new_afd = AFD(merged_states, new_initial_state, new_final_states, 
            self.alphabet, new_transitions)
        return new_afd

    def format(self):
        final_states = f"{{{','.join(sorted(self.final_states))}}}"
        alphabet = f"{{{','.join(sorted(self.alphabet))}}}"
        trans = sorted(self.transitions, key=lambda x: x[1])
        trans = sorted(trans, key=lambda x: x[0])
        transitions = ';'.join(','.join(transition) for transition in trans)        
        return f"{self.num_states};{self.initial_state};{final_states};{alphabet};{transitions}"

afd = ((parse(input())))
minimized_adf = (afd.minimize()).format()
print(minimized_adf)