import numpy as np
import plotly
import plotly.graph_objs as go

from .string_classifier import generate_training_set


def generate_3d_scatterplot(api_key_files, generic_text_files, dump_file):
    mat, strings = generate_training_set(api_key_files, generic_text_files, True)
    apis = []
    apis_text = []
    text = []
    text_text = []
    for row, string in zip(mat, strings):
        if row[3] == 1:
            apis_text.append(string)
            apis.append(row)
        else:
            text_text.append(string)
            text.append(row)
    apis = np.array(apis)
    text = np.array(text)
    api_trace = go.Scatter3d(
        name="Api-Key",
        x=apis[:, 0],
        y=apis[:, 1],
        z=apis[:, 2],
        text=apis_text,
        mode='markers',
        marker=dict(
            size=3,
            line=dict(
                color='rgba(0, 0, 255, 0.14)',
                width=0.5
            ),
            opacity=0.6
        )
    )
    text_trace = go.Scatter3d(
        name="Text",
        x=text[:, 0],
        y=text[:, 1],
        z=text[:, 2],
        text=text_text,
        mode='markers',
        marker=dict(
            size=3,
            line=dict(
                color='rgba(255, 0, 0, 0.14)',
                width=0.5
            ),
            opacity=0.6
        )
    )
    data = [api_trace, text_trace]
    layout = go.Layout(
        title="Dataset",
        margin=dict(
            l=1,
            r=1,
            b=1,
            t=1
        ),
        scene=dict(
            xaxis=dict(title="entropy"),
            yaxis=dict(title="sequentiality"),
            zaxis=dict(title="gibberish"))
    )
    fig = go.Figure(data=data, layout=layout)
    plotly.offline.plot(fig, filename=dump_file, auto_open=False)
    print("Saved to {0}".format(dump_file))
