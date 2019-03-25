import sys

"""
removes decorator import statement

Usage: python remove-decorator-import.py path-to-file
"""

src = sys.argv[1]
out = src

def file_to_lines(srcpath):
   with open(srcpath, 'r') as f:
      src_file_contents = [line for line in f]
   return list(map(lambda line: line.rstrip(), src_file_contents))

def contains_decorator(line):
   return '@api' in line or 'lib.decorators.api' in line

src_lines = file_to_lines(src)
src_without_decorator = [line for line in src_lines if not contains_decorator(line)]

if len(src_without_decorator) != len(src_lines):
   with open(src, 'w') as f:
      f.write('\n'.join(src_without_decorator))
