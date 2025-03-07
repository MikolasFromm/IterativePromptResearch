from instances.openAI import OpenAIWrapper
from workers.factory import WorkerFactory
from data_sources.worldBank.factory import WorldBankFactory
from consts import WORKER_TYPE, WORKER_MODE

if __name__ == "__main__":
    # worker = WorkerFactory().create(
    #     WORKER_TYPE.WEBPAGE, 
    #     {
    #         'mode': WORKER_MODE.STEP_BY_STEP, 
    #         'query': 'Find the page with the work he has done.', 
    #         'url': 'https://miko.fromm.one/',
    #         'isolated_domain': False
    #     })
    # openAI_wrapper = OpenAIWrapper(
    #     keep_whole_context=False, 
    #     system_message="You are an assistant that is trying to find the best link to find a page about a topic. You can not ask any questions, you can only suggest links to the user BY WRITING THE NUMBER OF THE BEST LINK. If YOU ARE FINISHED or YOU DONT KNOW, return -1."
    #     )

    # worker = WorkerFactory().create(
    #     WORKER_TYPE.WEBPAGE, 
    #     {
    #         'mode': WORKER_MODE.LOOK_AHEAD, 
    #         'query': 'Find the page with the work he has done.', 
    #         'url': 'https://miko.fromm.one/',
    #         'look_ahead_depth': 2,
    #         'isolated_domain': False
    #     })
    # openAI_wrapper = OpenAIWrapper(
    #     keep_whole_context=False, 
    #     system_message="You are an assistant that is trying to find the best link to find a page about a topic. You can not ask any questions, you can only suggest links to the user BY WRITING THE NUMBER OF THE BEST LINK. If YOU ARE FINISHED or YOU DONT KNOW, return -1."
    #     )
    
    worker = WorkerFactory().create(
        WORKER_TYPE.WEBPAGE, 
        {
            'mode': WORKER_MODE.LOOK_AHEAD, 
            'query': 'Najdi stránku s termíny zkoušek.', 
            'url': 'https://www.mff.cuni.cz/',
            'look_ahead_depth': 2,
            'isolated_domain': True
        })
    openAI_wrapper = OpenAIWrapper(
        keep_whole_context=False, 
        system_message="You are an assistant that is trying to find the best link to find a page about a topic. You can not ask any questions, you can only suggest links to the user BY WRITING THE NUMBER OF THE BEST LINK. If YOU ARE FINISHED or YOU DONT KNOW, return -1. At the beginning, you are given a query and you should generate keywords that might be relevant to the query."
        )
    
    # worker = WorkerFactory().create(
    #     WORKER_TYPE.WEBPAGE, 
    #     {
    #         'mode': WORKER_MODE.MATCH_AND_FILTER, 
    #         'query': 'Find their investing strategies.', 
    #         'url': 'https://www.wood.com/',
    #         'isolated_domain': False
    #     })
    
    # openAI_wrapper = OpenAIWrapper(
    #     keep_whole_context=False, 
    #     system_message="You are an assistant that is trying to find the best link to find a page about a topic. You can not ask any questions, you can only suggest links to the user BY WRITING THE NUMBER OF THE BEST LINK. If YOU ARE FINISHED or YOU DONT KNOW, return -1."
    #     )

    # ## execute the worker
    # worker.execute(openAI_wrapper)

    # worker = WorkerFactory().create(
    #     WORKER_TYPE.WORLDBANK, 
    #     {
    #         'mode': WORKER_MODE.LOOK_AHEAD, 
    #         'look_ahead_depth': 2,
    #         'query': 'Find carbon emissions of Czechia.',
    #     })
    # openAI_wrapper = OpenAIWrapper(
    #     keep_whole_context=False, 
    #     system_message="You are an assistant that is trying to find the path to find a table about a topic. You can not ask any questions, you can only suggest which subsection should the user open BY WRITING THE NUMBER OF THE BEST SUBSECTION NAME. If YOU ARE FINISHED or YOU DONT KNOW, return -1."
    #     )
    
    # worker.execute(openAI_wrapper)

    # worker = WorkerFactory().create(
    #     WORKER_TYPE.SQL, 
    #     {
    #         'mode': WORKER_MODE.STEP_BY_STEP, 
    #         'query': 'From table "employees" select all employees with salary higher than 1000.'
    #     })
    # openAI_wrapper = OpenAIWrapper(
    #     keep_whole_context=False, 
    #     system_message="You are an assistant that is trying to create a best SQL prompt. You can not ask any questions, you can only suggest which operation should the user choose BY WRITING THE NUMBER OF THE BEST SUBSECTION NAME. If YOU ARE FINISHED or YOU DONT KNOW, return -1."
    #     )
    
    worker.execute(openAI_wrapper)