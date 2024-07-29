#!/usr/bin/env python3
import argparse
import filecmp
import os

from mmengine.logging import MMLogger


def get_files(folder, extensions):
    """Get all file paths in the folder with specified extensions."""
    files = []
    for root, dirs, files_in_dir in os.walk(folder):
        for file in files_in_dir:
            if any(file.endswith(ext) for ext in extensions):
                files.append(os.path.relpath(os.path.join(root, file), folder))
    return files


def compare_folders(folder1, folder2, extensions):
    """Compare files with specified extensions in two folders."""
    logger = MMLogger.get_current_instance()
    files1 = set(get_files(folder1, extensions))
    files2 = set(get_files(folder2, extensions))

    # Check for files that are only in one folder
    only_in_folder1 = files1 - files2
    only_in_folder2 = files2 - files1
    common_files = files1 & files2

    if only_in_folder1:
        print(f'Only in {folder1}: {only_in_folder1}')
    if only_in_folder2:
        print(f'Only in {folder2}: {only_in_folder2}')

    # Compare the content of common files
    for file in common_files:
        file1 = os.path.join(folder1, file)
        file2 = os.path.join(folder2, file)
        if not filecmp.cmp(file1, file2, shallow=False):
            logger.warning(f'Files differ: {file1} and {file2}')
            raise ValueError(f'Files differ: {file1} and {file2}')
        else:
            pass
            # logger.info(f"Files are the same: {file1} and {file2}")


def main():
    parser = argparse.ArgumentParser(
        description='Compare specified files in two folders')
    parser.add_argument('folder1', help='Path to the first folder')
    parser.add_argument('folder2', help='Path to the second folder')
    parser.add_argument(
        '--extensions',
        nargs='+',
        default=['.py', '.json', '.md', '.yml', '.txt'],
        help='File extensions to compare (default: .py .json .md .yml .txt)')

    args = parser.parse_args()

    compare_folders(args.folder1, args.folder2, args.extensions)


if __name__ == '__main__':
    main()
