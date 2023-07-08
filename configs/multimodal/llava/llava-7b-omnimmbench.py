# dataloader settings
val_pipeline = [
    dict(type='mmpretrain.torchvision/Resize',
         size=(224, 224),
         interpolation=3),
    dict(type='mmpretrain.torchvision/ToTensor'),
    dict(
        type='mmpretrain.torchvision/Normalize',
        mean=(0.48145466, 0.4578275, 0.40821073),
        std=(0.26862954, 0.26130258, 0.27577711),
    ),
    dict(
        type='mmpretrain.PackInputs',
        algorithm_keys=[
            'question', 'answer', 'options', 'category', 'l2-category',
            'context', 'index', 'options_dict'
        ],
    ),
]

dataset = dict(type='opencompass.OmniMMBench',
               data_file='data/mm_benchmark/mmagi_v030_full_inferin.tsv',
               pipeline=val_pipeline)

dataloader = dict(
    batch_size=1,
    num_workers=4,
    dataset=dataset,
    collate_fn=dict(type='pseudo_collate'),
    sampler=dict(type='DefaultSampler', shuffle=False),
)

# model settings
model = dict(
    type='llava-omnimmbench',
    model_path='/mnt/petrelfs/share_data/libo/LLaVA-7B-v1',
)  # noqa
"""
You can download llava's weights to your own path, remember you need to convert the delta weights to full model weights
following: https://github.com/haotian-liu/LLaVA/blob/main/README.md#llava-weights
"""

# evaluation settings
evaluator = [
    dict(type='mm_benchmark.MMDump',
         save_path='work_dirs/llava-7b-omnimmbench.xlsx')
]
