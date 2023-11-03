from opencompass.openicl import BaseEvaluator
from opencompass.registry import TEXT_POSTPROCESSORS


@TEXT_POSTPROCESSORS.register_module('gsm8k_dataset')
def gsm8k_dataset_postprocess(text: str) -> str:
    return text.split('#### ')[1].replace(',', '')


@TEXT_POSTPROCESSORS.register_module('gsm8k')
def gsm8k_postprocess(text: str) -> str:
    text = text.split('\n\n')[0]
    text = text.split(' ')[::-1]
    flag = False
    ret = ''
    for i in range(len(text)):
        s = text[i]
        for i in range(len(s)):
            if s[i].isdigit():
                flag = True
                ret = s
                break
        if flag:
            break
    ret1 = ''
    for i in range(len(ret)):
        if ret[i].isdigit():
            ret1 += ret[i]
    return ret1


class Gsm8kEvaluator(BaseEvaluator):

    def score(self, predictions, references):
        if len(predictions) != len(references):
            return {
                'error': 'predictions and references have different '
                'length'
            }
        correct = 0
        count = 0
        details = []
        for i, j in zip(predictions, references):
            detail = {'pred': i, 'answers': j, 'correct': False}
            count += 1
            if i == j:
                correct += 1
                detail['correct'] = True
            details.append(detail)
        result = {'accuracy': 100 * correct / count, 'details': details}
        return result


class Gsm8kAgentEvaluator(BaseEvaluator):
    """Gsm8k agent evaluator for soft condition.

    Args:
        action (str): Action for catching internal prediction.
            Defaults to `PythonInterpreter`.
    """

    def __init__(self, action: str = 'PythonInterpreter'):
        self.action = action

    def soft_equal(self, pred, refer, step):
        try:
            soft_pred = step['result']['text']
            if str(int(float(soft_pred))) == refer:
                return True
        except Exception:
            # result might not exists
            # text cannot convert to float
            print(pred, soft_pred, refer)
        return False

    def get_action(self, step):
        for s in step:
            if s['type'] == self.action:
                return s

    def score(self, predictions, references, steps):
        """Calculate accuracy."""

        row_reasoning_scope = 0
        action_scope = 0
        code_scope = 0
        reasoning_scope = 0
        final_scope = 0
        total = len(references)
        for pred, refer, step in zip(predictions, references, steps):
            # if final answer right
            if pred == refer:
                if self.get_action(step):
                    final_scope += 1
                else:
                    row_reasoning_scope += 1
            else:
                s = self.get_action(step)
                if s:
                    action_scope += 1
                    if not s['errmsg']:
                        code_scope += 1
                        # whether action result is correct
                        reasoning_scope += self.soft_equal(pred, refer, s)

        result = dict(
            follow_acc=100 * (row_reasoning_scope + final_scope) / total,
            reasoning_acc=100 *
            (reasoning_scope + final_scope + row_reasoning_scope) / total,
            code_acc=100 * (code_scope + final_scope) / total,
            action_acc=100 * (action_scope + final_scope) / total,
        )
        return result
