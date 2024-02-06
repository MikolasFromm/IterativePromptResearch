from abc import abstractmethod
from typing import List, Dict, Optional
import uuid

class NodeContent:
    """Generic class to represent specific and complex content of the node."""
    def __init__(self, content):
        """Only saves the content of the node. The content is build by calling the build method."""
        self.dict: Dict = content

    @abstractmethod
    def build(self):
        """Builds the content of the node, implementation specific."""
        raise NotImplementedError

    def __str__(self):
        return f"NodeContent: {self.dict}"
    
class Node:
    """Generic class to represent a node in the decision tree. The node's content and children are lazy loaded by calling the expand method."""
    def __init__(self, tree_depth : int, textual_name : str, optional_content : Optional[NodeContent] = None,  alternative_id : Optional[str] = None):
        self.id = uuid.uuid4() ## unique id of the node
        self.alternative_id = alternative_id ## alternative human friendly id of the node
        self.tree_depth = tree_depth ## depth of the node in the tree
        self.textual_name = textual_name ## short representation of the node
        self.content = optional_content ## full representation of the node
        self.children: List['Node'] = [] ## all children of the node, lazy loaded by calling the expand method

    def __str__(self):
        return f"Node: {self.textual_name}, #children: {len(self.children)}, {self.alternative_id}"
    
    @abstractmethod
    def get_final_str_desc(self):
        raise NotImplementedError

    def child_count(self) -> 'int':
        return len(self.children)

    def get_child(self, index : int) -> 'Node':
        if (index >= len(self.children)):
            raise Exception(f'Index {index} out of range for node {self.textual_name}')
        
        return self.children[index]

    @abstractmethod
    def expand(self, mode : int, remaining_depth = 1, cache = {}) -> List['Node']:
        """Expands the node to the next depth, implementation specific."""
        raise NotImplementedError
    
    @abstractmethod
    def finalize_exapansion(self, args : [str]) -> None:
        """Finalizes the expansion of the node, implementation specific."""
        pass
    
class OperationOption:
    """Represents option for a specific operation. It should be an option that has no specific content."""
    def __init__(self, name : str, description : str, required : bool, argument = None):
        self.name = name
        self.description = description
        self.argument = argument
        self.required = required

class Operation:
    """Represents an operation that can be performed on the node. Each node has one operation that can be performed on it."""
    def __init__(self, name : str, description : str, options: List['OperationOption'] = []):
        self.name = name
        self.description = description
        self.options = options

    def __str__(self):
        return f"Operation: {self.name}"
    
class OperationNode(Node):
    """Represents a node that has an operation that can be performed on it."""
    def __init__(self, 
                 operation : Operation, 
                 tree_depth : int, 
                 textual_name : str, 
                 optional_content : Optional[NodeContent] = None,  
                 alternative_id : Optional[str] = None, 
                 mandatory_following_operation: Optional['OperationNode'] = None, 
                 predecessor : Optional['OperationNode'] = None):
        super().__init__(tree_depth, textual_name, optional_content, alternative_id)
        self.operation = operation
        self.mandatory_following_operation = mandatory_following_operation
        self.predecessor = predecessor

    def textual_reponse_expected(self) -> bool:
        """Returns true if the node expects textual response from the user."""
        return len(self.operation.options) > 0

## static operations
open_table_operation = Operation('open_table', 'opens the table')
select_subsection_operation = Operation('select_subsection', 'selects the subsection')
open_link_operation = Operation('open_link', 'opens the link in the browser')