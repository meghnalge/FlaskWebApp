
from datetime import datetime
from flask import render_template
from FlaskWeb import app
from flask import Flask, render_template, request, redirect, url_for, session
import pandas as pd
import pymysql
import os
import io
from pulp import *
import numpy as np
import pymysql
import pymysql.cursors
from pandas.io import sql
import pandas as pd
import numpy as np
import scipy.optimize as optimize
from math import sin, cos, sqrt, atan2, radians
#from sqlalchemy import create_engine
from collections import defaultdict
import scipy.stats as st
import pandas as pd
import numpy as np
from pulp import *
import pymysql
import math
import pyodbc

# app = Flask(__name__)
# app.secret_key = os.urandom(24)
localaddress="D:\\home\\site\\wwwroot\\FlaskWeb"
localpath=localaddress
os.chdir(localaddress)
@app.route('/')
def index():
    return redirect(url_for('home'))
@app.route('/home')
def home():
    return render_template('home.html')
	
@app.route("/Inventorymanagment",methods=["GET","POST"]) 
def Inventorymanagment():
    return render_template("Inventory_Management.html")
@app.route("/DISTRIBUTION_NETWORK_OPT",methods=["GET","POST"]) 
def DISTRIBUTION_NETWORK_OPT():
    return render_template("DISTRIBUTION_NETWORK_OPTIMIZATION.html")
@app.route("/Procurement_Plan",methods=["GET","POST"]) 
def Procurement_Plan():
    return render_template("Procurement_Planning.html")

#RAJESH THING

@app.route("/fleetallocation")
def fleetallocation():
	return render_template('fleetallocation.html')

@app.route("/reset")
def reset():

	conn = pymysql.connect(host='scdemoserver.mysql.database.azure.com',user='myadmin@scdemoserver',password='Megh@4420',db='Inventory_Management',charset='utf8mb4',cursorclass=pymysql.cursors.DictCursor)
	cur = conn.cursor()
	cur.execute("DELETE FROM `input`")
	cur.execute("DELETE FROM `output`")
	cur.execute("DELETE FROM `Scenario`")
	conn.commit()
	conn.close()
	open(localaddress+'\\static\\demodata.txt', 'w').close()
	return render_template('fleetallocation.html')

@app.route("/dalink",methods = ['GET','POST'])
def dalink():
	sql = "INSERT INTO `input` (`Route`,`SLoc`,`Ship-to Abb`,`Primary Equipment`,`Batch`,`Prod Dt`,`SW`,`Met Held`,`Heat No`,`Delivery Qty`,`Width`,`Length`,`Test Cut`,`Customer Priority`) VALUES( %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
	conn = pymysql.connect(host='scdemoserver.mysql.database.azure.com',
		user='myadmin@scdemoserver',password='Megh@4420',
		db='inventory_management',charset='utf8mb4',
		cursorclass=pymysql.cursors.DictCursor, ssl = {'ssl': {'ca': '/var/www/html/BaltimoreCyberTrustRoot.crt.pem'}})
	cur = conn.cursor()
	if request.method == 'POST':
		typ = request.form.get('type')
		frm = request.form.get('from')
		to = request.form.get('to')
		if typ and frm and to:
			conn = pymysql.connect(host='scdemoserver.mysql.database.azure.com',
				user='myadmin@scdemoserver',
				password='Megh@4420',
				db='Inventory_Management',
				charset='utf8mb4',
				cursorclass=pymysql.cursors.DictCursor, 
				ssl = {'ssl': {'ca': '/var/www/html/BaltimoreCyberTrustRoot.crt.pem'}})
				
			cur = conn.cursor()
			cur.execute("SELECT * FROM `inventory_data` WHERE `Primary Equipment` = '" + typ + "' AND `Prod Dt` BETWEEN '" + frm + "' AND '" + to + "'")
			res = cur.fetchall()


			if len(res)==0:
				conn.close()
				return render_template('fleetallocation.html',alert='No data available')
			sfile = pd.DataFrame(res)
			df1 = pd.DataFrame(sfile)
			df1['Prod Dt'] =df1['Prod Dt'].astype(object)
			for index, i in df1.iterrows():
				data = (i['Route'],i['SLoc'],i['Ship-to Abb'],i['Primary Equipment'],i['Batch'],i['Prod Dt'],i['SW'],i['Met Held'],i['Heat No'],i['Delivery Qty'],i['Width'],i['Length'],i['Test Cut'],i['Customer Priority'])
				cur.execute(sql,data)
			conn.commit()
			conn.close()
			return render_template('fleetallocation.html',typ="   Equipment type: "+typ,frm="From: "+frm,to="   To:"+to,data = sfile.to_html(index=False))
		else:
			return render_template('fleetallocation.html',alert ='All input fields are required')
	return render_template('fleetallocation.html')

