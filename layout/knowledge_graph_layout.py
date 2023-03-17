import dash_bootstrap_components as dbc
import dash_cytoscape as cyto
from dash import dcc, html

cyto.load_extra_layouts()

knowledge_graph_layout = html.Div([
    dbc.Row(
        dbc.Col(
            dbc.Nav([
                dcc.Dropdown(id='select-nr-of-nodes',
                             placeholder='Select nr of displayed nodes',
                             clearable=False,
                             searchable=True,

                             style={'width': 0},
                             ),
                # html.Div("Selected id: "),
                html.Div(id="selected-node-id")
            ]))),
    dbc.Row(
        children=[
            dbc.Col(cyto.Cytoscape(
                id='knowledge-graph',
                layout={
                    'name': 'cose-bilkent',
                    'animate': False,
                    'nodeRepulsion': 20000,
                    'idealEdgeLength': 400,
                    'nodeDimensionsIncludeLabels': True
                },
                style={
                    "width": "100%",
                    "height": "calc(100vh - 150px - 50px)",
                    "display": "none"
                },
                stylesheet=[
                    {'selector': 'edge', 'style': {'label': 'data(label)', 'curve-style': 'haystack',
                                                   'haystack-radius': 0,
                                                   'width': 5,
                                                   'opacity': 0.5,
                                                   'line-color': '#a8eae5'}, 'text-wrap': 'wrap'},
                    {'selector': 'node', 'style': {'label': 'data(label)', 'background-color': '#30c9bc'},
                     'text-wrap': 'wrap'},
                ]
            ), width=12),

            dbc.Col(cyto.Cytoscape(
                id='knowledge-graph-fallback',
                layout={
                    'name': 'concentric',
                },
                style={
                    "width": "100%",
                    "height": "calc(100vh - 150px - 50px)",
                    "display": "none"
                },
                stylesheet=[
                    {'selector': 'edge', 'style': {'label': 'data(label)', 'curve-style': 'haystack',
                                                   'haystack-radius': 0,
                                                   'width': 5,
                                                   'opacity': 0.5,
                                                   'line-color': '#a8eae5'}, 'text-wrap': 'wrap'},
                    {'selector': 'node', 'style': {'label': 'data(label)', 'background-color': '#30c9bc'},
                     'text-wrap': 'wrap'},
                ]
            ), width=12)

        ]
    )
])
