from mmengine.config import read_base

with read_base():
    from .groups.agieval import agieval_summary_groups
    from .groups.mmlu import mmlu_summary_groups
    from .groups.cmmlu import cmmlu_summary_groups
    from .groups.ceval import ceval_summary_groups
    from .groups.bbh import bbh_summary_groups
    from .groups.GaokaoBench import GaokaoBench_summary_groups
    from .groups.flores import flores_summary_groups


summarizer = dict(
    dataset_abbrs=[
        '--------- 考试 Exam ---------',  # category
        # 'Mixed', # subcategory
        "ceval",
        'agieval',
        'mmlu',
        'cmmlu',
        "GaokaoBench",
        'ARC-c',
        'ARC-e',
        '--------- 语言 Language ---------',  # category
        # '字词释义', # subcategory
        'WiC',
        # '成语习语', # subcategory
        'chid-dev',
        # '语义相似度', # subcategory
        'afqmc-dev',
        # '指代消解', # subcategory
        'WSC',
        # '多语种问答', # subcategory
        'tydiqa-goldp',
        # '翻译', # subcategory
        'flores_100',
        '--------- 知识 Knowledge ---------',  # category
        # '知识问答', # subcategory
        'BoolQ',
        'commonsense_qa',
        'triviaqa',
        'nq',
        '--------- 理解 Understanding ---------',  # category
        # '阅读理解', # subcategory
        'C3',
        'race-middle',
        'race-high',
        'openbookqa_fact',
        # '内容总结', # subcategory
        'csl_dev',
        'lcsts',
        'Xsum',
        # '内容分析', # subcategory
        'eprstmt-dev',
        'lambada',
        '--------- 推理 Reasoning ---------',  # category
        # '文本蕴含', # subcategory
        'cmnli',
        'ocnli',
        'AX_b',
        'AX_g',
        'RTE',
        # '常识推理', # subcategory
        'COPA',
        'ReCoRD',
        'hellaswag',
        'piqa',
        'siqa',
        # '数学推理', # subcategory
        'math',
        'gsm8k',
        # '定理应用', # subcategory
        # '阅读理解', # subcategory
        'drop',
        # '代码', # subcategory
        'openai_humaneval',
        'mbpp',
        # '综合推理', # subcategory
        "bbh",
    ],
    summary_groups=sum(
        [v for k, v in locals().items() if k.endswith("_summary_groups")], []),
    prompt_db=dict(
        database_path='configs/datasets/log.json',
        config_dir='configs/datasets',
        blacklist='.promptignore'),
)
