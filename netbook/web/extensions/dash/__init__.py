from dash import Dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output

import dash_bootstrap_components as dbc

import flask_login


def create_app(server, url_prefix=""):
    app = Dash(__name__,
               server=server,
               url_base_pathname=url_prefix+"/",
               external_stylesheets=[dbc.themes.DARKLY])
    app.layout = html.Div([
        dcc.Location(id='url', refresh=False),
        html.Div(id='page-content')
    ])

    from .layouts import inventory
    from .layouts import users

    @app.callback(
        Output('page-content', 'children'),
        Input('url', 'pathname'),
    )
    def display_page(pathname):
        if not flask_login.current_user.is_authenticated:
            return "403"
        path = pathname.removeprefix(url_prefix).removeprefix("/").split("/")
        if path[0] == inventory.PREFIX:
            return inventory.create_layout(*path)
        elif path[0] == "users":
            return users.create_layout(*path)
        else:
            return '404'

    inventory.register_callbacks(app)

