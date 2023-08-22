import os
from typed_ast import ast27
import ast

methods = []

def has_body(node):
    types = [ast.ClassDef, ast.FunctionDef, ast.If, ast.For, ast.While, ast.Try,
            ast27.ClassDef, ast27.FunctionDef, ast27.If, ast27.For, ast27.While, ast27.TryExcept]
    for tp in types:
        if isinstance(node, tp):
            return True
    return False

class CallVisitor(ast.NodeVisitor):
    def visit_Call(self, node):
        name_list = []
        if type(node.func).__name__ == 'Name':
            pass
        elif type(node.func).__name__ == 'Attribute':
            name_list.append(node.func.attr)
            value = node.func.value
            while type(value).__name__ == 'Attribute':
                name_list.append(value.attr)
                value = value.value
            if type(value).__name__ == 'Name':
                name_list.append(value.id)
                name_list.reverse()
                name = '.'.join(name_list)
                methods.append(name)
            else:
                pass

    def generic_visit(self, node):
        ast.NodeVisitor.generic_visit(self, node)


class ModuleParser(object):
    def __init__(self, _root, _exclude_dir=None):
        while _root.endswith(os.sep):
            _root = _root[:-1]
        self.root = _root
        self.exclude_dir = _exclude_dir
        self.python_files = []
        self.custom_modules = []
        self.modules = []
        self.api = []

    def get_custom_modules(self, need_init=True):
        if os.path.isdir(self.root):
            file_list = os.listdir(self.root)
            for file in file_list:
                full_path = os.path.join(self.root, file)
                if os.path.isdir(full_path):
                    subs = os.listdir(full_path)
                    if need_init and '__init__.py' not in subs:
                        continue
                    self.custom_modules.append(file)
                elif file.endswith('.py') or file.endswith('.so'):
                    if file == 'setup.py' or file.startswith('__'):
                        continue
                    self.custom_modules.append(file.split('.')[0])

    def get_python_file_list(self):
        if os.path.isdir(self.root):
            for cur_dir, folders, files in os.walk(self.root):
                for file in files:
                    if not file.endswith('.py'):
                        continue
                    py_path = os.path.join(cur_dir, file)
                    self.python_files.append(py_path)
        elif self.root.endswith(".py"):
            self.python_files.append(self.root)
        else:
            print(f'Please check the root path: {self.root}')
            raise TypeError('Unexpected root path.')

    def parse_module(self, body, modules):
        for node in body:

            if isinstance(node, ast27.Import) or isinstance(node, ast.Import):
                for stmt in node.names:
                    modules.append(stmt.name)
                    if '.' in stmt.name:
                        modules.append(stmt.name.split('.')[0])

            if isinstance(node, ast27.ImportFrom) or isinstance(node, ast.ImportFrom):
                if node.module != None:
                    modules.append(node.module)
                if node.module != None and '.' in node.module:
                    modules.append(node.module.split('.')[0])
                for stmt in node.names:
                    if node.module == None:
                        modules.append(stmt.name)
                    else:
                        modules.append(f'{node.module}.{stmt.name}')

            if isinstance(node, ast.With):
                call_sub = node.items[0].context_expr


            if has_body(node):
                sub_body = node.body
                modules = self.parse_module(sub_body, modules)
                if isinstance(node, ast.If) or isinstance(node, ast27.If):
                    sub_body = node.orelse
                    modules = self.parse_module(sub_body, modules)

        return modules            

    def get_import_modules(self, code):
        modules = []
        try:
            root_node = ast.parse(code)
        except SyntaxError:
            try:
                root_node = ast27.parse(code)
            except SyntaxError:
                return []
        
        modules = self.parse_module(root_node.body, modules)

        return modules

    def filter_custom_modules(self, modules):
        include = []

        for module in modules:
            # print(module)
            temp = module.split('.')[0] if '.' in module else module
            if temp not in self.custom_modules:
                include.append(module)
            
        return include

    def parse(self):
        self.get_custom_modules()
        self.get_python_file_list()

        # print(self.python_files)
        
        module_temp = []

        for file in self.python_files:
            with open(file, 'r') as f:
                print(file)
                lines = f.readlines()
                code = "".join(lines)
                # modules
                modules = self.get_import_modules(code)
                module_temp.extend(modules)
                # APIs
                visitor = CallVisitor()
                visitor.visit(ast.parse(code))
        
        module_temp = list(set(module_temp))
        
        self.modules = self.filter_custom_modules(module_temp)
        self.api = list(set(methods))
        return self.modules, self.api

