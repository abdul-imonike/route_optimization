import requests
import numpy as np
import csv
import os
import math
import ast
import googlemaps
from flask import render_template,request,jsonify, url_for, flash, redirect, Response, session
from flask_session import Session
from flask_login import login_required, login_user, logout_user, current_user 
#from geopy.geocoders import Nominatim
import geocoder
#from . import auth
#import auth
#from auth import *
#from .models import User
from models import User
from auth.forms import LoginForm, RegistrationForm
#from .forms import LoginForm
#from config import Config
#from flask_sqlalchemy import SQLAlchemy

from flask_login import LoginManager
from flask_bootstrap import Bootstrap
from dbobject import app
from dbobject import db 

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from io import BytesIO
#from reportlab.lib.pagesizes import letter
#from reportlab.lib.units import inch

#app = Flask(__name__)
#app.config.from_object(Config)
#db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.session_protection = 'strong'
#login_manager.login_view = 'auth.login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return None

bootstrap = Bootstrap(app)

db.init_app(app)

Session(app)


# @app.route('/')
# def index():
#   return render_template("auth/login.html")
   
#@app.route('/login',methods=['GET','POST'])

@app.route('/',methods=['GET','POST'])
def index():
	print("Inside index()")
	form = LoginForm()
	print("Instantiated form object")
	if form.validate_on_submit():
		print("Inside validation if clause")
		user = User.query.filter_by(email=form.email.data).first()
		if user is None:
			print("Query not returning user")
		else:
			print(user.email)
		if user is not None and user.check_password(form.password.data):
			print("Successfully confirmed username and password")

			#db.session.add(current_user)
			#db.session.commit()
			login_user(user, form.remember_me.data)
			print("Successfully logged in user")
			return redirect(request.args.get('next') or url_for('dashboard'))
			print("Redirected to the dashboard")
		flash('Invalid username or password.')
	return render_template('auth/login.html', form=form)

@app.route('/dashboard')	
def dashboard(): 	
	return render_template("index.html")
   
@app.route('/logout')
def logout():
	print("Inside logout function")

	#print('login template returned')
	logout_user()
	flash('You have been logged out.')
	return redirect(url_for('index'))
	#return render_template('auth/login.html', form=form)
	
@app.route('/register', methods=['GET', 'POST'])
def register():
    #if current_user.is_authenticated:
    #    return redirect(url_for('dashboard'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('index'))
    return render_template('auth/register.html', title='Register', form=form)

@app.route('/download_routes')
def download_routes():

	buffer = BytesIO()
	c = canvas.Canvas(buffer)

	#c.drawString(100,750,session["list_of_addresses"])
	
	
	
	#c.save()
	
	doc = SimpleDocTemplate(buffer,
                            pagesize=letter,
                            rightMargin=72,
                            leftMargin=72,
                            topMargin=72,
                            bottomMargin=18)
							
							
	styles = getSampleStyleSheet()
	mystyle = ParagraphStyle('mytitle',
                           fontName="Helvetica-Bold",
                           fontSize=16,
    #                      parent=style['Heading2'],
                           alignment=1,
                           spaceAfter=14)
	flowables = []

    
    
	
	text = session["list_of_addresses"].split('@')
	
	for j in range(len(text)):
		
		addresses = text[j].split('&')
		addresses_in_a_route = ''
		
		for k in range(len(addresses)):
			one_address = addresses[k]
			one_address = one_address[20:]
			one_address = one_address + ", "
			addresses_in_a_route += one_address
		
		addresses_in_a_route = addresses_in_a_route.replace(">","")
		route_label = "Route " + str(j + 1)
		text[j] = addresses_in_a_route
	#	text[j] = "Route " + str(j + 1) + '\n\n' + addresses_in_a_route + '\n\n'
	#	text[j] = "Route " + str(j + 1) + os.linesep + addresses_in_a_route + os.linesep
		
	#	para = Paragraph(text[j], style=styles["Normal"])
	
	#	textobject = c.beginText()
	#	textobject.textLine(route_label)
	#	route_header = c.drawText(textobject)
		
		para = Paragraph(route_label, style=styles["Normal"])
		flowables.append(para)
		para = Paragraph(text[j], style=mystyle)
		flowables.append(para)
		
		
		
	doc.build(flowables)
	
	pdf = buffer.getvalue()
	buffer.close()
	
	response = Response(pdf)
	response.headers['Content-Disposition'] = "attachment; filename='optimized_routes.pdf'"
	response.mimetype = 'application/pdf'
	
	return response


