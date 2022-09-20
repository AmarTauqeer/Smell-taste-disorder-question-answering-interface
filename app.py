# -*- coding: utf-8 -*-
import os
import re
import ssl
import textwrap
import time
from flask_cors import CORS
from flask import Flask

import dash_bootstrap_components as dbc
# import spacy
from dash import Input, Output, State, html
from dash_extensions.enrich import DashProxy, MultiplexerTransform

from layout.graph_sent_merge_filter_approach import generate_question_graph_v2, export_qg_with_kg_annotations
from layout.graph_utils import GraphUtils
from layout.knowledge_graph_layout import knowledge_graph_layout
from layout.question_graph_layout import question_graph_layout
from layout.select_question import question_select
from layout.view_export_layout import view_export_layout

from SPARQLWrapper import SPARQLWrapper, JSON, BASIC

from resources.data import graph_data
from dotenv import load_dotenv

ssl.SSLContext.verify_mode = ssl.VerifyMode.CERT_OPTIONAL

# app = Flask(__name__)
# cors = CORS(app)

app = DashProxy(prevent_initial_callbacks=True, transforms=[MultiplexerTransform()],
                external_stylesheets=[dbc.themes.BOOTSTRAP])

graph_id_ = ""
graph_triplets_ = ""
graph_ = None
data_table_arr = []
update_state_ = "false"
node_or_edge_ = "node"

load_dotenv('.env')
hostname=os.getenv("HOST_URI_GET")
username=os.getenv("user_name")
password=os.getenv("password")



# nlp = spacy.load("en_core_web_sm")
graph_utils = GraphUtils()
graph_utils_export = GraphUtils()
app.title = "Question understanding interface"

app.layout = html.Div([
    dbc.Row(
        dbc.Col(html.H2(
            children='Questioning/Answering Interface for Smell and Taste Disorder',
            style={
                'textAlign': 'center',
            }
        ), width=4), justify="center", align="center", style={"margin": "8px", "paddingTop": "10%"}),
    dbc.Row(
        dbc.Col(html.Header(
            "Select a question below and have a look on the knowledge graph or the generated question graph",
            style={
                'textAlign': 'center',
                'fontSize': '18px',
            }

        ), width=4), justify="center", align="center", style={"marginTop": "10%"}),
    dbc.Row([
        dbc.Col(question_select, width=5),
    ],
        justify="center",
        align="center", style={"margin": "8px"}),
    dbc.Row([
        dbc.Col(
            dbc.Button("Knowledge graph", id="open-kg", n_clicks=0, disabled=True, color="secondary",
                       style={'width': '110px', 'height': '80px', 'textAlign': 'center'}),
            width=1),
        dbc.Col(
            dbc.Button("Question graph", id="open-qg", n_clicks=0, disabled=True, color="success",
                       style={'width': '110px', 'height': '80px', 'textAlign': 'center'})
            , width=1),
        # dbc.Col(
        #     dbc.Button("View export", id="open-view-export", n_clicks=0, color="success",
        #                style={'width': '110px', 'height': '80px', 'textAlign': 'center'})
        #     , width=1),
        dbc.Col(dbc.Button("? Help", id="open-help", n_clicks=0, color="info",
                           style={'width': '110px', 'height': '80px', 'textAlign': 'center'}), width=1)
    ], justify="center", align="center", style={'textAlign': 'center'}),
    dbc.Modal(
        [
            dbc.ModalHeader(dbc.ModalTitle("Subset Knowledge Graph")),
            dbc.ModalBody(knowledge_graph_layout),
            dbc.ModalFooter(children=[html.Div(
                "For graphs with more than 500 nodes, only a subset of the nodes is displayed. "
                "The number can be adjusted via the selection list above the graph. "
                "A large number of nodes results in massive performance losses.")])
        ],
        id="modal-kg",
        fullscreen=True,
    ),
    dbc.Modal(
        [
            dbc.ModalHeader(dbc.ModalTitle("Question Graph")),
            dbc.ModalBody(question_graph_layout),
            dbc.ModalFooter(id="question-graph-footer")
        ],
        id="modal-qg",
        fullscreen=True,
    ),
    dbc.Modal(
        [
            dbc.ModalHeader(dbc.ModalTitle("View Export")),
            dbc.ModalBody(view_export_layout),
            dbc.ModalFooter(
                "Select an export with the select item above")
        ],
        id="modal-export",
        fullscreen=True,
    ),
    dbc.Offcanvas(
        children=[
            html.P("Welcome to the question understanding interface, following features are currently supported"),
            html.Ol(
                [
                    html.Li("Selection of a fixed sized set of questions"),
                    html.Li("Visualizing a subset of a knowledge graph, corresponding to the question"),
                    html.Li("Generating a question graph for this question"),
                    html.Li("Editing the generated question graph"),
                    html.Li("Export the question graph to the local filesystem"),
                    html.Li("The exported question graph can be displayed using the view export button"),
                ]

            ),
        ],
        id="help-menu",
        title="Help Menu",
        is_open=False,
        placement="end"
    ),

], style={"height": "100vh", "overflowY": "hidden", "overflowX": "hidden",
          "background": "linear-gradient(to bottom, #66ccff 17%, #ccffff 100%)"})


