from Evaluation import StatisticsManager as sm

def make_plots():
	for setname in ["general", "planar", "maxdeg", "maxclique"]:
		sm.make_all_stat_boxplots(setname)

if __name__ == "__main__":
	#make_plots()
	
	#sm.make_stat_boxplot("general", "ER_n20_p01")
	mrp = sm.compute_mean_relative_performance("general", "ER_n20_p01")
	print (mrp["SMS"])