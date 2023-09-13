import os
from typing import Iterable


def code_counter(path: str = os.path.abspath(os.path.join(os.path.sep))) -> Iterable[int]:
    for dirpath, dirnames, filenames in os.walk(path):
        for i_file in filenames:
            if i_file.endswith('.py'):
                filepath = dirpath+os.sep+i_file
                with open(filepath, 'r', encoding='utf-8') as file:
                    count = sum(1 for line in file if not line.startswith('#') and line != '\n')
                    yield count
    return



f = code_counter(path=os.getcwd())
code_string_count = 0
for i in f:
    code_string_count += i
print(code_string_count)

