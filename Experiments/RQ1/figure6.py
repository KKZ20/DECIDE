import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def get_figure_data():
    TOOLS = ['DECIDE', 'PyEGo', 'Watchman']
    data = []
    for tool in TOOLS:
        tool_data = []
        library, runtime, driver, os, hardware = 0, 0, 0, 0, 0
        with open(f'./data/{tool}.log', 'r') as f:
            line = f.readline()
            while line:
                if 'Library Layer' in line.strip():
                    library = int(line.strip().split(':')[-1].strip())
                elif 'Runtime Layer' in line.strip():
                    runtime = int(line.strip().split(':')[-1].strip())
                elif 'Driver Layer' in line.strip():
                    driver = int(line.strip().split(':')[-1].strip())
                elif 'OS/Container Layer' in line.strip():
                    os = int(line.strip().split(':')[-1].strip())
                elif 'Hardware Layer' in line.strip():
                    hardware = int(line.strip().split(':')[-1].strip())
                line = f.readline()
            tool_data = [library, runtime, driver, os, hardware]
        data.extend(tool_data)
    for i in range(len(data)):
        if data[i] == 0:
            data[i] = 0.1
    #create DataFrame
    df = pd.DataFrame(
        {
            'Layers': ['Library', 'Runtime', 'Driver', 'OS/Container', 'Hardware',
                    'Library', 'Runtime', 'Driver', 'OS/Container', 'Hardware',
                    'Library', 'Runtime', 'Driver', 'OS/Container', 'Hardware'],
            'Issues': data,
            '': ['DECIDE', 'DECIDE', 'DECIDE', 'DECIDE', 'DECIDE',
                    'PyEGo', 'PyEGo', 'PyEGo', 'PyEGo', 'PyEGo',
                    'Watchman', 'Watchman', 'Watchman', 'Watchman', 'Watchman']
        })
    return df

def draw_figure(df):
    plt.figure(figsize=(9, 4))
    sns.set(style='whitegrid', font='Helvetica')
    fig = sns.barplot(x='Layers', y='Issues', hue='', data=df, palette=['#A9D18E', '#C5E0B4', '#E2F0D9'])


    #add axis titles
    plt.ylabel('Numbers of Detected Issues', fontsize=14)
    plt.xlabel('')
    #rotate x-axis labels
    plt.xticks(fontsize=16)
    plt.legend(fontsize=12)
    plt.show()
    sns_plot = fig.get_figure()
    sns_plot.savefig('./figures&tables/figure6.png', dpi=300, pad_inches=0.1, bbox_inches='tight')

def main():
    df = get_figure_data()
    draw_figure(df)

if __name__ == '__main__':
    main()