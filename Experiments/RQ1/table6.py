TOTAL_ISSUE = 17

def get_tool_data():
    TOOLS = ['DECIDE', 'PyEGo', 'Watchman']
    data = {}
    for tool in TOOLS:
        with open(f'./data/{tool}.log', 'r') as f:
            line = f.readline()
            while line:
                if 'Detect Issues' in line.strip():
                    detect_issues = int(line.strip().split(':')[-1].strip())
                elif 'Report Issues' in line.strip():
                    report_issues = int(line.strip().split(':')[-1].strip())
                line = f.readline()
            data[tool] = [detect_issues, report_issues]
    return data

def calculate_score(tool_data):
    res = {}
    for tool in tool_data:
        precision = tool_data[tool][0] / tool_data[tool][1]
        recall = tool_data[tool][0] / TOTAL_ISSUE
        f1_score = 2 * precision * recall / (precision + recall)
        res[tool] = [precision, recall, f1_score]
    return res

def main():
    data = get_tool_data()
    scores = calculate_score(data)
    for key, value in scores.items():
        print(f'{key} results: ')
        print(f'Precision: {round(value[0]*100, 1)}%')
        print(f'Recall: {round(value[1]*100, 1)}%')
        print(f'F1 Score: {round(value[2]*100, 1)}%')
        print('---------------------------------------------')

if __name__ == '__main__':
    main()