from instances.openAI import OpenAIWrapper
from workers.factory import WorkerFactory
from consts import WORKER_TYPE, WORKER_MODE

if __name__ == "__main__":
    worker = WorkerFactory().create(
        WORKER_TYPE.WEBPAGE, 
        {
            'mode': WORKER_MODE.LOOK_AHEAD, 
            'query': 'Navigate me to the page of Wood & Company.', 
            'url': 'https://miko.fromm.one/',
            'look_ahead_depth': 2,
            'isolated_domain': False
        })
    openAI_wrapper = OpenAIWrapper(
        keep_whole_context=False, 
        system_message="You are an assistant that is trying to find the best link to find a page about a topic. You can not ask any questions, you can only suggest links to the user BY WRITING THE NUMBER OF THE BEST LINK. If YOU ARE FINISHED or YOU DONT KNOW, return -1."
        )
    ## execute the worker
    worker.execute(openAI_wrapper)