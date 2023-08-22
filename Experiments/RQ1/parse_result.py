import json

def get_ground_truth():
    with open('./data/ground_truth.json') as f:
        data = json.load(f)
    return data

def get_result(ground_truth):
    detect_issues = 0
    report_issues = 0
    layer_distribution = {
        'library': 0,
        'runtime': 0,
        'driver': 0,
        'os': 0,
        'hardware': 0
    }
    for key, value in ground_truth.items():
        incompatiblity_components = []
        f = open(f'./data/{key}.log', 'r')
        lines = f.readlines()
        for line in lines:
            if 'incompatibility issues found' in line.strip():
                report_issues += int(line.strip().split('incompatibility issues found')[0])
            elif 'is not compatible with' in line.strip():
                words = line.strip().split(' ')
                component_a = words[7] + ' ' + words[8][2:-2]
                component_b = words[1] + ' ' + words[2][2:-1]
                for issue in value:
                    if f'{component_a}, {component_b}' == issue['incompatible_components']:
                        detect_issues += 1
                        for layer in issue['involved_layers']:
                            layer_distribution[layer] += 1
        f.close()
    return report_issues, detect_issues, layer_distribution


def main():
    ground_truth = get_ground_truth()
    report_issues, detect_issues, layer_distribution = get_result(ground_truth)
    with open('./data/DECIDE.log', 'w') as f:
        f.write(f'Detect Issues: {detect_issues}\n')
        f.write(f'Report Issues: {report_issues}\n')
        f.write('\n')
        f.write(f'Library Layer: {layer_distribution["library"]}\n')
        f.write(f'Runtime Layer: {layer_distribution["runtime"]}\n')
        f.write(f'Driver Layer: {layer_distribution["driver"]}\n')
        f.write(f'OS/Container Layer: {layer_distribution["os"]}\n')
        f.write(f'Hardware Layer: {layer_distribution["hardware"]}\n')


if __name__ == '__main__':
    main()