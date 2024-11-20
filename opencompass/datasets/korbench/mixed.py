import json
import os
from datasets import Dataset
from opencompass.registry import LOAD_DATASET
from opencompass.utils import get_data_path
from ..base import BaseDataset
from opencompass.datasets.korbench.korbench_utils import evaluate_responses

def load_json_or_jsonl(file_path):
    """
    Load data from a JSON or JSONL file.
    """
    if not os.path.exists(file_path):
        return None
    with open(file_path, 'r', encoding='utf-8') as file:
        if file_path.endswith('.json'):
            return json.load(file)
        elif file_path.endswith('.jsonl'):
            return [json.loads(line) for line in file]
    return None


@LOAD_DATASET.register_module()
class korbenchmixedDataset(BaseDataset):
    @staticmethod
    def load(path):
        """
        Load data for the Mixed task.
        """
        base_path = get_data_path(path)
        modes = ["Multi-Q", "Multi-R", "Multi-RQ", "Multi-RQ_Hard"]
        all_data = []

        for mode in modes:
            file_path = os.path.join(base_path, "mixed", f"{mode}.jsonl")
            data = load_json_or_jsonl(file_path) or []
            for item in data:
                all_data.append({
                    "rule_list": "\n".join(item.get("rule_list", [])),
                    "question_list": "\n".join(item.get("question_list", [])),
                    "answer": item.get("answer"),
                })

        return Dataset.from_list(all_data)
    


import os
import json
from opencompass.openicl.icl_evaluator import BaseEvaluator
from opencompass.registry import ICL_EVALUATORS
from opencompass.datasets.korbench.korbench_utils import evaluate_responses


#TODO fix the related code for mixed task
@ICL_EVALUATORS.register_module()
class korbenchmixedEvaluator(BaseEvaluator):
    def __init__(self, metadata_file=None, output_folder=None):
        super().__init__()
        self.metadata_file = metadata_file or "/path/to/metadata.json"
        self.output_folder = output_folder or "/path/to/evaluation_results"

    def load_metadata(self):
        """
        Load metadata to get prediction file paths.
        """
        if not os.path.exists(self.metadata_file):
            raise FileNotFoundError(f"Metadata file not found: {self.metadata_file}")
        with open(self.metadata_file, "r") as f:
            return json.load(f)

    def score(self):
        """
        Evaluate predictions for the Mixed task.
        """
        metadata = self.load_metadata()
        os.makedirs(self.output_folder, exist_ok=True)
        dataset_scores = {}

        for entry in metadata:

            output_path = entry["output_path"]
            if not os.path.exists(output_path):
                print(f"[WARNING] Prediction file not found: {output_path}")
                continue

            with open(output_path, "r") as f:
                data = json.load(f)

            evaluation_results = evaluate_responses(data, "mixed", entry["mode"])
            correct_count = sum(res["is_correct"] for res in evaluation_results)
            accuracy = (correct_count / len(evaluation_results)) * 100 if evaluation_results else 0

            dataset_scores[entry["mode"]] = accuracy

        self._save_results(dataset_scores)
        return dataset_scores

    def _save_results(self, dataset_scores):
        json_output_path = os.path.join(self.output_folder, "mixed_scores.json")
        with open(json_output_path, "w", encoding="utf-8") as json_file:
            json.dump(dataset_scores, json_file, ensure_ascii=False, indent=4)