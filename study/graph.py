import argparse
import fileinput
import json

import plotly.graph_objects as go

def parse_command_line_arguments():
    parser = argparse.ArgumentParser(description="Produce graph for Cascade experimental results")
    parser.add_argument('file', nargs='*', help="File containing Cascade experimental results")
    args = parser.parse_args()
    return args

def produce_all_graphs():
    all_experiments = read_all_experiments()
    produce_demystifying_paper_graphs(all_experiments)

def produce_demystifying_paper_graphs(experiments):
    produce_demystifying_paper_figure_1_graph(experiments)
    produce_demystifying_paper_figure_2_graph(experiments)

def produce_demystifying_paper_figure_1_graph(experiments):
    produce_aggregate_vs_qber_graph(
        experiments,
        'Reconciliation efficiency',
        'unrealistic_efficiency')

def produce_demystifying_paper_figure_2_graph(experiments):
    produce_aggregate_vs_qber_graph(
        experiments,
        'Channel uses',
        'ask_parity_messages')

def produce_aggregate_vs_qber_graph(experiments, aggregate_title, aggregate_name):
    figure = go.Figure()
    figure.update_layout(
        xaxis=dict(
            showline=True,
            linecolor='black',
            showgrid=True,
            gridcolor='lightgray',
            showticklabels=True,
            linewidth=1,
            ticks='outside',
            tickfont=dict(family='Arial', size=12, color='black'),
        ),
        xaxis_title='Quantum Bit Error Rate (QBER)',
        yaxis=dict(
            showline=True,
            linecolor='black',
            showgrid=True,
            gridcolor='lightgray',
            showticklabels=True,
            linewidth=1,
            ticks='outside',
            tickfont=dict(family='Arial', size=12, color='black'),
        ),
        yaxis_title=aggregate_title,
        plot_bgcolor='white')
    plot_aggregate(experiments, figure, 'requested_error_rate', aggregate_name, 'blue')
    figure.show()

def plot_aggregate(experiments, figure, x_var, y_var, color):
    plot_deviation(experiments, figure, x_var, y_var, color)
    plot_average(experiments, figure, x_var, y_var, color)

def plot_average(experiments, figure, x_var, y_var, color):
    xs = []
    ys = []
    for experiment in experiments:
        xs.append(experiment[x_var])
        ys.append(experiment[y_var]['average'])
    line = go.Scatter(
        x=xs,
        y=ys,
        name='original',
        mode='lines',
        line=dict(color=color, width=1))
    figure.add_trace(line)

def plot_deviation(experiments, figure, x_var, y_var, color):
    xs = []
    ys_upper = []
    ys_lower = []
    for experiment in experiments:
        xs.append(experiment[x_var])
        average = experiment[y_var]['average']
        deviation = experiment[y_var]['deviation']
        ys_upper.append(average + deviation)
        ys_lower.append(average - deviation)
    xs = xs + xs[::-1]
    ys = ys_upper + ys_lower[::-1]
    color = 'light' + color
    line = go.Scatter(
        x=xs,
        y=ys,
        showlegend=False,
        hoverinfo='none',
        fill='toself',
        line_color=color,
        fillcolor=color,
        opacity=0.4)
    figure.add_trace(line)

def read_all_experiments():
    experiments = []
    for line in fileinput.input():
        experiment = json.loads(line)
        experiments.append(experiment)
    return experiments

def main():
    _args = parse_command_line_arguments()
    produce_all_graphs()

if __name__ == "__main__":
    main()
