#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#	 http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2
import csv
import os
from StringIO import StringIO
from django.template import Context, Template
from django.template.loader import render_to_string

class MainHandler(webapp2.RequestHandler):
	#class to 


	def get(self):
		
		
		csvFile = open('input.txt', 'rb')

		data = {'data':self.processData(csvFile),'sampleData':True}
		path = os.path.join(os.path.dirname(__file__), 'showData.html')
		pageDate = render_to_string( path, data)
		self.response.out.write(pageDate)
	def post(self):
		
		#reading the file data POST information.
		csvFile = self.request.get('csvFile')

		if csvFile:
			#to handle universal new line char for  MAC systems
			csvFile = csvFile.replace("\r","\n")
		
			#casting the data to stream for input to csvreader module.
			csvFile = StringIO(csvFile)	

			data = {'data':self.processData(csvFile) if csvFile else []}
			path = os.path.join(os.path.dirname(__file__), 'showData.html') 
			pageDate = render_to_string( path, data)
			self.response.out.write(pageDate)
		else: self.redirect('/')

	def processData(self,csvFile= None):

		if csvFile:

			#initateing CSV reader object to parse the csv file.
			fileReader = csv.DictReader(csvFile, skipinitialspace=True, restkey='uncategorized', restval='', quotechar='"', quoting=csv.QUOTE_MINIMAL)
			
			#parsing headers of csv to find all available company names to avoid validation conditions in the loop
			#consider n is number of companies, we can count iterations
			feilds =[companyName for companyName in fileReader.fieldnames if companyName not in ['Year','Month']]
			
			#initating a dictionary to store max and minmum of each company.
			structuredData = {}
			
			#fileReader holds the csv parser object, which returns a row of data in dict format for every iteration.
			for reader in fileReader:
				
				#defining year and month variables as index variables to be used over iterations.
				year = reader.get('Year')
				month = reader.get('Month')
				
				#Avoiding a validation check validating the existance of each company name in dict 
				#occouing on each operations with m rows initializing the values in first row. 
				if not structuredData:
					for companyName in fileReader.fieldnames:
						if companyName not in ['Year','Month']:
							#intializing the values of each company with max and min values with a list to hold possiblity of multiple max and min values. 
							structuredData.update({companyName:{'least':[(int(reader.get(companyName)),year,month)],
																'max':[(int(reader.get(companyName)),year,month)]}
													})
				else:
					for companyName in feilds:

						#fetching the current least and max for each company
						leastEle =  structuredData[companyName]['least'][0][0]
						maxEle   =  structuredData[companyName]['max'][0][0]

						#value for a "companyName" for a "year"  and "month"
						companyValue  = int(reader.get(companyName))
						
						#validating the validtiy for current minimum in the dict
						if companyValue < leastEle : 
							#statement to reset previous minmum with new minimum value
							structuredData[companyName]['least'] =[(companyValue,year,month)]
						elif companyValue == leastEle : 
							#statement to update the coourance the new min minmum with exisisting occurances 
							structuredData[companyName]['least'].append((companyValue,year,month))
						
						#validating the validtiy for current maximum in the dict
						if companyValue > maxEle : 
							#statement to reset previous maximum with new maximum value
							structuredData[companyName]['max'] =[(companyValue,year,month)]
						elif companyValue == maxEle : 
							#statement to update the coourance the new min maximum with exisisting occurances 
							structuredData[companyName]['max'].append((companyValue,year,month))
			return structuredData

			
		for key in structuredData:
			print 'Company Name: ',key
			print "Least: ",structuredData[key]["least"]
			print "Max: ",structuredData[key]["max"]
			print 


app = webapp2.WSGIApplication([
	('/', MainHandler)
], debug=True)
