from core.neo4j import neo4j_connect
from py2neo import *
import random
import csv, json

NODE_ID_LIST = [
    'database',
    'hardware',
    'library',
    'software',
    'operating_system',
    'programming_language',
    'tool'
]

def generate_post_url(post_id):
    return f'https://stackoverflow.com/questions/{post_id}'


def sample_relation(graph: Graph, num):
    random_list = random.sample(range(1, RELATION_NUM), num)
    idx = 1

    for i in random_list:
        res = graph.run(f"MATCH (n)-[r]->(m) WHERE id(r)={i} RETURN r LIMIT 5").data()
        e_name_1 = res[0]['r'].start_node['name']
        e_version_1 = res[0]['r'].start_node['version']
        e_name_2 = res[0]['r'].end_node['name']
        e_version_2 = res[0]['r'].end_node['version']

        verdict = res[0]['r']['verdict']
        confidence = res[0]['r']['confidence']
        probability = res[0]['r']['probability']
        print(f'----------------------------{idx}---------------------------')
        print(f'{e_name_1} {e_version_1}, {e_name_2} {e_version_2}, {verdict}, confidence: {confidence}, probability: {probability}')
        print('positive posts: ')
        for post_id in res[0]['r']['pos_post_id'].split('_'):
            print(generate_post_url(post_id))
        print('negative posts: ')
        for post_id in res[0]['r']['neg_post_id'].split('_'):
            print(generate_post_url(post_id))
        print('----------------------------------------------------------')
        idx += 1

def sample_relation_spec(graph: Graph, num, is_api):
    random_list = []
    idx = 1
    if is_api:
        relation = 'API_WORK_WITH'
    else:
        relation = 'LIB_WORK_WITH'
    while len(random_list) < num:
        i = random.randint(0, RELATION_NUM)
        if i in random_list:
            continue
        res = graph.run(f"MATCH (n)-[r:{relation}]->(m) WHERE id(r)={i} RETURN r LIMIT 5").data()
        if len(res) == 0:
            continue
        random_list.append(i)
        e_name_1 = res[0]['r'].start_node['name']
        e_version_1 = res[0]['r'].start_node['version']
        e_name_2 = res[0]['r'].end_node['name']
        e_version_2 = res[0]['r'].end_node['version']

        verdict = res[0]['r']['verdict']
        confidence = res[0]['r']['confidence']
        probability = res[0]['r']['probability']
        print(f'----------------------------{idx}---------------------------')
        print(f'{e_name_1} {e_version_1}, {e_name_2} {e_version_2}, {verdict}, confidence: {confidence}, probability: {probability}')
        print('positive posts: ')
        for post_id in res[0]['r']['pos_post_id'].split('_'):
            print(generate_post_url(post_id))
        print('negative posts: ')
        for post_id in res[0]['r']['neg_post_id'].split('_'):
            print(generate_post_url(post_id))
        print('----------------------------------------------------------')
        idx += 1

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

