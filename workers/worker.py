from instances.openAI import OpenAIWrapper
from instances.node import *
from data_sources.webPage_wrapper import WebPageLink
from abc import abstractmethod

from consts import *


class Worker:
    def __init__(self, mode : int, query : str, param : str):
        self.mode = mode
        self.query = query
        self.param = param
        self.steps_so_far = ""
        self.initial_node : 'Node | None' = None

    @abstractmethod
    def create_llm_query(self, initial_query : str, steps_so_far : str, current_node : Node) -> str:
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
        
        match self.mode:
            case WORKER_MODE.STEP_BY_STEP:
                while True:

                    current_node.expand()
                    if (current_node.child_count() == 0): break ## dont continue if there are no children
                    
                    query = self.create_llm_query(self.query, self.steps_so_far, current_node) ## creates the query for the LLM model, implementation specific
                    response = openAI_wrapper.upload_query(query) ## uploads the query to the LLM model and gets the response, generic
                    next_node = self.process_llm_response(current_node, response) ## processes the response from the LLM model, generic
                    
                    if (next_node is None):
                        print(self.get_final_steps_desc())
                        print(current_node.get_final_str_desc())
                        break
                    else:
                        self.steps_so_far += f"{next_node.textual_name} -> "
                        current_node = next_node
            
            case WORKER_MODE.LOOK_AHEAD:


class WorkerFactory:
    def create(self, type : int, arguments : dict) -> Worker:
        match type:
            case WORKER_TYPE.WEBPAGE:
                return WebpageWorker(arguments['mode'], arguments['query'], arguments['url'])
            case _:
                raise Exception("Not implemented")

class WebpageWorker(Worker):
    def __init__(self, mode : int, query : str, param : str):
        super().__init__(mode, query, param)
        self.reached_end = False
        self.current_path = List['OperationNode']
        self.initial_node = WebPageLink(param, set([param]), 0, "Base page")

    def __str__(self):
        return f"WorkerWebPage: {self.param}"
            
    def create_llm_query(self, initial_query : str, steps_so_far : str, current_node : WebPageLink) -> str:
        """Creates a query for the LLM model based on the current node."""
        next_moves = [f"\t{i}: {child.textual_name}\n" for i, child in enumerate(current_node.children)]
        prompt = (
        f"query: {initial_query}\n"
        f"steps done: {steps_so_far}\n"
        f"next possible link names:\n"
        f"{''.join(next_moves)}"
        )
        return prompt