def get_ranked_labels(question_id, data, node):
    # print("question-id = {}, data ={} and node= {}".format(question_id, data, node))
    if data is None or len(data) != 1:
        return [], ''
    label = data[0]['label']
    # labels = graph_utils.get_ranked_rdfs_labels(question_id, data[0]['label'], node)
    labels = get_list_of_disorder(hostname,username,password)
    if label not in labels:
        labels.insert(0, {'label': label, 'value': label})
    return labels, label


def label_callback(data, value, node):
    regex = "<(.*)><(.*)><(.*)>"
    res = re.match(regex, value)
    if res is not None:
        gr = res.groups()
        qid = gr[0]
        no_selection = data is None or len(data) == 0
        select_disabled = data is None or len(data) != 1
        labels, label = get_ranked_labels(qid, data, node)
        print("labels ={} and label= {}".format(labels, label))
        return labels, label, select_disabled, no_selection


@app.callback(Output('select-label-dropdown', 'options'),
              Output('select-label-dropdown', 'value'),
              Output('select-label-dropdown', 'disabled'),
              Output('delete-button', 'disabled'),
              Input('question-graph', 'selectedNodeData'),
              Input('input-dropdown', 'value'))
def display_selected_node_data(data, value):
    # print("node data ={} and value= {}".format(data, value))
    return label_callback(data, value, True)


@app.callback(Output('select-label-dropdown', 'options'),
              Output('select-label-dropdown', 'value'),
              Output('select-label-dropdown', 'disabled'),
              Output('delete-button', 'disabled'),
              Input('question-graph', 'selectedEdgeData'),
              Input('input-dropdown', 'value')
              )
def display_selected_edge_data(data, value):
    # print("edge data ={} and value= {}".format(data, value))
    return label_callback(data, value, False)


@app.callback(Output('selected-node-id', 'children'),
              Input('knowledge-graph', 'selectedEdgeData'))
def show_edge_id(selected_edge):
    if selected_edge is not None and len(selected_edge) == 1:
        return selected_edge[0]["uri"]
    return ""


@app.callback(Output('selected-node-id', 'children'),
              Input('knowledge-graph', 'selectedNodeData'))
def show_node_id(selected_node):
    if selected_node is not None and len(selected_node) == 1:
        return selected_node[0]["id"]
    return ""


# @app.callback(
#     Output('question-graph', 'elements'),
#     Input('delete-button', 'n_clicks'),
#     State('question-graph', 'selectedEdgeData'),
#     State('question-graph', 'selectedNodeData'),
#     State('question-graph', 'elements'),
# )
# def delete_nodes_edges(n_clicks, edges, nodes, elements):
#     if n_clicks <= 0:
#         return elements
#     if edges is None:
#         edges = []
#     if nodes is None:
#         nodes = []
#     elements_to_remove = edges + nodes
#     ids_to_remove = {ele_data['id'] for ele_data in elements_to_remove}
#     new_elements = [ele for ele in elements if ele['data']['id'] not in ids_to_remove]
#     # print("new elements {}".format(new_elements))
#     return new_elements


