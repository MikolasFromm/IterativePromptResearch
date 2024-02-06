from workers.worker import Worker
from typing import List
from instances.node import Operation, OperationNode, Node
from data_sources.SQL.node import SQLNode
from nltk.stem.snowball import SnowballStemmer
from consts import WORKER_MODE

NUM_OF_KEYWORDS = 40

class SQLWorker(Worker):
    def __init__(self, mode : int, query : str, params : {str, }):
        super().__init__(mode, query, params)
        self.current_path : List['OperationNode'] = []
        self.reached_end : bool = False
        self.stemmer : SnowballStemmer = SnowballStemmer("english", ignore_stopwords=True)
        self.initial_node : Node = SQLNode(operation=Operation(name="entry operation", description="entry point"), tree_depth=0, textual_name="entry operation")

    def __str__(self):
        return f"WorkerSQL: {self.query}"
    
    def create_llm_query(self, initial_query : str, steps_so_far : str, current_node : SQLNode, mode : int) -> str:
        """Creates a query for the LLM model based on the current node."""
        next_moves = []
        prompt = ""

        match mode:
            case WORKER_MODE.STEP_BY_STEP | WORKER_MODE.MATCH_AND_FILTER:
                next_moves = [f"\t{i}: {child.textual_name}\n" for i, child in enumerate(current_node.children)]
                prompt = (
                f"query: {initial_query}\n"
                f"steps done: {steps_so_far}\n"
                f"next possible moves names:\n"
                f"{''.join(next_moves)}"
                )
            case WORKER_MODE.LOOK_AHEAD:
                for i, child in enumerate(current_node.children):
                    next_moves.append(f"{i}: {self.create_look_ahead_prompt(child, self.params['look_ahead_depth']-1, self.params['look_ahead_depth']-1)}")
                prompt = (
                f"query: {initial_query}\n"
                f"steps done: {steps_so_far}\n"
                f"next possible moves names:\n"
                f"{''.join(next_moves)}"
                )
            case WORKER_MODE.KEYWORD_GEN_AND_MATCH:
                prompt = (
                f"query: {initial_query}\n"
                f"For the query above, please write {NUM_OF_KEYWORDS} keywords that might be relevant for creating SQL query. Prefere single words. Use the language of the query!\n"
                f"Please separate the keywords with semicolon. Dont write anything else!\n"
                )

        print(prompt)
        return prompt
    
    def process_llm_response(self, current_node : SQLNode, response : str, mode : int) -> Node | List['str'] | None:
        response = response.strip()

        match mode:
            case WORKER_MODE.STEP_BY_STEP | WORKER_MODE.LOOK_AHEAD | WORKER_MODE.MATCH_AND_FILTER:
                if (response == "-1"):
                    return None
                
                if not response.isdigit():
                    raise Exception(f"Response {response} is not digit")
                else:
                    try:
                        int_response = int(response)
                        return current_node.get_child(int_response)
                    except:
                        print("Invalid int_response")
                        return None
            case WORKER_MODE.KEYWORD_GEN_AND_MATCH:
                keywords = response.split(";")
                keywords = [self.stemmer.stem(x.strip().casefold()) for x in keywords]
                return keywords
            
    def create_look_ahead_prompt(self, child : Node, depth_total : int, depth_remaining : int):
        prompt = f"{''.join(['\t' for _ in range(depth_total - depth_remaining)])}: {child.textual_name}\n"
        
        if depth_remaining == 0:
            return prompt
        
        for i, grandchild in enumerate(child.children):
            prompt += f"{self.create_look_ahead_prompt(grandchild, depth_remaining - 1)}"
        return prompt
