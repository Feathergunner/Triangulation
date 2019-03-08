#!usr/bin/python
# -*- coding: utf-8 -*-

from Evaluation import PlotConstructor as pc

def make_plots():
	#plot_performance_by_algo_boxplots()
	#plot_performance_by_algo_lineplots()
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
	

if __name__ == "__main__":
	#make_plots()
	pc.performance_plot_analyze_reduction("general", "CMT")