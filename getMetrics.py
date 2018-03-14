import json
import os


with open('extraction/vms.json.2018-03-12') as json_data:
    vms = json.load(json_data)

metricsvm = []

for vm in vms:
	a = os.popen('az monitor metrics list --time-grain "PT1M" --metric-names "Percentage CPU" --resource "' + vm['id'] + '"').read()
	metricvm = json.loads(a)
	#metricvm[0]['date'] = "2018-03-12"
	#metricvm['']

	metricsvm.extend(metricvm)

	with open('metrics.json', 'w') as outfile:
		json.dump(metricsvm, outfile)

