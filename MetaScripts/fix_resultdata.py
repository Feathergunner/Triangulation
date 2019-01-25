import os
import re
import run_time_eval as rte

dir = "data/eval/random"
for file in os.listdir(dir+"/results"):
	if ".json" in file:
		filename = re.split(r'\.', file)[0]
		evaldata = rte.load_evaldata_from_json(dir, filename)
		rte.store_results_json(evaldata, dir+"/results/"+filename)
		rte.store_results_csv(evaldata, dir+"/results/"+filename)