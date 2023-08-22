from py2neo import Graph
import logging
import copy
from packaging.version import Version
from packaging.specifiers import SpecifierSet
import packaging
from core.neo4j import *
from config.library import ENTITY_LIST_REPLACEMENT
from utils.utils import cut_version

def get_name_version(ev: str):
    ev_list = ev.split()
    if len(ev_list) == 1:
        return ev_list[0], '', None
    elif len(ev_list) == 2:
        return ev_list[0], ev_list[1], None
    elif len(ev_list) == 3 and ev_list[-1] == '(range)':
        spec = SpecifierSet(ev_list[1])
        return ev_list[0], '', spec
    else:
        raise Exception('Invalid entity version format')

def generate_post_url(post_id):
    return f'https://stackoverflow.com/questions/{post_id}'

def checking_lib_dc_issue(local_info, requirements_info, graph: Graph):
    for req in requirements_info:
        entity_name, entity_version = get_name_version(req)

        if entity_name in ENTITY_LIST_REPLACEMENT.keys():
            entity_name = ENTITY_LIST_REPLACEMENT[entity_name]

        # --------------------------begin checking--------------------------
        # if the library is not installed in local, report it
        if entity_name not in local_info['library'].keys() and entity_version == '':
            print(f'{entity_name} is not installed in local')
            continue
        
        # if the version is not strongly specified, using the local version
        if entity_version == '':
            entity_version = local_info['library'][entity_name]
        
        # checking dc issue from knowledge base
        node_match_res = match_node(graph, 'library', entity_name, entity_version, False)
        if len(node_match_res) == 0:
            continue
        
        kb = {
            "library": {},
            "hardware": {},
            "programming_language": {},
            "operating_system": {},
            "tool": {},
            'database': {},
            'software': {}
        }

        for node in node_match_res:
            query_res = match_related_node(graph, 'library', node['n']['name'], node['n']['version'], False)
            for res in query_res:
                knowledge = decode_relation(res['n2'], res['r'], False)
                print(knowledge)
                if knowledge == 'unknown':
                    continue
                if knowledge['name'] not in kb[knowledge['label']].keys():
                    kb[knowledge['label']][knowledge['name']] = []
                kb[knowledge['label']][knowledge['name']].append((knowledge['version'], knowledge['verdict'], knowledge['post_id']))

        print('......................................................................................')
        print(f'Current library: {entity_name} (v{entity_version})')
        print(f'Knowledge base: {kb}')

        for label in kb.keys():
            if label == 'hardware':
                for name in kb[label].keys():
                    compatible_version_list = []
                    for version, verdict, post_id in kb[label][name]:
                        if verdict == 'yes':
                            compatible_version_list.append(version)
                    v_local = local_info[label][name] if name in local_info[label].keys() else ''
                    if v_local == '':
                        print('--------------------------------DC ISSUE-----------------------------------------')
                        print(f'{name} is not installed in local, the recommended version is {compatible_version_list}')
                        print('-----------------------------------END-------------------------------------------')
                    else:
                        flag = False
                        for k_version in compatible_version_list:
                            res = compare_version(v_local, k_version)
                            if res == 'equal':
                                flag = True
                                break
                        if flag == False:
                            print('--------------------------------DC ISSUE-----------------------------------------')
                            print(f'ERROR: Local {entity_name} (v{entity_version}) is not compatible with {name} (v{v_local}) (0)')
                            print('-----------------------------------END-------------------------------------------')
                continue

            for name in kb[label].keys():
                v_local = local_info[label][name] if name in local_info[label].keys() else ''
                if v_local == '':
                    continue
            
                if len(kb[label][name]) == 0:
                    continue
                elif len(kb[label][name]) == 1:
                    k_version, k_verdict, k_post_id = kb[label][name][0]

                    re_check = version_recheck(k_version)
                    if re_check == False:
                        continue

                    if k_verdict == 'yes':
                        res = compare_version(v_local, k_version)
                        if res == 'lower' or res == 'equal':
                            prompt = 'may not be' if res == 'lower' else 'is'
                            print('--------------------------------DC ISSUE-----------------------------------------')
                            print(f'ERROR: Local {entity_name} (v{entity_version}) {prompt} compatible with {name} (v{v_local}) (1)')
                            print('Recommend StackOverflow Posts: ')
                            for post_id in k_post_id:
                                print(generate_post_url(post_id))
                            print('-----------------------------------END-------------------------------------------')
                    elif k_verdict == 'no':
                        res = compare_version(v_local, k_version)
                        if res == 'higher' or res == 'equal':
                            prompt = 'may not be' if res == 'higher' else 'is'
                            print('--------------------------------DC ISSUE-----------------------------------------')
                            print(f'ERROR: Local {entity_name} (v{entity_version}) {prompt} not compatible with {name} (v{v_local}) (2)')
                            print('Recommend StackOverflow Posts: ')
                            for post_id in k_post_id:
                                print(generate_post_url(post_id))
                            print('-----------------------------------END-------------------------------------------')
                            
                else:
                    min_version, min_verdict, min_post_id = '', '', ''
                    max_version, max_verdict, max_post_id = '', '', ''
                    for version, verdict, post_id in kb[label][name]:
                        re_check = version_recheck(version)
                        if re_check == False:
                            continue
                        if min_version == '':
                            min_version = version
                            min_verdict = verdict
                            min_post_id = post_id
                        elif compare_version(version, min_version) == 'lower':
                            min_version = version
                            min_verdict = verdict
                            min_post_id = post_id
                        if max_version == '':
                            max_version = version
                            max_verdict = verdict
                            max_post_id = post_id
                        elif compare_version(version, max_version) == 'higher':
                            max_version = version
                            max_verdict = verdict
                            max_post_id = post_id

                    if min_verdict == 'no':
                        min_res = compare_version(v_local, min_version)
                        if min_res == 'lower' or min_res == 'equal':
                            prompt = 'may not be' if res == 'lower' else 'is'
                            print('--------------------------------DC ISSUE-----------------------------------------')
                            print(f'ERROR: Local {entity_name} (v{entity_version}) {prompt} not compatible with {name} (v{v_local}) (3)')
                            print('Recommend StackOverflow Posts: ')
                            for post_id in min_post_id:
                                print(generate_post_url(post_id))
                            print('-----------------------------------END-------------------------------------------')
                    
                    if max_verdict == 'no':
                        max_res = compare_version(v_local, max_version)
                        if max_res == 'higher' or max_res == 'equal':
                            prompt = 'may not be' if res == 'higher' else 'is'
                            print('--------------------------------DC ISSUE-----------------------------------------')
                            print(f'ERROR: Local {entity_name} (v{entity_version}) {prompt} compatible with {name} (v{v_local}) (4)')
                            print('Recommend StackOverflow Posts: ')
                            for post_id in max_post_id:
                                print(generate_post_url(post_id))
                            print('-----------------------------------END-------------------------------------------')

