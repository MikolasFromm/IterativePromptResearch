from instances.node import *
from typing import List
from consts import *

MAX_DEPTH = 10

class SQLNode(OperationNode):
    """An implementation of a SQL node representing a database table operation."""
    def __init__(self, operation : Operation, tree_depth : int, textual_name : str, optional_content : Optional[NodeContent] = None,  alternative_id : Optional[str] = None):
        super().__init__(
            operation=operation, 
            tree_depth=tree_depth, 
            textual_name=textual_name, 
            optional_content=optional_content, 
            alternative_id=alternative_id
            )
        self.expanded = False

    def expand(self, mode : int, params : {str, }, cache : {str : Node} = {}) -> List['Node']:
        """Exapnds the current SQL operation node with all possible following operations available in the pseduo-database."""

        remaining_depth = params['look_ahead_depth'] if mode == WORKER_MODE.LOOK_AHEAD else 1

        if (mode == WORKER_MODE.KEYWORD_GEN_AND_MATCH):
            remaining_depth = MAX_DEPTH - self.tree_depth

        if (mode == WORKER_MODE.KEYWORD_GEN_AND_MATCH and self.tree_depth > MAX_DEPTH): ## recursion limit when generating tree based on keywords
            return []
        

class OperationStack:
    """A class representing a stack of operations in the SQL database."""
    def __init__(self):
        self.operations : Dict[str, 'Operation'] = {
        }

        op_condition = OperationOption('condition', 'the condition to filter the data', True)
        op_where = Operation('where', 'filters the data', mandatory_following_operation=[op_condition])
        op_from = Operation('from', 'selects the table', mandatory_following_operation=[op_where])
        op_select = Operation('select', 'selects the data from the table', mandatory_following_operation=[op_from])
        
        op_order_by = Operation('order_by', 'orders the data')
        op_group_by = Operation('group_by', 'groups the data')
        op_having = Operation('having', 'filters the groups')
        op_limit = Operation('limit', 'limits the number of rows')
        op_offset = Operation('offset', 'offsets the rows')