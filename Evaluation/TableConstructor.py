#!usr/bin/python
# -*- coding: utf-8 -*-

import numpy as np
import json
import csv
import re
import os

try:
	import tkinter
except ImportError:
	import matplotlib
	matplotlib.use('agg')
	import matplotlib.pyplot as plt
else:
	import matplotlib.pyplot as plt
	import matplotlib.lines as mlines

from Evaluation import GraphDataOrganizer as gdo
from Evaluation import ExperimentManager as em
from Evaluation import StatisticsManager as sm
from MetaScripts import meta
from MetaScripts import global_settings as gs

def init_texoutputstring():
	texoutputstring = ""
	with open("tex_template.txt", "r") as tex_template:
		for line in tex_template:
			texoutputstring += line
	return texoutputstring

def construct_output_table_alldata(columns, dataset, outputfilenamesuffix=""):
	'''
	Constructs a tex-file containing a table that contains the statistics
	computed by the method "compute_statistics" from StatisticsManager
	'''
	# sort dataset:
	sorteddataset = sorted(dataset, key=lambda data: (data["avg n"], data["graph id"], data["algorithm"], data["repeats"], data["reduced"]))

	texoutputstring = init_texoutputstring()
	tabulardefline = "\\begin{longtable}{"
	for i in range(len(columns)):
		tabulardefline += "c"
	tabulardefline += "}"
	texoutputstring += tabulardefline+"\n"

	tabheadline = columns[0]
	for i in range(1,len(columns)):
		tabheadline += " & "+columns[i]
	tabheadline += " \\\\ \\hline \n"
	texoutputstring += tabheadline
	#all_graph_ids = [key for key in dataset if not key == "algo"]
	data_keys = [key for key in columns] #if not key == "algorithm" and not key == "graph id"]

	non_numeric_data_keys = ["algorithm", "graph id", "reduced"]
	string_data_keys = ["algorithm", "reduced"]
	might_be_string_data_keys = ["mean time", "var time", "moo", "voo", "mmo", "mvo"]

	for data in sorteddataset:
		rowstring = "\\verb+"+data["graph id"]+ "+"
		#rowstring = "\\verb+"+data["algo"] + "+ & \\verb+" + data["graph_id"] + "+"
		for data_key in data_keys:
			#print(data_key +": "+str(data[data_key]))
			if data_key not in non_numeric_data_keys and not isinstance(data[data_key], str):
				if data_key ==  "mean time":
					precision = 4
					formatstring = "${0:.4f}$"
				else:
					precision = 2
					formatstring = "${0:.2f}$"
				rowstring += " & "+formatstring.format(round(data[data_key],precision))
			elif data_key in string_data_keys+might_be_string_data_keys:
				rowstring += " & \\verb+"+data[data_key]+"+"
		texoutputstring += rowstring+"\\\\\n"
	texoutputstring += "\\end{longtable}\n"
	texoutputstring += "\\end{document}\n"

	outputfilename = "table_total_"+outputfilenamesuffix+".tex"
	
	with open(outputfilename, "w") as tex_output:
		tex_output.write(texoutputstring)
		
