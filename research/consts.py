from types import SimpleNamespace

NUM_OF_KEYWORDS = 40
MODEL = "gpt-4-32k"

WORKER_TYPE = SimpleNamespace()
WORKER_TYPE.WEBPAGE = 0
WORKER_TYPE.SQL = 1
WORKER_TYPE.WORLDBANK = 2

WORKER_MODE = SimpleNamespace()
WORKER_MODE.STEP_BY_STEP = 0
WORKER_MODE.LOOK_AHEAD = 1
WORKER_MODE.KEYWORD_GEN_AND_MATCH = 2
WORKER_MODE.MATCH_AND_FILTER = 3
WORKER_MODE.SQL_GENERATE_ARGUMENTS = 4