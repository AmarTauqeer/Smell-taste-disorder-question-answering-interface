from pathlib import PurePosixPath
from urllib.parse import unquote, urlparse
from layout.graph_utils import Graph
from thefuzz import fuzz
# import spacy
import os

# nlp = spacy.load("en_core_web_sm")


def extract_verb_constructions_from_sent(doc):
    verb_constructions = []
    root_verb = False
    root_verb_tok = None
    contains_no_verbs = True
    for tok in doc:
        if tok.dep_ == 'ROOT' and tok.pos_ == 'VERB':
            print("Root is verb")
            root_verb = True
            root_verb_tok = tok
        if tok.pos_ == 'VERB':
            print("Contains verbs")
            contains_no_verbs = False
    if root_verb:
        triple = [None, None, None, root_verb_tok.text, None]
        for ch in root_verb_tok.children:
            if ch.pos_ == 'AUX':
                triple[0] = ch.text
            if ch.dep_ == 'auxpass':
                triple[2] = ch.text
            if ch.dep_ == 'prep':
                triple[4] = ch.text
        triple = list(filter(lambda a: a != None, triple))
        verb_constructions.append((triple, root_verb_tok.text))
    else:
        if contains_no_verbs:
            print("No Verbs Looking for AUX")
            for tok in doc:
                if tok.pos_ == 'AUX':
                    triple = [tok.text, None, None, None]
                    for ch in tok.children:
                        if ch.dep_ == 'auxpass':
                            triple[1] = ch.text
                        if ch.dep_ == 'prep':
                            triple[2] = ch.text
                        if ch.dep_ == 'advmod':
                            triple[3] = ch.text
                    triple = list(filter(lambda a: a != None, triple))
                    verb_constructions.append((triple, tok.text))
        else:
            print("Looking for verbs")
            for tok in doc:
                if tok.pos_ == 'VERB':
                    triple = [None, None, None, root_verb_tok.text, None]
                    for ch in root_verb_tok.children:
                        if ch.pos_ == 'AUX':
                            triple[0] = ch.text
                        if ch.dep_ == 'auxpass':
                            triple[2] = ch.text
                        if ch.dep_ == 'prep':
                            triple[4] = ch.text
                        if ch.dep_ == 'advmod':
                            triple[3] = ch.text
                    triple = list(filter(lambda a: a != None, triple))
                    verb_constructions.append((triple,tok.text))
    return verb_constructions


def construct_linear_sent_graph(doc):
    lg = []
    for token in doc:
        if not token.pos_ == 'PUNCT':
            lg.append(token.text)
    return lg


def construct_entities_list(doc):
    entities_str_lab = []
    for ent in doc.ents:
        l = ent.text.split(" ")
        entities_str_lab.append((l, l[0], ent.label_))
    return entities_str_lab


def get_noun_chunk_list(doc):
    chunk_root_list = []
    for chunk in doc.noun_chunks:
        l = chunk.text.split(" ")
        chunk_root_list.append((l, l[0]))
    return chunk_root_list


def merge_items(linear_graph, item_list, merge_root):
    new_graph = []
    found_root = False
    for i, n in enumerate(linear_graph):
        if n == merge_root:
            if len(item_list) != 1:
                if (i - 1 != 0 and linear_graph[i-1] in item_list) or (i+1 != len(linear_graph) and linear_graph[i+1] in item_list):
                    new_graph.append(" ".join(item_list))
                    found_root = True
                    continue
            else:
                new_graph.append(" ".join(item_list))
                found_root = True
                continue
        if n not in item_list or (found_root and n == merge_root):
            new_graph.append(n)
    return new_graph


def filter_items(linear_graph, item_list, edge_placeholder_text):
    new_graph = []
    for n in linear_graph:
        if n == edge_placeholder_text:
            new_graph.append(("EDGE", " ".join(item_list)))
        if n not in item_list:
            new_graph.append(n)
    if type(new_graph[-1]) == tuple:
        new_graph.append(new_graph.pop(0))
    return new_graph


def generate_dash_graph_from_linear(linear_graph):
    g = Graph()
    prev_node = None
    prev_placeholder_edge = None
    for n in linear_graph:
        if type(n) == tuple:
            prev_placeholder_edge = n[1]
        else:
            g.add_node(n, n)
            if prev_node is not None:
                if prev_placeholder_edge is not None:
                    g.add_edge((n,prev_node), prev_placeholder_edge)
                    prev_placeholder_edge = None
                else:
                    g.add_edge((n, prev_node), "")
            prev_node = n
    nodes=[]
    # print(nodes.append({'data': {'source': 'http://example/base/102090', 'target': 'http://example/base/Disorder', 'label': 'hasDisorder', 'uri': 'http://example/base/hasDisorder'}}))
    # print(nodes)
    return g.get_dash_graph(len(g.node_neighbors.keys()))


def extract_particles_and_adpositions_from_sent(doc):
    p_adp_list = []
    for tok in doc:
        if tok.pos_ == 'PART' or tok.pos_ == 'ADP':
            p_adp_list.append(tok.text)
    return p_adp_list