@app.route('/optimise', methods=['GET', 'POST'])
def optimise():
	open(localaddress+'\\static\\demodata.txt', 'w').close()
	conn = pymysql.connect(host='scdemoserver.mysql.database.azure.com',
		user='myadmin@scdemoserver',password='Megh@4420',
		db='inventory_management',charset='utf8mb4',
		cursorclass=pymysql.cursors.DictCursor, ssl = {'ssl': {'ca': '/var/www/html/BaltimoreCyberTrustRoot.crt.pem'}})
	cur = conn.cursor()
	curr = conn.cursor()
	cur.execute("DELETE FROM `output`")
	conn.commit()
	os.system('python optimising.py')

	sa=1
	cur.execute("SELECT * FROM `output`")
	result = cur.fetchall()
	if len(result)==0:
		say=0
	else:
		say=1
	curr.execute("SELECT * FROM `input`")
	sfile = curr.fetchall()
	if len(sfile)==0:
		conn.close()
		return render_template('fleetallocation.html',say=say,sa=sa,alert='No data available')
	sfile = pd.DataFrame(sfile)
	conn.close()
	with open(localaddress+"\\static\\demodata.txt", "r") as f:
		content = f.read()
	return render_template('fleetallocation.html',say=say,sa=sa,data = sfile.to_html(index=False),content=content)

@app.route("/scenario")
def scenario():
	return render_template('scenario.html')

@app.route("/scenario_insert", methods=['GET','POST'])
def scenario_insert():
		if request.method == 'POST':
			scenario = request.form.getlist("scenario[]")
			customer_priority = request.form.getlist("customer_priority[]")
			oldest_sw = request.form.getlist("oldest_sw[]")
			production_date = request.form.getlist("production_date[]")
			met_held_group = request.form.getlist("met_held_group[]")
			test_cut_group = request.form.getlist("test_cut_group[]")
			sub_grouping_rules = request.form.getlist("sub_grouping_rules[]")
			load_lower_bounds = request.form.getlist("load_lower_bounds[]")
			load_upper_bounds = request.form.getlist("load_upper_bounds[]")
			width_bounds = request.form.getlist("width_bounds[]")
			length_bounds = request.form.getlist("length_bounds[]")
			description = request.form.getlist("description[]")
			
			conn = pymysql.connect(host='scdemoserver.mysql.database.azure.com',
				user='myadmin@scdemoserver',password='Megh@4420',
				db='inventory_management',charset='utf8mb4',
				cursorclass=pymysql.cursors.DictCursor, ssl = {'ssl': {'ca': '/var/www/html/BaltimoreCyberTrustRoot.crt.pem'}})
			cur = conn.cursor()
			curr = conn.cursor()
			lngth = len(scenario)
			curr.execute("DELETE FROM `scenario`")
			if scenario and customer_priority and oldest_sw and production_date and met_held_group and test_cut_group and sub_grouping_rules and load_lower_bounds and load_upper_bounds and width_bounds and length_bounds and description:
				say=0
				for i in range(lngth):
					scenario_clean = scenario[i]
					customer_priority_clean = customer_priority[i]
					oldest_sw_clean = oldest_sw[i]
					production_date_clean = production_date[i]
					met_held_group_clean = met_held_group[i]
					test_cut_group_clean = test_cut_group[i]
					sub_grouping_rules_clean = sub_grouping_rules[i]
					load_lower_bounds_clean = load_lower_bounds[i]
					load_upper_bounds_clean = load_upper_bounds[i]
					width_bounds_clean = width_bounds[i]
					length_bounds_clean = length_bounds[i]
					description_clean = description[i]
					if scenario_clean and customer_priority_clean and oldest_sw_clean and production_date_clean and met_held_group_clean and test_cut_group_clean and sub_grouping_rules_clean and load_lower_bounds_clean and load_upper_bounds_clean and width_bounds_clean and length_bounds_clean:
						cur.execute("INSERT INTO `scenario`(scenario, customer_priority, oldest_sw, production_date, met_held_group, test_cut_group, sub_grouping_rules, load_lower_bounds, load_upper_bounds, width_bounds, length_bounds, description) VALUES('"+scenario_clean+"' ,'"+customer_priority_clean+"','"+oldest_sw_clean+"','"+production_date_clean+"','"+met_held_group_clean+"','"+test_cut_group_clean+"', '"+sub_grouping_rules_clean+"','"+load_lower_bounds_clean+"', '"+load_upper_bounds_clean+"','"+width_bounds_clean+"','"+length_bounds_clean+"','"+description_clean+"')")
					else:
						say = 1
					conn.commit()
				if(say==0):
					alert='All Scenarios inserted'
				else:
					alert='Some scenarios were not inserted'
				return (alert)
			conn.close()
			return ('All fields are required!')
		return ('Failed!!!')

