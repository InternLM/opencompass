import json
import os
import os.path as osp
import re
import subprocess

import h5py
import scipy
from datasets import Dataset

from opencompass.openicl.icl_evaluator import BaseEvaluator
from opencompass.registry import ICL_EVALUATORS, LOAD_DATASET

from .base import BaseDataset


@LOAD_DATASET.register_module()
class SciCodeDataset(BaseDataset):

    @staticmethod
    def load(path, **kwargs):
        test_data = []

        file_path = osp.join(path, 'SciCode_datasets.json')
        with open(file_path, 'r', encoding='utf-8') as file:
            test_data = json.load(file)

        dataset = Dataset.from_list(test_data)
        return dataset

    def return_dataset(self):
        return self.dataset


H5PY_FILE = './data/SciCode/test_data.h5'


def process_hdf5_list(group):
    lst = []
    for key in group.keys():
        lst.append(group[key][()])
    return lst


def process_hdf5_dict(group):
    dict = {}
    for key, obj in group.items():
        if isinstance(obj, h5py.Group):
            dict[key] = process_hdf5_sparse_matrix(obj['sparse_matrix'])
        elif isinstance(obj[()], bytes):
            dict[key] = obj[()].decode('utf-8', errors='strict')
        else:
            try:
                tmp = float(key)
                dict[tmp] = obj[()]
            except ValueError:
                dict[key] = obj[()]
    return dict


def process_hdf5_sparse_matrix(group):
    data = group['data'][()]
    shape = tuple(group['shape'][()])
    if 'row' in group and 'col' in group:
        row = group['row'][()]
        col = group['col'][()]
        return scipy.sparse.coo_matrix((data, (row, col)), shape=shape)
    elif 'blocksize' in group:
        indices = group['indices'][()]
        indptr = group['indptr'][()]
        blocksize = tuple(group['blocksize'][()])
        return scipy.sparse.bsr_matrix((data, indices, indptr),
                                       shape=shape,
                                       blocksize=blocksize)
    else:
        indices = group['indices'][()]
        indptr = group['indptr'][()]
        return scipy.sparse.csr_matrix((data, indices, indptr), shape=shape)


def process_hdf5_datagroup(group):
    for key in group.keys():
        if key == 'list':
            return process_hdf5_list(group[key])
        if key == 'sparse_matrix':
            return process_hdf5_sparse_matrix(group[key])
        else:
            return process_hdf5_dict(group)


def process_hdf5_to_tuple(step_id, test_num):
    data_lst = []
    with h5py.File(H5PY_FILE, 'r') as f:
        for test_id in range(test_num):
            group_path = f'{step_id}/test{test_id + 1}'
            if isinstance(f[group_path], h5py.Group):
                group = f[group_path]  # test1, test2, test3
                num_keys = [key for key in group.keys()]
                if len(num_keys) == 1:  # only 1 var in the test
                    subgroup = group[num_keys[0]]
                    if isinstance(subgroup, h5py.Dataset):
                        if isinstance(subgroup[()], bytes):
                            data_lst.append(subgroup[()].decode(
                                'utf-8', errors='strict'))
                        else:
                            data_lst.append(subgroup[()])
                    elif isinstance(subgroup, h5py.Group):
                        data_lst.append(process_hdf5_datagroup(subgroup))
                else:
                    var_lst = []
                    for key in group.keys():  # var1, var2, var3
                        subgroup = group[key]
                        if isinstance(subgroup, h5py.Dataset):
                            if isinstance(subgroup[()], bytes):
                                var_lst.append(subgroup[()].decode(
                                    'utf-8', errors='strict'))
                            else:
                                var_lst.append(subgroup[()])
                        elif isinstance(subgroup, h5py.Group):
                            var_lst.append(process_hdf5_datagroup(subgroup))
                    data_lst.append(tuple(var_lst))
            else:
                raise FileNotFoundError(
                    f'Path {group_path} not found in the file.')
    return data_lst


