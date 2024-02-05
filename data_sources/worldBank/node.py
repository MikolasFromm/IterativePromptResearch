from instances.node import *
from nltk.stem.snowball import SnowballStemmer
from copy import deepcopy
from typing import List
from consts import *

MAX_DEPTH = 10

class WorldBankNode(OperationNode):
    """An Implementation of a WorldBank node representing a database table operation."""
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
        """Exapnds the current WorldBank operation node with all possible following operations available in the pseduo-database."""

        remaining_depth = params['look_ahead_depth'] if mode == WORKER_MODE.LOOK_AHEAD else 1

        if (mode == WORKER_MODE.KEYWORD_GEN_AND_MATCH):
            remaining_depth = MAX_DEPTH - self.tree_depth

        if (mode == WORKER_MODE.KEYWORD_GEN_AND_MATCH and self.tree_depth > MAX_DEPTH):
            return []
        
        if (not self.expanded):
            if (mode == WORKER_MODE.KEYWORD_GEN_AND_MATCH): ## filtering when generating tree based on keywords
                stemmer = SnowballStemmer("english", ignore_stopwords=True)
                keywords = [stemmer.stem(x.strip().casefold()) for x in params['query'].split()]
                self.children = [child for child in self.children if any(stemmer.stem(word.strip().casefold()) in keywords for word in child.textual_name.split())]

            if (mode == WORKER_MODE.MATCH_AND_FILTER):
                stemmer = SnowballStemmer("english", ignore_stopwords=True)
                keywords = [stemmer.stem(x.strip().casefold()) for x in params['query'].split()]
                self.children = [child for child in self.children if any(stemmer.stem(word.strip().casefold()) in keywords for word in child.textual_name.split())]

        if (remaining_depth > 1):
            for child in self.children:
                new_params = deepcopy(params)
                new_params['look_ahead_depth'] = remaining_depth - 1
                child.expand(mode, params, cache)
        
        self.expanded = True
        return self.children
    
    def get_final_str_desc(self) -> str:
        return f"{self.textual_name}"