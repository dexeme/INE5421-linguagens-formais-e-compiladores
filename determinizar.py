determinizar1 = "4;A;{D};{a,b};A,a,A;A,a,B;A,b,A;B,b,C;C,b,D"
determinizar2 = "3;A;{C};{1,2,3,&};A,1,A;A,&,B;B,2,B;B,&,C;C,3,C"
determinizar3 = "4;P;{S};{0,1};P,0,P;P,0,Q;P,1,P;Q,0,R;Q,1,R;R,0,S;S,0,S;S,1,S"

inputs = [determinizar1, determinizar2, determinizar3]

# ----------------------------------------------------------------- #

def parse(input_str: str):
    # Divide a string de entrada nas suas principais partes
    parts = input_str.split(';')
    
    # Processa cada parte
    num_states = int(parts[0])  # Converte o número de estados para inteiro
    initial_state = parts[1]  # Estado inicial é uma string simples
    
    # Estados finais, removendo as chaves e dividindo pela vírgula
    final_states = parts[2].strip('{}').split(',')
    
    # Alfabeto, removendo as chaves e dividindo pela vírgula
    alphabet = parts[3].strip('{}').split(',')
    
    # Transições, que são as partes restantes após o alfabeto
    transitions = [transition.split(',') for transition in parts[4:]]
    
    # Retorna os componentes formatados conforme especificado
    return [num_states, initial_state, final_states, alphabet, transitions]

# ----------------------------------------------------------------- #

print(parse(inputs[0]))