@app.callback(
    Output('question-graph', 'elements'),
    # Output('delete-button', 'disabled'),
    Input('select-label-dropdown', 'value'),
    State('question-graph', 'selectedEdgeData'),
    State('question-graph', 'selectedNodeData'),
    State('question-graph', 'elements'),
)
def delete_nodes_edges(value, edges, nodes, elements):
    global data_table_arr
    global update_state_
    global node_or_edge_
    global hostname
    global username
    global password

    if value is None:
        return elements
    if edges is None:
        edges = []
    if nodes is None:
        nodes = []
    elements_to_change = edges + nodes
    if len(elements_to_change) != 1:
        return elements
    id_to_change = elements_to_change[0]['id']
    update_state_ = "true"
    data_table_arr = []
    # print('elements_to_change = {}'.format(elements_to_change))
    for element in elements:
        if element['data']['id'] == id_to_change:
            element['data']['label'] = value
            edge = value
            # print('edge data={}'.format(edge))
            if len(nodes) > 0 and len(edges) == 0:
                edge = ""
            # clear the data table array
            data_table_arr = []
            # print("elements = {}".format(elements))
            source_node = elements[1]["data"]["label"]
            target_node = elements[2]["data"]["target"]
            data = get_query(graph_id_, source_node, target_node, edge)
            result = get_query_result(graph_id_, data, hostname, username, password)
            print("change result= {}".format(result))
            if len(result) != 0:

                for r in result:
                    types = ""
                    if "etiology" in r:
                        types = r['etiology']
                    elif 'medication' in r:
                        types = r['medication']
                    elif 'complaint_duration' in r:
                        types = r['complaint_duration']
                    elif 'comorbidities' in r:
                        types = r['comorbidities']

                    new_data = {
                        'types': types,
                        'total': r['total']
                    }
                    data_table_arr.append(new_data)
            break
    return elements


def create_node_menu_items(elements):
    menu_list = []

    for element in elements:
        data = element['data']
        if 'target' not in data:
            label = data['label']
            id_ = data['id']
            menu_list.append({'label': label, 'value': id_})
    menu_list = sorted(menu_list, key=lambda d: d['label'])
    return menu_list


# @app.callback(
#     Output("modal-add-dialog", "is_open"),
#     Output("from-node-dropdown", "options"),
#     Output("to-node-dropdown", "options"),
#     Input("add-button", "n_clicks"),
#     State('question-graph', 'elements')
# )
# def toggle_modal(n_clicks, elements):
#     menu_list = create_node_menu_items(elements)
#
#     return n_clicks > 0, menu_list, menu_list
#
#
# def add_new_node(n_clicks, elements, new_label, from_options, to_options):
#     if n_clicks > 0:
#         new_id = time.time()
#         new_node = {'id': new_id, 'label': new_label}
#         elements.append({'data': new_node})
#         from_options.append({'value': new_id, 'label': new_label})
#         to_options.append({'value': new_id, 'label': new_label})
#         from_options = sorted(from_options, key=lambda d: d['label'])
#         to_options = sorted(to_options, key=lambda d: d['label'])
#         return elements, from_options, to_options, [new_node]


@app.callback(
    Output('question-graph', 'elements'),
    Output("question-graph", "selectedEdgeData"),
    Input("add-new-edge-button", "n_clicks"),
    State('question-graph', 'elements'),
    State("from-node-dropdown", "value"),
    State("to-node-dropdown", "value"),
    State("new-edge-label-input", "value"),
)
def add_new_edge(n_clicks, elements, from_node_id, to_node_id, edge_label):
    if n_clicks > 0:
        new_id = time.time()
        new_node = {'source': from_node_id, 'target': to_node_id, 'label': edge_label, 'id': new_id}
        elements.append({'data': new_node})
        return elements, [new_node]


# select-nr-of-nodes style
# displayed nodes
# list for select item
def calculate_nr_of_nodes(all_nodes):
    nodes_to_display = all_nodes
    steps = 50
    if all_nodes <= 500:
        return {'width': 300, 'display': 'none'}, nodes_to_display, []
    if all_nodes > 1000:
        steps = 100
    if all_nodes > 2000:
        steps = 150
    current_nr = 0
    nodes_list = []
    while current_nr < all_nodes:
        nodes_list.append({'label': current_nr, 'value': current_nr})
        if current_nr <= 500:
            nodes_to_display = current_nr
        current_nr += steps

    nodes_list.append({'label': all_nodes, 'value': all_nodes})

    return {'width': 300, 'display': 'inherit'}, nodes_to_display, nodes_list