@app.route('/compute',methods=['POST', 'GET'])
#@login_required
def compute_paths():

	orders = request.args.get("customer_orders")
	#orders = request.args.get("orders_string") 
	
	print(orders)
	print("The length of orders is: ")
	print(len(orders))
	orders_array = orders.split('\t')
	del orders_array[0]
	print(orders_array)
	print("The length of orders_array is: ")
	print(len(orders_array))
	orders_array_clean = np.empty((len(orders_array),5),dtype=object,order='C')

	savings_dict = {}
	quantity = []
	truck_capacity = 5000
	
	
	for i in range(len(orders_array)):
		print("Element " + str(i) + " is equal to " + orders_array[i])
		order_details = orders_array[i].split(':')
		print("The length of order details is:")
		print(len(order_details))
		for j in range(len(order_details)):
			if j == 0:
				if len(order_details[j]) <= 3:
					order_details[j] = order_details[j][1]
				elif len(order_details[j]) == 4:
					order_details[j] = order_details[j][1:3]
				else:
					order_details[j] = order_details[j][1:4]
			elif j == 1:
				order_details[j] = order_details[j][2:]
				quantity.append(order_details[j])
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

	print("The size of orders_array_clean is ")
	print(len(orders_array_clean))
	
	
	print("The customer demand list is:")
	print(quantity)
		
	#quantity = quantity[1:]
	#print(quantity)
			
	
	

	print(orders_array_clean)
		

	
	auth = ('imonikemohammed@gmail.com', 'data_scientist')
	
	
	print("The range of orders_array_clean is")
	print(range(len(orders_array_clean)))
	
	distance_matrix = np.zeros((len(orders_array_clean),len(orders_array_clean)))
	savings_matrix = np.zeros((len(orders_array_clean),len(orders_array_clean)))

	
	for i in range(len(orders_array_clean)):
		long_str1 = orders_array_clean[i][4]
		lat_str1 = orders_array_clean[i][3]
		
		print("long_str1 is equal to " + long_str1)
		print("lat_str1 is equal to " + lat_str1)
		
		long_str1 = long_str1[0:len(long_str1)-2]
		
		print("long_str1 is equal to " + long_str1)
		
	
		print("i is equal to ")
		print(i)
		
		long_str1 = float(long_str1)
		lat_str1 = float(lat_str1)
		
		orders_array_clean[i][4] = long_str1
		orders_array_clean[i][3] = lat_str1
		
		print(orders_array_clean)
		
		#print(len(distance_matrix))
		
	j = 0
	for i in range(len(distance_matrix)):
		j = i + 1
		while (j < len(distance_matrix[0])):
			distance_matrix[i][j] = math.sqrt(math.pow(float(orders_array_clean[i][3]) - float(orders_array_clean[j][3]),2) + math.pow(float(orders_array_clean[i][4]) - float(orders_array_clean[j][4]),2))
			j = j + 1
			
	print("The distance matrix is: ")
	print(distance_matrix)
	
	n = 1
	for m in range(1,len(orders_array_clean)-1):
		n = m + 1
		while (n <= len(orders_array_clean)-1):
			savings_matrix[m][n] = distance_matrix[0][m] + distance_matrix[0][n] - distance_matrix[m][n]
			nodes = "%s-%s" % (m,n)
			savings_dict[nodes] = savings_matrix[m][n]
			n = n + 1
	

	print("The savings matrix is: ")	
	print(savings_matrix)
	
#	sorted_savings = sorted(savings_dict.items(), key=lambda x: (-x[1],x[0]))
	
