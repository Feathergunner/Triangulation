#!usr/bin/python
# -*- coding: utf-8 -*-

import json
import sys

def print_progress(part, total, front_string="Progress:", end_string=""):
	if not total == 0:
		print (front_string+" "+str("%6.2f" % ((float(part)/(float(total)/100)))) + "% "+end_string, end='\r')
		if part >= total:
			print ()
		sys.stdout.flush()

class My_JSON_Encoder(json.JSONEncoder):
	def default(self, obj):
		return obj.__json__()