def is_same_version(v1, v2):
    v1_list = v1.split('.')
    v2_list = v2.split('.')
    # align the length of two version lists
    if len(v1_list) > len(v2_list):
        for i in range(len(v1_list) - len(v2_list)):
            v2_list.append('0')
    elif len(v1_list) < len(v2_list):
        for i in range(len(v2_list) - len(v1_list)):
            v1_list.append('0')
    if len(v1_list) == 1:
        if v1_list[0] == v2_list[0]:
            return True
        else:
            return False
    else:
        if v1_list[0] + '.' + v1_list[1] == v2_list[0] + '.' + v2_list[0]:
            return True
        else:
            return False

def has_relations(component_list, component_name):
    for component in component_list:
        if component[0] == component_name:
            return True
    return False

def check_incompatibliity(local_stack, label, compatible_components, incompatible_components, compatible_posts, incompatible_posts):
    local_component_list = local_stack[label].keys()
    res = []
    if label == 'driver':
        for lcl_component in local_component_list:
            res_posts = []
            lcl_version = cut_version(local_stack[label][lcl_component])
            if lcl_version == '' or has_relations(compatible_components + incompatible_components, lcl_component) == False:
                continue
            if (lcl_component, lcl_version, label) not in compatible_components or (lcl_component, lcl_version, label) in incompatible_components:
                for items in incompatible_posts:
                    if items['component'] == (lcl_component, lcl_version, label):
                        res_posts.extend(items['post_id'].split('_'))
                if len(res_posts) == 0:
                    for _component, _version, _label in compatible_components:
                        if _component == lcl_component:
                            for items in compatible_posts:
                                if items['component'] == (_component, _version, _label):
                                    res_posts.extend(items['post_id'].split('_'))
                res.append({
                    'component': lcl_component,
                    'version': lcl_version,
                    'post_id': res_posts
                })
                # return lcl_component, lcl_version, res_posts
            # else:
            #     return res
    else:
        for lcl_component in local_component_list:
            res_posts = []
            lcl_version = cut_version(local_stack[label][lcl_component])
            if lcl_version == '' or has_relations(compatible_components + incompatible_components, lcl_component) == False:
                continue
            if (lcl_component, lcl_version, label) in incompatible_components:
                for items in incompatible_posts:
                    if items['component'] == (lcl_component, lcl_version, label):
                        res_posts.extend(items['post_id'].split('_'))
                res.append({
                    'component': lcl_component,
                    'version': lcl_version,
                    'post_id': res_posts
                })
                # return lcl_component, lcl_version, res_posts
            # else:
            #     return res
    return res