@app.route("/fetch", methods=['GET','POST'])
def fetch():
		if request.method == 'POST':
			conn = pymysql.connect(host='scdemoserver.mysql.database.azure.com',
				user='myadmin@scdemoserver',password='Megh@4420',
				db='inventory_management',charset='utf8mb4',
				cursorclass=pymysql.cursors.DictCursor, ssl = {'ssl': {'ca': '/var/www/html/BaltimoreCyberTrustRoot.crt.pem'}})
			cur = conn.cursor()
			cur.execute("SELECT * FROM scenario")
			result = cur.fetchall()
			if len(result)==0:
				conn.close()
				return render_template('scenario.html',alert1='No scenarios Available')
			result1 = pd.DataFrame(result)
			result1 = result1.drop('Sub-grouping rules', axis=1)
			conn.close()
			return render_template('scenario.html',sdata = result1.to_html(index=False))
		return ("Error")

@app.route("/delete", methods=['GET','POST'])
def delete():
		if request.method == 'POST':
			conn = pymysql.connect(host='scdemoserver.mysql.database.azure.com',
				user='myadmin@scdemoserver',password='Megh@4420',
				db='inventory_management',charset='utf8mb4',
				cursorclass=pymysql.cursors.DictCursor, ssl = {'ssl': {'ca': '/var/www/html/BaltimoreCyberTrustRoot.crt.pem'}})
			cur = conn.cursor()
			cur.execute("DELETE FROM scenario")
			conn.commit()
			conn.close()
			return render_template('scenario.html',alert1="All the scenerios were dropped!")
		return ("Error")

