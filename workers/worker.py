from instances.openAI import OpenAIWrapper
from instances.node import *
from abc import abstractmethod

from consts import *


class Worker:
    def __init__(self, mode : int, query : str, params : {str, }):
        self.mode = mode
        self.query = query
        self.params = params
        self.steps_so_far = ""
        self.initial_node : 'Node | None' = None

    @abstractmethod
    def create_llm_query(self, initial_query : str, steps_so_far : str, current_node : Node, mode : int) -> str:
        """Creates a query for the LLM model based on the current node. Implementation specific."""
        raise NotImplementedError

    def process_llm_response(self, current_node : Node, response : str) -> Node | None:
        response = response.strip()

        if (response == "-1"):
            return None

        if not response.isdigit():
            raise Exception(f"Response {response} is not digit")
        
        int_response = int(response)

        if (int_response == -1):
            return None
        else:
            return current_node.get_child(int_response)

    def get_final_steps_desc(self):
        return self.steps_so_far.strip(" -> ")

    def execute(self, openAI_wrapper : OpenAIWrapper):
        current_node = self.initial_node

        if (current_node is None):
            raise Exception("Initial node not set")
        
        cache = {}
        match self.mode:
            case WORKER_MODE.STEP_BY_STEP | WORKER_MODE.LOOK_AHEAD:
                while True:
                
                    current_node.expand(self.mode, self.params, cache)

                    if (current_node.child_count() == 0): 
                        print(self.get_final_steps_desc())
                        print(current_node.get_final_str_desc())
                        break
                    
                    query = self.create_llm_query(self.query, self.steps_so_far, current_node, self.mode) ## creates the query for the LLM model, implementation specific
                    response = openAI_wrapper.upload_query(query) ## uploads the query to the LLM model and gets the response, generic
                    next_node = self.process_llm_response(current_node, response) ## processes the response from the LLM model, generic
                    
                    if (next_node is None):
                        print(self.get_final_steps_desc())
                        print(current_node.get_final_str_desc())
                        break
                    else:
                        self.steps_so_far += f"{next_node.textual_name} -> "
                        current_node = next_node