def find_latest_version(version_list):
    # find the latest version in a list of version numbers
    latest_version = Version(version_list[0])
    for version in version_list:
        if Version(version) > latest_version:
            latest_version = Version(version)
    return str(latest_version)

def sort_version(version_list):
    # sort a dictionary where its keys are version numbers
    version_list.sort(key=lambda x: Version(x))
    return version_list

def inference_compatible_versions(local_component, local_version, target_name, graph: Graph):
    res = []
    related_posts = {}
    compatible_components, incompatible_components, compatible_posts, incompatible_posts = match_related_components(local_component, local_version, graph)
    if len(compatible_components) == 0:
        return [], {}
    for component, version, label in compatible_components:
        if component == target_name:
            res.append(version)
            for items in compatible_posts:
                if items['component'] == (component, version, label):
                    related_posts[version] = (items['post_id'].split('_'))
    return res, related_posts

def detect_version_issue(local_stack, req_stack, graph: Graph):
    cur_local_stack = copy.deepcopy(local_stack)
    cur_req_stack = {}
    incompatible_issue_num = 0
    for req in req_stack:
        maintain_req_stack = {}
        kb = { "library": {}, "driver": {}, "runtime": {}, "operating_system": {}, "hardware": {}}
        detect_version = ''
        # get component name and version
        component_name, req_version, req_spec = get_name_version(req)
        if component_name in ENTITY_LIST_REPLACEMENT.keys():
            component_name = ENTITY_LIST_REPLACEMENT[component_name]
        # If Not in Knowledge Base
        cypher = f'MATCH (n) WHERE n.name="{component_name}" RETURN COUNT(n)'
        res = graph.run(cypher).data()
        if res[0]['COUNT(n)'] == 0:
            continue
        # check if the component is installed locally
        # if not locally installed
        # print(f'Checking {component_name} (v{req_version}) ...')
        if component_name not in cur_local_stack['library'].keys():
            if req_spec is None:
                if req_version != '':
                    detect_version = req_version
                    compatible_components, incompatible_components, compatible_posts, incompatible_posts = match_related_components(component_name, detect_version, graph)
                    if len(compatible_components) == 0 and len(incompatible_components) == 0:
                        compatible_components, incompatible_components, compatible_posts, incompatible_posts = match_related_components(component_name, cut_version(detect_version), graph)
                        if len(compatible_components) == 0 and len(incompatible_components) == 0:
                            cur_local_stack['library'][component_name] = detect_version
                            continue
                    for label in kb.keys():
                        # incompatible_lcl_name, incompatible_lcl_version, related_posts = check_incompatibliity(cur_local_stack, label, compatible_components, incompatible_components, compatible_posts, incompatible_posts)
                        res = check_incompatibliity(cur_local_stack, label, compatible_components, incompatible_components, compatible_posts, incompatible_posts)
                        if len(res) == 0:
                            cur_local_stack['library'][component_name] = detect_version
                            continue
                        for item in res:
                            incompatible_lcl_name = item['component']
                            incompatible_lcl_version = item['version']
                            related_posts = item['post_id']
                            incompatible_issue_num += 1
                            print(f'-------------------------------------Incompatiblility Issue({incompatible_issue_num})-----------------------------------------')
                            print(f'Local {incompatible_lcl_name} (v{incompatible_lcl_version}) is not compatible with {component_name} (v{detect_version}).')
                            print("See more details in the following Stack Overflow posts:")
                            for post in related_posts:
                                print(generate_post_url(post))
                            inferenced_versions, inference_compatible_posts = inference_compatible_versions(incompatible_lcl_name, incompatible_lcl_version, component_name, graph)
                            if len(inferenced_versions) == 0:
                                continue
                            else:
                                sorted_version = sort_version(inferenced_versions)
                                while len(sorted_version) > 0:
                                    latest_version = sorted_version[-1]
                                    maintain_req_stack[component_name] = sorted_version
                                    inf_compatible_components, inf_incompatible_components, inf_compatible_posts, inf_incompatible_posts = match_related_components(component_name, latest_version, graph)
                                    flag = False
                                    for label in kb.keys():
                                        inf_res = check_incompatibliity(cur_local_stack, label, inf_compatible_components, inf_incompatible_components, inf_compatible_posts, inf_incompatible_posts)
                                        if len(inf_res) == 0:
                                            flag = True
                                    if flag == True:
                                        operation = 'upgrade' if Version(latest_version) > Version(detect_version) else 'downgrade'
                                        print(f'We recommend you to {operation} {component_name} to v{latest_version}.')
                                        print("See more details in the following Stack Overflow posts:")
                                        for post in inference_compatible_posts[latest_version]:
                                            print(generate_post_url(post))
                                        print(f'-------------------------------------Incompatiblility Issue End----------------------------------------')
                                        cur_local_stack['library'][component_name] = latest_version
                                        break
                                    else:
                                        sorted_version.pop()
                                        continue
                                if len(sorted_version) == 0:
                                    print('No compatible version found.')

        else:
            local_version = local_stack['library'][component_name]
            if req_spec is None:
                if is_same_version(req_version, local_version):
                    detect_version = local_version
                elif req_version != '':
                    print(f'Local {component_name} (v{local_version}) does not follow the requirements: {component_name} (v{req_version}).')
                    detect_version = req_version
                    compatible_components, incompatible_components = match_related_components(component_name, detect_version, graph)
                    if len(compatible_components) == 0 and len(incompatible_components) == 0:
                        compatible_components, incompatible_components = match_related_components(component_name, cut_version(detect_version), graph)
                        if len(compatible_components) == 0 and len(incompatible_components) == 0:
                            cur_local_stack['library'][component_name] = detect_version
                            continue
                    for label in kb.keys():
                        res = check_incompatibliity(cur_local_stack, label, compatible_components, incompatible_components, compatible_posts, incompatible_posts)
                        if len(res) == 0:
                            cur_local_stack['library'][component_name] = detect_version
                            continue
                        for item in res:
                            incompatible_lcl_name = item['component']
                            incompatible_lcl_version = item['version']
                            related_posts = item['post_id']
                            incompatible_issue_num += 1
                            print(f'Incompatiblility Issue({incompatible_issue_num}): Local {incompatible_lcl_name} (v{incompatible_lcl_version}) is not compatible with {component_name} (v{detect_version}).')
                            print("See more details in the following Stack Overflow posts:")
                            for post in related_posts:
                                print(generate_post_url(post))
                            inferenced_versions, compatible_posts = inference_compatible_versions(incompatible_lcl_name, incompatible_lcl_version, component_name, graph)
                            if len(inferenced_versions) == 0:
                                continue
                            else:
                                sorted_version = sort_version(inferenced_versions)
                                while len(sorted_version) > 0:
                                    latest_version = sorted_version[-1]
                                    maintain_req_stack[component_name] = sorted_version
                                    inf_compatible_components, inf_incompatible_components, inf_compatible_posts, inf_incompatible_posts = match_related_components(component_name, latest_version, graph)
                                    flag = False
                                    for label in kb.keys():
                                        inf_res = check_incompatibliity(cur_local_stack, label, inf_compatible_components, inf_incompatible_components, inf_compatible_posts, inf_incompatible_posts)
                                        if len(inf_res) == 0:
                                            flag = True
                                    if flag == True:
                                        operation = 'upgrade' if Version(latest_version) > Version(detect_version) else 'downgrade'
                                        print(f'We recommend you to {operation} {component_name} to v{latest_version}.')
                                        print("See more details in the following Stack Overflow posts:")
                                        for post in inference_compatible_posts[latest_version]:
                                            print(generate_post_url(post))
                                        cur_local_stack['library'][component_name] = latest_version
                                        break
                                    else:
                                        sorted_version.pop()
                                        continue
                                if len(sorted_version) == 0:
                                    print('No compatible version found.')
    print(f'{incompatible_issue_num} incompatibility issues found.')