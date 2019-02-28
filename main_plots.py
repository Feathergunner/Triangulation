#!usr/bin/python
# -*- coding: utf-8 -*-

from Evaluation import StatisticsManager as sm

def make_plots():
	for setname in ["general", "planar", "maxdeg", "maxclique"]:
		sm.make_all_stat_boxplots(setname)

if __name__ == "__main__":
	#make_plots()
	
	#sm.make_stat_boxplot("general", "ER_n20_p01")
	#mrp = sm.compute_mean_relative_performance("general", "ER_n20_p01")
	#for algo in mrp:
	#	print (algo + ": " + str(round(mrp[algo],2)))

	#rp = sm.compute_relative_performance("general", "ER_n20_p01")
	#print ([algo + ": "+str(rp[algo][:10]) for algo in rp])
	
	#sm.make_boxplots_all("maxclique", axis="TIME", type="ABSOLUTE")

	sm.make_performance_plots_all("general", axis="OUTPUT", type="RP")