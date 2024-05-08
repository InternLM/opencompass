import json
import re
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List, Optional

import numpy as np
import requests

from opencompass.registry import MODELS
from opencompass.utils.logging import get_logger

from .base import BaseModel
from .base_api import TokenBucket


@MODELS.register_module()
class LightllmAPI(BaseModel):

    is_api: bool = True

    def __init__(
            self,
            path: str = 'LightllmAPI',
            url: str = 'http://localhost:8080/generate',
            meta_template: Optional[Dict] = None,
            max_workers_per_task: int = 2,
            rate_per_worker: int = 2,
            retry: int = 2,
            generation_kwargs: Optional[Dict] = dict(),
    ):

        super().__init__(path=path,
                         meta_template=meta_template,
                         generation_kwargs=generation_kwargs)
        self.logger = get_logger()
        self.url = url
        self.retry = retry
        self.generation_kwargs = generation_kwargs
        self.max_out_len = self.generation_kwargs.get('max_new_tokens', 1024)
        self.meta_template = meta_template
        self.max_workers_per_task = max_workers_per_task
        self.token_bucket = TokenBucket(rate_per_worker, False)

    def generate(self, inputs: List[str], max_out_len: int,
                 **kwargs) -> List[str]:
        """Generate results given a list of inputs.

        Args:
            inputs (List[str]): A list of strings or PromptDicts.
                The PromptDict should be organized in OpenCompass'
                API format.
            max_out_len (int): The maximum length of the output.

        Returns:
            List[str]: A list of generated strings.
        """

        with ThreadPoolExecutor(
                max_workers=self.max_workers_per_task) as executor:
            results = list(
                executor.map(self._generate, inputs,
                             [self.max_out_len] * len(inputs)))
        return results

    def _generate(self, input: str, max_out_len: int) -> str:
        max_num_retries = 0
        while max_num_retries < self.retry:
            self.wait()
            header = {'content-type': 'application/json'}
            try:
                data = dict(inputs=input, parameters=self.generation_kwargs)
                raw_response = requests.post(self.url,
                                             headers=header,
                                             data=json.dumps(data))
            except requests.ConnectionError:
                self.logger.error('Got connection error, retrying...')
                continue
            try:
                response = raw_response.json()
                generated_text = response['generated_text']
                if isinstance(generated_text, list):
                    generated_text = generated_text[0]
                return generated_text
            except requests.JSONDecodeError:
                self.logger.error('JsonDecode error, got',
                                  str(raw_response.content))
            except KeyError:
                self.logger.error(f'KeyError. Response: {str(response)}')
            max_num_retries += 1

        raise RuntimeError('Calling LightllmAPI failed after retrying for '
                           f'{max_num_retries} times. Check the logs for '
                           'details.')

    def get_ppl(self, inputs: List[str], max_out_len: int,
                **kwargs) -> List[float]:
        """Generate results given a list of inputs.

        Args:
            inputs (List[str]): A list of strings or PromptDicts.
                The PromptDict should be organized in OpenCompass'
                API format.
            max_out_len (int): The maximum length of the output.

        Returns:
            List[str]: A list of generated strings.
        """

        with ThreadPoolExecutor(
                max_workers=self.max_workers_per_task) as executor:
            results = list(
                executor.map(self._get_ppl, inputs,
                             [self.max_out_len] * len(inputs)))
        return np.array(results)

    def _get_ppl(self, input: str, max_out_len: int) -> float:
        max_num_retries = 0
        if max_out_len is None:
            max_out_len = 1
        while max_num_retries < self.retry:
            self.wait()
            header = {'content-type': 'application/json'}
            try:
                data = dict(inputs=input, parameters=self.generation_kwargs)
                raw_response = requests.post(self.url,
                                             headers=header,
                                             data=json.dumps(data))
            except requests.ConnectionError:
                self.logger.error('Got connection error, retrying...')
                continue
            try:
                response = raw_response.json()

                assert ('prompt_token_ids' in response and 'prompt_logprobs'
                        in response), f'prompt_token_ids and prompt_logprobs \
                    must be in the output. \
                    Please consider adding \
                    --return_all_prompt_logprobs argument \
                    when starting lightllm service. Response: {str(response)}'

                prompt_token_ids = response['prompt_token_ids'][1:]
                prompt_logprobs = [
                    item[1] for item in response['prompt_logprobs']
                ]
                logprobs = [
                    item[str(token_id)] for token_id, item in zip(
                        prompt_token_ids, prompt_logprobs)
                ]
                if len(logprobs) == 0:
                    return 0.0
                ce_loss = -sum(logprobs) / len(logprobs)
                return ce_loss
            except requests.JSONDecodeError:
                self.logger.error('JsonDecode error, got',
                                  str(raw_response.content))
            max_num_retries += 1
        raise RuntimeError('Calling LightllmAPI failed after retrying for '
                           f'{max_num_retries} times. Check the logs for '
                           'details.')

    def wait(self):
        """Wait till the next query can be sent.

        Applicable in both single-thread and multi-thread environments.
        """
        return self.token_bucket.get_token()

    def get_token_len(self, prompt: str) -> int:
        """Get lengths of the tokenized string. Only English and Chinese
        characters are counted for now. Users are encouraged to override this
        method if more accurate length is needed.

        Args:
            prompt (str): Input string.

        Returns:
            int: Length of the input tokens
        """

        english_parts = re.findall(r'[A-Za-z0-9]+', prompt)
        chinese_parts = re.findall(r'[\u4e00-\u9FFF]+', prompt)

        # Count English words
        english_count = sum(len(part.split()) for part in english_parts)

        # Count Chinese words
        chinese_count = sum(len(part) for part in chinese_parts)

        return english_count + chinese_count
