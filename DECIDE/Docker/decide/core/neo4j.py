from py2neo import *
from packaging.specifiers import SpecifierSet
from packaging.version import Version
import json

from utils.utils import cut_version
from config.version_range import COMPONENT_VERSION_RANGE

def neo4j_connect(config_file='config/neo4j.json'):
    with open(config_file) as f:
        config = json.load(f)
        url = f'{config["protocol"]}://{config["host"]}:{config["port"]}'
        user = config['user']
        password = config['password']
        graph = Graph(url, user=user, password=password)
        return graph

def get_label(node):
    label = list(set(node.labels))[0]
    return label

def match_components(component_name, graph: Graph):
    components = []
    cypher = f'MATCH (n) WHERE n.name="{component_name}" RETURN n'
    res = graph.run(cypher).data()
    for n in res:
        name = n['n']['name']
        version = n['n']['version']
        if version[0] < '0' or version[0] > '9':
            version = version[1:]
        if len(version.split('.')) > 2:
            version = '.'.join(version.split('.')[:2])
        version_range = SpecifierSet(f">={COMPONENT_VERSION_RANGE[name]['min']}") & SpecifierSet(f"<={COMPONENT_VERSION_RANGE[name]['max']}")
        if Version(f'{version}') not in version_range:
            continue
        # min_res = compare_version(version, COMPONENT_VERSION_RANGE[name]['min'])
        # max_res = compare_version(version, COMPONENT_VERSION_RANGE[name]['max'])
        # if min_res == 'lower' or max_res == 'higher':
        #     continue
        components.append((name, version))
    components = list(set(components))
    return components

def match_related_components(component_name, component_version, graph: Graph):
    incompatible_components = []
    compatible_components = []
    incompatible_posts = []
    compatible_posts = []
    cypher = f'MATCH (n)-[r]->(m) WHERE n.name="{component_name}" AND n.version="{component_version}" RETURN r'
    res = graph.run(cypher).data()
    for r in res:
        pos_post_id = r['r']['pos_post_id']
        neg_post_id = r['r']['neg_post_id']
        pos_post_list = pos_post_id.split('_')
        while '' in pos_post_list:
            pos_post_list.remove('')
        neg_post_list = neg_post_id.split('_')
        while '' in neg_post_list:
            neg_post_list.remove('')
        num_verdict = 'yes' if len(pos_post_list) >= len(neg_post_list) else 'no'
        res = cut_version(r['r'].end_node['version'])
        if num_verdict == 'no':
            incompatible_components.append((r['r'].end_node['name'], res, str(r['r'].end_node.labels)[1:]))
            incompatible_posts.append({
                'post_id': neg_post_id,
                'component': (r['r'].end_node['name'], res, str(r['r'].end_node.labels)[1:])
            })
            # incompatible_posts[neg_post_id] = (r['r'].end_node['name'], res, str(r['r'].end_node.labels)[1:])
        else:
            compatible_components.append((r['r'].end_node['name'], res, str(r['r'].end_node.labels)[1:]))
            compatible_posts.append({
                'post_id': pos_post_id,
                'component': (r['r'].end_node['name'], res, str(r['r'].end_node.labels)[1:])
            })
            # compatible_posts[pos_post_id] = (r['r'].end_node['name'], res, str(r['r'].end_node.labels)[1:])
    # compatible_components = list(set(compatible_components))
    # incompatible_components = list(set(incompatible_components))
    # print(f'Incompatible components: {incompatible_components}')
    # print(f'Compatible components: {compatible_components}')
    return compatible_components, incompatible_components, compatible_posts, incompatible_posts
