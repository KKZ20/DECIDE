from core.neo4j import neo4j_connect
from py2neo import *
import random
import csv, json

def generate_post_url(post_id):
    return f'https://stackoverflow.com/questions/{post_id}'

def get_consolidate_relation(graph: Graph, is_api):
    if is_api:
        relation = 'API_WORK_WITH'
    else:
        relation = 'LIB_WORK_WITH'
    f = open('./consolidate.csv', 'w')
    writer = csv.writer(f)
    writer.writerow(['ID', 'NUMBER', 'VOTE', 'LOSS', 'GROUD_TRUTH'])
    res = graph.run(f"MATCH (n)-[r:{relation}]->(m) RETURN r").data()
    idx = 0
    for r in res:
        idx += 1
        pos_post_id = r['r']['pos_post_id']
        pos_vote = r['r']['pos_vote']
        neg_post_id = r['r']['neg_post_id']
        neg_vote = r['r']['neg_vote']
        pos_post_list = pos_post_id.split('_')
        while '' in pos_post_list:
            pos_post_list.remove('')
        pos_vote_list = pos_vote.split('_')
        while '' in pos_vote_list:
            pos_vote_list.remove('')
        neg_post_list = neg_post_id.split('_')
        while '' in neg_post_list:
            neg_post_list.remove('')
        neg_vote_list = neg_vote.split('_')
        while '' in neg_vote_list:
            neg_vote_list.remove('')

        pos_post_num = len(pos_post_list)
        neg_post_num = len(neg_post_list)
        pos_vote_sum = sum([int(v) for v in pos_vote_list]) if len(pos_vote_list) > 0 else 0
        neg_vote_sum = sum([int(v) for v in neg_vote_list]) if len(neg_vote_list) > 0 else 0

        if pos_post_num > 1 or neg_post_num > 1:
            num_verdict = 'yes' if pos_post_num > neg_post_num else 'no'
            vote_verdict = 'yes' if pos_vote_sum > neg_vote_sum else 'no'
            loss_verdict = r['r']['verdict']
            start_node = r['r'].start_node
            end_node = r['r'].end_node
            e_name_1 = start_node['name']
            e_version_1 = start_node['version']
            e_name_2 = end_node['name']
            e_version_2 = end_node['version']
            writer.writerow([idx, f'{num_verdict} ({pos_post_num} - {neg_post_num})', f'{vote_verdict} ({pos_vote_sum} - {neg_vote_sum})', f'{loss_verdict}'])
            print(f'---------------------------{idx}---------------------------')
            print(f'{e_name_1} {e_version_1}, {e_name_2} {e_version_2}')
            print(f'num_verdict: {num_verdict}')
            print(f'vote_verdict: {vote_verdict}')
            print(f'loss_verdict: {loss_verdict}')
            print('positive posts: ')
            for post_id in pos_post_list:
                print(generate_post_url(post_id))
            print('negative posts: ')
            for post_id in neg_post_list:
                print(generate_post_url(post_id))
            print('---------------------------------------------------------')
    return

def get_all_relation(graph: Graph, rtype):
    if rtype == 'api':
        relation = 'API_WORK_WITH'
    elif rtype == 'lib':
        relation = 'LIB_WORK_WITH'
    res = graph.run(f"MATCH (n)-[r:{relation}]->(m) RETURN r").data()
    f = open('./result_KG_3.csv', 'w')
    writer = csv.writer(f)
    writer.writerow(['ID', 'CONFIDENCE', 'NUMBER', 'VOTE'])
    idx = 1
    for r in res: 
        e_name_1 = r['r'].start_node['name']
        e_version_1 = r['r'].start_node['version']
        e_name_2 = r['r'].end_node['name']
        e_version_2 = r['r'].end_node['version']
        pos_post_id = r['r']['pos_post_id']
        pos_vote = r['r']['pos_vote']
        neg_post_id = r['r']['neg_post_id']
        neg_vote = r['r']['neg_vote']

        pos_post_list = pos_post_id.split('_')
        while '' in pos_post_list:
            pos_post_list.remove('')
        
        pos_vote_list = pos_vote.split('_')
        while '' in pos_vote_list:
            pos_vote_list.remove('')
        
        neg_post_list = neg_post_id.split('_')
        while '' in neg_post_list:
            neg_post_list.remove('')
        
        neg_vote_list = neg_vote.split('_')
        while '' in neg_vote_list:
            neg_vote_list.remove('')

        pos_post_num = len(pos_post_list)
        neg_post_num = len(neg_post_list)
        pos_vote_sum = sum([int(v) for v in pos_vote_list]) if len(pos_vote_list) > 0 else 0
        neg_vote_sum = sum([int(v) for v in neg_vote_list]) if len(neg_vote_list) > 0 else 0

        num_verdict = 'yes' if pos_post_num > neg_post_num else 'no'
        vote_verdict = 'yes' if pos_vote_sum > neg_vote_sum else 'no'
        confidence = (pos_vote_sum - neg_vote_sum) / (pos_vote_sum + neg_vote_sum)
        writer.writerow([idx, confidence, f'{num_verdict} ({pos_post_num} - {neg_post_num})', f'{vote_verdict} ({pos_vote_sum} - {neg_vote_sum})'])
        print(f'----------------------------{idx}---------------------------')
        print(f'{e_name_1} {e_version_1}, {e_name_2} {e_version_2}')
        print(f'num_verdict: {num_verdict}')
        print(f'vote_verdict: {vote_verdict}')
        print(f'confidence: {confidence}')
        print('positive posts: ')
        for post_id in pos_post_list:
            print(generate_post_url(post_id))
        print('negative posts: ')
        for post_id in neg_post_list:
            print(generate_post_url(post_id))
        print('----------------------------------------------------------')
        idx += 1


def main():
    graph = neo4j_connect()
    # res = graph.run("MATCH (n)-[r]->(m) RETURN r LIMIT 5")
    # print(res.data())
    get_consolidate_relation(graph, False)
    # get_all_relation(graph, 'lib')


if __name__ == '__main__':
    main()