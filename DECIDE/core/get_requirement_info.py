from packaging.requirements import Requirement
from config.library import SYS_STANDARD_LIBARARY
from utils.utils import *

def read_requirement_file(req_file):
    f = open(req_file, 'r')
    lines = f.readlines()
    req_l = []
    for line in lines:
        l = ignore_comment(line)
        if l == '' or not (l[0] >='a' and l[0] <= 'z'):
            continue
        req_l.append(l)
    
    return req_l

def requirements_info(req_file):
    req_info = []
    req_l = read_requirement_file(req_file)
    for rl in req_l:
        req = Requirement(rl)
        if len(req.specifier) == 0:
            version = ''
            req_info.append(f'{req.name.lower()} {version}')
        elif len(req.specifier) == 1:
            for sp in req.specifier:
                version = str(sp.version) if str(sp.operator) == '==' else str(req.specifier) + ' (range)'
            req_info.append(f'{req.name.lower()} {version}')
        else:
            req_info.append(f'{req.name.lower()} {str(req.specifier)} (range)')
    return req_info

def filter_using_module(proj_module):
    res = []

    for module in proj_module:
        if '.' not in module and module not in SYS_STANDARD_LIBARARY:
            res.append(module)
    return res

def combine_requirement_info(req_lib, proj_lib):
    res = req_lib
    temp_req = []
    for req in req_lib:
        temp_req.append(req.split(' ')[0].lower())

    for proj in proj_lib:
        if proj.lower() not in temp_req:
            res.append(proj)
    return res