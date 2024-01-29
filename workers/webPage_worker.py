from workers.worker import Worker
from data_sources.webPage_node import WebPageLink
from typing import List
from instances.node import OperationNode
from consts import WORKER_MODE

class WebpageWorker(Worker):
    def __init__(self, mode : int, query : str, params : {str, str}):
        super().__init__(mode, query, params)
        self.reached_end = False
        self.current_path = List['OperationNode']
        self.initial_node = WebPageLink(params['url'], set([params['url']]), 0, "Base page")

    def __str__(self):
        return f"WorkerWebPage: {self.params['url']}"
            
    def create_llm_query(self, initial_query : str, steps_so_far : str, current_node : WebPageLink, mode : int) -> str:
        """Creates a query for the LLM model based on the current node."""
        next_moves = []
        prompt = ""

        match mode:
            case WORKER_MODE.STEP_BY_STEP:
                next_moves = [f"\t{i}: {child.textual_name}\n" for i, child in enumerate(current_node.children)]
                prompt = (
                f"query: {initial_query}\n"
                f"steps done: {steps_so_far}\n"
                f"next possible link names:\n"
                f"{''.join(next_moves)}"
                )
                return prompt
            case WORKER_MODE.LOOK_AHEAD:
                for i, child in enumerate(current_node.children):
                    next_moves.append(f"\t{i}: {child.textual_name}\n")
                    for j, grandchild in enumerate(child.children):
                        next_moves.append(f"\t\t-: {grandchild.textual_name}\n")
                prompt = (
                f"query: {initial_query}\n"
                f"steps done: {steps_so_far}\n"
                f"next possible link names:\n"
                f"{''.join(next_moves)}"
                )
                print(prompt)

        return prompt