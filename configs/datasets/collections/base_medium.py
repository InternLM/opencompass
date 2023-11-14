from mmengine.config import read_base

with read_base():
    from ..mmlu.mmlu_ppl_ac766d import mmlu_datasets
    from ..ceval.ceval_ppl_578f8d import ceval_datasets
    from ..agieval.agieval_mixed_2f14ad import agieval_datasets
    from ..GaokaoBench.GaokaoBench_mixed_f2038e import GaokaoBench_datasets
    from ..bbh.bbh_gen_5b92b0 import bbh_datasets
    from ..humaneval.humaneval_gen_8e312c import humaneval_datasets
    from ..mbpp.mbpp_gen_1e1056 import mbpp_datasets
    from ..CLUE_C3.CLUE_C3_ppl_e24a31 import C3_datasets
    from ..CLUE_CMRC.CLUE_CMRC_gen_1bd3c8 import CMRC_datasets
    from ..CLUE_DRCD.CLUE_DRCD_gen_1bd3c8 import DRCD_datasets
    from ..CLUE_afqmc.CLUE_afqmc_ppl_6507d7 import afqmc_datasets
    from ..CLUE_cmnli.CLUE_cmnli_ppl_fdc6de import cmnli_datasets
    from ..CLUE_ocnli.CLUE_ocnli_ppl_fdc6de import ocnli_datasets
    from ..FewCLUE_bustm.FewCLUE_bustm_ppl_e53034 import bustm_datasets
    from ..FewCLUE_chid.FewCLUE_chid_ppl_8f2872 import chid_datasets
    from ..FewCLUE_cluewsc.FewCLUE_cluewsc_ppl_4284a0 import cluewsc_datasets
    from ..FewCLUE_csl.FewCLUE_csl_ppl_841b62 import csl_datasets
    from ..FewCLUE_eprstmt.FewCLUE_eprstmt_ppl_f1e631 import eprstmt_datasets
    from ..FewCLUE_ocnli_fc.FewCLUE_ocnli_fc_ppl_c08300 import ocnli_fc_datasets
    from ..FewCLUE_tnews.FewCLUE_tnews_ppl_d10e8a import tnews_datasets
    from ..lcsts.lcsts_gen_8ee1fe import lcsts_datasets
    from ..lambada.lambada_gen_217e11 import lambada_datasets
    from ..storycloze.storycloze_ppl_496661 import storycloze_datasets
    from ..SuperGLUE_AX_b.SuperGLUE_AX_b_ppl_6db806 import AX_b_datasets
    from ..SuperGLUE_AX_g.SuperGLUE_AX_g_ppl_66caf3 import AX_g_datasets
    from ..SuperGLUE_BoolQ.SuperGLUE_BoolQ_ppl_314b96 import BoolQ_datasets
    from ..SuperGLUE_CB.SuperGLUE_CB_ppl_0143fe import CB_datasets
    from ..SuperGLUE_COPA.SuperGLUE_COPA_ppl_9f3618 import COPA_datasets
    from ..SuperGLUE_MultiRC.SuperGLUE_MultiRC_ppl_ced824 import MultiRC_datasets
    from ..SuperGLUE_RTE.SuperGLUE_RTE_ppl_66caf3 import RTE_datasets
    from ..SuperGLUE_ReCoRD.SuperGLUE_ReCoRD_gen_30dea0 import ReCoRD_datasets
    from ..SuperGLUE_WiC.SuperGLUE_WiC_ppl_312de9 import WiC_datasets
    from ..SuperGLUE_WSC.SuperGLUE_WSC_ppl_003529 import WSC_datasets
    from ..race.race_ppl_a138cd import race_datasets
    from ..Xsum.Xsum_gen_31397e import Xsum_datasets
    from ..gsm8k.gsm8k_gen_1d7fe4 import gsm8k_datasets
    from ..summedits.summedits_ppl_1fbeb6 import summedits_datasets
    from ..math.math_gen_265cce import math_datasets
    from ..TheoremQA.TheoremQA_gen_ef26ca import TheoremQA_datasets
    from ..hellaswag.hellaswag_ppl_47bff9 import hellaswag_datasets
    from ..ARC_e.ARC_e_ppl_a450bd import ARC_e_datasets
    from ..ARC_c.ARC_c_ppl_a450bd import ARC_c_datasets
    from ..commonsenseqa.commonsenseqa_ppl_5545e2 import commonsenseqa_datasets
    from ..piqa.piqa_ppl_1cf9f0 import piqa_datasets
    from ..siqa.siqa_ppl_ced5f6 import siqa_datasets
    from ..strategyqa.strategyqa_gen_1180a7 import strategyqa_datasets
    from ..winogrande.winogrande_ppl_55a66e import winogrande_datasets
    from ..obqa.obqa_ppl_c7c154 import obqa_datasets
    from ..nq.nq_gen_c788f6 import nq_datasets
    from ..triviaqa.triviaqa_gen_2121ce import triviaqa_datasets
    from ..flores.flores_gen_806ede import flores_datasets

datasets = sum((v for k, v in locals().items() if k.endswith('_datasets')), [])