#	print("sorted_savings initialized")
#	print(sorted_savings)

	sorted_savings = sorted(savings_dict.items(), key=lambda x: (-x[1],x[0]))

	print("sorted_savings initialized")
	print(sorted_savings)
	
	optimized_routes = []
	customer_ids = []
	customer_lat = []
	customer_lon = []
	customer_ids_nodes = []
	
	customer_addresses = {}
	optimized_addresses = []
	
	# optimized_route1 = []
	# optimized_routes.append(optimized_route1)
	i = 0
	current_load = 0
	skipped_nodes = []
	
	while len(sorted_savings) > 0:
		key = sorted_savings[i][0].split('-')
		route_end1 = int(key[0])
		route_end2 = int(key[1])
	
		print("key is %s " % (key))
	
		if len(optimized_routes) == 0:
	
			print("Inside optimized_routes is equal to 0")
        
	    
	
			if current_load + float(quantity[route_end1]) + float(quantity[route_end2]) < truck_capacity:
				optimized_routes.append([])
				optimized_routes[0].append(route_end1)
				optimized_routes[0].append(route_end2)
			
				current_load = current_load + float(quantity[route_end1]) + float(quantity[route_end2])
	#		continue
			else :
				skipped_nodes.append(sorted_savings[i])		
	#		continue		
		elif len(optimized_routes) > 0:
	
			print("Inside optimized_routes is greater than 0")
		
	    
	
		
			outer_list_size = len(optimized_routes)
		
			print("outer list size is %s " % (outer_list_size))
		
			current_list = optimized_routes[outer_list_size-1]
			current_inner_list_size = len(optimized_routes[outer_list_size-1])
		
			print("current list is %s and the list size is %s " % (current_list,current_inner_list_size))
		
			if outer_list_size == 1:
				print("Inside outer_list_size == 1")
				if len(optimized_routes[outer_list_size-1]) >= 2:
					print("The type of key[0] and key[1] is %s " % (type(key[0])))
					print("The type of current_list[0] and current_list[current_inner_list_size-1] is %s and %s " % (type(current_list[0]),type(current_list[current_inner_list_size-1])))
					if optimized_routes[outer_list_size-1][0] == route_end1 and optimized_routes[outer_list_size-1][len(optimized_routes[outer_list_size-1])-1] == route_end2:
						print("Inside current_list[0] == route_end1 and current_list[current_inner_list_size-1] == route_end2")
						i = i + 1
						continue
					elif optimized_routes[outer_list_size-1][0] == route_end2 and optimized_routes[outer_list_size-1][len(optimized_routes[outer_list_size-1])-1] == route_end1:
						print("Inside current_list[0] == route_end2 and current_list[current_inner_list_size-1] == route_end1")
						i = i + 1
						continue
					elif optimized_routes[outer_list_size-1][0] == route_end1:
						print("Inside current_list[0] == route_end1")
						if current_load + float(quantity[route_end2]) < truck_capacity and route_end2 not in optimized_routes[outer_list_size-1]:
							optimized_routes[outer_list_size-1].insert(0,route_end2)
							current_load = current_load + float(quantity[route_end2])
			#			continue
							for x in range(len(skipped_nodes)):
								skipped_key = skipped_nodes[x][0].split('-')
								route_end3 = int(skipped_key[0])
								route_end4 = int(skipped_key[1])
							
								if optimized_routes[outer_list_size-1][0] == route_end3:
									print("optimized_routes[outer_list_size-1][0] == route_end3")
									if current_load + float(quantity[route_end4]) < truck_capacity and route_end4 not in optimized_routes[outer_list_size-1]:
										optimized_routes[outer_list_size-1].insert(0,route_end4)
										current_load = current_load + float(quantity[route_end4])
									
								
								elif optimized_routes[outer_list_size-1][0] == route_end4:
									print("optimized_routes[outer_list_size-1][0] == route_end4")
									if current_load + float(quantity[route_end3]) < truck_capacity and route_end3 not in optimized_routes[outer_list_size-1]:
										optimized_routes[outer_list_size-1].insert(0,route_end3)
										current_load = current_load + float(quantity[route_end3])
								
								else:
									print("Nothing to do 4")
						else:
							skipped_nodes.append(sorted_savings[i])
			#			continue
					 
					elif optimized_routes[outer_list_size-1][len(optimized_routes[outer_list_size-1])-1] == route_end1:
						print("Inside current_list[current_inner_list_size-1] == route_end1")
						if current_load + float(quantity[route_end2]) < truck_capacity and route_end2 not in optimized_routes[outer_list_size-1]:
							optimized_routes[outer_list_size-1].append(route_end2)
							current_load = current_load + float(quantity[route_end2])
			#		continue
							for x in range(len(skipped_nodes)):
								skipped_key = skipped_nodes[x][0].split('-')
								route_end3 = int(skipped_key[0])
								route_end4 = int(skipped_key[1])
							
								if optimized_routes[outer_list_size-1][len(optimized_routes[outer_list_size-1])-1] == route_end3:
									print("optimized_routes[outer_list_size-1][len(optimized_routes[outer_list_size-1])-1] == route_end3")
									if current_load + float(quantity[route_end4]) < truck_capacity and route_end4 not in optimized_routes[outer_list_size-1]:
										optimized_routes[outer_list_size-1].append(route_end4)
										current_load = current_load + float(quantity[route_end4])
									
								
								elif optimized_routes[outer_list_size-1][len(optimized_routes[outer_list_size-1])-1] == route_end4:
									print("optimized_routes[outer_list_size-1][len(optimized_routes[outer_list_size-1])-1] == route_end4")
									if current_load + float(quantity[route_end3]) < truck_capacity and route_end3 not in optimized_routes[outer_list_size-1]:
										optimized_routes[outer_list_size-1].append(route_end3)
										current_load = current_load + float(quantity[route_end3])
								
								else:
									print("Nothing to do 5")
						else:
							skipped_nodes.append(sorted_savings[i]) 
			#		continue
					 
					elif optimized_routes[outer_list_size-1][0] == route_end2:
						print("Inside current_list[0] == route_end2")
						if current_load + float(quantity[route_end1]) < truck_capacity and route_end1 not in optimized_routes[outer_list_size-1]:
							optimized_routes[outer_list_size-1].insert(0,route_end1)
							current_load = current_load + float(quantity[route_end1])
			#		continue
							for x in range(len(skipped_nodes)):
								skipped_key = skipped_nodes[x][0].split('-')
								route_end3 = int(skipped_key[0])
								route_end4 = int(skipped_key[1])
							
								if optimized_routes[outer_list_size-1][0] == route_end3:
									print("optimized_routes[outer_list_size-1][0] == route_end3")
									if current_load + float(quantity[route_end4]) < truck_capacity and route_end4 not in optimized_routes[outer_list_size-1]:
										optimized_routes[outer_list_size-1].insert(0,route_end4)
										current_load = current_load + float(quantity[route_end4])
									
								
								elif optimized_routes[outer_list_size-1][0] == route_end4:
									print("optimized_routes[outer_list_size-1][0] == route_end4")
									if current_load + float(quantity[route_end3]) < truck_capacity and route_end3 not in optimized_routes[outer_list_size-1]:
										optimized_routes[outer_list_size-1].insert(0,route_end3)
										current_load = current_load + float(quantity[route_end3])
								
								else:
									print("Nothing to do 6")
						else:
							skipped_nodes.append(sorted_savings[i])
			#		continue
					
					elif optimized_routes[outer_list_size-1][len(optimized_routes[outer_list_size-1])-1] == route_end2:
						print("Inside current_list[current_inner_list_size-1] == route_end2")
						if current_load + float(quantity[route_end1]) < truck_capacity and route_end1 not in optimized_routes[outer_list_size-1]:
							optimized_routes[outer_list_size-1].append(route_end1)
							current_load = current_load + float(quantity[route_end1])
			#		continue
							for x in range(len(skipped_nodes)):
								skipped_key = skipped_nodes[x][0].split('-')
								route_end3 = int(skipped_key[0])
								route_end4 = int(skipped_key[1])
							
								if optimized_routes[outer_list_size-1][len(optimized_routes[outer_list_size-1])-1] == route_end3:
									print("optimized_routes[outer_list_size-1][len(optimized_routes[outer_list_size-1])-1] == route_end3")
									if current_load + float(quantity[route_end4]) < truck_capacity and route_end4 not in optimized_routes[outer_list_size-1]:
										optimized_routes[outer_list_size-1].append(route_end4)
										current_load = current_load + float(quantity[route_end4])
									
								
								elif optimized_routes[outer_list_size-1][len(optimized_routes[outer_list_size-1])-1] == route_end4:
									print("optimized_routes[outer_list_size-1][len(optimized_routes[outer_list_size-1])-1] == route_end4")
									if current_load + float(quantity[route_end3]) < truck_capacity and route_end3 not in optimized_routes[outer_list_size-1]:
										optimized_routes[outer_list_size-1].append(route_end3)
										current_load = current_load + float(quantity[route_end3])
								
								else:
									print("Nothing to do 7")
						else:
							skipped_nodes.append(sorted_savings[i])
			#		continue
					else :
			#	continue
						print ("Nothing to do 1")
						skipped_nodes.append(sorted_savings[i])
				else:
					if current_load + float(quantity[route_end1]) + float(quantity[route_end2]) < truck_capacity:
						optimized_routes[outer_list_size-1].append(route_end1)
						optimized_routes[outer_list_size-1].append(route_end2)
				
						current_load = current_load + float(quantity[route_end1]) + float(quantity[route_end2])
		#		continue
				
					else:
						skipped_nodes.append(sorted_savings[i])		
		#		continue
			else:
				print("Inside outer_list_size > 1")
				previous_list = optimized_routes[outer_list_size-2]
				print("previous list is %s and its type is %s " % (previous_list, type(previous_list)))
			
			
				
				if route_end1 in previous_list or route_end2 in previous_list:
					print("Inside break")
					
				else:
					
					if current_inner_list_size >= 2:
						print("The type of key[0] and key[1] is %s " % (type(key[0])))
						print("The type of current_list[0] and current_list[current_inner_list_size-1] is %s and %s " % (type(current_list[0]),type(current_list[current_inner_list_size-1])))
						if current_list[0] == route_end1 and current_list[current_inner_list_size-1] == route_end2:
							print("Inside current_list[0] == route_end1 and current_list[current_inner_list_size-1] == route_end2")
							i = i + 1
							continue
						elif current_list[0] == route_end2 and current_list[current_inner_list_size-1] == route_end1:
							print("Inside current_list[0] == route_end2 and current_list[current_inner_list_size-1] == route_end1")
							i = i + 1
							continue
						elif optimized_routes[outer_list_size-1][0] == route_end1:
							print("Inside current_list[0] == route_end1")
							if current_load + float(quantity[route_end2]) < truck_capacity and route_end2 not in optimized_routes[outer_list_size-1]:
								optimized_routes[outer_list_size-1].insert(0,route_end2)
								current_load = current_load + float(quantity[route_end2])
			#			continue
								for x in range(len(skipped_nodes)):
									skipped_key = skipped_nodes[x][0].split('-')
									route_end3 = int(skipped_key[0])
									route_end4 = int(skipped_key[1])
							
									if optimized_routes[outer_list_size-1][0] == route_end3:
										print("optimized_routes[outer_list_size-1][0] == route_end3")
										if current_load + float(quantity[route_end4]) < truck_capacity and route_end4 not in optimized_routes[outer_list_size-1]:
											optimized_routes[outer_list_size-1].insert(0,route_end4)
											current_load = current_load + float(quantity[route_end4])
									
								
									elif optimized_routes[outer_list_size-1][0] == route_end4:
										print("optimized_routes[outer_list_size-1][0] == route_end4")
										if current_load + float(quantity[route_end3]) < truck_capacity and route_end3 not in optimized_routes[outer_list_size-1]:
											optimized_routes[outer_list_size-1].insert(0,route_end3)
											current_load = current_load + float(quantity[route_end3])
								
									else:
										print("Nothing to do 8")
							else:
								skipped_nodes.append(sorted_savings[i])
			#			continue
					 
						elif optimized_routes[outer_list_size-1][len(optimized_routes[outer_list_size-1])-1] == route_end1:
							print("Inside current_list[current_inner_list_size-1] == route_end1")
							if current_load + float(quantity[route_end2]) < truck_capacity and route_end2 not in optimized_routes[outer_list_size-1]:
								optimized_routes[outer_list_size-1].append(route_end2)
								current_load = current_load + float(quantity[route_end2])
			#		continue
								for x in range(len(skipped_nodes)):
									skipped_key = skipped_nodes[x][0].split('-')
									route_end3 = int(skipped_key[0])
									route_end4 = int(skipped_key[1])
							
									if optimized_routes[outer_list_size-1][len(optimized_routes[outer_list_size-1])-1] == route_end3:
										print("optimized_routes[outer_list_size-1][len(optimized_routes[outer_list_size-1])-1] == route_end3")
										if current_load + float(quantity[route_end4]) < truck_capacity and route_end4 not in optimized_routes[outer_list_size-1]:
											optimized_routes[outer_list_size-1].append(route_end4)
											current_load = current_load + float(quantity[route_end4])
									
								
									elif optimized_routes[outer_list_size-1][len(optimized_routes[outer_list_size-1])-1] == route_end4:
										print("optimized_routes[outer_list_size-1][len(optimized_routes[outer_list_size-1])-1] == route_end4")
										if current_load + float(quantity[route_end3]) < truck_capacity and route_end3 not in optimized_routes[outer_list_size-1]:
											optimized_routes[outer_list_size-1].append(route_end3)
											current_load = current_load + float(quantity[route_end3])
								
									else:
										print("Nothing to do 9")
							else:
								skipped_nodes.append(sorted_savings[i]) 
			#		continue
					 
						elif optimized_routes[outer_list_size-1][0] == route_end2:
							print("Inside current_list[0] == route_end2")
							if current_load + float(quantity[route_end1]) < truck_capacity and route_end1 not in optimized_routes[outer_list_size-1]:
								optimized_routes[outer_list_size-1].insert(0,route_end1)
								current_load = current_load + float(quantity[route_end1])
			#		continue
								for x in range(len(skipped_nodes)):
									skipped_key = skipped_nodes[x][0].split('-')
									route_end3 = int(skipped_key[0])
									route_end4 = int(skipped_key[1])
							
									if optimized_routes[outer_list_size-1][0] == route_end3:
										print("optimized_routes[outer_list_size-1][0] == route_end3")
										if current_load + float(quantity[route_end4]) < truck_capacity and route_end4 not in optimized_routes[outer_list_size-1]:
											optimized_routes[outer_list_size-1].insert(0,route_end4)
											current_load = current_load + float(quantity[route_end4])
									
								
									elif optimized_routes[outer_list_size-1][0] == route_end4:
										print("optimized_routes[outer_list_size-1][0] == route_end4")
										if current_load + float(quantity[route_end3]) < truck_capacity and route_end3 not in optimized_routes[outer_list_size-1]:
											optimized_routes[outer_list_size-1].insert(0,route_end3)
											current_load = current_load + float(quantity[route_end3])
								
									else:
										print("Nothing to do 10")
							else:
									skipped_nodes.append(sorted_savings[i])
			#		continue
					
						elif optimized_routes[outer_list_size-1][len(optimized_routes[outer_list_size-1])-1] == route_end2:
							print("Inside current_list[current_inner_list_size-1] == route_end2")
							if current_load + float(quantity[route_end1]) < truck_capacity and route_end1 not in optimized_routes[outer_list_size-1]:
								optimized_routes[outer_list_size-1].append(route_end1)
								current_load = current_load + float(quantity[route_end1])
			#		continue
								for x in range(len(skipped_nodes)):
									skipped_key = skipped_nodes[x][0].split('-')
									route_end3 = int(skipped_key[0])
									route_end4 = int(skipped_key[1])
							
									if optimized_routes[outer_list_size-1][len(optimized_routes[outer_list_size-1])-1] == route_end3:
										print("optimized_routes[outer_list_size-1][len(optimized_routes[outer_list_size-1])-1] == route_end3")
										if current_load + float(quantity[route_end4]) < truck_capacity and route_end4 not in optimized_routes[outer_list_size-1]:
											optimized_routes[outer_list_size-1].append(route_end4)
											current_load = current_load + float(quantity[route_end4])
									
								
									elif optimized_routes[outer_list_size-1][len(optimized_routes[outer_list_size-1])-1] == route_end4:
										print("optimized_routes[outer_list_size-1][len(optimized_routes[outer_list_size-1])-1] == route_end4")
										if current_load + float(quantity[route_end3]) < truck_capacity and route_end3 not in optimized_routes[outer_list_size-1]:
											optimized_routes[outer_list_size-1].append(route_end3)
											current_load = current_load + float(quantity[route_end3])
								
									else:
										print("Nothing to do 11")
							else:
								skipped_nodes.append(sorted_savings[i])
			#		continue
						else :
			#	continue
							print ("Nothing to do 2")
							skipped_nodes.append(sorted_savings[i])
					else:
						print("Inside current_inner_list_size < 2")
						if current_load + float(quantity[route_end1]) + float(quantity[route_end2]) < truck_capacity:
							optimized_routes[outer_list_size-1].append(route_end1)
							optimized_routes[outer_list_size-1].append(route_end2)
				
							current_load = current_load + float(quantity[route_end1]) + float(quantity[route_end2])
		#		continue
				
						else:
							skipped_nodes.append(sorted_savings[i])		
		#		continue
					
					
		else:	
	#	continue
			print("Nothing to do 3")
		 
		if i == len(sorted_savings) - 1:
			print("Finished going through sorted_savings array about to print skipped nodes")
			if len(skipped_nodes) > 0:
				sorted_savings = skipped_nodes
				print("skipped nodes: %s" % (skipped_nodes))
				skipped_nodes = []
				optimized_routes.append([])
				i = 0
				current_load = 0
			else:
				sorted_savings = skipped_nodes 
		else:
			i = i + 1
			print("i is equal to: %s" % i)
			
	print("orders_array_clean:")
	print(orders_array_clean)
	print("The length of a row in orders_array_clean is ")
	print(len(orders_array_clean[0]))
	print("Type of orders_array_clean:")
	print(type(orders_array_clean))
	print("Type of optimized route is:")
	print(type(optimized_routes))
	print optimized_routes
	
	print("The type of orders_array_clean[0][0]:")
	print(type(orders_array_clean[0][0]))
	
	print("The type of orders_array_clean[0][3]:")
	print(type(orders_array_clean[0][3]))
	
	print("The type of int(orders_array_clean[0][0]):")
	print(type(int(orders_array_clean[0][0])))
	
	print("The type of optimized_routes[0][0]:")
	print(type(optimized_routes[0][0]))
	
	#geolocator = Nominatim(domain='localhost:8080', scheme='http')
	
	url='http://45.33.99.172/nominatim/'

	
	
	for x in range(len(orders_array_clean)):
		customer_ids.append(int(orders_array_clean[x][0]))
	
	#        "52.509669, 13.376294"
		
		#lat_lon_string = str(orders_array_clean[x][3]) + ", " + str(orders_array_clean[x][4])
		lat_lon_list = [orders_array_clean[x][3], orders_array_clean[x][4]]
		
		#print("The lat_lon_list is: ")
		#print(lat_lon_list)
		
		location = geocoder.osm(lat_lon_list, method='reverse', url=url)
		
		print("The geocoder location returned:")
		print(location)
		
		customer_addresses[int(orders_array_clean[x][0])] = location
		# place location in dictionary
		
	customer_ids = customer_ids[1:]
	
	
	
	
	
	
	routes_string = ''
	optimized_addresses_string = ''

