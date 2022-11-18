import requests
import numpy as np
import csv
import math
import ast
import googlemaps
from flask import Flask,render_template,request
 
app = Flask(__name__)
@app.route('/')
def open_layer():
   return render_template("index.html")
@app.route('/compute',methods=['POST', 'GET'])
def compute_paths():
	#orders_array_clean = []
	#orders_array_clean.append([])
	orders = request.args.get("customer_orders")
	#print(orders, file=sys.stderr)
	print(orders)
	print("The length of orders is: ")
	print(len(orders))
	orders_array = orders.split('\t')
	del orders_array[0]
	print(orders_array)
	print("The length of orders_array is: ")
	print(len(orders_array))
	orders_array_clean = np.empty((len(orders_array),5),dtype=object,order='C')
	#print("The first element of order_array is: " + orders_array[0])
	# Remember to write code to add DC coords to orders_array
	
	# distance_matrix = np.zeros((len(orders_array),len(orders_array)))
	savings_matrix = np.zeros((len(orders_array),len(orders_array)))
	savings_dict = {}
	
#	url = 'http://45.77.99.111:5000/table/v1/driving/'
#	url2 = 'http://45.77.99.111:5000/route/v1/driving/'
#	url2_end = '?overview=false'

#	url2 = 'https://api.mapbox.com/directions/v5/mapbox/driving/'
#	url2_end = '?access_token=pk.eyJ1IjoiaW1vbmlrZSIsImEiOiJjajU4OXhnOXgxdW9zMndtejlnMWRtYmtpIn0.MlvV3UbYX5iuHnYlk5rkWA'
	
#	url2 = 'https://maps.googleapis.com/maps/api/distancematrix/json?units=metric&origins='
#	destinations = '&destinations='
#	url2_end = '&key=AIzaSyAO1lIUiB1WtqyfEMWXEeXWnn6fCWlf93U'

	url2 = 'https://graphhopper.com/api/1/matrix?'
	url2_end = 'type=json&vehicle=car&debug=true&out_array=distances&key=2286b69a-062f-48b8-9c37-d21cbb9c376a'
	
	
#	long_str = ''
#	lat_str = ''	
	
	for i in range(len(orders_array)):
		print("Element " + str(i) + " is equal to " + orders_array[i])
		order_details = orders_array[i].split(':')
		print("The length of order details is:")
		print(len(order_details))
		for j in range(len(order_details)):
			if j == 0:
				order_details[j] = order_details[j][1]
			elif j == 1:
				order_details[j] = order_details[j][2:]
			elif j == 3:
				latitude = order_details[j].split(',')
				order_details[j] = latitude[0]
				lat_str = latitude[0]
			elif j == 4:
				longitude = order_details[j].split('"')
				order_details[j] = longitude[0]
				long_str = longitude[0]
			else:
				order_details[j] = order_details[j]
		
			
			orders_array_clean[i][j] = order_details[j]
			print("The current entry is " + orders_array_clean[i][j])
#		url = url + long_str + "," + lat_str + ";"
	print("The size of orders_array_clean is ")
	print(len(orders_array_clean))
		
		
			
	
	
#	url = url[:-1]
#	print(url)
#	auth = ('root', 'u2B%zrNuPV.,S1E=')
#	r = requests.get(url, auth=auth)
#	print r.content
#	print type(r.content)
	print(orders_array_clean)
	
#	osrm_output = (r.content).split(':')
#	durations = (osrm_output[2]).split(',"')
	
#	print(durations[0])
#	print type(durations[0])
	
#	durations_array = ast.literal_eval(durations[0])
	
#	print len(durations_array)
#	print len(durations_array[0])
#	print durations_array[0][1]
#	print len(durations_array[6])
#	print type(durations_array)
#	print(osrm_output)
	
#	distance_matrix = durations_array
#	print type(distance_matrix)
#	print distance_matrix
	
#	long_str1 = ''
#	lat_str1 = ''
	
#	long_str2 = ''
#	lat_str2 = ''
	
	auth = ('imonikemohammed@gmail.com', 'data_scientist')
	
	
	print("The range of orders_array_clean is")
	print(range(len(orders_array_clean)))
	
	for i in range(len(orders_array_clean)):
		long_str1 = orders_array_clean[i][4]
		lat_str1 = orders_array_clean[i][3]
		
		print("long_str1 is equal to " + long_str1)
		print("lat_str1 is equal to " + lat_str1)
		
	#	j = i + 1
		print("i is equal to ")
		print(i)
		
		url2 = url2 + 'point=' + lat_str1 + ',' + long_str1 + '&'
	
	url3 = url2 + url2_end
	print(url3)
	
	r = requests.get(url3)
	
	with open("C:/flask_apps/leaflet/control_search/graphhop_distance_matrix.txt", "a") as myfile:
		myfile.write(url3)
		myfile.write(r.content)
		
		
		
	#	while (j < len(orders_array_clean)):
	#		print("j is equal to ")
	#		print(j)
			
			
			
			
			
			
	#		long_str2 = orders_array_clean[j][4]
	#		lat_str2 = orders_array_clean[j][3]
			
		#	url3 = url2 + long_str1 + "," + lat_str1 + ";" + long_str2 + "," + lat_str2 + url2_end
	#		url3 = url2 + lat_str1 + "," + long_str1 + destinations + lat_str2 + "," + long_str2 + url2_end
			
	#		print(url3)
	#		print('\n')
			
	#		j = j + 1
			
		#	r = requests.get(url3, auth=auth)
		
	#		r = requests.get(url3)
	#		print r.content
			
	#		with open("C:/flask_apps/leaflet/control_search/google_dist_matrix.txt", "a") as myfile:
	#			myfile.write(url3)
	#   			myfile.write(r.content)
			
		
			
				
			
				
			
			
			
	
	
	
		
		
	
	return render_template("paths.html")
 
if __name__ == '__main__':
   app.run(debug=True)