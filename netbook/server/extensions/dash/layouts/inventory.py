import dash_bootstrap_components as dbc
from dash import html

from netbook.db import Object, Folder, Group, Device, DoesNotExist

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
        create_object_table(obj.list_folders()),
        create_object_table(obj.list_groups()),
        create_object_table(obj.list_devices()),
    ])


def create_group_layout(obj):
    return html.Div([
        create_breadcrumb(obj),
        create_object_table(obj.list_devices()),
    ])


def create_device_layout(obj):
    return html.Div([
        create_breadcrumb(obj),
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


def create_object_table(object_list):

    table_header = html.Thead(
        html.Tr([
            html.Th("Name"),
        ])
    )

    table_body = html.Tbody([
        html.Tr([
            html.Th(create_link(obj)),
        ]) for obj in object_list
    ])

    return dbc.Table([
        table_header,
        table_body
    ], bordered=True)


def create_link(obj):
    return html.A(obj.name, href=f"{DASH_PREFIX}/{PREFIX}/{obj.path}")