#	for x in range(len(optimized_routes)):
#		routes_string = routes_string + str(optimized_routes[x]) + 'x'

	for x in range(len(optimized_routes)):
		if len(optimized_routes[x]) > 0:
			routes_string = routes_string + str(optimized_routes[x]) + '@'
			for y in range(len(optimized_routes[x])):
				customer_ids_nodes.append((optimized_routes[x][y]))
				
#	Adding optimized addresses

	for x in range(len(optimized_routes)):
		if len(optimized_routes[x]) > 0:
			for y in range(len(optimized_routes[x])):
				optimized_addresses_string = optimized_addresses_string + str(customer_addresses[optimized_routes[x][y]]) + "& "
		optimized_addresses_string = optimized_addresses_string[:-1]
		optimized_addresses_string = optimized_addresses_string + '@'
				

#	End of optimized addresses addition
				
	print("customer_ids is equal to: ")
	print(customer_ids)
	print("customer_ids_nodes is equal to: ")
	print(customer_ids_nodes)
	
	left_out_node = list(set(customer_ids).difference(customer_ids_nodes))
	
	print("left out node is: ")
	print(left_out_node)
	
	routes_string = routes_string[:-1]
	optimized_addresses_string = optimized_addresses_string[:-1]
	
	if len(left_out_node) == 1:
		routes_string = routes_string + '@' + str(left_out_node)
		optimized_addresses_string = optimized_addresses_string + '@' + str(customer_addresses[int(left_out_node[0])]) # Check whether you have to cast left_out_node to int.
		# You need to test left_out_node[0] thoroughly to make sure there is only one node left over all the time. 
	print routes_string
	
	
	
	session["list_of_routes"] = routes_string
	print("list_of_addresses:")
	print(optimized_addresses_string)
	session["list_of_addresses"] = optimized_addresses_string
    
    
    

	
	
	#return jsonify(result=optimized_routes)
	return jsonify(result=routes_string)

	
	#return render_template("paths.html")
#@app.route('/render')
#def render_paths():
 
if __name__ == '__main__':
#   app.run(debug=True)
#   app.run(threaded=True)
    app.run(host=0.0.0.0)