from datasets import Dataset, load_dataset

from opencompass.registry import LOAD_DATASET

from .base import BaseDataset
import json

@LOAD_DATASET.register_module()
class ReasonBenchDataset(BaseDataset):

    @staticmethod
    def load(path: str):
        raw_data = []
        with open(path, 'r') as f:
            for line in f:
                line = json.loads(line)
                prompt = line['prompt']
                label = line['label']
                choices = line['choices']
                tag = line['tag']
                source = line['source']
                A = line['A']
                B = line['B']
                C = line['C']
                D = line['D']
                raw_data.append({
                    'prompt': prompt,
                    'label': label,
                    'choices': choices,
                    'tag': tag,
                    'source': source,
                    'A': A,
                    'B': B,
                    'C': C,
                    'D': D
                })
        dataset = Dataset.from_list(raw_data)
        return dataset
