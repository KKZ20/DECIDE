import json

def ignore_comment(_str: str):
    l = _str.split('#')
    res = l[0].strip().lower()
    return res

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

def read_json(file):
    with open(file, 'r') as f:
        data = json.load(f)
        return data

def output_dict_to_json(data, file):
    with open(file, 'w') as f:
        json.dump(data, f, indent=4)

def cut_version(version):
    res = version
    v_list = version.split('.')
    if len(v_list) > 2:
        res = '.'.join(v_list[:2])
    return res

def compare_version(_v1, _v2):
    v1 = _v1
    v2 = _v2
    if _v1 == '' or _v2 == '':
        return 'missing'
    if _v1[0] < '0' or _v1[0] > '9':
        v1 = _v1[1:]
    if _v2[0] < '0' or _v2[0] > '9':
        v2 = _v2[1:]
    
    vlist_1 = v1.split('.')
    vlist_2 = v2.split('.')
    # align two versions
    if len(vlist_1) > len(vlist_2):
        for i in range(len(vlist_1) - len(vlist_2)):
            vlist_2.append('0')
    elif len(vlist_1) < len(vlist_2):
        for i in range(len(vlist_2) - len(vlist_1)):
            vlist_1.append('0')
    # compare two versions
    for i in range(len(vlist_1)):
        if int(vlist_1[i]) > int(vlist_2[i]):
            return 'higher'
        elif int(vlist_1[i]) < int(vlist_2[i]):
            return 'lower'
    return 'equal'