from instances.node import *
from pypika import Query
from typing import List
from consts import *
from typing import Dict
from copy import deepcopy

from nltk.stem.snowball import SnowballStemmer

MAX_DEPTH = 10

class SQLNode(OperationNode):
    """An implementation of a SQL node representing a database table operation."""
    def __init__(self, 
                 operation : Operation, 
                 tree_depth : int, 
                 textual_name : str,
                 previous_query : Optional[Query] = None,  
                 mandatory_following_operation: Optional['OperationNode'] = None,
                 predecessor : Optional['OperationNode'] = None,
                 current_query : Optional[Query] = None):
        super().__init__(
            operation=operation, 
            tree_depth=tree_depth, 
            textual_name=textual_name,
            mandatory_following_operation=mandatory_following_operation,
            predecessor=predecessor
            )
        self.previous_query : Query = previous_query if previous_query else Query()
        self.current_query : Query | None = current_query
        self.expanded = False

    def expand(self, mode : int, params : {str, }, cache : {str : Node} = {}) -> List['Node']:
        """Exapnds the current SQL operation node with all possible following operations available in the pseduo-database."""

        remaining_depth = params['look_ahead_depth'] if mode == WORKER_MODE.LOOK_AHEAD else 1

        if (len(self.operation.options) > 0):
            ## only return the mandatory following operation, dont expand it further at the moment
            self.children = [
                SQLNode(
                    operation=Operation(
                        name=option.name,
                        description=option.description
                    ),
                    tree_depth=self.tree_depth + 1,
                    textual_name=option.name,
                    previous_query=self.previous_query,
                    current_query=self.current_query,
                    predecessor=self.predecessor
                    ) for option in self.operation.options if option.required
            ]
            self.expanded = False
            return self.children

        if (mode == WORKER_MODE.KEYWORD_GEN_AND_MATCH):
            remaining_depth = MAX_DEPTH - self.tree_depth

        if (mode == WORKER_MODE.KEYWORD_GEN_AND_MATCH and self.tree_depth > MAX_DEPTH): ## recursion limit when generating tree based on keywords
            self.expanded = True
            return []

        if (not self.expanded):
            next_moves = self.__get_next_moves(self.previous_query)

            if (mode == WORKER_MODE.KEYWORD_GEN_AND_MATCH):
                stemmer = SnowballStemmer("english", ignore_stopwords=True)
                next_moves = {k: v for k, v in next_moves.items() if any(stemmer.stem(word.strip().casefold()) in params['keywords'] for word in k.replace('_', '').replace('.','').split())}

            if (mode == WORKER_MODE.MATCH_AND_FILTER):
                stemmer = SnowballStemmer("english", ignore_stopwords=True)
                keywords = [stemmer.stem(x.strip().casefold()) for x in params['query'].split()]
                next_moves = {k: v for k, v in next_moves.items() if any(stemmer.stem(word.strip().casefold()) in keywords for word in k.split())}

            self.children = [
                SQLNode(
                    operation=Operation(
                        name=name, 
                        description=f"SQL operation {name}", 
                        options=[OperationOption(name=arg, description=f"Fill the following arguments: \"{arg}\"", required=True) for arg in v["args"]]
                    ),
                    tree_depth=self.tree_depth + 1,
                    textual_name=name,
                    previous_query=v["func"] if not v["args"] else self.previous_query, ## if there are no arguments, next move can be added, otherwise the query remains the same until the argument is filled
                    current_query=v["func"] if v["args"] else None, ## if there are some arguments, saves the current query to be able to fill the arguments
                    predecessor=self.predecessor if not v["args"] else self ## keep the same predecessor to be able to continue the chain when argument filled
                ) for name, v in next_moves.items()
            ]

        if (remaining_depth > 1): ## if remaining depth is 1, we are currently on the last page
            for child in self.children:
                new_params = deepcopy(params)
                new_params['look_ahead_depth'] = remaining_depth - 1
                child.expand(mode, new_params, cache)

        self.expanded = True
        return self.children
    
    def finalize_exapansion(self, args : [str]) -> None:
        """Finalizes the expansion of the node, implementation specific."""
        self.previous_query = self.current_query(*args)
        self.operation.options = []
        self.expanded = True

    def __get_next_moves(self, query : Query) -> Dict[str, callable]:
        functions = {
            func: {
                "func": getattr(query, func), 
                "args": [arg for arg in getattr(query, func).__code__.co_varnames if arg not in ["cls", "kwargs"]]
                } for func in dir(query) if callable(getattr(query, func)) and not func.startswith("__") and not func.startswith("_")
            }
        
        return functions