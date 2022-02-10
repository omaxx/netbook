from datetime import date, datetime, timedelta

from dash import html, dcc
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import plotly.graph_objects as go


from netbook.db import Object, Folder, Group, Device
from netbook.db.errors import DoesNotExist
from netbook.db.mongo.models.syslog import SEVERITIES

DASH_PREFIX = "/dash"
PREFIX = "inventory"


def create_layout(*path):
    try:
        obj_path = path[1]
    except IndexError:
        obj_path = None

    try:
        obj = Object.get(path=obj_path)
    except DoesNotExist:
        return html.Div(f"Object {path[1:2]} not found")

    if isinstance(obj, Folder):
        return create_folder_layout(obj)
    if isinstance(obj, Group):
        return create_group_layout(obj)
    if isinstance(obj, Device):
        return create_device_layout(obj)
    return html.Div()


def create_folder_layout(obj):
    return html.Div([
        create_breadcrumb(obj),
        html.Div([
            html.H4("Folders:"),
            create_object_table(obj.list_folders(), fields=[
                {"title": "Total"},
                {"title": "Count (Poll Status == OK)"},
                {"title": "Count (Poll Status == ERROR)"},
            ]),
        ]),
        html.Div([
            html.H4("Devices:"),
            create_object_table([obj], fields=[
                {"title": "Total"},
                {"title": "Count (Poll Status == OK)"},
                {"title": "Count (Poll Status == ERROR)"},
            ]),
            create_object_table(obj.list_devices(), fields=[
                {"title": "IP", "value": "vars.ip"},
                {"title": "Hostname", "value": "info.hostname"},
                {"title": "Family", "value": "info.family"},
                {"title": "Model", "value": "info.model"},
                {"title": "Poll Status", "value": "poll_status.value"},
                {"title": "Poll Status Updated", "value": "poll_status.updated"},
                {"title": "Last OK Poll Status", "value": "poll_status.last_ok"},
                {"title": "State", "value": "state.value"},
                {"title": "State Updated", "value": "state.updated"},
                {"title": "Last Normal State", "value": "state.last_normal"},
            ]),
        ]),
        html.Div([
            html.H4("Groups:"),
            create_object_table(obj.list_groups()),
        ]),
    ])


def create_group_layout(obj):
    return html.Div([
        create_breadcrumb(obj),
        html.Div([
            html.H4("Devices:"),
            create_object_table([obj], fields=[
                {"title": "Total"},
                {"title": "Count (Poll Status == OK)"},
                {"title": "Count (Poll Status == ERROR)"},
            ]),
            create_object_table(obj.list_devices(), fields=[
                {"title": "IP", "value": "vars.ip"},
                {"title": "Hostname", "value": "info.hostname"},
                {"title": "Family", "value": "info.family"},
                {"title": "Model", "value": "info.model"},
                {"title": "Poll Status", "value": "poll_status.value"},
                {"title": "Poll Status Updated", "value": "poll_status.updated"},
                {"title": "Last OK Poll Status", "value": "poll_status.last_ok"},
                {"title": "State", "value": "state.value"},
                {"title": "State Updated", "value": "state.updated"},
                {"title": "Last Normal State", "value": "state.last_normal"},
            ]),
        ]),
    ])


def create_device_layout(obj):
    return html.Div([
        create_breadcrumb(obj),
        html.H3(obj.name, title=obj.path, style={'text-align': 'center'}, id='device-path'),
        dcc.DatePickerRange(
            id='date-picker',
            start_date=date.today(),
            end_date=date.today() + timedelta(days=1),
            minimum_nights=1,
        ),
        dcc.Graph(
            id='bar-graph',
        )

    ])


def create_breadcrumb(obj):
    items = [
        {"label": "inventory", "href": f"{DASH_PREFIX}/{PREFIX}", "active": False},
        *[{"label": parent, "href": f"{DASH_PREFIX}/{PREFIX}/{parent}", "active": False} for parent in obj.parents()]
    ]
    items[-1]["active"] = True
    return dbc.Breadcrumb(
        items=items
    )


def create_object_table(object_list, fields=None):
    fields = fields or []
    table_header = html.Thead(
        html.Tr([
            html.Th("Name"),
            *[html.Th(field.get("title", "")) for field in fields]
        ])
    )

    table_body = html.Tbody([
        html.Tr([
            html.Th(create_object_link(obj)),
            *[html.Th(get_object_value(obj, field)) for field in fields]
        ]) for obj in object_list
    ])

    return dbc.Table([
        table_header,
        table_body
    ], bordered=True)


def create_object_link(obj):
    return html.A(obj.name, href=f"{DASH_PREFIX}/{PREFIX}/{obj.path}")


def get_object_value(obj, field):
    # FIXME:
    value = field.get("value", "").split(".")
    try:
        return obj[value[0]][value[1]]
    except:
        return ""


SEVERITY_COLOR = [
    "violet",
    "lightpink",
    "red",
    "orange",
    "yellow",
    "cyan",
    "green",
    "blue"
]


def register_callbacks(app):
    @app.callback(
        Output('bar-graph', 'figure'),
        [
            Input('device-path', 'title'),
            Input('date-picker', 'start_date'),
            Input('date-picker', 'end_date'),
        ]
    )
    def create_bar_graph(path, start_date, end_date):
        fig = go.Figure()
        ts_begin = datetime.fromisoformat(start_date)
        ts_end = datetime.fromisoformat(end_date)
        if ts_end - ts_begin > timedelta(days=1):
            aggregate_time = 60
        else:
            aggregate_time = 15
        device = Device.get(path)
        for severity in range(8):
            events = device.get_syslog_aggregate(
                ts_begin=ts_begin,
                ts_end=ts_end,
                aggregate_time=aggregate_time,
                match={"severity_level": severity}
            )
            fig.add_trace(
                # go.Scatter(
                go.Bar(
                    x=[event["_id"] for event in events],
                    y=[event["count"] for event in events],
                    legendgroup="syslog",
                    name=SEVERITIES[severity],
                    marker={'color': SEVERITY_COLOR[severity]}
                )
            )

        fig.update_layout(xaxis_range=(ts_begin, ts_end), barmode="stack")
        return fig