@app.route('/papadashboard', methods=['GET', 'POST'])
def papadashboard():
		sql1 = "SELECT `Scenario`, MAX(`Wagon-No`) AS 'Wagon Used', COUNT(`Batch`) AS 'Products Allocated', SUM(`Delivery Qty`) AS 'Total Product Allocated', SUM(`Delivery Qty`)/(MAX(`Wagon-No`)) AS 'Average Load Carried', SUM(`Width`)/(MAX(`Wagon-No`)) AS 'Average Width Used' FROM `output` WHERE `Wagon-No`>0 GROUP BY `Scenario`"
		
		conn = pymysql.connect(host='scdemoserver.mysql.database.azure.com',
			user='myadmin@scdemoserver',password='Megh@4420',
			db='inventory_management',charset='utf8mb4',
			cursorclass=pymysql.cursors.DictCursor, ssl = {'ssl': {'ca': '/var/www/html/BaltimoreCyberTrustRoot.crt.pem'}})
		curs = conn.cursor()
		curs.execute("SELECT `scenario` FROM `scenario`")
		sdata = curs.fetchall()
		if len(sdata)==0:
			conn.close()
			return render_template('warning.html',alert='No data available')
		cur1 = conn.cursor()
		cur1.execute(sql1)
		data1 = cur1.fetchall()
		if len(data1)==0:
			conn.close()
			return render_template('warning.html',alert='Infeasible to due Insufficient Load')
		cu = conn.cursor()
		cu.execute("SELECT `length_bounds`,`width_bounds`,`load_lower_bounds`,`load_upper_bounds` FROM `scenario`")
		sdaa = cu.fetchall()
		sdaa = pd.DataFrame(sdaa)
		asa=list()
		for index, i in sdaa.iterrows():
			hover = "Length Bound:"+str(i['length_bounds'])+", Width Bound:"+str(i['width_bounds'])+", Load Upper Bound:"+str(i['load_upper_bounds'])+", Load Lower Bound:"+str(i['load_lower_bounds'])
			asa.append(hover)
		asa=pd.DataFrame(asa)
		asa.columns=['Details']
		data1 = pd.DataFrame(data1)
		data1['Average Width Used'] = data1['Average Width Used'].astype(int)
		data1['Total Product Allocated'] = data1['Total Product Allocated'].astype(int)
		data1['Average Load Carried'] = data1['Average Load Carried'].astype(float)
		data1['Average Load Carried'] = round(data1['Average Load Carried'],2)
		data1['Average Load Carried'] = data1['Average Load Carried'].astype(str)
		fdata = pd.DataFrame(columns=['Scenario','Wagon Used','Products Allocated','Total Product Allocated','Average Load Carried','Average Width Used','Details'])
		fdata[['Scenario','Wagon Used','Products Allocated','Total Product Allocated','Average Load Carried','Average Width Used']] = data1[['Scenario','Wagon Used','Products Allocated','Total Product Allocated','Average Load Carried','Average Width Used']]
		fdata['Details'] = asa['Details']
		fdata = fdata.values

		sql11 = "SELECT `Scenario`, SUM(`Delivery Qty`)/(MAX(`Wagon-No`)) AS 'Average Load Carried', COUNT(`Batch`) AS 'Allocated', SUM(`Delivery Qty`) AS 'Load Allocated' FROM `output`WHERE `Wagon-No`>0 GROUP BY `Scenario`"
		sql21 = "SELECT COUNT(`Batch`) AS 'Total Allocated' FROM `output` GROUP BY `Scenario`"
		sql31 = "SELECT `load_upper_bounds` FROM `scenario`"
		conn1 = pymysql.connect(host='scdemoserver.mysql.database.azure.com',
			user='myadmin@scdemoserver',password='Megh@4420',
			db='inventory_management',charset='utf8mb4',
			cursorclass=pymysql.cursors.DictCursor, ssl = {'ssl': {'ca': '/var/www/html/BaltimoreCyberTrustRoot.crt.pem'}})
		cur11 = conn1.cursor()
		cur21 = conn1.cursor()
		cur31 = conn1.cursor()
		cur11.execute(sql11)
		data11 = cur11.fetchall()
		data11 = pd.DataFrame(data11)
		cur21.execute(sql21)
		data21 = cur21.fetchall()
		data21 = pd.DataFrame(data21)
		cur31.execute(sql31)
		data31 = cur31.fetchall()
		data31 = pd.DataFrame(data31)
		data11['Average Load Carried']=data11['Average Load Carried'].astype(float)
		fdata1 = pd.DataFrame(columns=['Scenario','Utilisation Percent','Allocation Percent','Total Load Allocated'])
		fdata1['Utilisation Percent'] = round(100*(data11['Average Load Carried']/data31['load_upper_bounds']),2)
		data11['Load Allocated']=data11['Load Allocated'].astype(int)
		fdata1[['Scenario','Total Load Allocated']]=data11[['Scenario','Load Allocated']]
		data11['Allocated']=data11['Allocated'].astype(float)
		data21['Total Allocated']=data21['Total Allocated'].astype(float)
		fdata1['Allocation Percent'] = round(100*(data11['Allocated']/data21['Total Allocated']),2)
		fdata1['Allocation Percent'] = fdata1['Allocation Percent'].astype(str)
		fdat1 = fdata1.values
		conn1.close()

		if request.method == 'POST':
			conn2 = pymysql.connect(host='scdemoserver.mysql.database.azure.com',
				user='myadmin@scdemoserver',password='Megh@4420',
				db='inventory_management',charset='utf8mb4',
				cursorclass=pymysql.cursors.DictCursor, ssl = {'ssl': {'ca': '/var/www/html/BaltimoreCyberTrustRoot.crt.pem'}})
			cur = conn2.cursor()
			ata = request.form['name']
			cur.execute("SELECT * FROM `output` WHERE `Scenario` = '"+ata+"' ")
			ssdata = cur.fetchall()
			datasss = pd.DataFrame(ssdata)
			data=datasss.replace("Not Allocated", 0)
			df=data[['Delivery Qty','Wagon-No','Width','Group-Number']]
			df['Wagon-No']=df['Wagon-No'].astype(int)
			a=df['Wagon-No'].max()
			
			##bar1
			result_array = np.array([])
			for i in range (a):
				data_i = df[df['Wagon-No'] == i+1]
				del_sum_i = data_i['Delivery Qty'].sum()
				per_i=[((del_sum_i)/(205000)*100)]
				result_array = np.append(result_array, per_i)
			
			result_array1 = np.array([])
			for j in range (a):
				data_j = df[df['Wagon-No'] == j+1]
				del_sum_j = data_j['Width'].sum()
				per_util_j=[((del_sum_j)/(370)*100)]
				result_array1 = np.append(result_array1, per_util_j)
			##pie1           
			df112 = df[df['Wagon-No'] == 0]
			pie1 = df112 ['Width'].sum()
				   
			df221 = df[df['Wagon-No'] > 0]
			pie11 = df221['Width'].sum()
			
			df1=data[['SW','Group-Number']]
			dff1 = df1[data['Wagon-No'] == 0]
			da1 =dff1.groupby(['SW']).count()
			re11 = np.array([])
			res12 = np.append(re11,da1)
			da1['SW'] = da1.index
			r1 = np.array([])
			r12 = np.append(r1, da1['SW'])
			df0=data[['Group-Number','Route','SLoc','Ship-to Abb','Wagon-No','Primary Equipment']]
			df1=df0.replace("Not Allocated", 0)
			f2 = pd.DataFrame(df1)
			f2['Wagon-No']=f2['Wagon-No'].astype(int)
			####Not-Allocated
			f2['Group']=data['Group-Number']
			df=f2[['Group','Wagon-No']]
			dee =  df[df['Wagon-No'] == 0]
			deer =dee.groupby(['Group']).count()##Not Allocated
			deer['Group'] = deer.index
			##Total-Data
			f2['Group1']=data['Group-Number']
			dfc=f2[['Group1','Wagon-No']]
			dfa=pd.DataFrame(dfc)
			der = dfa[dfa['Wagon-No'] >= 0]
			dear =der.groupby(['Group1']).count()##Wagons >1
			
			dear['Group1'] = dear.index
			dear.rename(columns={'Wagon-No': 'Allocated'}, inplace=True)
							 
			result = pd.concat([deer, dear], axis=1, join_axes=[dear.index])
			resu=result[['Group1','Wagon-No','Allocated']]
			result1=resu.fillna(00)
			
				
			r5 = np.array([])
			r6 = np.append(r5, result1['Wagon-No'])
			r66=r6[0:73]###Not Allocated
			r7 = np.append(r5, result1['Allocated'])
			r77=r7[0:73]####total
			r8 = np.append(r5, result1['Group1'])
			r88=r8[0:73]###group

			conn2.close()
			return render_template('papadashboard.html',say=1,data=fdata,data1=fdat1,ata=ata,bar1=result_array,bar11=result_array1,pie11=pie1,pie111=pie11,x=r12,y=res12,xname=r88, bar7=r77,bar8=r66)
		conn.close()
		return render_template('papadashboard.html',data=fdata,data1=fdat1)