@app.callback(
    Input('input-dropdown', 'value'),
    Output('knowledge-graph', 'elements'),
    Output('knowledge-graph-fallback', 'elements'),
    Output('knowledge-graph', 'style'),
    Output('knowledge-graph-fallback', 'style'),
    Output('question-graph', 'elements'),
    Output('open-kg', 'disabled'),
    Output('open-qg', 'disabled'),
    Output('select-nr-of-nodes', 'style'),
    Output('select-nr-of-nodes', 'value'),
    Output('select-nr-of-nodes', 'options'),
)
def load_question_files(value):
    global graph_triplets_
    global graph_id_
    global graph_
    regex = "<(.*)><(.*)><(.*)>"
    res = re.match(regex, value)
    if res is not None:
        gr = res.groups()
        file = gr[2]
        nr_of_edges, graph_triplets_ = graph_utils.load_file("./resources/" + file)
        graph_id_ = gr[0]
        if graph_id_ == '8':
            graph_ = graph_data.graph_1
        elif graph_id_ == '9':
            graph_ = graph_data.graph_2
        elif graph_id_ == '12':
            graph_ = graph_data.graph_3
        elif graph_id_ == '13':
            graph_ = graph_data.graph_4
        elif graph_id_ == '14':
            graph_ = graph_data.graph_5
        elif graph_id_ == '15':
            graph_ = graph_data.graph_6
        elif graph_id_ == '16':
            graph_ = graph_data.graph_7
        elif graph_id_ == '17':
            graph_ = graph_data.graph_8
        elif graph_id_ == '18':
            graph_ = graph_data.graph_9
        else:
            graph_ = graph_data.graph_10

        # graph_ = generate_question_graph_v2(nlp(gr[1]))

        nodes_select_enabled, nodes_to_display, nodes_list = calculate_nr_of_nodes(nr_of_edges)

        style = {
            "width": "100%",
            "height": "calc(100vh - 150px - 50px)",
        }
        normal_style = dict(style)
        fallback_style = dict(style)
        if nr_of_edges > 500:
            normal_style['display'] = 'none'
        else:
            fallback_style['display'] = 'none'

        knowledge_graph = graph_utils.get_dash_graph(nodes_to_display)
        # knowledge_graph=graph_data.graph_1
        print("knowledge graph= {}".format(knowledge_graph))

        return knowledge_graph, knowledge_graph, normal_style, fallback_style, graph_, \
               False, False, nodes_select_enabled, nodes_to_display, nodes_list


@app.callback(
    Input('select-nr-of-nodes', 'value'),
    State('knowledge-graph', 'elements'),
    Output('knowledge-graph', 'elements'),
    Output('knowledge-graph-fallback', 'elements'),
)
def load_question_files_with_more_nodes(nr_of_nodes, knowledge_graph_elements):
    if knowledge_graph_elements is not None:
        nodes = graph_utils.get_dash_graph(nr_of_nodes)
        return nodes, nodes
    return knowledge_graph_elements, knowledge_graph_elements


@app.callback(
    Output("modal-kg", "is_open"),
    Input("open-kg", "n_clicks")
)
def open_kg(n_clicks):
    return n_clicks > 0


# @app.callback(
#     Output("modal-export", "is_open"),
#     Input("open-view-export", "n_clicks")
# )
# def open_export(n_clicks):
#     return n_clicks > 0


@app.callback(
    Output("modal-qg", "is_open"),
    Output("question-graph-footer", "children"),
    Output("question", "children"),
    Input("open-qg", "n_clicks"),
    Input('input-dropdown', 'value'),

)
def open_qg(n_clicks, value):
    global value_str

    sub_list_question = ["><question_8.nxhd>", "><question_9.nxhd>", "><question_12.nxhd>", "><question_13.nxhd>",
                         "><question_14.nxhd>", "><question_15.nxhd>", "><question_16.nxhd>", "><question_17.nxhd>"]
    sub_list_question_no = ["<8><", "<9><", "<12><", "<13><", "<14><", "<15><", "<16><", "<17><"]

    for sub in sub_list_question:
        if sub in value:
            value_str = value.replace(sub, "")
            break
    for no in sub_list_question_no:
        if no in value_str:
            value_str = value_str.replace(no, "")
            break
    return n_clicks > 0, "", value_str


@app.callback(
    Output("help-menu", "is_open"),
    Input("open-help", "n_clicks")
)
def open_qg(n_clicks):
    return n_clicks > 0


# @app.callback(
#     Output("view-export-graph", "elements"),
#     Input("select-export", "value")
# )
# def generate_export_graph(export_file):
#     edges, _ = graph_utils_export.load_file(export_file)
#
#     return graph_utils_export.get_dash_graph(edges)

