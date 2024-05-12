class Node:
    def __init__(self, parent):
        self.parent = parent
        self.firstpos = None
        self.lastpos = None
        self.nullable = None

class ConcatNode(Node):
    def __init__(self, parent):
        super(ConcatNode, self).__init__(parent)
        self.lchild = None
        self.rchild = None
        
    def create_subtree(self, nodestack):
        operand2 = nodestack.pop()
        operand1 = nodestack.pop()
        self.lchild = operand1 if isinstance(operand1, Node) else LeafNode(parent=self, string=operand1)
        self.rchild = operand2 if isinstance(operand2, Node) else LeafNode(parent=self, string=operand2)


        if isinstance(operand1, Node):
            self.lchild = operand1
            operand1.parent = self
        else:
            self.lchild = LeafNode(parent=self, string=operand1)

        if isinstance(operand2, Node):
            self.rchild = operand2
            operand2.parent = self
        else:
            self.rchild = LeafNode(parent=self, string=operand2)

    def __str__(self):
        return '[' + str(self.lchild) + '.' + str(self.rchild) + ']'

    def isnullable(self):
        a = self.lchild.isnullable()
        b = self.rchild.isnullable()
        self.nullable = a and b
        return self.nullable

    def findfirstpos(self):
        a = self.lchild.findfirstpos()
        b = self.rchild.findfirstpos()
        if self.lchild.nullable:
            self.firstpos = list(set(a + b))
        else:
            self.firstpos = a
        return self.firstpos

    def findlastpos(self):
        a = self.lchild.findlastpos()
        b = self.rchild.findlastpos()
        if self.rchild.nullable:
            self.lastpos = list(set(a + b))
        else:
            self.lastpos = b
        return self.lastpos


class StarNode(Node):
    def __init__(self, parent):
        super(StarNode, self).__init__(parent)
        self.child = None

    def create_subtree(self, nodestack):
        operand = nodestack.pop()
        if isinstance(operand, Node):
            self.child = operand
        else:
            self.child = LeafNode(parent=self, string=operand)

    def __str__(self):
        return '[ (' + str(self.child) + ') * ]'

    def isnullable(self):
        self.child.isnullable()
        self.nullable = True
        return True

    def findfirstpos(self):
        self.firstpos = self.child.findfirstpos()
        return self.firstpos

    def findlastpos(self):
        self.lastpos = self.child.findlastpos()
        return self.lastpos


class OrNode(Node):
    def __init__(self, parent):
        super(OrNode, self).__init__(parent)
        self.lchild = None
        self.rchild = None

    def create_subtree(self, nodestack):
        operand2 = nodestack.pop()
        operand1 = nodestack.pop()

        if isinstance(operand1, Node):
            self.lchild = operand1
            operand1.parent = self
        else:
            self.lchild = LeafNode(parent=self, string=operand1)

        if isinstance(operand2, Node):
            self.rchild = operand2
            operand2.parent = self
        else:
            self.rchild = LeafNode(parent=self, string=operand2)

    def __str__(self):
        return '[' + str(self.lchild) + '|' + str(self.rchild) + ']'

    def isnullable(self):
        a = self.lchild.isnullable()
        b = self.rchild.isnullable()
        self.nullable = a or b
        return self.nullable

    def findfirstpos(self):
        self.firstpos = list(set(self.lchild.findfirstpos() + self.rchild.findfirstpos()))
        return self.firstpos

    def findlastpos(self):
        self.lastpos = list(set(self.lchild.findlastpos() + self.rchild.findlastpos()))
        return self.lastpos


class LeafNode(Node):
    num_of_instances = 0

    def __init__(self, parent, string):
        super(LeafNode, self).__init__(parent)

        self.string = string

        LeafNode.num_of_instances += 1
        self.number = LeafNode.num_of_instances

    def __str__(self):
        return '[' + self.string + ']'

    def isnullable(self):
        if self.string == '&':
            self.nullable = True
            return True
        else:
            self.nullable = False
            return False

    def findfirstpos(self):
        if self.string == '&':
            self.firstpos = []
            return self.firstpos
        else:
            self.firstpos = [self.number, ]
            return self.firstpos

    def findlastpos(self):
        if self.string == '&':
            self.lastpos = []
            return self.lastpos
        else:
            self.lastpos = [self.number, ]
            return self.lastpos


