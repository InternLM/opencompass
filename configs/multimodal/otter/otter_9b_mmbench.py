# dataloader settings
from opencompass.multimodal.models.otter import (
    OTTERMMBenchPromptConstructor, OTTERMMBenchPostProcessor)

val_pipeline = [
    dict(type="mmpretrain.torchvision/Resize", size=(224, 224), interpolation=3),
    dict(type="mmpretrain.torchvision/ToTensor"),
    dict(
        type="mmpretrain.torchvision/Normalize",
        mean=(0.48145466, 0.4578275, 0.40821073),
        std=(0.26862954, 0.26130258, 0.27577711),
    ),
    dict(
        type="mmpretrain.PackInputs",
        algorithm_keys=["question", "answer", "options", "category", "l2-category", "context", "index", "options_dict"],
    ),
]

dataset = dict(
    type="opencompass.MMBenchDataset", data_file="/path/to/mmbench/mmbench_test_20230712.tsv", pipeline=val_pipeline
)

otter_9b_mmbench_dataloader = dict(
    batch_size=1,
    num_workers=4,
    dataset=dataset,
    collate_fn=dict(type="pseudo_collate"),
    sampler=dict(type="DefaultSampler", shuffle=False),
)

# model settings
otter_9b_mmbench_model = dict(
    type="otter-9b",
    model_path="luodian/OTTER-Image-MPT7B",  # noqa
    load_bit="bf16",
    prompt_constructor=dict(type=OTTERMMBenchPromptConstructor,
                            model_label='GPT',
                            user_label='User'),
    post_processor=dict(type=OTTERMMBenchPostProcessor)
)

# evaluation settings
otter_9b_mmbench_evaluator = [dict(type="opencompass.DumpResults", save_path="work_dirs/otter-9b-mmbench.xlsx")]