def generate_question_graph_v2(doc):
    linear_graph = construct_linear_sent_graph(doc)
    entities_str_lab = construct_entities_list(doc)
    print(entities_str_lab)
    chunk_root_list = get_noun_chunk_list(doc)
    print(chunk_root_list)
    verb_constructions = extract_verb_constructions_from_sent(doc)
    print(verb_constructions)
    part_adposition_list = extract_particles_and_adpositions_from_sent(doc)
    print(part_adposition_list)
    for ent in entities_str_lab:
        linear_graph = merge_items(linear_graph, ent[0], ent[1])
    for chunk in chunk_root_list:
        linear_graph = merge_items(linear_graph, chunk[0], chunk[1])
    for v in verb_constructions:
        linear_graph = filter_items(linear_graph, v[0], v[1])
    for p in part_adposition_list:
        linear_graph = filter_items(linear_graph, [p], p)
    r = generate_dash_graph_from_linear(linear_graph)
    return r


def convert_uri_to_string_label(uri):
    url_path = PurePosixPath(unquote(urlparse(uri).path))
    string = url_path.name
    if type(string) != str:
        string = str(string)
    for c in ["_", "-", "#", "(", ")", "<", ">"]:
        if c in string:
            string = string.replace(c, " ")
    return string


def write_uri_list_to_file(uri_list, file_id):
    print(uri_list)
    file_name = "qg_output_{}.nxhd".format(file_id)
    file_dir = os.path.dirname(os.path.realpath('__file__'))
    file_path = os.path.join(file_dir, '..\\output\\')
    file_path = file_path + file_name
    file_path = file_path.replace("\\new\\..\\", "\\")
    f = open(file_path, "w")
    for l in uri_list:
        total_str = ""
        for e in l:
            total_str += "{}{}{}\t".format("<", e, ">")
        total_str = total_str.rstrip()
        total_str += "\n"
        f.write(total_str)
    f.close()
    return file_path


def export_qg_with_kg_annotations(linear_qg, rdf_triples, file_id):
    potential_uri_list = []
    for s in linear_qg:
        label = s['data']['label']
        if label == '':
            continue
        for k in rdf_triples:
            s = convert_uri_to_string_label(k[0])
            p = convert_uri_to_string_label(k[1])
            o = convert_uri_to_string_label(k[2])
            f_s = fuzz.ratio(label, s)
            f_p = fuzz.ratio(label, p)
            f_o = fuzz.ratio(label, o)
            if f_s > 50 or f_p > 50 or f_o > 50:
                potential_uri_list.append(((s,k[0]),(p,k[1]),(o,k[2])))
    kg_qg_list = []
    for pot in potential_uri_list:
        s = pot[0]
        p = pot[1]
        o = pot[2]
        linear_triple = []
        best_matching_triple = None
        best_matching_triple_score = 0.45
        ignore_first_node = True
        for n in linear_qg:
            if n['data']['label'] == '':
                continue
            linear_triple.append(n['data']['label'])
            if len(linear_triple) == 3:
                if not ignore_first_node:
                    f_t = (fuzz.ratio(linear_triple[0], s[0]) + fuzz.ratio(linear_triple[1], p[0]) + fuzz.ratio(linear_triple[2], o[0]))/300.0
                else:
                    f_t = (fuzz.ratio(linear_triple[1], p[0]) + fuzz.ratio(linear_triple[2], o[0]))/200.0
                    ignore_first_node = False
                if f_t > best_matching_triple_score:
                    best_matching_triple_score = f_t
                    best_matching_triple = [s[1], p[1], o[1]]
                linear_triple.pop(0)
        if best_matching_triple is None or len(best_matching_triple) != 3:
            continue
        else:
            kg_qg_list.append(best_matching_triple)
    print(len(potential_uri_list))
    print(len(kg_qg_list))
    return write_uri_list_to_file(kg_qg_list, file_id)


def export_v2(elements, file_id):
    nodes = {}
    edges = []

    urls = []

    for element in elements:
        data = element['data']
        if 'source' in data:
            edges.append(data)
        else:
            nodes[data['id']] = data

    prefix = "http://dbpedia.org/resource/"
    for edge in edges:
        subj = edge['target']
        pred = edge['source']
        obj = edge['label']

        subj = subj.replace(" ", "_")
        pred = pred.replace(" ", "_")
        obj = obj.replace(" ", "_")

        subj = prefix + subj.capitalize()
        pred = prefix + pred.capitalize()
        obj = prefix + obj.capitalize()

        urls.append([subj, obj, pred])
    return write_uri_list_to_file(urls, file_id)







#print(generate_question_graph_v2(nlp("Which electronics companies were founded in Beijing?"), []))
#generate_question_graph_v2(nlp("What is the largest country in the world ? "))
#generate_question_graph_v2(nlp("How many people live in Poland ?"))
#generate_question_graph_v2(nlp("Who wrote Harry Potter ? "))
