import argparse
import json

import plotly.graph_objects as go

def parse_command_line_arguments():
    parser = argparse.ArgumentParser(description="Produce graph for Cascade experimental results")
    parser.add_argument('graphs_file_name', metavar="graphs-file", type=str, 
                        help="graphs definition file")
    args = parser.parse_args()
    return args

def parse_graphs_file(graphs_file_name):
    with open(graphs_file_name) as graphs_file:
        graphs = json.load(graphs_file)
    return graphs

def produce_graph(graph):
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
        xaxis_title=graph['x_axis']['title'],
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
        yaxis_title=graph['y_axis']['title'],
        plot_bgcolor='white')
    x_axis_variable = graph['x_axis']['variable']
    y_axis_variable = graph['y_axis']['variable']
    for series in graph['series']:
        plot_series(figure, x_axis_variable, y_axis_variable, series)
    figure.show()

def plot_series(figure, x_axis_variable, y_axis_variable, series):
    data_file_name = series['data_file']
    data_points = read_data_points(data_file_name)
    plot_deviation(figure, series, x_axis_variable, y_axis_variable, data_points)
    plot_average(figure, series, x_axis_variable, y_axis_variable, data_points)

def plot_average(figure, series, x_axis_variable, y_axis_variable, data_points):
    xs = []
    ys = []
    for data_point in data_points:
        xs.append(data_point[x_axis_variable])
        ys.append(data_point[y_axis_variable]['average'])
    line = go.Scatter(
        x=xs,
        y=ys,
        name=series['legend'],
        mode='lines',
        line=dict(color=series['line_color'], width=1))
    figure.add_trace(line)

def plot_deviation(figure, series, x_axis_variable, y_axis_variable, data_points):
    xs = []
    ys_upper = []
    ys_lower = []
    for data_point in data_points:
        xs.append(data_point[x_axis_variable])
        average = data_point[y_axis_variable]['average']
        deviation = data_point[y_axis_variable]['deviation']
        ys_upper.append(average + deviation)
        ys_lower.append(average - deviation)
    xs = xs + xs[::-1]
    ys = ys_upper + ys_lower[::-1]
    line = go.Scatter(
        x=xs,
        y=ys,
        showlegend=False,
        hoverinfo='none',
        fill='toself',
        line_color=series['deviation_color'],
        fillcolor=series['deviation_color'],
        opacity=0.4)
    figure.add_trace(line)

def read_data_points(data_file_name):
    data_points = []
    with open(data_file_name) as data_file:
        for line in data_file:
            data_point = json.loads(line)
            data_points.append(data_point)
    return data_points

def main():
    args = parse_command_line_arguments()
    graphs = parse_graphs_file(args.graphs_file_name)
    for graph in graphs:
        produce_graph(graph)

if __name__ == "__main__":
    main()
