# Parse the input
def parse_input(input):
    input = input.strip().split(';')
    productions = {}
    for production in input:
        if '=' in production:
            left, right = production.split('=')
            left = left.strip()
            right = right.strip()
            if left in productions:
                productions[left].append(right)
            else:
                productions[left] = [right]
    return productions

# Get the first set of a given production
def first_set(productions, production):
    first = set()
    if production in productions:
        for right in productions[production]:
            if right == '&':
                first.add('&')
            elif right[0].islower():
                first.add(right[0])
            else:
                for symbol in right:
                    if symbol.isupper():
                        first = first.union(first_set(productions, symbol))
                        if '&' not in first:
                            break
                    else:
                        first.add(symbol)
                        break
    return first

# Get the follow set of a given production
def follow_set(productions, production, start):
    follow = set()
    if production == start:
        follow.add('$')
    for left in productions:
        for right in productions[left]:
            for i in range(len(right)):
                if right[i] == production:
                    if i == len(right) - 1:
                        if left != production:
                            follow = follow.union(follow_set(productions, left, start))
                    else:
                        if right[i + 1].isupper():
                            first_of_next = first_set(productions, right[i + 1])
                            if '&' in first_of_next:
                                first_of_next.remove('&')
                                follow = follow.union(first_of_next)
                                follow = follow.union(follow_set(productions, left, start))
                            else:
                                follow = follow.union(first_of_next)
                        else:
                            follow.add(right[i + 1])
    return follow

# Get the first and follow sets of a given set of productions
def first_follow(productions):
    first = {}
    follow = {}
    for production in productions:
        first[production] = first_set(productions, production)
    for production in productions:
        follow[production] = follow_set(productions, production, list(productions.keys())[0])
    return first, follow

# Print the first and follow sets
def print_first_follow(first, follow):
    first_str = "; ".join([f"First({prod}) = {{{', '.join(sorted(first[prod]))}}}" for prod in first])
    follow_str = "; ".join([f"Follow({prod}) = {{{', '.join(sorted(follow[prod]))}}}" for prod in follow])
    print(f"{first_str}; {follow_str};")

# Main
input_ = input()
productions = parse_input(input_)
first, follow = first_follow(productions)
print_first_follow(first, follow)