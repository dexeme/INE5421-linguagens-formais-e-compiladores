class Automato:
    def __init__(self, num_states, initial_state, final_states, alphabet, transitions):
        self.num_states = num_states
        self.initial_state = initial_state
        self.final_states = set(final_states)
        self.alphabet = set(alphabet)
        self.transitions = transitions
        self.epsilon_closures = {}

    def compute_epsilon_closure(self, state, closure=None):
        if closure is None:
            closure = set()

        if state not in closure:
            closure.add(state)
            if '&' in self.transitions.get(state, {}):
                for next_state in self.transitions[state]['&']:
                    self.compute_epsilon_closure(next_state, closure)
        return closure

    def determinize(self):
        # Calcular o fecho épsilon para todos os estados
        for state in range(self.num_states):
            state = chr(state + 65)  # Converter número para letra maiúscula
            self.epsilon_closures[state] = self.compute_epsilon_closure(state)

        new_states = [frozenset(self.epsilon_closures[self.initial_state])]
        unmarked_states = [frozenset(self.epsilon_closures[self.initial_state])]
        new_transitions = {}
        new_final_states = []

        while unmarked_states:
            current = unmarked_states.pop()
            current_name = self.state_name(current)
            new_transitions[current_name] = {}

            for symbol in self.alphabet:
                if symbol == '&':  # Ignorar símbolos épsilon na determinização
                    continue

                next_state = set()
                for substate in current:
                    if symbol in self.transitions.get(substate, {}):
                        for target in self.transitions[substate][symbol]:
                            next_state.update(self.epsilon_closures[target])

                if next_state:
                    next_state = frozenset(next_state)
                    next_state_name = self.state_name(next_state)
                    new_transitions[current_name][symbol] = next_state_name

                    if next_state not in new_states:
                        new_states.append(next_state)
                        unmarked_states.append(next_state)
                        if any(state in self.final_states for state in next_state):
                            new_final_states.append(next_state_name)

        return Automato(len(new_states), self.state_name(frozenset(self.epsilon_closures[self.initial_state])), 
                        new_final_states, self.alphabet, new_transitions)

    def state_name(self, state_set):
        return ''.join(sorted(state_set))


def parse_input(input_str):
    parts = input_str.split(';')
    num_states = int(parts[0])
    initial_state = parts[1]
    final_states = parts[2].strip('{}').split(',')
    alphabet = parts[3].strip('{}').split(',')
    transition_list = parts[4].strip().split(',')
    transitions = {}

    for i in range(0, len(transition_list), 3):
        src = transition_list[i].strip()
        sym = transition_list[i+1].strip()
        dst = transition_list[i+2].strip()

        if src not in transitions:
            transitions[src] = {}
        if sym not in transitions[src]:
            transitions[src][sym] = []
        transitions[src][sym].append(dst)

    return Automato(num_states, initial_state, final_states, alphabet, transitions)


def debug_print(automato: Automato):
    print("Automato:")
    print("  num_states:", automato.num_states)
    print("  initial_state:", automato.initial_state)
    print("  final_states:", automato.final_states)
    print("  alphabet:", automato.alphabet)
    print("  transitions:")
    for src in automato.transitions:
        for sym in automato.transitions[src]:
            for dst in automato.transitions[src][sym]:
                print("    ", src, sym, dst)
    print()

# Exemplo de entrada
input_str = "3;A;{B,C};{a,b,&};A,a,B,A,b,C,A,&,A,B,b,B,C,a,C"
automato = parse_input(input_str)
debug_print(automato)
new_automato = automato.determinize()
debug_print(new_automato)