def construct_table_compare_randomized(graphclass, density_class, outputfilenamesuffix=""):
	'''
	Constructs a table that compares the results of randomized and deterministic runs
	'''
	# init data:
	data = {}
	for algo in ["EG", "SMS", "CMT", "EGPLUS"]:
		data[algo] = {}
		data[algo]["D"] = sm.load_data(graphclass, density_class, d=5, c=4, algocode=algo, keep_nulls=True, cutoff_at_timelimit=True)
		data[algo]["R3"] = sm.load_data(graphclass, density_class, d=5, c=4, algocode=algo, randomized=True, rand_repetitions=3, keep_nulls=False, cutoff_at_timelimit=True)
		data[algo]["R5"] = sm.load_data(graphclass, density_class, d=5, c=4, algocode=algo, randomized=True, rand_repetitions=5, keep_nulls=False, cutoff_at_timelimit=True)
		data[algo]["R10"] = sm.load_data(graphclass, density_class, d=5, c=4, algocode=algo, randomized=True, rand_repetitions=10, keep_nulls=False, cutoff_at_timelimit=True)
		
	data["MCSM"] = sm.load_data(graphclass, density_class, d=5, c=4, algocode="MCSM", keep_nulls=True, cutoff_at_timelimit=True)
		
	texoutputstring = init_texoutputstring()
	tabulardefline = ""
	tabulartitleline_1 = ""
	if (density_class == "dense" and graphclass == "general") or density_class == "sparse":
		tabulardefline = "\\begin{longtable}{l||ccc|ccc|ccc}\n"
		tabulartitleline_1 = "n & \multicolumn{3}{|c}{20} & \multicolumn{3}{|c}{60} & \multicolumn{3}{|c}{100} \\\\ \n"
	else:
		tabulardefline = "\\begin{longtable}{l||cc|cc|cc}\n"
		tabulartitleline_1 = "n & \multicolumn{2}{|c}{20} & \multicolumn{2}{|c}{60} & \multicolumn{2}{|c}{100} \\\\ \n"
	texoutputstring += tabulardefline
	texoutputstring += tabulartitleline_1
	
	tabulartitleline_2 = ""
	if density_class == "dense":
		options_for_relm = [-1]
		if graphclass == "general":
			options_for_p = [0.1, 0.5, 0.8]
			tabulartitleline_2 = "p & 0.1 & 0.5 & 0.8 & 0.1 & 0.5 & 0.8 & 0.1 & 0.5 & 0.8 \\\\ \\hline \\hline \n"
		else:
			options_for_p = [0.1, 0.5]
			tabulartitleline_2 = "p & 0.1 & 0.5 & 0.1 & 0.5 & 0.1 & 0.5 \\\\ \\hline \\hline \n"
	else:
		options_for_p = [-1]
		options_for_relm = [1.5, 2.0, 2.5]
		tabulartitleline_2 = "p & 1.5 & 2.0 & 2.5 & 1.5 & 2.0 & 2.5 & 1.5 & 2.0 & 2.5 \\\\ \\hline \\hline \n"
	texoutputstring += tabulartitleline_2
	
	options_for_n = [20, 60, 100]
	if graphclass == "maxdeg":
		options_for_d = [5]
	else:
		options_for_d = [-1]
		
	if graphclass == "maxclique":
		options_for_c = [4]
	else:
		options_for_c = [-1]
	
	formatstring = "${0:.2f}$"
	for algo in ["EG", "SMS", "CMT", "EGPLUS"]:
		algosetsting = ""
		for set in ["D", "R3", "R5", "R10"]:
			rowdata = []
			label = algo+" "+set
			for n in options_for_n:
				for p in options_for_p:
					for rel_m in options_for_relm:
						for d in options_for_d:
							for c in options_for_c:
								thisdata = data[algo][set][n][p][rel_m][d][c][density_class]
								if len(thisdata) > 0:
									mean = np.mean(thisdata)
									if mean > 0:
										rowdata.append(formatstring.format(round(mean,2)))
									else:
										rowdata.append("N/A")
								else:
									rowdata.append("N/A")
								
			algosetsting += label+" &"+" & ".join(rowdata)+" \\\\"
			if not set == "R10":
				algosetsting += "\n"
		texoutputstring += algosetsting+"\\hline \n"
	
	rowdata = []
	for n in options_for_n:
		for p in options_for_p:
			for rel_m in options_for_relm:
				for d in options_for_d:
					for c in options_for_c:
						thisdata = data["MCSM"][n][p][rel_m][d][c][density_class]
						if len(thisdata) > 0:
							mean = np.mean(thisdata)
							rowdata.append(formatstring.format(round(mean,2)))
						else:
							rowdata.append("N/A")
						
	texoutputstring += "MCSM &"+" & ".join(rowdata)+" \\\\ \n"
			
	texoutputstring += "\\end{longtable}\n"
	texoutputstring += "\\end{document}\n"
	
	outputfilename = "table_cmprand_"+graphclass+"_"+density_class
	if not outputfilenamesuffix == "":
		outputfilename += "_"+outputfilenamesuffix
	#print (texoutputstring)
	
	with open(outputfilename+".tex", "w") as tex_output:
		tex_output.write(texoutputstring)