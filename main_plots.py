#!usr/bin/python
# -*- coding: utf-8 -*-

import os
from subprocess import call

from Evaluation import PlotConstructor as pc
from Evaluation import TableConstructor as tc
from Evaluation import StatisticsManager as sm
from MetaScripts import global_settings as gs

algo_restriction_reduced = ["EG_X_X", "EGPLUS_X_X", "CMT_X_X", "MT_X_X", "SMS_X_X", "LexM_X_X", "MCSM_X_X"]
algo_restriction_basic = ["EG_X_B", "EGPLUS_X_B", "CMT_X_B", "MT_X_B", "SMS_X_B", "LexM_X_B", "MCSM_X_B"]
set_gen = ["general"]
sets_all = ["general", "planar", "maxdeg", "maxclique"]

def make_plots():
	plot_performance_by_algo_boxplots()
	plot_performance_by_algo_lineplots()
	#plot_performance_by_density()
	#plot_cmp_reduction()
	
def make_tables():
	build_all_tables_detrand_compare()
	build_tables_general_compare()

def plot_cmp_reduction():
	for setname in sets_all:
		for axis in ["TIME", "OUTPUT"]:
			for density in ["dense", "sparse"]:
				if setname == "general" or  density == "sparse":
					pc.performance_plot_analyze_reduction(setname, density, n=20, axis=axis)
				
	
def plot_performance_by_algo_boxplots():
	for setname in sets_all:
		pc.make_boxplots_total(setname, algos=algo_restriction_basic, axis="TIME", type="ABSOLUTE")
		pc.make_boxplots_total(setname, algos=algo_restriction_basic, axis="OUTPUT", type="RP")

def plot_performance_by_algo_lineplots():
	for setname in sets_all:
		for density in ["dense", "sparse"]:
			if density == "dense":
				algo_restriction = algo_restriction_basic
			else:
				algo_restriction = algo_restriction_reduced
			if setname == "general" or  density == "sparse":
				# this is broken 
				#pc.plot_performance_by_algorithm(setname, algos=algo_restriction, axis="TIME", type="ABSOLUTE")
				
				pc.plot_performance_by_algorithm(setname, density_class=density, algos=algo_restriction, axis="OUTPUT", type="RP")

def plot_performance_by_density():
	for setname in sets_all:
		pc.make_performance_plots_all(setname, axis="TIME", type="ABSOLUTE")
		pc.make_performance_plots_all(setname, axis="OUTPUT", type="RP")

def build_all_tables_detrand_compare():
	for setname in set_gen:
		outputfilenames = []
		
		outputfilenames.append(tc.construct_table_compare(
			setname, 
			"dense",
			options_for_n=[20, 40, 60],
			algocodes=["EG", "SMS", "CMT", "EGPLUS", "MCSM"],
			randcodes=["D", "R3", "R5", "R10"],
			axis="OUTPUT",
			type="ABSOLUTE",
			values="MEAN",
			filename_suffix="cmp_rnd",
			colormode="CMP_MCSM",
			min_pterm=50
		))
		
		outputfilenames.append(tc.construct_table_compare(
			setname, 
			"dense",
			options_for_n=[20, 40, 60],
			algocodes=["EG", "SMS", "CMT", "EGPLUS", "MCSM"],
			randcodes=["D", "R3", "R5", "R10"],
			axis="TIME",
			type="ABSOLUTE",
			values="MEAN",
			filename_suffix="cmp_rnd",
			colormode="CMP_MCSM",
			min_pterm=50
		))
		
		outputfilenames.append(tc.construct_table_compare(
			setname, 
			"sparse",
			options_for_n=[20, 40, 60],
			algocodes=["EG", "SMS", "CMT", "EGPLUS", "MCSM"],
			randcodes=["D", "R3", "R5", "R10"],
			axis="OUTPUT",
			type="ABSOLUTE",
			values="MEAN",
			filename_suffix="cmp_rnd",
			colormode="CMP_MCSM",
			min_pterm=50
		))
		
		outputfilenames.append(tc.construct_table_compare(
			setname, 
			"sparse",
			options_for_n=[20, 40, 60],
			algocodes=["EG", "SMS", "CMT", "EGPLUS", "MCSM"],
			randcodes=["D", "R3", "R5", "R10"],
			axis="TIME",
			type="ABSOLUTE",
			values="MEAN",
			filename_suffix="cmp_rnd",
			colormode="CMP_MCSM",
			min_pterm=50
		))
		
		os.chdir("data/eval/random_"+setname+"/tables")
		for tablefile in outputfilenames:
			call(["pdflatex",tablefile+".tex"])
		os.chdir("../../../..")
		
def build_tables_general_compare():
	options_for_n = gs.GRAPH_SIZES
	for setname in sets_all:
		outputfilenames = []
		for density_class in ["dense", "sparse"]:
			if setname == "general" or  density_class == "sparse":
				outputfilenames.append(tc.construct_table_compare(
					setname, 
					density_class,
					options_for_n=options_for_n,
					axis="OUTPUT",
					type="ABSOLUTE",
					values="MEAN"
				))
				outputfilenames.append(tc.construct_table_compare(
					setname, 
					density_class,
					options_for_n=options_for_n,
					axis="OUTPUT",
					type="ABSOLUTE",
					values="VAR"
				))
				outputfilenames.append(tc.construct_table_compare(
					setname, 
					density_class,
					options_for_n=options_for_n,
					axis="TIME",
					type="ABSOLUTE",
					values="MEAN"
				))
				outputfilenames.append(tc.construct_table_compare(
					setname, 
					density_class,
					options_for_n=options_for_n,
					axis="OUTPUT",
					type="ABSOLUTE",
					values="PTERM"
				))
		
		os.chdir("data/eval/random_"+setname+"/tables")
		for tablefile in outputfilenames:
			call(["pdflatex",tablefile+".tex"])
		os.chdir("../../../..")

if __name__ == "__main__":
	make_plots()
	make_tables()
