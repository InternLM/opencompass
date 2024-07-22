from mmengine.config import read_base

with read_base():
    # from .datasets.subjective.multiround.mtbench_single_judge_diff_temp import subjective_datasets
    from .datasets.subjective.wildbench.wildbench_pair_judge import wildbench_datasets
    from .models.openai.gpt_4 import models as gpt4_models
    from .models.hf_llama.hf_llama2_70b_chat import models as llama2_models
    # from .models.gemma.hf_gemma_2b_it import models
    # from .models.hf_llama.hf_llama3_70b_instruct import models as llama3_model
    # # from .models.hf_internlm.hf_internlm2_chat_7b import models
    # from .models.yi.hf_yi_1_5_34b_chat import models as yi_model
    # from .models.qwen.hf_qwen1_5_72b_chat import models as qwen_model

from opencompass.models import HuggingFaceCausalLM, HuggingFace, HuggingFaceChatGLM3, OpenAI
from opencompass.partitioners import NaivePartitioner, SizePartitioner
from opencompass.partitioners.sub_naive import SubjectiveNaivePartitioner
from opencompass.partitioners.sub_size import SubjectiveSizePartitioner
from opencompass.runners import LocalRunner
from opencompass.runners import SlurmSequentialRunner
from opencompass.tasks import OpenICLInferTask
from opencompass.tasks.subjective_eval import SubjectiveEvalTask
from opencompass.summarizers import WildBenchPairSummarizer
from opencompass.models.claude_api.claude_api import Claude
from opencompass.models import HuggingFacewithChatTemplate


models = sum([v for k, v in locals().items() if k.endswith('_model')], [])

api_meta_template = dict(
    round=[
        dict(role='SYSTEM', api_role='SYSTEM'),
        dict(role='HUMAN', api_role='HUMAN'),
        dict(role='BOT', api_role='BOT', generate=True),
    ]
)

# -------------Inference Stage ----------------------------------------
# For subjective evaluation, we often set do sample for models

models = [
    dict(
        type=HuggingFacewithChatTemplate,
        abbr='llama-3-8b-instruct-hf',
        path='meta-llama/Meta-Llama-3-8B-Instruct',
        max_out_len=4096,
        batch_size=8,
        run_cfg=dict(num_gpus=1),
        stop_words=['<|end_of_text|>', '<|eot_id|>'],
    ),
    dict(
        type=HuggingFacewithChatTemplate,
        abbr='yi-1.5-6b-chat-hf',
        path='01-ai/Yi-1.5-6B-Chat',
        max_out_len=4096,
        batch_size=8,
        run_cfg=dict(num_gpus=1),
    ),
    # dict(
    #     type=HuggingFacewithChatTemplate,
    #     abbr='qwen1.5-7b-chat-hf',
    #     path='Qwen/Qwen1.5-7B-Chat',
    #     max_out_len=4096,
    #     batch_size=8,
    #     run_cfg=dict(num_gpus=1),
    # )
]

datasets = [*wildbench_datasets]

# -------------Evalation Stage ----------------------------------------

## ------------- JudgeLLM Configuration
judge_models = [dict(
    abbr='GPT4-Turbo',
    type=OpenAI,
    path='gpt-4-0613', # To compare with the official leaderboard, please use gpt4-0613
    meta_template=api_meta_template,
    query_per_second=16,
    max_out_len=2048,
    max_seq_len=2048,
    batch_size=8,
    temperature=0,
)]

## single evaluation
# eval = dict(
#     partitioner=dict(type=SubjectiveSizePartitioner, strategy='split', max_task_size=10000, mode='singlescore', models=models, judge_models=judge_models),
#     runner=dict(type=LocalRunner, max_num_workers=32, task=dict(type=SubjectiveEvalTask)),
# )
infer = dict(
    partitioner=dict(type=SizePartitioner, max_task_size=1000, strategy='split'),
    runner=dict(
        type=SlurmSequentialRunner,
        max_num_workers=64,
        quotatype='reserved',
        partition='llmeval',
        task=dict(type=OpenICLInferTask)),
)

eval = dict(
    partitioner=dict(
        type=SubjectiveNaivePartitioner,
        judge_models=judge_models
    ),
    runner=dict(
        type=LocalRunner,
        max_num_workers=3,
        task=dict(
            type=SubjectiveEvalTask
        ))
)

summarizer = dict(type=WildBenchPairSummarizer)

work_dir = 'outputs/wildbench/'
