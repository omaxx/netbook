from dash import html


def create_layout(*path):
    layout = html.Div([f"Dash Inventory: path = {path}"])

    return layout