class SyntaxTree:
    def __init__(self, string):
        LeafNode.num_of_instances = 0
        self.regex = self.add_concat(string) + '.#'
        self.root = self.convert_regex_to_syntaxtree()

        self.root.isnullable()
        self.root.findfirstpos()
        self.root.findlastpos()

        self.followpos = []
        for i in range(0, LeafNode.num_of_instances):
            self.followpos.append(None)

    def add_concat(self, string):
        opstack = []
        nodestack = []

        result = ''

        for i in range(0, len(string) - 1):
            result = result + string[i]
            if (string[i].isalpha() and string[i + 1].isalpha()) or \
                    (string[i].isalpha() and string[i + 1] == '(') or \
                    (string[i] == ')' and string[i + 1].isalpha()) or \
                    (string[i] == '*' and string[i + 1].isalpha()) or \
                    (string[i] == '*' and string[i + 1] == '(') or \
                    (string[i] == ')' and string[i + 1] == '('):
                result += '.'
        result = result + string[-1]
        return result

    def not_greater(self, i, j):
        prioriy = {'*': 3, '.': 2, '|': 1}
        try:
            a = prioriy[i]
            b = prioriy[j]
            return True if a <= b else False
        except KeyError:
            return False

    def convert_regex_to_syntaxtree(self):
        nodestack = []
        opstack = []

        for r in self.regex:
            if r.isalpha() or r == '#':
                nodestack.append(LeafNode(parent=None, string=r))
            elif r == '&':
                nodestack.append(EpsilonNode(parent=None))
            elif r == '(':
                opstack.append(r)
            elif r == ')':
                while len(opstack) != 0 and opstack[-1] != '(':
                    self.convert_substr_to_subtree(opstack, nodestack)
                opstack.pop()
            else:
                while len(opstack) != 0 and self.not_greater(r, opstack[-1]):
                    self.convert_substr_to_subtree(opstack, nodestack)
                opstack.append(r)

        while len(opstack) != 0:
            self.convert_substr_to_subtree(opstack, nodestack)

        return nodestack.pop() if nodestack else None


    def convert_substr_to_subtree(self, opstack, nodestack):
        op = opstack.pop()

        if op == '*':
            op = StarNode(parent=None)
        elif op == '.':
            op = ConcatNode(parent=None)
        elif op == '|':
            op = OrNode(parent=None)
        else:
            raise Exception('Unknown Operator!')

        op.create_subtree(nodestack)
        nodestack.append(op)

    def findfollowpos(self, node):
        if isinstance(node, ConcatNode):
            for i in node.lchild.lastpos:
                if self.followpos[i - 1]:
                    self.followpos[i - 1] = list(set(self.followpos[i - 1] + node.rchild.firstpos))
                else:
                    self.followpos[i - 1] = node.rchild.firstpos

            self.findfollowpos(node.lchild)
            self.findfollowpos(node.rchild)

        elif isinstance(node, StarNode):
            for i in node.lastpos:
                if self.followpos[i - 1]:
                    self.followpos[i - 1] = list(set(self.followpos[i - 1] + node.firstpos))
                else:
                    self.followpos[i - 1] = node.firstpos
            self.findfollowpos(node.child)

        return


class State:
    def __init__(self, name, statenumber):
        self.name = name
        self.statenumber = statenumber
        self.Dtran = {}

    def __str__(self):
        s = '<' + self.name + ' ,' + str(self.statenumber) + ' ,'
        for transition in self.Dtran:
            s = s + 'Dtran(' + transition + ')=' + self.Dtran[transition].name
            s = s + '\t'
        s = s + '>\n'
        return s


