ANSWER = 'answer'
QUESTION = 'question'

LIB = 'lib'
API = 'api'
T5 = 't5'
GPT_MODEL = "text-davinci-002"
T5_MODEL = "allenai/unifiedqa-v2-t5-large-1363200"

QUESTION_TEMPLATE = 'all' # 'pos': positive question, 'neg': negative question, 'all': all questions

CONTENT_REPLACEMENT = {
    'tensorflow_gpu': 'tensorflow',
    't.f.': 'tensorflow',
    'tensorflow-gpu': 'tensorflow',
    'tesnorflow': 'tensorflow',
    'tensforflow': 'tensorflow',
    'cudadnn': 'cudnn'
}

ENTITY_LIST_REPLACEMENT = {
    'tf': 'tensorflow',
    'tf-gpu': 'tensorflow',
    'tensorflow-gpu': 'tensorflow'
}

API_IGNORE_LIST = [
    'e.g', 'i.e', 'x.x', 
    '.org', '.so', '.py', '.c', '.cpp', '.java', '.whl'
]

