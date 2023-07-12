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
                    'nodeDimensionsIncludeLabels': True,
                    'directed': True,
                },
                style={
                    "width": "100%",
                    "height": "calc(100vh - 150px - 50px)",
                    "display": "none"
                },
                stylesheet=[
                    {'selector': 'edge', 'style': {'label': 'data(label)', 'curve-style': 'bezier',
                                                   # 'haystack-radius': 5,
                                                   'width': 3,
                                                   'opacity': 1,
                                                   'fontSize': '30px',
                                                   'line-color': 'lightgreen',
                                                   'source-arrow-color': 'red',
                                                   'source-arrow-shape': 'triangle',
                                                   'source-arrow-size': '150px'}, 'text-wrap': 'wrap'},
                    {
                        'selector': '.blue',
                        'style': {
                            'color': 'blue',
                            'shape': 'triangle',

                        }
                    }
                    ,
                    {'selector': 'node', 'style': {'label': 'data(label)','fontSize': '30px',}, 'text-wrap': 'wrap'},
                    {'selector': '.red',
                     'style': {'background-color': 'red', 'color': 'red', 'fontWeight': 'bold', 'fontSize': '30px', }},
                    {'selector': '.green',
                     'style': {'background-color': 'green', 'color': 'green','fontSize': '30px', }}

                ]
            ), width=50),

            dbc.Col(cyto.Cytoscape(
                id='knowledge-graph-fallback',
                layout={
                    'name': 'concentric',
                    'directed': True
                },
                style={
                    "width": "100%",
                    "height": "calc(100vh - 150px - 50px)",
                    "display": "none",
                    'fontSize': '22px',
                },
                stylesheet=[
                    {'selector': 'edge', 'style': {'label': 'data(label)', 'curve-style': 'haystack',
                                                   'haystack-radius': 0,
                                                   'width': 5,
                                                   'opacity': 1,
                                                   'fontSize': '50px',
                                                   'line-color': '#a8eae5'}, 'text-wrap': 'wrap'},
                    {'selector': 'node',
                     'style': {'label': 'data(label)', 'background-color': '#30c9bc', 'fontSize': '50px', },
                     'text-wrap': 'wrap'},
                ]
            ), width=50)

        ]
    )
])
