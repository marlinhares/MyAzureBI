import json
from elasticsearch import Elasticsearch


def loadJsonExport(filename, index_name, doc_type_name):
    with open(filename) as json_data:
        dicts = json.load(json_data)

    loadElastic(dicts, index_name, doc_type_name)


def loadElastic(dicts, index_name, doc_type_name):
    es = Elasticsearch([{'host': 'localhost', 'port': 9200}])
    for dic in dicts:

        try:
            if(dic['subscription']['name'] == 'Microsoft Azure Sponsorship(Converted to EA)' and dic['name']=='armazem'): continue
        except:
            pass

        #print dic['subscription']['name'] + ' - ' + dic['name']
        es.index(index=index_name, doc_type=doc_type_name, body=dic, request_timeout=120)


print "import subscriptions"
loadJsonExport('subs.json', 'subscription', 'subscription')

print "import disks"
loadJsonExport('disks.json', 'disk', 'disk')

print "import sas"
loadJsonExport('sas.json', 'sas', 'sas')

print "import vms"
loadJsonExport('vms.json', 'vm', 'vm')
