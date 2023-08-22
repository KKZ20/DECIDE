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
            wrong_num = 0
            gt_num = len(ground_relation)
            model_num = len(model_relation)
            for relation in model_relation:
                if relation in ground_relation:
                    intersec_num += 1
                elif relation not in ground_relation:
                    wrong_num += 1
                else:
                    print(f'{key}: {relation}')
            compare_res[key] = {
                'intersec_num': intersec_num,
                'model_num': model_num,
                'gt_num': gt_num,
                'wrong_num': wrong_num
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
    total_wrong = 0

    for key, value in compare_res.items():
        total_intersec += value['intersec_num']
        total_model += value['model_num']
        total_gt += value['gt_num']
        total_wrong += value['wrong_num']
    precision = total_intersec / total_model
    recall = total_intersec / total_gt
    assert total_intersec + total_wrong == total_model
    return total_intersec, total_wrong, total_model, total_gt, precision, recall

def main():
    GROUND_TRUTH = './data/ground_truth.txt'
    SINGLE_TEST = ['Q1', 'Q2', 'Q3', 'Q4', 'Q5', 'Q6', 'Q7', 'Q8']
    COMBINE_TEST = ['Q12', 'Q34', 'Q56', 'Q78', 'Q1357', 'Q2468', 'Q1-8']
    gt = get_file_info(GROUND_TRUTH)

    print('Single Question Template Test Begin!')
    for st in SINGLE_TEST:
        test_file = f'./data/{st}.log'
        model_output = get_file_info(test_file)
        compare_res = compare_result(model_output, gt)
        total_intersec, total_wrong, total_model, total_gt, precision, recall = calculate_score(compare_res)
        print(f'{st} test result:')
        print(f'Number of Model Output: {total_model}')
        print(f'Number of Ground Truth: {total_gt}')
        print(f'Number of Correct Knowledge: {total_intersec}')
        print(f'Number of Wrong Knowledge: {total_wrong}')
        print(f'Precision = {round(precision*100, 1)}%, Recall = {round(recall*100, 1)}%')
        print('----------------------------------------')
    print('\n')
    print('Combined Question Template Test Begin!')
    for st in COMBINE_TEST:
        test_file = f'./data/{st}.log'
        model_output = get_file_info(test_file)
        compare_res = compare_result(model_output, gt)
        total_intersec, total_wrong, total_model, total_gt, precision, recall = calculate_score(compare_res)
        print(f'{st} test result:')
        print(f'Number of Model Output: {total_model}')
        print(f'Number of Ground Truth: {total_gt}')
        print(f'Number of Correct Knowledge: {total_intersec}')
        print(f'Number of Wrong Knowledge: {total_wrong}')
        print(f'Precision = {round(precision*100, 1)}%, Recall = {round(recall*100, 1)}%')
        print('----------------------------------------')


if __name__ == '__main__':
    main()