# @app.callback(
#     Input('export-button', 'n_clicks'),
#     Output('question-graph-footer', 'children'),
# )
# def export_question_graph(n_clicks):
#     global graph_triplets_
#     global graph_id_
#     global graph_
#     if n_clicks > 0:
#         if graph_id_ is not None and graph_triplets_ is not None and graph_ is not None:
#             res = export_qg_with_kg_annotations(graph_, graph_triplets_, graph_id_)
#             return "Question graph exported to: {}".format(res)
#         return "Something went wrong"


@app.callback(
    Output("modal-answer-dialog", "is_open"),
    Output("data-table", "data"),
    Input('answer-button', 'n_clicks'),

)
def toggle_model(n_clicks):
    print("graph_= {}".format(graph_))
    source_node = graph_[2]["data"]["source"]
    target_node = graph_[2]["data"]["target"]
    edge = graph_[2]["data"]["label"]
    # print("data table length= {}, update= {}".format(len(data_table_arr),update_state_))
    if len(data_table_arr) == 0 and update_state_ == "false":
        if node_or_edge_ == "node":
            edge = ""
        data = get_query(graph_id_, source_node, target_node, edge)

        result = get_query_result(graph_id_, data, hostname, username, password)
        print("result= {}".format(result))
        arr = []
        for r in result:
            types = ""
            if "etiology" in r:
                types = r['etiology']
            elif 'medication' in r:
                types = r['medication']
            elif 'complaint_duration' in r:
                types = r['complaint_duration']
            elif 'comorbidities' in r:
                types = r['comorbidities']

            new_data = {
                'types': types,
                'total': r['total']
            }
            arr.append(new_data)
        return n_clicks > 0, arr
    return n_clicks > 0, data_table_arr


def get_list_of_disorder(hostname, username, password):
    print("host_name= {}, username= {}, password= {}".format(hostname, username, password))
    sparql = SPARQLWrapper(hostname)
    sparql.setCredentials(username, password)
    # sparql.setHTTPAuth(BASIC)
    sparql.setReturnFormat(JSON)

    query = textwrap.dedent("""
    PREFIX :  <http://example.com/base/>  
    select * 
    where{{
        {{
            select distinct ?x 
            where {{
    
                    ?patient a :Patient;
                             :hasSmellDisorder ?x .
            }}
            }}
            UNION
        {{
            select distinct ?x 
            where {{
                    ?patient a :Patient;
                             :hasTasteDisorder ?x .
    
                }}
        }}
            
    }}

                    """)

    sparql.setQuery(query)
    data = []
    ret = sparql.queryAndConvert()
    for r in ret["results"]["bindings"]:
        new_data = {
            'label': r['x']['value'],
            'value': r['x']['value']
        }
        data.append(new_data)
    return data