@app.route('/facilityallocation')
def facilityallocation():
		return render_template('facilityhome.html')
		
@app.route('/dataimport')
def dataimport():
		return render_template('facilityimport.html')
		
@app.route('/dataimport1')		
def dataimport1():
		return redirect(url_for('dataimport'))
		
@app.route('/facility_location')
def facility_location():
		return render_template('facility_location.html')

@app.route('/facility')
def facility():
		return redirect(url_for('facilityallocation'))

@app.route("/imprt", methods=['GET','POST'])
def imprt():
		global customerdata
		global factorydata
		global Facyy
		global Custo
		customerfile = request.files['CustomerData'].read()
		factoryfile = request.files['FactoryData'].read()
		if len(customerfile)==0 or len(factoryfile)==0:
			return render_template('facilityhome.html',warning='Data Invalid')
		cdat=pd.read_csv(io.StringIO(customerfile.decode('utf-8')))
		customerdata=pd.DataFrame(cdat)
		fdat=pd.read_csv(io.StringIO(factoryfile.decode('utf-8')))
		factorydata=pd.DataFrame(fdat)
		Custo=customerdata.drop(['Lat','Long'],axis=1)
		Facyy=factorydata.drop(['Lat','Long'],axis=1)
		return render_template('facilityimport1.html',loc1=factorydata.values,loc2=customerdata.values,factory=Facyy.to_html(index=False),customer=Custo.to_html(index=False))

