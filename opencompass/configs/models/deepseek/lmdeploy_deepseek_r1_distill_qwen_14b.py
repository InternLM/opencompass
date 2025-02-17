from opencompass.models import TurboMindModelwithChatTemplate

models = [
    dict(
        type=TurboMindModelwithChatTemplate,
        abbr='deepseek-r1-distill-qwen-14b-turbomind',
        path='deepseek-ai/DeepSeek-R1-Distill-Qwen-14B',
        engine_config=dict(session_len=32768, max_batch_size=16, tp=2),
        gen_config=dict(top_k=1,
                        temperature=1e-6,
                        top_p=0.9,
                        max_new_tokens=4096),
        max_seq_len=32768,
        max_out_len=32768,
        batch_size=16,
        run_cfg=dict(num_gpus=2),
    )
]
