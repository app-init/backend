import sys

"""
removes import dictionary

Usage: python remove-import-dict.py path-to-file
"""

src = sys.argv[1]
out = src

def file_to_lines(srcpath):
   with open(srcpath, 'r') as f:
      src_file_contents = [line for line in f]
   return list(map(lambda line: line.rstrip(), src_file_contents))

def is_import_start(line):
   return 'imports =' in line

def is_import_end(line):
   return len(line) > 0 and line[0] == '}'

src_lines = file_to_lines(src)
import_start_index = -1
import_end_index = -1

for i in range(len(src_lines)):
   line = src_lines[i]
   if is_import_start(line):
      import_start_index = i
   elif is_import_end(line):
      if import_start_index >= 0:
         import_end_index = i
         break

if import_start_index >= 0 and import_start_index < import_end_index:
   src_without_import_dict = src_lines[:import_start_index] + src_lines[import_end_index+1:]
   with open(src, 'w') as f:
      f.write('\n'.join(src_without_import_dict))