@ICL_EVALUATORS.register_module()
class SciCodeEvaluator(BaseEvaluator):

    def __init__(self, dataset_path, testcode_path='./tmp/SciCode'):
        super().__init__()
        test_data = []
        file_path = osp.join(dataset_path, 'SciCode_datasets.json')
        with open(file_path, 'r', encoding='utf-8') as file:
            test_data = json.load(file)
        self.dataset = Dataset.from_list(test_data)
        self.testcode_path = testcode_path
        H5PY_FILE = osp.join(dataset_path, 'test_data.h5')  # noqa: F841

    def extract_python_script(self, response: str):
        start_marker = '```python'
        end_marker = '```'

        if start_marker not in response or end_marker not in response:
            # If the markers are not present, return an empty string
            # print("fail to follow the instruct")
            return ''

        # Split the response at the start marker and take the second part
        after_start = response.split(start_marker)
        if len(after_start) < 2:
            return ''  # No valid split was made

        # Split the part after the start marker at the end marker
        python_script = after_start[1].split(end_marker)[0]

        # Remove leading import statements using regex
        python_script = re.sub(r'^\s*(import .*|from .*\s+import\s+.*)',
                               '',
                               python_script,
                               flags=re.MULTILINE)

        return python_script

    def run_script(self, script_path):
        try:
            subprocess.run(['python', script_path],
                           check=True,
                           capture_output=True,
                           text=True,
                           timeout=60)
            return 0
        except subprocess.CalledProcessError:
            return 1
        except subprocess.TimeoutExpired:
            return 2

    def score(self, predictions, references):
        correct, sub_correct = 0, 0
        count, sub_count = 0, 0
        details = []

        # generate all python test codes and than test
        for idx, prediction_list in enumerate(predictions):
            # traverse each test sample
            problem_id = self.dataset[idx]['id']
            num_of_subproblems = len(prediction_list)

            # create dir for each test sample
            testdir_path = os.path.join(self.testcode_path, str(problem_id))
            os.makedirs(testdir_path, exist_ok=True)

            python_code = ''
            # add import statement
            python_code += self.dataset[idx]['import']

            is_all_correct = True
            for sub_idx in range(num_of_subproblems):
                # extract code
                response = prediction_list[sub_idx]
                python_code += self.extract_python_script(response)

                # process special examples
                if problem_id == '13' and sub_idx >= 5 or \
                   problem_id == '62' and sub_idx >= 0 or \
                   problem_id == '76' and sub_idx >= 2:
                    sub_idx += 1

                # test cases
                test_lst = self.dataset[idx]['test'][sub_idx]

                testfile_path = os.path.join(testdir_path,
                                             f'{problem_id}-{sub_idx + 1}.py')
                # write python code and test cases to a real python file
                with open(testfile_path, 'w', encoding='utf-8') as f:
                    f.write(python_code)
                    f.write("""

from opencompass.datasets.SciCode import process_hdf5_to_tuple

""")
                    f.write('targets = process_hdf5_to_tuple(' +
                            f"'{problem_id}.{sub_idx + 1}', {len(test_lst)})" +
                            '\n')
                    for idx2 in range(len(test_lst)):
                        f.write(f'target = targets[{idx2}]\n\n')
                    for line in test_lst[idx2].split('\n'):
                        f.write(line + '\n')

                # test
                ret = self.run_script(testfile_path)
                msg = {'problem': f'{problem_id}-{sub_idx + 1}'}
                if ret == 0:  # correct
                    sub_correct += 1
                    msg['is_correct'] = True
                elif ret == 1:  # error
                    is_all_correct = False
                    msg['is_correct'] = False
                else:  # time out
                    is_all_correct = False
                    msg['is_correct'] = False
                sub_count += 1
                details.append(msg)

        correct += is_all_correct
        count += 1

        result = {
            'accuracy': 100 * correct / count,
            'sub_accuracy': 100 * sub_correct / sub_count,
            'details': details
        }
        return result
