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

def construct_output_table_alldata(graphclass, columns, dataset, outputfilenamesuffix=""):
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
	
	if not outputfilenamesuffix == "":
		outputfilename = "table_total_"+outputfilenamesuffix+".tex"
	else:
		outputfilename = "table_stats"+".tex"
		
	tablesdir = "data/eval/random_"+graphclass+"/tables"
	if not os.path.exists(tablesdir):
		os.mkdir(tablesdir)
		
	with open(tablesdir+"/"+outputfilename, "w") as tex_output:
		tex_output.write(texoutputstring)
		
def construct_table_compare_randomized(graphclass, density_class, outputfilenamesuffix="", axis="OUTPUT"):
	'''
	Constructs a table that compares the results of randomized and deterministic runs
	'''
	# init data:
	data = {}
	for algo in ["EG", "SMS", "CMT", "EGPLUS"]:
		data[algo] = {}
		data[algo]["D"] = sm.load_data(graphclass, density_class, d=5, c=4, algocode=algo, axis=axis, reduced=True, keep_nulls=True, cutoff_at_timelimit=True)
		data[algo]["R3"] = sm.load_data(graphclass, density_class, d=5, c=4, algocode=algo, axis=axis, reduced=True, randomized=True, rand_repetitions=3, keep_nulls=False, cutoff_at_timelimit=True)
		data[algo]["R5"] = sm.load_data(graphclass, density_class, d=5, c=4, algocode=algo, axis=axis, reduced=True, randomized=True, rand_repetitions=5, keep_nulls=False, cutoff_at_timelimit=True)
		data[algo]["R10"] = sm.load_data(graphclass, density_class, d=5, c=4, algocode=algo, axis=axis, reduced=True, randomized=True, rand_repetitions=10, keep_nulls=False, cutoff_at_timelimit=True)
		
	data["MCSM"] = sm.load_data(graphclass, density_class, d=5, c=4, algocode="MCSM", axis=axis, reduced=True, keep_nulls=True, cutoff_at_timelimit=True)
		
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
		tabulartitleline_2 = "$\\frac{m}{n}$ & 1.5 & 2.0 & 2.5 & 1.5 & 2.0 & 2.5 & 1.5 & 2.0 & 2.5 \\\\ \\hline \\hline \n"
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
								comparedata = data["MCSM"][n][p][rel_m][d][c][density_class]
								if len(comparedata) > 0:
									cmpmean = np.mean(comparedata)
								else:
									cmpmean = -1
								if len(thisdata) > 0:
									mean = np.mean(thisdata)
									if mean > 0:
										datatext = formatstring.format(round(mean,2))
									else:
										datatext = "N/A"
								else:
									datatext = "N/A"
									
								if datatext == "N/A":
									if cmpmean > 0:
										rowdata.append("\\cellcolor{red!30}"+datatext)
									else:
										rowdata.append("\\cellcolor{blue!30}"+datatext)
								elif axis == "TIME" and mean >= gs.TIMELIMIT:
									rowdata.append("\\cellcolor{red!30}"+datatext)
								else:
									if axis == "OUTPUT" and (cmpmean < 0 or mean < 0.9*cmpmean):
										rowdata.append("\\cellcolor{blue!30}"+datatext)
									elif mean < cmpmean:
										rowdata.append("\\cellcolor{green!30}"+datatext)
									elif axis == "OUTPUT" and mean < 1.1*cmpmean:
										rowdata.append("\\cellcolor{yellow!30}"+datatext)
									else:
										rowdata.append("\\cellcolor{red!30}"+datatext)
								
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
	
	outputfilename = "table_cmprand_"+graphclass+"_"+density_class+"_"+axis
	if not outputfilenamesuffix == "":
		outputfilename += "_"+outputfilenamesuffix
	#print (texoutputstring)
	
	tablesdir = "data/eval/random_"+graphclass+"/tables"
	if not os.path.exists(tablesdir):
		os.mkdir(tablesdir)
		
	with open(tablesdir+"/"+outputfilename+".tex", "w") as tex_output:
		tex_output.write(texoutputstring)
	return outputfilename