class ConvertToDfa:
    def __init__(self, tree):
        self.tree = tree
        self.followpos = tree.followpos
        self.initial_statenumber = tree.root.firstpos
        self.initial_state = None
        self.leaf_nodes = {}
        self.final_number = next((leaf.number for leaf in self.get_leaf_nodes(tree.root) if leaf.string == '#'), None)
        self.final_states = set()
        self.discovered_order = []

    def get_final_number(self):
        return self.final_number

    def get_leaf_nodes(self, node):
        if node is None:
            return []
        elif isinstance(node, LeafNode) or isinstance(node, EpsilonNode):
            return [node] if isinstance(node, LeafNode) else []
        else:
            lchild_nodes = self.get_leaf_nodes(node.lchild) if hasattr(node, 'lchild') else []
            rchild_nodes = self.get_leaf_nodes(node.rchild) if hasattr(node, 'rchild') else []
            return lchild_nodes + rchild_nodes

    def find_leaf_nodes(self, node):
        if isinstance(node, LeafNode) and node.string not in ('#', '&'):
            try:
                self.leaf_nodes[node.string].append(node.number)
            except KeyError:
                self.leaf_nodes[node.string] = [node.number]
        elif isinstance(node, StarNode):
            self.find_leaf_nodes(node.child)
        elif isinstance(node, ConcatNode) or isinstance(node, OrNode):
            self.find_leaf_nodes(node.lchild)
            self.find_leaf_nodes(node.rchild)



    def convert(self):
        def state_name(statenumber):
            return "{" + ",".join(map(str, sorted(statenumber))) + "}"

        self.find_leaf_nodes(self.tree.root)
        initial_statename = state_name(self.initial_statenumber)
        self.initial_state = State(name=initial_statename, statenumber=self.initial_statenumber)
        states = {initial_statename: self.initial_state}
        final_states = set()
        queue = [self.initial_state]
        self.discovered_order.append(self.initial_state)

        while queue:
            current_state = queue.pop(0)
            if self.final_number in current_state.statenumber:
                final_states.add(current_state.name)

            for symbol in self.leaf_nodes:
                next_statenumber = frozenset(
                    pos for elem in current_state.statenumber if elem in self.leaf_nodes[symbol]
                    for pos in self.followpos[elem - 1]
                )
                next_statename = state_name(next_statenumber)
                if next_statename not in states:
                    next_state = State(name=next_statename, statenumber=next_statenumber)
                    states[next_statename] = next_state
                    queue.append(next_state)
                    self.discovered_order.append(next_state)
                current_state.Dtran[symbol] = states[next_statename]

        return self.initial_state



class DFAToFormattedOutput:
    def __init__(self, dfa, fn):
        self.dfa = dfa
        self.all_states = []
        self.final_states = set()
        self.alphabet = set()
        self.transitions = []
        self.fn = fn
        self.collect_dfa_info()

    def collect_dfa_info(self):
        queue = [self.dfa]
        visited = set()

        while queue:
            state = queue.pop(0)
            if state not in visited:
                visited.add(state)
                if state.name != '{}':
                    self.all_states.append(state)
                if self.fn in state.statenumber:
                    if state not in self.final_states:
                        self.final_states.add(state)

                for symbol, target in state.Dtran.items():
                    self.alphabet.add(symbol)
                    self.transitions.append((state.name, symbol, target.name))
                    queue.append(target)

    def generate_formatted_output(self):
        total_states = len(self.all_states)
        initial_state = self.dfa.name
        final_state_names = ",".join(sorted([state.name for state in self.final_states]))
        alphabet_str = ",".join(sorted(self.alphabet))
        transitions_dict = {}
        for src, symbol, dest in self.transitions:
            if dest != "{}":
                if src not in transitions_dict:
                    transitions_dict[src] = {}
                transitions_dict[src][symbol] = dest

        transitions_str = ""
        for src in sorted(transitions_dict.keys()):
            for symbol in sorted(self.alphabet):
                if symbol in transitions_dict[src]:
                    dest = transitions_dict[src][symbol]
                    transitions_str += f"{src},{symbol},{dest};"

        formatted_output = f"{total_states};{{{initial_state}}};{{{final_state_names}}};{{{alphabet_str}}};{transitions_str}"

        return formatted_output


class EpsilonNode(Node):
    def __init__(self, parent):
        super(EpsilonNode, self).__init__(parent)
        self.nullable = True

    def isnullable(self):
        return True

    def findfirstpos(self):
        self.firstpos = []
        return self.firstpos

    def findlastpos(self):
        self.lastpos = []
        return self.lastpos


tree = SyntaxTree(input())
tree.findfollowpos(tree.root)
converttree = ConvertToDfa(tree=tree)
dfa = converttree.convert()
formatted_output_converter = DFAToFormattedOutput(dfa, converttree.get_final_number())
formatted_output = formatted_output_converter.generate_formatted_output()
print(formatted_output)
