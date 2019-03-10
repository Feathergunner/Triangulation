#!usr/bin/python
# -*- coding: utf-8 -*-

from Evaluation import PlotConstructor as pc
from Evaluation import TableConstructor as tc
from Evaluation import StatisticsManager as sm
import os
from subprocess import call

def make_plots():
	plot_performance_by_algo_boxplots()
	plot_performance_by_algo_lineplots()
	plot_performance_by_density()

def plot_performance_by_algo_boxplots():
	for setname in ["general", "planar", "maxdeg", "maxclique"]:
		pc.make_boxplots_total(setname, axis="TIME", type="ABSOLUTE")
		pc.make_boxplots_total(setname, axis="OUTPUT", type="RP")
		pc.make_boxplots_allsets(setname, axis="TIME", type="ABSOLUTE")
		pc.make_boxplots_allsets(setname, axis="OUTPUT", type="RP")

def plot_performance_by_algo_lineplots():
	for setname in ["general", "planar", "maxdeg", "maxclique"]:
		pc.plot_performance_by_algorithm(setname, axis="TIME", type="ABSOLUTE")
		pc.plot_performance_by_algorithm(setname, axis="OUTPUT", type="RP")

def plot_performance_by_density():
	for setname in ["general", "planar", "maxdeg", "maxclique"]:
		pc.make_performance_plots_all(setname, axis="TIME", type="ABSOLUTE")
		pc.make_performance_plots_all(setname, axis="OUTPUT", type="RP")

def build_all_tables_detrand_compare():
	for setname in ["general", "planar", "maxdeg", "maxclique"]:
		outputfilenames = []
		for density_class in ["dense", "sparse"]:
			if not (setname == "planar" and density_class == "dense"):
				print (setname+", "+density_class)
				tc.construct_table_compare_randomized(setname, density_class)
				outputfilenames.append("table_cmprand_"+setname+"_"+density_class)
	
		os.chdir("data/eval/random_"+setname+"/tables")
		for tablefile in outputfilenames:
			call(["pdflatex",tablefile+".tex"])
		os.chdir("../../../..")

if __name__ == "__main__":
	#make_plots()
	build_all_tables_detrand_compare()