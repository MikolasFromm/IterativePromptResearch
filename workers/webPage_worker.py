from worker import Worker
from data_sources.webPage_wrapper import WebPageLink
from typing import List
from instances.node import OperationNode

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