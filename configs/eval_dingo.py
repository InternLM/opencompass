from mmengine.config import read_base

from opencompass.openicl.icl_prompt_template import PromptTemplate
from opencompass.openicl.icl_retriever import ZeroRetriever
from opencompass.openicl.icl_inferencer import GenInferencer
from opencompass.datasets import dingoDataset, dingoEvaluator


with read_base():
    from .models.hf_internlm.hf_internlm_7b import models

dingo_paths = [
    './data/dingo/en_162.csv',
    './data/dingo/zh_90.csv',
]

dingo_datasets = []
for path in dingo_paths:
    dingo_reader_cfg = dict(input_columns='input', output_column=None)
    dingo_infer_cfg = dict(
        prompt_template=dict(
            type=PromptTemplate,
            template=dict(round=[dict(role='HUMAN', prompt='{input}')])),
        retriever=dict(type=ZeroRetriever),
        inferencer=dict(type=GenInferencer),
    )
    dingo_eval_cfg = dict(evaluator=dict(type=dingoEvaluator), pred_role='BOT')

    dingo_datasets.append(
        dict(
            abbr='dingo_' + path.split('/')[-1].split('.csv')[0],
            type=dingoDataset,
            path=path,
            reader_cfg=dingo_reader_cfg,
            infer_cfg=dingo_infer_cfg,
            eval_cfg=dingo_eval_cfg,
        ))

datasets = dingo_datasets

work_dir = './outputs/eval_dingo'