def construct_table_compare(graphclass, density_class, algocodes=None, randcodes=None, options_for_n=None, options_for_p=None, options_for_relm=None, filename_suffix="", axis="OUTPUT", type="ABSOLUTE", values="MEAN"):
	'''
	General method to construct tables to compare and evaluate algorithm output
	'''
	if algocodes == None:
		algocodes = ["MT", "EG", "SMS", "CMT", "EGPLUS", "LexM", "MCSM"]
	if randcodes == None:
		randcodes = ["D", "R10"]
	if graphclass == "maxdeg":
		options_for_d = [5]
	else:
		options_for_d = [-1]
	if graphclass == "maxclique":
		options_for_c = [4]
	else:
		options_for_c = [-1]

	if options_for_n == None:
		options_for_n = [20, 60, 100]
	if options_for_p == None:
		if graphclass == "general":
			options_for_p = [0.1, 0.5, 0.8]
		else:
			options_for_p = [0.1, 0.5]
	if options_for_relm == None:
		options_for_relm = [1.5, 2.0, 2.5]
		
	if density_class == "dense":
		reduced = False
	else:
		reduced = True
		
	data = {}
	for algo in algocodes:
		data[algo] = {}
		for r in randcodes:
			if r == "D":
				data[algo][r] = sm.load_data(graphclass, density_class, d=5, c=4, algocode=algo, axis=axis, reduced=reduced, keep_nulls=False, cutoff_at_timelimit=True)
			elif algo in ["EG", "SMS", "CMT", "EGPLUS"]:
				rr = int(r[1:])
				data[algo][r] = sm.load_data(graphclass, density_class, d=5, c=4, algocode=algo, axis=axis, reduced=reduced, keep_nulls=False, randomized=True, rand_repetitions=rr, cutoff_at_timelimit=True)

	#print ([algo+": "+r for r in data[algo] for algo in data])
	#print (data[algocodes[0]][randcodes[0]])
				
	texoutputstring = init_texoutputstring()
	puretexstring = ""
	tabulardefline = ""
	tabulartitleline_1 = ""
	if density_class == "dense":
		tabulardefline = "\\begin{longtable}{l||"
		for n in options_for_n:
			for p in options_for_p:
				tabulardefline += "c"
			tabulardefline += "|"
		tabulardefline += "}\n"
		tabulartitleline_1 = "n"
		for n in options_for_n:
			tabulartitleline_1 += " & \multicolumn{"+str(len(options_for_p))+"}{c|}{"+str(n)+"}"
		tabulartitleline_1 += " \\\\ \n"
	else:
		tabulardefline = "\\begin{longtable}{l||"
		for n in options_for_n:
			for rm in options_for_relm:
				tabulardefline += "c"
			tabulardefline += "|"
		tabulardefline += "}\n"
		tabulartitleline_1 = "n"
		for n in options_for_n:
			tabulartitleline_1 += " & \multicolumn{"+str(len(options_for_relm))+"}{c|}{"+str(n)+"}"
		tabulartitleline_1 += " \\\\ \n"
	texoutputstring += tabulardefline
	texoutputstring += tabulartitleline_1
	puretexstring += tabulardefline.replace("longtable", "tabular")
	puretexstring += tabulartitleline_1
	
	tabulartitleline_2 = ""
	if density_class == "dense":
		options_for_relm = [-1]
		tabulartitleline_2 = "p"
		for n in options_for_n:
			for p in options_for_p:
				tabulartitleline_2 += " & "+str(p)
		tabulartitleline_2 += " \\\\ \\hline \\hline \n"
	else:
		options_for_p = [-1]
		tabulartitleline_2 = "$\\frac{m}{n}$"
		for n in options_for_n:
			for rm in options_for_relm:
				tabulartitleline_2 += " & "+str(rm)
		tabulartitleline_2 += " \\\\ \\hline \\hline \n"
	texoutputstring += tabulartitleline_2
	puretexstring += tabulartitleline_2

	formatstring_2 = "${0:.2f}$"
	formatstring_1 = "${0:.1f}$"
	formatstring_0 = "${0:.0f}$"
	for algo in algocodes:
		algosetstring = ""
		for r_set in randcodes:
			if not "R" in r_set or algo in ["EG", "SMS", "CMT", "EGPLUS"]:
				rowdata = []
				label = algo+" "+r_set
				for n in options_for_n:
					for p in options_for_p:
						for rel_m in options_for_relm:
							for d in options_for_d:
								for c in options_for_c:
									thisdatalist = data[algo][r_set][n][p][rel_m][d][c][density_class]
									if axis == "TIME":
										pterm = len([d for d in thisdatalist if d < gs.TIMELIMIT and d > 0])
									else:
										pterm = len(thisdatalist)
									if len(thisdatalist) > 0:
										if values == "MEAN":
											thisdata = np.mean(thisdatalist)
										elif values == "VAR":
											thisdata = np.var(thisdatalist)
										elif values == "PTERM":
											thisdata = pterm
											
										if thisdata >= 0:
											if not values == "PTERM":
												if thisdata >= 100:
													datatext = formatstring_0.format(round(thisdata,0))
												elif thisdata >= 10:
													datatext = formatstring_1.format(round(thisdata,1))
												else:
													datatext = formatstring_2.format(round(thisdata,2))
											else:
												datatext = str(pterm)
										else:
											datatext = "N/A"
									elif values == "PTERM":
										thisdata = 0
										datatext = "0"
									else:
										datatext = "N/A"
									
									if pterm == 0:
										rowdata.append("\\cellcolor{red!30}"+datatext)
									elif pterm < 50:
										rowdata.append("\\cellcolor{orange!30}"+datatext)
									elif pterm < 80:
										rowdata.append("\\cellcolor{yellow!30}"+datatext)
									elif pterm < 100:
										rowdata.append("\\cellcolor{green!30}"+datatext)
									else:
										rowdata.append("\\cellcolor{blue!30}"+datatext)
									
				algosetstring += label+" &"+" & ".join(rowdata)+" \\\\"
				if not r_set == randcodes[-1]:
					algosetstring += "\n"
		texoutputstring += algosetstring+"\\hline \n"
		puretexstring += algosetstring+"\\hline \n"
			
	texoutputstring += "\\end{longtable}\n"
	texoutputstring += "\\end{document}\n"
	puretexstring += "\\end{tabular}\n"
	
	outputfilename = "table_cmp_"+graphclass+"_"+density_class+"_"+axis+"_"+type+"_"+values
	if not filename_suffix == "":
		outputfilename += "_"+filename_suffix
	#print (texoutputstring)
	
	tablesdir = "data/eval/random_"+graphclass+"/tables"
	if not os.path.exists(tablesdir):
		os.mkdir(tablesdir)
		
	with open(tablesdir+"/"+outputfilename+".tex", "w") as tex_output:
		tex_output.write(texoutputstring)
		
	with open(tablesdir+"/puretex_"+outputfilename+".tex", "w") as tex_output:
		tex_output.write(puretexstring)
		
	return outputfilename