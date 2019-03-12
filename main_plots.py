#!usr/bin/python
# -*- coding: utf-8 -*-

from Evaluation import PlotConstructor as pc
from Evaluation import TableConstructor as tc
from Evaluation import StatisticsManager as sm
import os
from subprocess import call

algo_restriction = ["EG_X_X"]#, "EGPLUS_X_X", "CMT_X_X", "MT_X_X", "SMS_X_X", "LexM_X_X", "MCSM_X_X"]

def make_plots():
	plot_performance_by_algo_boxplots()
	plot_performance_by_algo_lineplots()
	plot_performance_by_density()

def plot_performance_by_algo_boxplots():
	for setname in ["general", "planar", "maxdeg", "maxclique"]:
		pc.make_boxplots_total(setname, algos=algo_restriction, axis="TIME", type="ABSOLUTE")
		pc.make_boxplots_total(setname, algos=algo_restriction, axis="OUTPUT", type="RP")
		pc.make_boxplots_allsets(setname, axis="TIME", type="ABSOLUTE")
		pc.make_boxplots_allsets(setname, axis="OUTPUT", type="RP")

def plot_performance_by_algo_lineplots():
	for setname in ["general", "planar", "maxdeg", "maxclique"]:
		# this is broken 
		#pc.plot_performance_by_algorithm(setname, algos=algo_restriction, axis="TIME", type="ABSOLUTE")
		
		pc.plot_performance_by_algorithm(setname, algos=algo_restriction, axis="OUTPUT", type="RP")

def plot_performance_by_density():
	for setname in ["general", "planar", "maxdeg", "maxclique"]:
		pc.make_performance_plots_all(setname, axis="TIME", type="ABSOLUTE")
		pc.make_performance_plots_all(setname, axis="OUTPUT", type="RP")

def build_all_tables_detrand_compare():
	for setname in ["general", "planar", "maxdeg", "maxclique"]:
		outputfilenames = []
		for density_class in ["dense", "sparse"]:
			if not (setname == "planar" and density_class == "dense"):
				tc.construct_table_compare_randomized(setname, density_class, axis="OUTPUT")
				outputfilenames.append("table_cmprand_"+setname+"_"+density_class+"_OUTPUT")
				tc.construct_table_compare_randomized(setname, density_class, axis="TIME")
				outputfilenames.append("table_cmprand_"+setname+"_"+density_class+"_TIME")
		
		os.chdir("data/eval/random_"+setname+"/tables")
		for tablefile in outputfilenames:
			call(["pdflatex",tablefile+".tex"])
		os.chdir("../../../..")
		
def build_tables_general_compare():
	for setname in ["general", "planar", "maxdeg", "maxclique"]:
		outputfilenames = []
		for density_class in ["dense", "sparse"]:
			if not (setname == "planar" and density_class == "dense"):
				outputfilenames.append(tc.construct_table_compare(
					setname, 
					density_class,
					axis="OUTPUT",
					type="ABSOLUTE",
					values="MEAN"
				))
				outputfilenames.append(tc.construct_table_compare(
					setname, 
					density_class,
					axis="OUTPUT",
					type="ABSOLUTE",
					values="VAR"
				))
				outputfilenames.append(tc.construct_table_compare(
					setname, 
					density_class,
					axis="TIME",
					type="ABSOLUTE",
					values="MEAN"
				))
		
		os.chdir("data/eval/random_"+setname+"/tables")
		for tablefile in outputfilenames:
			call(["pdflatex",tablefile+".tex"])
		os.chdir("../../../..")

if __name__ == "__main__":
	make_plots()
	build_all_tables_detrand_compare()
	build_tables_general_compare()