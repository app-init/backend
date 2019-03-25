import ast
import sys
from astor import dump, parsefile

"""
This script removes the @api decorator and converts the
import dictionary into import statements. It also adds
a default import statement.

Usage: python decorator-to-imports.py path-to-file
"""


def file_to_lines(srcpath):
   with open(srcpath, 'r') as f:
      src_file_contents = [line for line in f]
   return list(map(lambda line: line.rstrip(), src_file_contents))

def has_decorator(src_text):
   return any(['@api' in line for line in src_text])

def remove_decorator(src):
   decorator_index = list(filter(lambda x: '@api' in x, src))[0]
   src.pop(decorator_index)

def remove_decorator_import(src):
   import_index = list(filter(lambda x: 'lib.decorators.api' in x, src))[0]
   src.pop(import_index)

def insert_imports(src, existing_imports, imports_dict):
   for module, alias in imports_dict.items():
      module_path = 'lib.{}'.format(module)
      if module_path not in existing_imports or existing_imports[module_path] != existing_imports[module]:
         import_stmt = 'import {} as {}'.format(module_path, alias)
         src.insert(0, import_stmt)

def insert_default_import(src):
   default_import_stmt = 'from lib.imports.default import *'
   src.insert(0, default_import_stmt)

def convert(src_tree):
   imports = {}
   existing_imports = {}
   found_decorator = False

   # inspecting the AST to find what the imported modules are
   # as well as the key, value pairs in the imports dictionary
   for node in src_tree.body:
      node_type = type(node).__name__

      if (node_type == 'Assign'):
         target = node.targets[0]

         if target.id == 'imports':
            found_imports = True
            import_dict = node.value
            keys = import_dict.keys
            values = import_dict.values

            for i in range(len(keys)):
               module_name = values[i].s
               alias_name = keys[i].s
               imports[module_name] = alias_name

      if (node_type == 'Import'):
         import_name = node.names[0]
         if hasattr(import_name, 'asname'):
            existing_imports[import_name.name] = import_name.asname

      elif (node_type == 'FunctionDef' and node.name == 'call'):
         if len(node.decorator_list) > 0:
            found_decorator = True

         node.decorator_list = []

   # print(imports)
   # print(existing_imports)

   return found_decorator, imports, existing_imports

src = sys.argv[1]

# writing to the same file
out = src

src_tree = parsefile(src)
src_lines = file_to_lines(src)

# print(dump(src_tree))
found_decorator, imports_dict, existing_imports = convert(src_tree)

if found_decorator:
   insert_imports(src_lines, existing_imports, imports_dict)
   insert_default_import(src_lines)

   with open(src, 'w') as f:
      f.write('\n'.join(src_lines))
