import json
from elasticsearch import Elasticsearch


def loadJsonExport(filename, index_name, doc_type_name):
    with open(filename) as json_data:
        dicts = json.load(json_data)

    loadElastic(dicts, index_name, doc_type_name)


def loadElastic(dicts, index_name, doc_type_name):
    es = Elasticsearch([{'host': 'localhost', 'port': 9200}])
    for dic in dicts:
        if(dic['name']=='Microsoft Azure Sponsorship(Converted to EA)'): continue
        es.index(index=index_name, doc_type=doc_type_name, body=dic, request_timeout=60)


print "import metrics"
loadJsonExport('metrics.json', 'metrics', 'metrics')
