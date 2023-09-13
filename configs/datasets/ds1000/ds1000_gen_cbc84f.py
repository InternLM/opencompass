from opencompass.openicl.icl_prompt_template import PromptTemplate
from opencompass.openicl.icl_retriever import ZeroRetriever
from opencompass.openicl.icl_inferencer import GenInferencer
from opencompass.datasets import DS1000Dataset, ds1000_postprocess, DS1000Evaluator

ds1000_reader_cfg = dict(
    input_columns=["prompt"],
    output_column="test_column",
    train_split='test',
    test_split='test')

ds1000_infer_cfg = dict(
    prompt_template=dict(
        type=PromptTemplate,
        template=dict(round=[
            dict(
                role="HUMAN",
                prompt="{prompt}",
            ),
        ]),
    ),
    retriever=dict(type=ZeroRetriever),
    inferencer=dict(type=GenInferencer),
)

ds1000_eval_cfg = dict(
    evaluator=dict(type=DS1000Evaluator),
    pred_role="BOT",
    pred_postprocessor=dict(type=ds1000_postprocess),
)

ds1000_datasets = [
    dict(
        abbr=f"ds1000_{lib}",
        type=DS1000Dataset,  # bustm share the same format with AFQMC
        path="ds1000_data/",
        libs=f"{lib}",
        reader_cfg=ds1000_reader_cfg,
        infer_cfg=ds1000_infer_cfg,
        eval_cfg=ds1000_eval_cfg,
    ) for lib in [
        'Pandas',
        'Numpy',
        'Matplotlib',
        'Tensorflow',
        'Scipy',
        'Sklearn',
        'Pytorch',
    ]
]
