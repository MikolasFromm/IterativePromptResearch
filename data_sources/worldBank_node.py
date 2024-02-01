from instances.node import *
from typing import List
from consts import *

MAX_DEPTH = 10

class WorldBankNode(OperationNode):
    """An Implementation of a WorldBank node representing a database table operation."""
    def __init__(self, operation : Operation, tree_depth : int, textual_name : str, mandatory_following_operation: Optional['Operation'] = None, optional_content : Optional[NodeContent] = None,  alternative_id : Optional[str] = None):
        super().__init__(
            operation=operation, 
            tree_depth=tree_depth, 
            textual_name=textual_name, 
            mandatory_following_operation=mandatory_following_operation, 
            optional_content=optional_content, 
            alternative_id=alternative_id
            )
        self.expanded = False

    def expand(self, mode : int, params : {str, }, cache : {str : Node} = {}) -> List['Node']:
        """Exapnds the current WorldBank operation node with all possible following operations available in the pseduo-database."""

        remaining_depth = params['look_ahead_depth'] if mode == WORKER_MODE.LOOK_AHEAD else 1

        if (mode == WORKER_MODE.KEYWORD_GEN_AND_MATCH):
            remaining_depth = MAX_DEPTH - self.tree_depth

        if (mode == WORKER_MODE.KEYWORD_GEN_AND_MATCH and self.tree_depth > MAX_DEPTH):
            return []
        
        if (not self.expanded):
            ...