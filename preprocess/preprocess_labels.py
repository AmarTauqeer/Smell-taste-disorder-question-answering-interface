import json
import re
from time import sleep

from SPARQLWrapper import SPARQLWrapper, JSON
from tqdm import trange


def process_labels(uris):
    nr_batches = len(uris)
    labels = set()
    for i in trange(nr_batches):
        batch = uris[i]
        sparql_uris = ', '.join(str(e) for e in batch)

        query = base_query.replace('URIS_REPLACE', sparql_uris)

        sparql.setQuery(query)
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()
        for res in results['results']['bindings']:
            label = res['label']['value']
            labels.add(label)
        sleep(10)
    return labels


if __name__ == '__main__':
    question_ids = [24] # 22, 24
    regex = "(<.*>)\s(<.*>)\s(<.*>)"
    sparql = SPARQLWrapper("http://dbpedia.org/sparql")

    base_query = """
                        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                        SELECT ?uri ?label {
                        ?uri rdfs:label ?label
                        FILTER (?uri IN (URIS_REPLACE))
                        FILTER (lang(?label) = 'en')
                        } 
                    """

    for i in trange(len(question_ids)):
        qid = question_ids[i]
        qraph_file = "../resources/question_" + str(qid) + ".nxhd"
        node_uris = set()
        edge_uris = set()
        file = open(qraph_file, 'r', encoding='utf8')
        lines = file.readlines()
        for line in lines:
            res = re.match(regex, line)
            if res is not None:
                gr = res.groups()
                subject = gr[0]
                pred = gr[1]
                obj = gr[2]
                if subject.startswith("<http://dbpedia.org/"):
                    node_uris.add(subject)
                if pred.startswith("<http://dbpedia.org/"):
                    edge_uris.add(pred)
                if obj.startswith("<http://dbpedia.org/"):
                    node_uris.add(obj)
        n = 50
        node_uris = list(node_uris)
        edge_uris = list(edge_uris)
        node_batches = [node_uris[i:i + n] for i in range(0, len(node_uris), n)]
        edge_batches = [edge_uris[i:i + n] for i in range(0, len(edge_uris), n)]
        edge_labels = process_labels(edge_batches)
        node_labels = process_labels(node_batches)
        j = {"node_labels": list(node_labels), "edge_labels": list(edge_labels)}
        with open('../resources/question_labels_' + str(qid) + '.json', 'w', encoding='utf8') as json_d:
            json.dump(j, json_d)
        sleep(20)
