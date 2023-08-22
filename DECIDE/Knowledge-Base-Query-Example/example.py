from py2neo import *
import json

def neo4j_connect(config_file='./config.json'):
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

def match_component(component_name, component_version, graph: Graph, debug=False):
    components = []
    cypher = f'MATCH (n) WHERE n.name="{component_name}" AND n.version="{component_version}" RETURN n'
    res = graph.run(cypher).data()[0]
    name = res['n']['name']
    version = res['n']['version']
    label = get_label(res['n'])
    if debug:
        print(f'Component name: {name}')
        print(f'Version: {version}')
        print(f'Label: {label}')
    return [name, version, label]

def match_relation(component_name1, component_version1, component_name2, component_version2, graph: Graph, debug=False):
    cypher = f'MATCH (n)-[r]->(m) WHERE n.name="{component_name1}" AND n.version="{component_version1}" AND m.name="{component_name2}" AND m.version="{component_version2}" RETURN r'
    res = graph.run(cypher).data()[0]
    pos_post_id = res['r']['pos_post_id']
    neg_post_id = res['r']['neg_post_id']
    pos_post_list = pos_post_id.split('_')
    while '' in pos_post_list:
        pos_post_list.remove('')
    neg_post_list = neg_post_id.split('_')
    while '' in neg_post_list:
        neg_post_list.remove('')
    relation = 'yes' if len(pos_post_list) >= len(neg_post_list) else 'no'
    if debug:
        print(f'Start node: {res["r"].start_node["name"]} {res["r"].start_node["version"]}')
        print(f'End node: {res["r"].end_node["name"]} {res["r"].end_node["version"]}')
        print(f'Relation: {relation}')
        print(f'Stack Overflow Posts (Compatible): {pos_post_list}')
        print(f'Stack Overflow Posts (Incompatible): {neg_post_list}')
    return [relation, pos_post_list, neg_post_list]

# define your own query function here
# def query():
#     ...

def test():
    DEBUG = True
    graph = neo4j_connect()
    print('Successfully connected to knowledge base!')
    print('Matching components in knowledege base...')
    component_res = match_component('numpy', '1.18.3', graph, debug=DEBUG)
    print('------------------------------------------------------------')
    print('Matching relations in knowledege base...')
    relation_res = match_relation('tensorflow', '1.12', 'cuda', '9', graph, debug=DEBUG)

if __name__ == '__main__':
    test()