def knowledge_base_relation_statistic(graph: Graph, rtype):
    if rtype == 'api':
        relation = 'API_WORK_WITH'
    elif rtype == 'lib':
        relation = 'LIB_WORK_WITH'
    res = graph.run(f"MATCH (n)-[r:{relation}]->(m) RETURN r").data()

    statistic_res = {}
    # count the number of different types of relations
    yes_num = 0
    no_num = 0
    unknown_num = 0
    # for one relation, count the number of: max posts number, min posts number, avg posts number
    max_post_num = 0
    min_post_num = 100000
    total_post_num = 0
    # for one relation, count the number of: max votes number, min votes number, avg votes number
    max_vote_num = 0
    min_vote_num = 100000
    total_vote_num = 0
    # count how many posts in total
    pos_posts = []
    neg_posts = []
    # count how many votes in total
    pos_votes = {}
    neg_votes = {}

    for r in res:
        # print(r)
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
        
        assert len(pos_post_list) == len(pos_vote_list)
        assert len(neg_post_list) == len(neg_vote_list)
        
        pos_post_num = len(pos_post_list)
        neg_post_num = len(neg_post_list)
        pos_vote_sum = sum([int(v) for v in pos_vote_list]) if len(pos_vote_list) > 0 else 0
        neg_vote_sum = sum([int(v) for v in neg_vote_list]) if len(neg_vote_list) > 0 else 0
        
        post_num = pos_post_num + neg_post_num
        vote_num = pos_vote_sum + neg_vote_sum

        total_post_num += post_num
        total_vote_num += vote_num

        if post_num > max_post_num:
            max_post_num = post_num
        if post_num < min_post_num:
            min_post_num = post_num
        
        if vote_num > max_vote_num:
            max_vote_num = vote_num
        if vote_num < min_vote_num:
            min_vote_num = vote_num
        
        num_verdict = ''
        vote_verdict = ''
        if pos_post_num > neg_post_num:
            num_verdict = 'yes'
        elif pos_post_num < neg_post_num:
            num_verdict = 'no'
        else:
            num_verdict = 'unknown'
        
        if pos_vote_sum > neg_vote_sum:
            vote_verdict = 'yes'
        elif pos_vote_sum < neg_vote_sum:
            vote_verdict = 'no'
        else:
            vote_verdict = 'unknown'
        
        if num_verdict == 'yes':
            yes_num += 1
        elif num_verdict == 'no':
            no_num += 1
        elif num_verdict == 'unknown':
            unknown_num += 1
        else:
            raise Exception(f"num_verdict error, {r['r'].start_node['name']}, {r['r'].start_node['version']}, {r['r'].end_node['name']}, {r['r'].end_node['version']}")
        
        pos_posts += pos_post_list
        neg_posts += neg_post_list
        pos_posts = list(set(pos_posts))
        neg_posts = list(set(neg_posts))

        for i in range(len(pos_vote_list)):
            if pos_post_list[i] in pos_votes.keys():
                continue
            else:
                pos_votes[pos_post_list[i]] = pos_vote_list[i]
        
        for i in range(len(neg_vote_list)):
            if neg_post_list[i] in neg_votes.keys():
                continue
            else:
                neg_votes[neg_post_list[i]] = neg_vote_list[i]

    
    statistic_res['yes_num'] = yes_num
    statistic_res['no_num'] = no_num
    statistic_res['unknown_num'] = unknown_num
    statistic_res['max_post_num'] = max_post_num
    statistic_res['min_post_num'] = min_post_num
    statistic_res['avg_post_num'] = total_post_num / (yes_num + no_num + unknown_num)
    statistic_res['total_post_num'] = total_post_num
    statistic_res['max_vote_num'] = max_vote_num
    statistic_res['min_vote_num'] = min_vote_num
    statistic_res['avg_vote_num'] = total_vote_num / (yes_num + no_num + unknown_num)
    statistic_res['total_vote_num'] = total_vote_num

    total_post_wo_repeat = len(pos_posts) + len(neg_posts)
    total_vote_wo_repeat = 0
    for k, v in pos_votes.items():
        total_vote_wo_repeat += int(v)
    for k, v in neg_votes.items():
        total_vote_wo_repeat += int(v)
    
    statistic_res['total_post_wo_repeat'] = total_post_wo_repeat
    statistic_res['total_vote_wo_repeat'] = total_vote_wo_repeat


    with open('./result/relation_statistic.json', 'w') as f:
        json.dump(statistic_res, f, indent=4)

def knowledge_base_node_statistic(graph: Graph, rtype):
    statistic_res = {}
    for id in NODE_ID_LIST:
        res = graph.run(f"MATCH (n:{id}) RETURN n").data()
        for r in res:
            name = r['n']['name']
            if name not in statistic_res.keys():
                statistic_res[name] = 1
            else:
                statistic_res[name] += 1
    x = 0
    for k, v in statistic_res.items():
        x += v
    print(x)
    with open(f'./result/node_statistic.json', 'w') as f:
        json.dump(statistic_res, f, indent=4)

def main():
    graph = neo4j_connect()
    # res = graph.run("MATCH (n)-[r:LIB_WORK_WITH]->() RETURN COUNT(r)")
    # print(res.data()[0]['COUNT(r)'])
    # sample_relation_spec(graph, 100, False)
    # get_all_relation(graph, 'lib')
    # knowledge_base_relation_statistic(graph, 'lib')
    knowledge_base_node_statistic(graph, 'lib')


if __name__ == '__main__':
    main()