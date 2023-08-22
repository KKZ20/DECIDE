import json

def parse_relation(relation):
    if relation[0] == '(' and relation[-1] == ')':
        relation = relation[1:-1]
        relation = relation.split(',')
        if len(relation) != 3:
            return 'Error'
        entity1 = relation[0].strip()[1:-1]
        entity2 = relation[1].strip()[1:-1]
        relation = relation[2].strip()[1:-1]
        if entity1 < entity2:
            return [entity1, entity2, relation]
        elif entity1 > entity2:
            return [entity2, entity1, relation]
        else:
            return 'Error'
    else:
        return 'Error'

def get_file_info(file_name):
    info = {}
    with open(file_name, 'r') as f:
        line = f.readline()
        while line:
            if 'current post' in line:
                tmp = {}
                so_id = line.split()[-1]
                tmp['so_id'] = line.split()[-1]
                tmp['relation'] = []
                while line:
                    line = f.readline()
                    if 'libaray knowledge extract' in line:
                        continue
                    elif 'end of library knowledge' in line:
                        break
                    else:
                        line_tmp = line.strip()
                        if line_tmp == '':
                            continue
                        res = parse_relation(line_tmp)
                        if res != 'Error':
                            tmp['relation'].append(line_tmp)
                        if res == 'Error':
                            print(f"id: {tmp['so_id']}, {line}")
                info[so_id] = tmp
            line = f.readline()
    return info

def parse_realtion(relation):
    if relation[0] == '(' and relation[-1] == ')':
        relation = relation[1:-1]
        relation = relation.split(',')
        if len(relation) != 3:
            return 'Error'
        entity1 = relation[0].strip()[1:-1]
        entity2 = relation[1].strip()[1:-1]
        relation = relation[2].strip()[1:-1]
        if entity1 < entity2:
            return [entity1, entity2, relation]
        elif entity1 > entity2:
            return [entity2, entity1, relation]
        else:
            return 'Error'

def compare_result(model_output, ground_truth):
    compare_res = {}
    for key, value in model_output.items():
        if key in list(ground_truth.keys()):
            ground_dict = {}
            model_relation = value['relation']
            ground_relation = ground_truth[key]['relation']
            for gr in ground_relation:
                entity1, entity2, relation = parse_realtion(gr)
                entity_pair = entity1 + '-' + entity2
                if entity_pair not in ground_dict.keys():
                    ground_dict[entity_pair] = relation
            intersec_num = 0
            gt_num = len(ground_relation)
            model_num = len(model_relation)
            for relation in model_relation:
                if relation in ground_relation:
                    intersec_num += 1
                elif relation not in ground_relation:
                    print(f'Post ID: {key}')
                    print(f'wrong: {relation}')
                    # ...
                else:
                    print(f'{key}: {relation}')
            compare_res[key] = {
                'intersec_num': intersec_num,
                'model_num': model_num,
                'gt_num': gt_num
            }
        else:
            print(f'ground truth not contain {key}')
    return compare_res

def calculate_score(compare_res):
    precision = 0
    recall = 0

    total_intersec = 0
    total_model = 0
    total_gt = 0

    for key, value in compare_res.items():
        total_intersec += value['intersec_num']
        total_model += value['model_num']
        total_gt += value['gt_num']
    
    # print(f'total_intersec: {total_intersec}, total_model: {total_model}, total_gt: {total_gt}')
    
    precision = total_intersec / total_model
    recall = total_intersec / total_gt
    return total_intersec, total_model, total_gt, precision, recall

def main():
    GROUND_TRUTH = './data/ground_truth.txt'
    OPTIMAL_TEST = 'Q12'
    gt = get_file_info(GROUND_TRUTH)
    test_file = f'./data/{OPTIMAL_TEST}.log'
    model_output = get_file_info(test_file)
    compare_res = compare_result(model_output, gt)
    total_intersec, total_model, total_gt, precision, recall = calculate_score(compare_res)
    print(f'Number of Model Output: {total_model}')
    print(f'Number of Ground Truth: {total_gt}')
    print(f'Number of Correct Knowledge: {total_intersec}')
    print(f'Number of Wrong Knowledge: {total_model - total_intersec}')
    print(f'Test result: Precision = {round(precision*100, 1)}%, Recall = {round(recall*100, 1)}%')


if __name__ == '__main__':
    main()