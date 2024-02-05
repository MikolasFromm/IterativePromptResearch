from workers.worker import Worker
from workers.webPage.worker import WebpageWorker
from workers.worldBank.worker import WorldBankWorker
from consts import *

class WorkerFactory:
    def create(self, type : int, arguments : dict) -> Worker:
        match type:
            case WORKER_TYPE.WEBPAGE:
                return WebpageWorker(arguments['mode'], arguments['query'], arguments)
            case WORKER_TYPE.WORLDBANK:
                return WorldBankWorker(arguments['mode'], arguments['query'], arguments)
            case _:
                raise Exception("Not implemented")