def get_query(id, source_node, target_node, edge):
    print("source_node = {}, target node= {}, edge= {}".format(source_node, target_node, edge))
    if id == '8':
        query = ""
        query = textwrap.dedent("""
            PREFIX :  <http://example.com/base/> 
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            select  ?etiology (count(?etiology) as ?total) 
            where{{
            select *
            where {{ 
                ?patient a :Patient;
                      :hasSmellDisorder ?smell;
                      :hasEtiology ?etiology .
                 filter(?smell="{0}")   
            }}
            }}
            group by ?etiology
            order by desc(?total) 
                """.format(source_node))
        # print(query)
        return query
    elif id == '9':
        query = ""
        query = textwrap.dedent("""
        PREFIX :  <http://example.com/base/> 
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        select  ?medication (count(?medication) as ?total) 
        where{{
        select *
        where {{ 
            ?patient a :Patient;
                  :hasSmellDisorder ?smell;
                  :takeMedication ?medication .
             filter(?smell="{0}")   
        }}
        }}
        group by ?medication
        order by desc(?total)
        """.format(source_node))
        # print(query)
        return query
    elif id == '12':
        query = ""
        query = textwrap.dedent("""
            PREFIX :  <http://example.com/base/> 
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            select  ?etiology (count(?etiology) as ?total) 
            where{{
            select *
            where {{ 
                ?patient a :Patient;
                      :hasTasteDisorder ?taste;
                      :hasEtiology ?etiology .
                 filter(?taste="{0}")   
            }}
            }}
            group by ?etiology
            order by desc(?total)
               """.format(source_node))
        # print(query)
        return query
    elif id == '13':
        query = ""
        query = textwrap.dedent("""
                PREFIX :  <http://example.com/base/> 
                PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                select  ?medication (count(?medication) as ?total) 
                where{{
                select *
                where {{ 
                    ?patient a :Patient;
                          :hasTasteDisorder ?taste;
                          :takeMedication ?medication .
                     filter(?taste="{0}")   
                }}
                }}
                group by ?medication
                order by desc(?total)
                """.format(source_node))
        return query

    elif id == '14':
        query = ""
        query = textwrap.dedent("""
                PREFIX :  <http://example.com/base/> 
                PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                select  ?comorbidities (count(?comorbidities) as ?total) 
                where{{
                select *
                where {{ 
                    ?patient a :Patient;
                          :hasTasteDisorder ?taste;
                          :hasComorbidities ?comorbidities .
                     filter(?taste="{0}")   
                }}
                }}
                group by ?comorbidities
                order by desc(?total)  
                       """.format(source_node))
        return query
    elif id == '15':
        query = ""
        query = textwrap.dedent("""
                PREFIX :  <http://example.com/base/> 
                PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                select  ?comorbidities (count(?comorbidities) as ?total) 
                where{{
                select *
                where {{ 
                    ?patient a :Patient;
                          :hasSmellDisorder ?smell;
                          :hasComorbidities ?comorbidities .
                     filter(?smell="{0}")   
                }}
                }}
                group by ?comorbidities
                order by desc(?total)
               """.format(source_node))
        return query
    elif id == '16':
        query = ""
        query = textwrap.dedent("""
                PREFIX :  <http://example.com/base/> 
                PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                select  ?complaint_duration (count(?complaint_duration) as ?total) 
                where{{
                        select *
                        where {{ 
                                ?patient a :Patient;
                                         :hasSmellDisorder ?smell;
                                         :hasComplaintDuration ?complaint_duration .
                                filter(?smell="{0}")   
                            }}
                    }}
                group by ?complaint_duration
                order by desc(?total)
               """.format(source_node))
        return query
    elif id == '17':
        query = ""
        query = textwrap.dedent("""
                PREFIX :  <http://example.com/base/> 
                PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                select  ?complaint_duration (count(?complaint_duration) as ?total) 
                where{{
                        select *
                        where {{ 
                                ?patient a :Patient;
                                         :hasTasteDisorder ?taste;
                                         :hasComplaintDuration ?complaint_duration .
                                filter(?taste="{0}")   
                            }}
                    }}
                group by ?complaint_duration
                order by desc(?total)
               """.format(source_node))
        return query
# sparql setting

def get_query_result(id, query, hostname, username, password):
    # sparql setting

    print("host_name= {}, username= {}, password= {}".format(hostname, username, password))
    sparql = SPARQLWrapper(hostname)
    sparql.setCredentials(username, password)
    sparql.setReturnFormat(JSON)

    sparql.setQuery(query)
    data = []
    try:
        ret = sparql.queryAndConvert()
        # header
        # if id == '8':
        #     data.append("Etiology Type")
        # elif id == '9':
        #     data.append("Medication")

        for r in ret["results"]["bindings"]:
            # print("r= {}".format(ret["results"]["bindings"]))
            if id == '8':
                new_data = {
                    'etiology': r["etiology"]["value"],
                    'total': r["total"]["value"],
                }
                data.append(new_data)
            elif id == '9':
                new_data = {
                    'medication': r["medication"]["value"],
                    'total': r["total"]["value"],
                }
                data.append(new_data)
            elif id == '12':
                new_data = {
                    'etiology': r["etiology"]["value"],
                    'total': r["total"]["value"],
                }
                data.append(new_data)
            elif id == '13':
                new_data = {
                    'medication': r["medication"]["value"],
                    'total': r["total"]["value"],
                }
                data.append(new_data)
            elif id == '14':
                new_data = {
                    'comorbidities': r["comorbidities"]["value"],
                    'total': r["total"]["value"],
                }
                data.append(new_data)
            elif id == '15':
                new_data = {
                    'comorbidities': r["comorbidities"]["value"],
                    'total': r["total"]["value"],
                }
                data.append(new_data)
            elif id == '16':
                new_data = {
                    'complaint_duration': r["complaint_duration"]["value"],
                    'total': r["total"]["value"],
                }
                data.append(new_data)
            elif id == '17':
                new_data = {
                    'complaint_duration': r["complaint_duration"]["value"],
                    'total': r["total"]["value"],
                }
                data.append(new_data)
        return data
    except Exception as e:
        print(e)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
    # app.run_server(debug=True)