@app.route("/gmap")
def gmap():
		custdata=customerdata
		Factorydata=factorydata
		price=1
		#to get distance beetween customer and factory
		#first get the Dimension
		#get no of factories
		Numberoffact=len(Factorydata)

		#get Number of Customer
		Numberofcust=len(custdata)

		#Get The dist/unit cost
		cost=price

		#def function for distance calculation
		# approximate radius of earth in km
		def dist(lati1,long1,lati2,long2,cost):
				   R = 6373.0
				   lat1 = radians(lati1)
				   lon1 = radians(long1)
				   lat2 = radians(lati2)
				   lon2 = radians(long2)
				   dlon = lon2 - lon1
				   dlat = lat2 - lat1
				   a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
				   c = 2 * atan2(sqrt(a), sqrt(1 - a))
				   distance =round(R * c,2)
				   return distance*cost     
		#Create a list for customer and factory
		def costtable(custdata,Factorydata):
				  distance=list()     
				  for lat1,long1 in zip(custdata.Lat, custdata.Long):
						 for lat2,long2 in zip(Factorydata.Lat, Factorydata.Long):
								   distance.append(dist(lat1,long1,lat2,long2,cost))
				  distable=np.reshape(distance, (Numberofcust,Numberoffact)).T
				  tab=pd.DataFrame(distable,index=[Factorydata.Factory],columns=[custdata.Customer])
				  return tab

		DelCost=costtable(custdata,Factorydata)#return cost table of the customer and factoery

		#creating Demand Table
		demand=np.array(custdata.Demand)
		col1=np.array(custdata.Customer)
		Demand=pd.DataFrame(demand,col1).T
		cols=sorted(col1)

		#Creating capacity table
		fact=np.array(Factorydata.Capacity)
		col2=np.array(Factorydata.Factory)
		Capacity=pd.DataFrame(fact,index=col2).T
		colo=sorted(col2)

		#creating Fixed cost table
		fixed_c=np.array(Factorydata.FixedCost)
		col3=np.array(Factorydata.Factory)
		FixedCost= pd.DataFrame(fixed_c,index=col3)


		# Create the 'prob' variable to contain the problem data
		model = LpProblem("Min Cost Facility Location problem",LpMinimize)
		production = pulp.LpVariable.dicts("Production",
											 ((factory, cust) for factory in Capacity for cust in Demand),
											 lowBound=0,
											 cat='Integer')

		factory_status =pulp.LpVariable.dicts("factory_status", (factory for factory in Capacity),
											 cat='Binary')

		cap_slack =pulp.LpVariable.dicts("capslack",
											 (cust for cust in Demand),
											 lowBound=0,
											 cat='Integer')


		model += pulp.lpSum(
			[DelCost.loc[factory, cust] * production[factory, cust] for factory in Capacity for cust in Demand]
			+ [FixedCost.loc[factory] * factory_status[factory] for factory in Capacity] + 5000000*cap_slack[cust] for cust in Demand)

		for cust in Demand:
			model += pulp.lpSum(production[factory, cust] for factory in Capacity)+cap_slack[cust] == Demand[cust]
			
		for factory in Capacity:
			model += pulp.lpSum(production[factory, cust] for cust in Demand) <= Capacity[factory]*factory_status[factory]

		model.solve()
		print("Status:", LpStatus[model.status])

		for v in model.variables():
			print(v.name, "=", v.varValue)

			
		print("Total Cost of Ingredients per can = ", value(model.objective))
		# Getting the table for the Factorywise Allocation
		def factoryalloc(model,Numberoffact,Numberofcust,listoffac,listofcus):
				  listj=list()
				  listk=list()
				  listcaps=list()
				  for v in model.variables():
					   listj.append(v.varValue)
				  customer=listj[(len(listj)-Numberofcust-Numberoffact):(len(listj)-Numberoffact)]
				  del listj[(len(listj)-Numberoffact-Numberofcust):len(listj)]
				  for row in listj:
					  if row==0:
						  listk.append(0)
					  else:
						  listk.append(1)
				  x=np.reshape(listj,(Numberoffact,Numberofcust))
				  y=np.reshape(listk,(Numberoffact,Numberofcust))
				  FactoryAlloc_table=pd.DataFrame(x,index=listoffac,columns=listofcus)
				  Factorystatus=pd.DataFrame(y,index=listoffac,columns=listofcus)
				  return FactoryAlloc_table,Factorystatus,customer
			  
		Alltable,FactorystatusTable,ded=factoryalloc(model,Numberoffact,Numberofcust,colo,cols)

		Allstatus=list()
		dede=pd.DataFrame(ded,columns=['UnSatisfied'])
		finaldede=dede[dede.UnSatisfied != 0]
		colss=pd.DataFrame(cols,columns=['CustomerLocation'])
		fina=pd.concat([colss,finaldede],axis=1, join='inner')
		print(fina)

		for i in range(len(Alltable)):
			for j in range(len(Alltable.columns)):
				if (Alltable.loc[Alltable.index[i], Alltable.columns[j]]>0):
					all=[Alltable.index[i], Alltable.columns[j], Alltable.loc[Alltable.index[i], Alltable.columns[j]]]
					Allstatus.append(all)
		Status=pd.DataFrame(Allstatus,columns=['Factory','Customer','Allocation']).astype(str)

		#To get the Factory Data
		conn = pymysql.connect(host='scdemoserver.mysql.database.azure.com',
			user='myadmin@scdemoserver',password='Megh@4420',
			db='inventory_management',charset='utf8mb4',
			cursorclass=pymysql.cursors.DictCursor, ssl = {'ssl': {'ca': '/var/www/html/BaltimoreCyberTrustRoot.crt.pem'}})

		#Making Connection to the Database
		cur = con.cursor()
		con = pymysql.connect(host='scdemoserver.mysql.database.azure.com',
			user='myadmin@scdemoserver',password='Megh@4420',
			db='inventory_management',charset='utf8mb4',
			cursorclass=pymysql.cursors.DictCursor, ssl = {'ssl': {'ca': '/var/www/html/BaltimoreCyberTrustRoot.crt.pem'}})

		cur = con.cursor()
		cur1 = con.cursor()
		cur.execute("SELECT * FROM `facilityallocation`")
		file=cur.fetchall()
		dat=pd.DataFrame(file)
		lst=dat[['Factory','Customer']]
		mlst=[]
		names=lst['Factory'].unique().tolist()
		for name in names:
			lsty=lst.loc[lst.Factory==name]
			mlst.append(lsty.values)
		data=dat[['Factory','Customer','Allocation']]
		sql="SELECT SUM(`Allocation`) AS 'UseCapacity', `Factory` FROM `facilityallocation` GROUP BY `Factory`"
		cur1.execute(sql)
		file2=cur1.fetchall()
		udata=pd.DataFrame(file2)
		bdata=factorydata.sort_values(by=['Factory'])
		adata=bdata['Capacity']
		con.close()
		
		infdata=dat[['Customer','Factory','Allocation']]
		infodata=infdata.sort_values(by=['Customer'])
		namess=infodata.Customer.unique()
		lstyy=[]
		for nam in namess:
			bb=infodata[infodata.Customer==nam]
			comment=bb['Factory']+":"+bb['Allocation']
			prin=[nam,str(comment.values).strip('[]')]
			lstyy.append(prin)

		return render_template('facilityoptimise.html',say=1,lstyy=lstyy,x1=adata.values,x2=udata.values,dat=mlst,loc1=factorydata.values,
		loc2=customerdata.values,factory=Facyy.to_html(index=False),customer=Custo.to_html(index=False),summary=data.to_html(index=False))
