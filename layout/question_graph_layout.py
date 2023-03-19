import dash_bootstrap_components as dbc
import dash_cytoscape as cyto
from dash import dcc, html, dash_table

data = 'hi from modal'

question_graph_layout = html.Div([
    dbc.Row(
        dbc.Col(
            dbc.Nav([
                dcc.Dropdown(id='select-label-dropdown',
                             placeholder='Select new label',
                             clearable=False,
                             searchable=True,
                             style={'width': 400},
                             disabled=True
                             ),
                html.Button('Delete', id='delete-button', n_clicks=0, disabled=True, style=dict(display='none')),
                # html.Button('Add nodes/edges', id='add-button', n_clicks=0, disabled=False),
                html.Button('Answer', id='answer-button', n_clicks=0, disabled=False),
            ]))),
    html.Br(),
    dbc.Row(
        html.Div([
            html.H3(id="question", children=[], className="hello",
                    style={'color': '#00361c', 'text-align': 'center'
                           })
        ])

    ),
    dbc.Row(
        children=[
            dbc.Col(cyto.Cytoscape(
                id='question-graph',
                elements=[],
                layout={
                    'name': 'cose-bilkent',
                    'animate': False,
                    'nodeRepulsion': 2000,
                    'idealEdgeLength': 50,
                    'nodeDimensionsIncludeLabels': True
                },
                style={
                    "width": "800px",
                    "height": "calc(100vh - 500px)",
                    # "height": "calc(100vh - 210px)",
                },
                stylesheet=[
                    {'selector': 'edge', 'style': {'label': 'data(label)'}, 'text-wrap': 'wrap'},
                    {'selector': 'node', 'style': {'label': 'data(label)'}, 'text-wrap': 'wrap'},
                ]
            ), className="d-flex justify-content-center")
        ],
    ),
    dbc.Modal(
        [
            dbc.ModalHeader(dbc.ModalTitle("Add nodes and egdes"), close_button=True, style={'background': '#28C3DC'}),
            dbc.ModalBody([
                dbc.InputGroup(
                    [
                        dbc.InputGroupText("Label"),
                        dbc.Input(placeholder="Label", id="new-node-label-input"),
                        dbc.Button("Add node", id="add-new-node-button", n_clicks=0)
                    ],
                    className="mb-3",
                ),
                dbc.InputGroup(
                    [
                        dbc.InputGroupText("From"),
                        dcc.Dropdown(id='from-node-dropdown',
                                     placeholder='Node',
                                     value='',
                                     style={'width': 800},
                                     clearable=False,
                                     searchable=True,
                                     options=[]),
                        dbc.InputGroupText("To"),
                        dcc.Dropdown(id='to-node-dropdown',
                                     placeholder='Node',
                                     value='',
                                     style={'width': 800},
                                     clearable=False,
                                     searchable=True,
                                     options=[]),

                    ],
                    className="mb-3",
                ),
                dbc.InputGroup(
                    [
                        dbc.InputGroupText("Label"),
                        dbc.Input(placeholder="Label", id="new-edge-label-input"),
                        dbc.Button("Add edge", id="add-new-edge-button", n_clicks=0)
                    ],
                    className="mb-3",
                )

            ])

        ],
        id="modal-add-dialog",
        centered=True,
        is_open=False,
        size='lg'
    ),
    dbc.Modal(
        [
            dbc.ModalHeader(dbc.ModalTitle("Answer"), close_button=True, style={'background': '#28C3DC'}),
            dash_table.DataTable(id="data-table", columns=[
                {"name": "Results", 'id': 'types', 'type': 'text'},
                {"name": "Total", 'id': 'total', 'type': 'text'}],
                                 style_header={'textAlign': 'center', 'fontWeight': 'bold'},
                                 data=[],
                                 page_size=5,
                                 style_data={'width': '400px', 'minWidth': '400px',
                                             'maxWidth': '400px',
                                             'overflow': 'hidden', 'textOverflow': 'ellipsis', 'textAlign': 'left'},
                                 page_action="native"),
        ],
        id="modal-answer-dialog",
        centered=True,
        is_open=False,
        # fullscreen=True,
        size='lg',
        scrollable=True,
    )

])
