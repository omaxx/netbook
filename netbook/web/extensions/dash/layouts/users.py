from dash import html


def create_layout(*path):
    layout = html.Div([f"Dash Users: path = {path}"])

    return layout
