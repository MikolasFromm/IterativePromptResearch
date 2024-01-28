from instances.openAI import OpenAIWrapper
from workers.worker import WorkerFactory
from consts import WORKER_TYPE, WORKER_MODE

if __name__ == "__main__":
    worker = WorkerFactory().create(
        WORKER_TYPE.WEBPAGE, 
        {
            'mode': WORKER_MODE.STEP_BY_STEP, 
            'query': 'Find the page with my coding projects.', 
            'url': 'https://miko.fromm.one/'
        })
    openAI_wrapper = OpenAIWrapper("You are an assistant that is trying to find the best link to find a page about a topic. You can not ask any questions, you can only suggest links to the user BY WRITING THE NUMBER OF THE BEST LINK. If YOU ARE FINISHED or YOU DONT KNOW, return -1.")
    worker.execute(openAI_wrapper)