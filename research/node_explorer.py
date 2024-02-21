from typing import List
import pickle
import os
import sys

class Node:
    def __init__(self, name : str, predecessor : 'Node' = None, alternative_name : str = None):
        self.name = name
        self.predecessor = predecessor
        self.alternative_name : str = alternative_name
        self.children : List['Node'] = []

    def get_child(self, index : int):
        if (index >= len(self.children)):
            assert IndexError
        return self.children[index]
    
    def add_children(self, children : List['Node']):
        for child in children:
            child.predecessor = self
            self.children.append(child)

    def number_of_children(self) -> int:
        return len(self.children)

    def __str__(self) -> str:
        return f"{self.name}, #children: {len(self.children)}"
    
    def __repr__(self) -> str:
        return self.__str__()

class Leaf(Node):
    def __init__(self, name : str, predecessor : 'Node' = None, alternative_name : str = None):
        super().__init__(name, predecessor, alternative_name)
    
    def __str__(self) -> str:
        return f"{self.name}"
    

if __name__ == "__main__":
    filename = sys.argv[1]
    with open(filename, "rb") as f:
        root : Node = pickle.load(f)

    current_node = root
    while(True):
        print(f"Current node: {current_node}")
        user_input = input()
        if (user_input == ""):
            for i, child in enumerate(current_node.children):
                print(f"\t{i}: {child}")
        else:
            current_node = current_node.get_child(int(user_input)) 
