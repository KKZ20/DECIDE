import json, re
from bs4 import BeautifulSoup
from config.constrain import SAME_LIST
from config.regex import PATH_PATTERN, IP_ADDRESS_PATTERN, DATE_PATTERN, TIME_PATTERN, MEMORY_PATTERN, ENCODE_PATTERN, TIME_PATTERN_2, FILENAME_PATTERN, TIME_PATTERN_3
from config.config import CONTENT_REPLACEMENT, ENTITY_LIST_REPLACEMENT
from pynvml import *

def print_gpu_utilization():
    nvmlInit()
    handle = nvmlDeviceGetHandleByIndex(1)
    info = nvmlDeviceGetMemoryInfo(handle)
    print(f"GPU memory occupied: {info.used//1024**2} MB.")

def read_json(path):
    with open(path, "r") as f:
        return json.load(f)

def html_parser(body):
    html_content = BeautifulSoup(body, "html.parser")
    pre_list = html_content.find_all("pre")
    for pre in pre_list:
        pre.extract()
    p_list = html_content.find_all("p")
    ul_ol_list = html_content.find_all(["ul", "ol"])

    p_content = []
    for p in p_list:
        content = p.get_text().strip().lower()
        content = replace_noise(content)
        content = replace_entity(content)
        if len(content) > 0:
            p_content.append(content)

    ol_ul_content = []
    for ul_ol in ul_ol_list:
        li_list = ul_ol.find_all("li")
        li_content_list = []
        for li in li_list:
            li_content = replace_noise(li.get_text().strip().lower())
            li_content = replace_entity(li_content)
            if len(li_content) > 0:
                li_content_list.append(li_content)
        ol_ul_content.append(li_content_list)

    post_content = html_content.get_text().strip().lower()

    return post_content, p_content, ol_ul_content

def is_short_post(post_content, threshold=750):
    if len(post_content) < threshold:
        return True
    return False

def exclude_code_tag(body, extract_all=False):
    content = BeautifulSoup(body, "html.parser")
    code_list = content.find_all("code")
    for code in code_list:
        code_text = code.get_text().strip()
        if len(code_text) > 50:
            code.extract()
        else:
            if extract_all == True:
                code.extract()
    body = content.get_text().strip().lower()
    return body, code_list

def replace_noise(content):
    res = content
    # remove path, ip address, date, tmie
    res = PATH_PATTERN.sub(" --p-- ", res)
    res = IP_ADDRESS_PATTERN.sub(" --i-- ", res)
    res = DATE_PATTERN.sub(" --d-- ", res)
    res = TIME_PATTERN.sub(" --t-- ", res)
    res = TIME_PATTERN_2.sub(" --2-- ", res)
    res = TIME_PATTERN_3.sub(" --3-- ", res)
    res = MEMORY_PATTERN.sub(" --m-- ", res)
    res = ENCODE_PATTERN.sub(" --e-- ", res)

    regex_match_list = FILENAME_PATTERN.findall(content)
    flag = True
    if len(regex_match_list) > 0:
        for match in regex_match_list:
            re_str = match[0]
            for pattern in [re.compile(r'((\d{1,2})(\.x)(\.x){0,1})'), re.compile(r'((\d{1,2})(\.\d{1,3})(\.x))')]:
                version_x_res = pattern.findall(re_str)
                if len(version_x_res) > 0:
                    flag = False
                    break
            if flag == False:
                continue
            res = res.replace(re_str, " --f-- ")

    return res

# replace abnormal entity name
def replace_entity(body):
    lower_body = body.lower()
    for key, value in CONTENT_REPLACEMENT.items():
        lower_body = lower_body.replace(key, value)

    return lower_body

def compute_min_distance(vidx: list, eidx: list, final_zip):
    vidx.sort()
    eidx.sort()
    n, m = len(vidx), len(eidx)
    i, j, res = 0, 0, 99999999
    while i < n and j < m:
        if vidx[i] < eidx[j]:
            temp = final_zip[vidx[i]: eidx[j]]
        else:
            temp = final_zip[eidx[j]: vidx[i]]
        dist = abs(vidx[i] - eidx[j])
        for tp in temp:
            if tp == ('.', 'PUNCT'):
                dist = 9999
                break
        res = min(res, dist)
        if vidx[i] > eidx[j]:
            j += 1
        else:
            i += 1
    return res

def opposite_verdict(verdict):
    if verdict == "yes":
        return "no"
    elif verdict == "no":
        return "yes"
    else:
        return "Unknown"

def is_same(name1, name2):
    if name1 == name2:
        return True
    
    for same_list in SAME_LIST:
        if name1 in same_list and name2 in same_list:
            return True

    return False

def strip_version(version: str):
    res = version.lower()
    while res[-2:] == '.0' or res[-2:] == '.x':
        res = res[:-2]
    
    if res[0] == 'v':
        res = res[1:]
    return res

def replace_knowledge_name(entity_name):
    res = entity_name
    if res in ENTITY_LIST_REPLACEMENT.keys():
        return ENTITY_LIST_REPLACEMENT[res]
    else:
        return res

def clean_knowledge(knowledge_list):
    res = []
    for knowledge in knowledge_list:
        e_v1 = knowledge[0].split()
        e_v2 = knowledge[1].split()
        e1 = replace_knowledge_name(e_v1[0])
        e2 = replace_knowledge_name(e_v2[0])
        v1 = strip_version(e_v1[1])
        v2 = strip_version(e_v2[1])
        if e1 < e2:
            res.append((f'{e1} {v1}', f'{e2} {v2}', knowledge[2], knowledge[3]))
        elif e1 > e2:
            res.append((f'{e2} {v2}', f'{e1} {v1}', knowledge[2], knowledge[3]))
        else:
            raise Exception(f'{e1} {v1} and {e2} {v2} are the same')
    return res

def remove_duplicate_knowledge(knowledge_list):
    res = []
    check = []
    for knowledge in knowledge_list:
        temp = (knowledge[0], knowledge[1], knowledge[2])
        if temp not in check:
            check.append(temp)
            res.append(knowledge)
        else:
            for dup in res:
                if dup[0] == knowledge[0] and dup[1] == knowledge[1] and dup[2] == knowledge[2]:
                    if dup[3] > knowledge[3]:
                        res.remove(dup)
                        res.append(knowledge)
                    else:
                        break

    return res

def knowledge_conflict_solve(knowledge_list):
    res = []
    check = []
    for knowledge in knowledge_list:
        temp = (knowledge[0], knowledge[1])
        if temp not in check:
            check.append(temp)
            res.append(knowledge)
        else:
            for dup in res:
                if dup[0] == knowledge[0] and dup[1] == knowledge[1]:
                    if dup[2] == knowledge[2]:
                        raise Exception(f'{dup[0]} {dup[1]} and {knowledge[0]} {knowledge[1]} are the same (res: {res}, kl: {knowledge_list})')
                    else:
                        if dup[3] > knowledge[3]:
                            res.remove(dup)
                            res.append(knowledge)
                            break
                        else:
                            break
    return res