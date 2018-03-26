import json


def adjustDic(dest, key, value, novo):

	for d in dest:
		if(d[key] == value):
			d['tamanho'] = d['tamanho'] + novo['tamanho']
			break


	dest.extend([novo])




filename = "/home/marcelo/projetosGithub/tmpextraction/sas.json"

with open(filename) as json_data:
    dicionario = json.load(json_data)

dicdest = []

for sa in dicionario:
	for c in sa['containers']:
		for b in c['blobs']:			
			res = {'name': b['name'], 'tamanho': b['properties']['contentLength']}
			dicdest.extend([res])


newlist = sorted(dicdest, key=lambda k: k['tamanho'], reverse=True) 

for l in newlist:
	print l['tamanho'] / 1024 / 1024 / 1024, l['name']

