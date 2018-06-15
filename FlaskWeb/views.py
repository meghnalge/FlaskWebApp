

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

app = Flask(__name__)
app.secret_key = os.urandom(24)
localaddress="D:\\home\\site\\wwwroot"
localpath=localaddress
os.chdir(localaddress)
@app.route('/')
def index():
    return redirect(url_for('home'))
@app.route('/home')
def home():
    return render_template('home.html')
@app.route('/demandplanning')
def demandplanning():
    return render_template("Demand_Planning.html")
@app.route("/elasticopt",methods = ['GET','POST'])
def elasticopt():
    if request.method== 'POST':
        start_date =request.form['from']
        end_date=request.form['to']
        prdct_name=request.form['typedf']
#        connection = pymysql.connect(host='localhost',
#             user='user',
#             password='',
#             db='test',
#             charset='utf8mb4',
#             cursorclass=pymysql.cursors.DictCursor)
#
#        x=connection.cursor()
#        x.execute("select * from `transcdata`")
#        connection.commit()
#        datass=pd.DataFrame(x.fetchall())
        
        datass = pd.read_csv("C:\\Users\\1026819\\Downloads\\optimizdata.csv")

#        datas = datass[(datass['Week']>=start_date) & (datass['Week']<=end_date )]
        datas=datass
        df = datas[datas['Product'] == prdct_name]
        df=datass
        changeData=pd.concat([df['Product_Price'],df['Product_Qty']],axis=1)
        changep=[]
        changed=[]
        for i in range(0,len(changeData)-1):
            changep.append(changeData['Product_Price'].iloc[i]-changeData['Product_Price'].iloc[i+1])
            changed.append(changeData['Product_Qty'].iloc[1]-changeData['Product_Qty'].iloc[i+1])
        cpd=pd.concat([pd.DataFrame(changep),pd.DataFrame(changed)],axis=1)
        cpd.columns=['Product_Price','Product_Qty']   
        sortedpricedata=df.sort_values(['Product_Price'], ascending=[True])
        spq=pd.concat([sortedpricedata['Product_Price'],sortedpricedata['Product_Qty']],axis=1).reset_index(drop=True)
        
        pint=[]
        dint=[]
        
         
        x = spq['Product_Price']
        num_bins = 5
#        n, pint, patches = plt.hist(x, num_bins, facecolor='blue', alpha=0.5)
        
        
        y = spq['Product_Qty']
        num_bins = 5
#        n, dint, patches = plt.hist(y, num_bins, facecolor='blue', alpha=0.5)
               
        arr= np.zeros(shape=(len(pint),len(dint)))
        
        count=0      
        for i in range(0, len(pint)):
            lbp=pint[i]
            if i==len(pint)-1:
                ubp=pint[i]+1
            else:
                ubp=pint[i+1]
                    
            
            for j in range(0, len(dint)):
                    lbd=dint[j]
                    if j==len(dint)-1:
                        ubd=dint[j]+1
                    else:
                        ubd=dint[j+1]
                    print(lbd,ubd)
                    for k in range(0, len(spq)):
                        if (spq['Product_Price'].iloc[k]>=lbp\
                            and spq['Product_Price'].iloc[k]<ubp):
                             if(spq['Product_Qty'].iloc[k]>=lbd\
                                and spq['Product_Qty'].iloc[k]<ubd):
                                 count+=1
                                 arr[i][j]+=1
             
        price_range=np.zeros(shape=(len(pint),2))                           
        for j in range(0,len(pint)):
           lbp=pint[j]
           price_range[j][0]=lbp
           if j==len(pint)-1:
               ubp=pint[j]+1
               price_range[j][1]=ubp
           else:
               ubp=pint[j+1] 
               price_range[j][1]=ubp
               
        demand_range=np.zeros(shape=(len(dint),2))                           
        for j in range(0,len(dint)):
           lbd=dint[j]
           demand_range[j][0]=lbd
           if j==len(dint)-1:
               ubd=dint[j]+1
               demand_range[j][1]=ubd
           else:
               ubd=dint[j+1] 
               demand_range[j][1]=ubd
               
        pr=pd.DataFrame(price_range)
        pr.columns=['Price','Demand']
        dr=pd.DataFrame(demand_range)
        dr.columns=['Price','Demand']                         
                                 
                                 
        priceranges=pr.Price.astype(str).str.cat(pr.Demand.astype(str), sep='-')
        demandranges=dr.Price.astype(str).str.cat(dr.Demand.astype(str), sep='-')                         
                        
        price=pd.DataFrame(arr)
        price.columns=demandranges
        price.index=priceranges
        pp=price.reset_index()
        global data
        data=pd.concat([df['Week'],df['Product_Qty'],df['Product_Price'],df['Comp_Prod_Price'],df['Promo1'],df['Promo2'],df['overallsale']],axis=1)
        return render_template('dataview.html',cpd=cpd.values,pp=pp.to_html(index=False),data=data.to_html(index=False),graphdata=data.values,ss=1)
    return render_template('dataview.html')

@app.route('/priceelasticity',methods = ['GET','POST'])
def priceelasticity():
    return render_template('Optimisation_heatmap_revenue.html')
@app.route("/elasticity",methods = ['GET','POST'])
def elasticity():
    if request.method== 'POST':
        Price=0
        Average_Price=0
        Promotions=0
        Promotionss=0
        if request.form.get('Price'):
            Price=1
        if request.form.get('Average_Price'):
            Average_Price=1
        if request.form.get('Promotion_1'):
            Promotions=1
        if request.form.get('Promotion_2'):
            Promotionss=1
        Modeldata=pd.DataFrame()
        Modeldata['Product_Qty']=data.Product_Qty
        lst=[]
        for row in data.index:
            lst.append(row+1)
        Modeldata['Week']=np.log(lst)
        if Price == 1:
           Modeldata['Product_Price']=data['Product_Price']
        if Price == 0:
           Modeldata['Product_Price']=0
        if Average_Price==1:
           Modeldata['Comp_Prod_Price']=data['Comp_Prod_Price']
        if Average_Price==0:
           Modeldata['Comp_Prod_Price']=0  
        if Promotions==1:
         Modeldata['Promo1']=data['Promo1']
        if Promotions==0:
           Modeldata['Promo1']=0  
        if Promotionss==1:
            Modeldata['Promo2']=data['Promo2']
        if Promotionss==0:
            Modeldata['Promo2']=0
        diffpriceprodvscomp= (Modeldata['Product_Price']-Modeldata['Comp_Prod_Price'])
        
        promo1=Modeldata.Promo1
        promo2=Modeldata.Promo2
        week=Modeldata.Week
        quantityproduct=Modeldata.Product_Qty
        
        df=pd.concat([quantityproduct,diffpriceprodvscomp,promo1,promo2,week],axis=1)
        
        df.columns=['quantityproduct','diffpriceprodvscomp','promo1','promo2','week']
        
        Model = smf.ols(formula='df.quantityproduct ~ df.diffpriceprodvscomp + df.promo1 + df.promo2 + df.week', data=df)
        res = Model.fit()
        global intercept,diffpriceprodvscomp_param,promo1_param,promo2_param,week_param
        intercept=res.params[0]
        diffpriceprodvscomp_param=res.params[1]
        promo1_param=res.params[2]
        promo2_param=res.params[3]
        week_param=res.params[4]
        
        Product_Price_min=0
        maxvalue_of_price=int(Modeldata['Product_Price'].max())
        Product_Price_max=int(Modeldata['Product_Price'].max())
        if maxvalue_of_price==0:
            Product_Price_max=1
        
        maxfunction=[]
        pricev=[]
        weeks=[]
        dd=[]
        ddl=[]
        for vatr in range(0,len(Modeldata)):
            weeks.append(lst[vatr])
            for Product_Price in range(Product_Price_min,Product_Price_max+1):
                function=0
                function=(intercept+(Modeldata['Promo1'].iloc[vatr]*promo1_param)+(Modeldata['Promo2'].iloc[vatr]*promo2_param) +
                          (diffpriceprodvscomp_param*(Product_Price-Modeldata['Comp_Prod_Price'].iloc[vatr]))+(Modeldata['Week'].iloc[vatr]*lst[vatr]))
                maxfunction.append(function)
                dd.append(Product_Price)
                ddl.append(vatr)
        
        for Product_Price in range(Product_Price_min,Product_Price_max+1):
            pricev.append(Product_Price)
        df1=pd.DataFrame(maxfunction)
        df2=pd.DataFrame(dd)
        df3=pd.DataFrame(ddl)
        dfo=pd.concat([df3,df2,df1],axis=1)
        dfo.columns=['weeks','prices','Demandfunctions']
        demand=[]
        for rows in dfo.values:
            w=int(rows[0])
            p=int(rows[1])
            d=int(rows[2])
            demand.append([w,p,d])
        Co_eff=pd.DataFrame(res.params.values)#intercept
        standard_error=pd.DataFrame(res.bse.values)#standard error
        p_values=pd.DataFrame(res.pvalues.values)
        conf_lower =pd.DataFrame(res.conf_int()[0].values)
        conf_higher =pd.DataFrame(res.conf_int()[1].values)
        R_square=res.rsquared
        atr=['Intercept','DeltaPrice','Promo1','Promo2','Week']
        atribute=pd.DataFrame(atr)
        SummaryTable=pd.concat([atribute,Co_eff,standard_error,p_values,conf_lower,conf_higher],axis=1)
        SummaryTable.columns=['Atributes','Co_eff','Standard_error','P_values','conf_lower','conf_higher']    
        reshapedf=df1.values.reshape(len(Modeldata),(-Product_Price_min+(Product_Price_max+1)))
        
        dataofmas=pd.DataFrame(reshapedf)
        maxv=dataofmas.apply( max, axis=1 )
        minv=dataofmas.apply(min,axis=1)
        avgv=dataofmas.sum(axis=1)/(-Product_Price_min+(Product_Price_max+1))
        wks=pd.DataFrame(weeks)
        ddofs=pd.concat([wks,minv,avgv,maxv],axis=1)
        dataofmas=pd.DataFrame(reshapedf)
        
        kk=pd.DataFrame()
        sums=0
        for i in range(0,len(dataofmas.columns)):
         sums=sums+i
         vv=i*dataofmas[[i]]
         kk=pd.concat([kk,vv],axis=1)
        dfr=pd.DataFrame(kk)
        mrevenue=dfr.apply( max, axis=1 )
        prices=dfr.idxmax(axis=1)
        wks=pd.DataFrame(weeks)
        revenuedf=pd.concat([wks,mrevenue,prices],axis=1) 
            
        
        return render_template('Optimisation_heatmap_revenue.html',revenuedf=revenuedf.values,ddofs=ddofs.values,SummaryTable=SummaryTable.to_html(index=False),ss=1,weeks=weeks,demand=demand,pricev=pricev,R_square=R_square)
@app.route('/inputtomaxm',methods=["GET","POST"])
def inputtomaxm(): 
    return render_template("Optimize.html")
@app.route("/maxm",methods=["GET","POST"]) 
def maxm():
    if request.method=="POST":
            week=request.form['TimePeriod']
            price_low=request.form['Price_Lower']
            price_max=request.form['Price_Upper']
            promofirst=request.form['Promotion_1']
            promosecond=request.form['Promotion_2']
#            week=24
#            price_low=6
#            price_max=20
#            promofirst=1
#            promosecond=0
#
#            time_period=24
#    
#            global a
#            a=243.226225
#            global b
#            b=-9.699634
#            global d
#            d=1.671505
#            global pr1
#            pr1=21.866260
#            global pr2
#            pr2=-0.511606
#            global cm
#            cm=-14.559594
#            global s_0
#            s_0= 2000
#            promo1=1
#            promo2=0
            
            time_period=int(week)
            global a
            a=intercept
            global b
            b=diffpriceprodvscomp_param
            global d
            d=week_param
            global pr1
            pr1=promo1_param
            global pr2
            pr2=promo2_param
            global s_0
            s_0= 2000
            promo1=int(promofirst)
            promo2=int(promosecond)

            global comp
            comp=np.random.randint(7,15,time_period)

            def demand(p, a=a, b=b, d=d, promo1=promo1,promo2_param=promo2,comp=comp, t=np.linspace(1,time_period,time_period)):
                """ Return demand given an array of prices p for times t
                (see equation 5 above)"""
                return  a+(b*(p-comp))+(d*t)+(promo1*pr1)+(promo2*pr2)

            def objective(p_t, a, b, d,promo1,promo2, comp, t=np.linspace(1,time_period,time_period)):
          
                return -1.0 * np.sum( p_t * demand(p_t, a, b, d,promo1,promo2, comp, t) )


            def constraint_1(p_t, s_0, a, b, d, promo1,promo2, comp, t=np.linspace(1,time_period,time_period)):
                """ Inventory constraint. s_0 - np.sum(x_t) >= 0.
                This is an inequality constraint. See more below.
                """
                return s_0 - np.sum(demand(p_t, a, b, d,promo1,promo2, comp, t))

            def constraint_2(p_t):
            #""" Positive demand. Another inequality constraint x_t >= 0 """
                return p_t


            t = np.linspace(1,time_period,time_period)

            # Starting values :
            b_min=int(price_low)
            p_start = b_min * np.ones(len(t))
                # bounds on the values :
            bmax=int(price_max)
            bounds = tuple((0,bmax) for x in p_start)

            import scipy.optimize as optimize
            # Constraints :
            constraints = ({'type': 'ineq', 'fun':  lambda x, s_0=s_0:  constraint_1(x,s_0, a, b, d,promo1,promo2, comp, t=t)},
                        {'type': 'ineq', 'fun':  lambda x: constraint_2(x)}
                        )

            opt_results = optimize.minimize(objective, p_start, args=(a, b, d,promo1,promo2, comp, t),
                            method='SLSQP', bounds=bounds,  constraints=constraints)

            np.sum(opt_results['x'])
            opt_price=opt_results['x']
            opt_demand=demand(opt_results['x'], a, b, d, promo1,promo2_param, comp, t=t)
            weeks=[]
            for row in range(1,len(opt_price)+1):
                weeks.append(row)
            d=pd.DataFrame(weeks).astype(int)
            dd=pd.DataFrame(opt_price)
            optimumumprice_perweek=pd.concat([d,dd,pd.DataFrame(opt_demand).astype(int)],axis=1)
            optimumumprice_perweek.columns=['Week','Price','Demand']
            dataval=optimumumprice_perweek
            diff=[]
            diffs=[]
            for i in range(0,len(opt_demand)-1):
                valss=opt_demand[i]-opt_demand[i+1]
                diff.append(valss)
                diffs.append(i+1)
            differenceofdemand_df=pd.concat([pd.DataFrame(diffs),pd.DataFrame(diff)],axis=1)
            MP=round(optimumumprice_perweek.loc[optimumumprice_perweek['Price'].idxmin()],1)
            minimumprice=pd.DataFrame(MP).T
            MaxP=round(optimumumprice_perweek.loc[optimumumprice_perweek['Price'].idxmax()],1)
            maximumprice=pd.DataFrame(MaxP).T
            averageprice=round((optimumumprice_perweek['Price'].sum()/len(optimumumprice_perweek)),2)
            MD=round(optimumumprice_perweek.loc[optimumumprice_perweek['Demand'].idxmin()],0)
            minimumDemand=pd.DataFrame(MD).T
            MaxD=round(optimumumprice_perweek.loc[optimumumprice_perweek['Demand'].idxmax()],0)
            maximumDemand=pd.DataFrame(MaxD).T
            averageDemand=round((optimumumprice_perweek['Demand'].sum()/len(optimumumprice_perweek)),0)
            totaldemand=round(optimumumprice_perweek['Demand'].sum(),0)
            return render_template("Optimize.html",totaldemand=totaldemand,averageDemand=averageDemand,maximumDemand=maximumDemand.values,minimumDemand=minimumDemand.values,averageprice=averageprice,maximumprice=maximumprice.values,minimumprice=minimumprice.values,dataval=dataval.values,differenceofdemand_df=differenceofdemand_df.values,optimumumprice_perweek=optimumumprice_perweek.to_html(index=False),ll=1)
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
	conn = pymysql.connect(host='localhost',user='root',password='',db='inventory_management',charset='utf8mb4',cursorclass=pymysql.cursors.DictCursor)
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
	conn = pymysql.connect(host='localhost',user='root',password='',db='inventory_management',charset='utf8mb4',cursorclass=pymysql.cursors.DictCursor)
	cur = conn.cursor()
	if request.method == 'POST':
		typ = request.form.get('type')
		frm = request.form.get('from')
		to = request.form.get('to')
		if typ and frm and to:
			conn = pymysql.connect(host='localhost',user='root',password='',db='inventory_management',charset='utf8mb4',cursorclass=pymysql.cursors.DictCursor)
			cur = conn.cursor()
			curr = conn.cursor()
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
				curr.execute(sql,data)
			conn.commit()
			conn.close()
			return render_template('fleetallocation.html',typ="   Equipment type: "+typ,frm="From: "+frm,to="   To:"+to,data = sfile.to_html(index=False))
		else:
			return render_template('fleetallocation.html',alert ='All input fields are required')
	return render_template('fleetallocation.html')

@app.route('/optimise', methods=['GET', 'POST'])
def optimise():
	open(localaddress+'\\static\\demodata.txt', 'w').close()
	conn = pymysql.connect(host='localhost',user='root',password='',db='inventory_management',charset='utf8mb4',cursorclass=pymysql.cursors.DictCursor)
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
			conn = pymysql.connect(host='localhost',user='root',password='',db='inventory_management',charset='utf8mb4',cursorclass=pymysql.cursors.DictCursor)
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
			conn = pymysql.connect(host='localhost',user='root',password='',db='inventory_management',charset='utf8mb4',cursorclass=pymysql.cursors.DictCursor)
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
			conn = pymysql.connect(host='localhost',user='root',password='',db='inventory_management',charset='utf8mb4',cursorclass=pymysql.cursors.DictCursor)
			cur = conn.cursor()
			cur.execute("DELETE FROM scenario")
			conn.commit()
			conn.close()
			return render_template('scenario.html',alert1="All the scenerios were dropped!")
		return ("Error")

@app.route('/papadashboard', methods=['GET', 'POST'])
def papadashboard():
		sql1 = "SELECT `Scenario`, MAX(`Wagon-No`) AS 'Wagon Used', COUNT(`Batch`) AS 'Products Allocated', SUM(`Delivery Qty`) AS 'Total Product Allocated', SUM(`Delivery Qty`)/(MAX(`Wagon-No`)) AS 'Average Load Carried', SUM(`Width`)/(MAX(`Wagon-No`)) AS 'Average Width Used' FROM `output` WHERE `Wagon-No`>0 GROUP BY `Scenario`"
		conn = pymysql.connect(host='localhost',user='root',password='',db='inventory_management',charset='utf8mb4',cursorclass=pymysql.cursors.DictCursor)
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
		conn1 = pymysql.connect(host='localhost',user='root',password='',db='inventory_management',charset='utf8mb4',cursorclass=pymysql.cursors.DictCursor)
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
			conn2 = pymysql.connect(host='localhost',user='root',password='',db='inventory_management',charset='utf8mb4',cursorclass=pymysql.cursors.DictCursor)
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
		con = pymysql.connect(host='localhost',user='root',password='',db='inventory_management',charset='utf8mb4',cursorclass=pymysql.cursors.DictCursor)

		#Making Connection to the Database
		cur = con.cursor()
		engine = create_engine("mysql+pymysql://{user}:{pw}@localhost/{db}".format(user="root",pw="",db="inventory_management"))
		Status.to_sql(con=engine, name='facilityallocation',index=False, if_exists='replace')

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

#Demand Forecast
@app.route('/demandforecast')
def demandforecast():
		return render_template('demandforecast.html')


@app.route("/demandforecastdataimport",methods = ['GET','POST'])
def demandforecastdataimport():
		if request.method== 'POST':
			global actualforecastdata
			flat=request.files['flat'].read()
			if len(flat)==0:
				return('No Data Selected')
			cdat=pd.read_csv(io.StringIO(flat.decode('utf-8')))
			actualforecastdata=pd.DataFrame(cdat)
			return render_template('demandforecast.html',data=actualforecastdata.to_html(index=False))


@app.route('/demandforecastinput', methods = ['GET', 'POST'])
def demandforecastinput():
		if request.method=='POST':
			global demandforecastfrm
			global demandforecasttoo
			global demandforecastinputdata
			demandforecastfrm=request.form['from']
			demandforecasttoo=request.form['to']
			value=request.form['typedf']
			demandforecastinputdata=actualforecastdata[(actualforecastdata['Date'] >= demandforecastfrm) & (actualforecastdata['Date'] <= demandforecasttoo)]

			if value=='monthly': ##monthly
				engine = create_engine("mysql+pymysql://{user}:{pw}@localhost/{db}".format(user="root",pw="",db="inventory_management"))
				demandforecastinputdata.to_sql(con=engine, name='demandforecastinputdata', index=False,if_exists='replace')
				return redirect(url_for('monthlyforecast'))
			if value=='quarterly': ##quarterly
				global Quaterdata
				dated2 = demandforecastinputdata['Date']
				nlst=[]
				for var in dated2:
					var1 = int(var[5:7])
					if var1 >=1 and var1 <4:
						varr=var[:4]+'-01-01' 
					elif var1 >=4 and var1 <7:
						varr=var[:4]+'-04-01'        
					elif var1 >=7 and var1 <10:
						varr=var[:4]+'-07-01'        
					else:
						varr=var[:4]+'-10-01'
					nlst.append(varr)
				nwlst=pd.DataFrame(nlst,columns=['Newyear'])
				demandforecastinputdata=demandforecastinputdata.reset_index()
				demandforecastinputdata['Date']=nwlst['Newyear']
				Quaterdata=demandforecastinputdata.groupby(['Date']).sum()
				Quaterdata=Quaterdata.reset_index()
				Quaterdata=Quaterdata.drop('index',axis=1)
				engine = create_engine("mysql+pymysql://{user}:{pw}@localhost/{db}".format(user="root",pw="",db="inventory_management"))
				Quaterdata.to_sql(con=engine, name='demandforecastinputdata', index=False,if_exists='replace')
				return redirect(url_for('quarterlyforecast'))
			if value=='yearly': ##yearly
				global Yeardata
				#copydata=demandforecastinputdata
				dated1 = demandforecastinputdata['Date']
				lst=[]
				for var in dated1:
					var1 = var[:4]+'-01-01'
					lst.append(var1)

				newlst=pd.DataFrame(lst,columns=['NewYear'])
				demandforecastinputdata=demandforecastinputdata.reset_index()
				demandforecastinputdata['Date']=newlst['NewYear']
				Yeardata=demandforecastinputdata.groupby(['Date']).sum()
				Yeardata=Yeardata.reset_index()
				Yeardata=Yeardata.drop('index',axis=1)
				engine = create_engine("mysql+pymysql://{user}:{pw}@localhost/{db}".format(user="root",pw="",db="inventory_management"))
				Yeardata.to_sql(con=engine, name='demandforecastinputdata', index=False,if_exists='replace')
				
				return redirect(url_for('yearlyforecast'))

			#if value=='weakly': ##weakly
			#	return redirect(url_for('output4'))
		return render_template('demandforecast.html')


@app.route("/monthlyforecast",methods = ['GET','POST'])
def monthlyforecast():
		data = pd.DataFrame(demandforecastinputdata)
		# container1
		a1=data.sort_values(['GDP','TotalDemand'], ascending=[True,True])
		# container2
		a2=data.sort_values(['Pi_Exports','TotalDemand'], ascending=[True,True])
		# container3
		a3=data.sort_values(['Market_Share','TotalDemand'], ascending=[True,True])
		# container4
		a4=data.sort_values(['Advertisement_Expense','TotalDemand'], ascending=[True,True])
		# container1
		df=a1[['GDP']]
		re11 = np.array([])
		res11 = np.append(re11,df)

		df1=a1[['TotalDemand']]
		r1 = np.array([]) 
		r11 = np.append(r1, df1)

		# top graph
		tdf=data['Date'].astype(str)
		tre11 = np.array([])
		tres11 = np.append(tre11,tdf)
		tr1 = np.array([]) 
		tr11 = np.append(tr1, df1)

		# container2
		udf=a2[['Pi_Exports']]
		ure11 = np.array([])
		ures11 = np.append(ure11,udf)
		ur1 = np.array([]) 
		ur11 = np.append(ur1, df1)

		# container3
		vdf=a3[['Market_Share']]
		vre11 = np.array([])
		vres11 = np.append(vre11,vdf)
		vr1 = np.array([]) 
		vr11 = np.append(vr1, df1)

		# container4
		wdf=a4[['Advertisement_Expense']]
		wre11 = np.array([])
		wres11 = np.append(wre11,wdf)
		wr1 = np.array([])
		wr11 = np.append(wr1, df1)

		if request.method == 'POST':
			mov=0
			exp=0
			reg=0
			ari=0
			arx=0
			till = request.form.get('till')
			if request.form.get('moving'):
				mov=1

			if request.form.get('ESPO'):
				exp=1
				
			if request.form.get('regression'):
				reg=1
				
			if request.form.get('ARIMA'):
				ari=1
				
			if request.form.get('ARIMAX'):
				arx=1
			
			con = pymysql.connect(host='localhost',user='root',password='',db='inventory_management',charset='utf8mb4',cursorclass=pymysql.cursors.DictCursor)
			cur = con.cursor()
			cur.execute("CREATE TABLE IF NOT EXISTS `ftech` (`mov` VARCHAR(1),`exp` VARCHAR(1), `reg` VARCHAR(1),`ari` VARCHAR(1),`arx` VARCHAR(1),`till` VARCHAR(10))")
			cur.execute("DELETE FROM `ftech`")
			con.commit()
			cur.execute("INSERT INTO `ftech` VALUES('"+str(mov)+"','"+str(exp)+"','"+str(reg)+"','"+str(ari)+"','"+str(arx)+"','"+str(till)+"')")
			con.commit()
			cur.execute("CREATE TABLE IF NOT EXISTS `forecastoutput`(`Model` VARCHAR(25),`Date` VARCHAR(10),`TotalDemand` VARCHAR(10),`RatioIncrease` VARCHAR(10),`Spain` VARCHAR(10),`Austria` VARCHAR(10),`Japan` VARCHAR(10),`Hungary` VARCHAR(10),`Germany` VARCHAR(10),`Polland` VARCHAR(10),`UK` VARCHAR(10),`France` VARCHAR(10),`Romania` VARCHAR(10),`Italy` VARCHAR(10),`Greece` VARCHAR(10),`Crotia` VARCHAR(10),`Holland` VARCHAR(10),`Finland` VARCHAR(10),`Hongkong` VARCHAR(10))")
			con.commit()
			cur.execute("DELETE FROM `forecastoutput`")
			con.commit()
			sql = "INSERT INTO `forecastoutput` (`Model`,`Date`,`TotalDemand`,`RatioIncrease`,`Spain`,`Austria`,`Japan`,`Hungary`,`Germany`,`Polland`,`UK`,`France`,`Romania`,`Italy`,`Greece`,`Crotia`,`Holland`,`Finland`,`Hongkong`) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"


			#read the monthly file and index that with time
			df=data.set_index('Date')
			split_point =int(0.7*len(df))
			D, V = df[0:split_point],df[split_point:]
			data=pd.DataFrame(D)

			#Functions for ME, MAE, MAPE
			#ME
			def ME(y_true, y_pred):
				y_true, y_pred = np.array(y_true), np.array(y_pred)
				return np.mean(y_true - y_pred) 

			#MAE
			def MAE(y_true, y_pred):
				y_true, y_pred = np.array(y_true), np.array(y_pred)
				return np.mean(np.abs(y_true - y_pred))

			#MAPE 
			def MAPE(y_true, y_pred):
				y_true, y_pred = np.array(y_true), np.array(y_pred)
				return np.mean(np.abs((y_true - y_pred) / y_pred)) * 100 

			cur1=con.cursor()
			cur1.execute("SELECT * FROM `ftech`")
			ftech=pd.DataFrame(cur1.fetchall())
			ari=int(ftech['ari'])
			arx=int(ftech['arx'])
			exp=int(ftech['exp'])
			mov=int(ftech['mov'])
			reg=int(ftech['reg'])
			start_index1=str(D['GDP'].index[-1])
			end_index1=str(ftech['till'][0])
			#end_index1=indx[:4]

			df2 = pd.DataFrame(data=0,index=["ME","MAE","MAPE"],columns=["Moving Average","ARIMA","Exponential Smoothing","Regression"])

			if mov==1:
				#2---------------simple moving average-------------------------
				#################################MovingAverage#######################
				list1=list()
				def mavg(data):
					 m=len(data.columns.tolist())
					 for i in range(0,m-5):
						 #Arima Model Fitting
						 model1=ARIMA(data[data.columns.tolist()[i]].astype(float), order=(0,0,1))
						 results_ARIMA1=model1.fit(disp=0)   
			#             start_index1 = '2017-01-01'
			#             end_index1 = '2022-01-01' #4 year forecast
						 ARIMA_fit1= results_ARIMA1.fittedvalues
						 forecast2=results_ARIMA1.predict(start=start_index1, end=end_index1)
						 list1.append(forecast2)
						 if(i==0):
							 #ME
							 s=ME(data['TotalDemand'],ARIMA_fit1)
							 #MAE
							 so=MAE(data['TotalDemand'],ARIMA_fit1)
							 #MAPE 
							 son=MAPE(data['TotalDemand'],ARIMA_fit1)
							 df2["Moving Average"].iloc[0]=s
							 df2["Moving Average"].iloc[1]=so
							 df2["Moving Average"].iloc[2]=son
							 s=pd.DataFrame(forecast2)
							 ratio_inc=[]
							 ratio_inc.append(0)
							 for j in range(2,len(s)+1):
								 a=s.iloc[j-2]
								 b=s.iloc[j-1]
								 ratio_inc.append(int(((b-a)/a)*100))
					 return list1,ratio_inc
				print(data)
				Ma_Out,ratio_incma=mavg(data)
				dfs=pd.DataFrame(Ma_Out)
				tdfs=dfs.T
				print(tdfs)
				tdfs.columns=["TotalDemand","Spain","Austria","Japan","Hungary","Germany","Polland","UK","France","Romania","Italy","Greece","Crotia","Holland","Finland","Hongkong"]
				tdfs['Model']='Moving Average'
				tdfs['RatioIncrease']=ratio_incma
				tdfs['Date']=(tdfs.index).strftime("20%y-%m-%d")


				tdfs.astype(str)
				for index, i in tdfs.iterrows():
					dat = (i['Model'],i['Date'],i['TotalDemand'],i['RatioIncrease'],i['Spain'],i['Austria'],i['Japan'],i['Hungary'],i['Germany'],i['Polland'],i['UK'],i['France'],i['Romania'],i['Italy'],i['Greece'],i['Crotia'],i['Holland'],i['Finland'],i['Hongkong'])
					cur.execute(sql,dat)
					con.commit()
				
				
			if ari==1:
				##--------------min errors--ARIMA (1,0,0)----------------------------- 
				############################for Total Demand Monthly####################################
				list2=list()
				def AutoRimavg(data):
					 m=len(data.columns.tolist())
					 for i in range(0,m-5):
						 #Arima Model Fitting
						 model1=ARIMA(data[data.columns.tolist()[i]].astype(float), order=(1,0,0))
						 results_ARIMA1=model1.fit(disp=0)   
						 ARIMA_fit1= results_ARIMA1.fittedvalues
						 forecast2=results_ARIMA1.predict(start=start_index1, end=end_index1)
						 list2.append(forecast2)
						 if(i==0):
							  #ME
							 s=ME(data['TotalDemand'],ARIMA_fit1)
							 #MAE
							 so=MAE(data['TotalDemand'],ARIMA_fit1)
							 #MAPE 
							 son=MAPE(data['TotalDemand'],ARIMA_fit1)
							 df2["ARIMA"].iloc[0]=s
							 df2["ARIMA"].iloc[1]=so
							 df2["ARIMA"].iloc[2]=son
							 Ars=pd.DataFrame(forecast2)
							 ratio_inc=[]
							 ratio_inc.append(0)
							 for j in range(2,len(Ars)+1):
								 As=(Ars.iloc[j-2])
								 bs=(Ars.iloc[j-1])
								 ratio_inc.append(int(((As-bs)/As)*100))
					 return list1,ratio_inc
				
						
				Arimamodel,ratio_inc=AutoRimavg(data)
				Amodel=pd.DataFrame(Arimamodel)
				Results=Amodel.T
				Results.astype(str)
				Results.columns=["TotalDemand","Spain","Austria","Japan","Hungary","Germany","Polland","UK","France","Romania","Italy","Greece","Crotia","Holland","Finland","Hongkong"]
				Results['Model']="ARIMA"
				Results['RatioIncrease']=ratio_inc
				Results['Date']=Results.index.astype(str)
				
				for index, i in Results.iterrows():
					dat = (i['Model'],i['Date'],i['TotalDemand'],i['RatioIncrease'],i['Spain'],i['Austria'],i['Japan'],i['Hungary'],i['Germany'],i['Polland'],i['UK'],i['France'],i['Romania'],i['Italy'],i['Greece'],i['Crotia'],i['Holland'],i['Finland'],i['Hongkong'])
					cur.execute(sql,dat)
					con.commit()

			if reg==1:
				
				#Linear Regression
				#Regression Modeling
				dates=pd.date_range(start_index1,end_index1,freq='M')
				lprd=len(dates)
				dateofterms= pd.PeriodIndex(freq='M', start=start_index1, periods=lprd+1)
				dofterm=dateofterms.strftime("20%y-%m-%d")
				Rdate=pd.DataFrame(dofterm)
				noofterms=len(dofterm)
				def regression(data,V,noofterms):
					#Getting length of Data Frame
					lenofdf=len(data.columns.tolist())

					#Getting List Of Atributes in Data Frame
					listofatr=list()
					listofatr=data.columns.tolist()

					#making list of pred
					pred=pd.DataFrame()

					#now riun for each row
					for i in range(0,(lenofdf)-5):
						df=pd.DataFrame(data[data.columns.tolist()[i]].reset_index())
						xvar=list()
						for row in df[listofatr[i]]:
							xvar.append(row)
						df5=pd.DataFrame(xvar)
						yvar=list()
						for j in range(0,len(df[listofatr[i]])):
							yvar.append(j)
						dfss=pd.DataFrame(yvar)
						clf = linear_model.LinearRegression()
						clf.fit(dfss,df5)
						# Make predictions using the testing set

						dfv=pd.DataFrame(V[V.columns.tolist()[i]].reset_index())
						k=list()
						for l in range(len(df[listofatr[i]]),len(df[listofatr[i]])+len(dfv)):
							k.append(l)
						ks=pd.DataFrame(k)

						#Future prediction

						predlist=list()
						for j in range(len(df[listofatr[i]]),len(df[listofatr[i]])+noofterms):
							predlist.append(j)
						dataframeoflenofpred=pd.DataFrame(predlist)
						dateframeofpred=pd.DataFrame(clf.predict(dataframeoflenofpred))
						pred=pd.concat([pred,dateframeofpred],axis=1)

						#Accuracy Of the mODEL
						y_pred = clf.predict(ks)
						if(i==0):
							meanerror=ME(dfv[listofatr[i]], y_pred)
							mae=MAE(dfv[listofatr[i]], y_pred)
							mape=MAPE(dfv[listofatr[i]],y_pred)
							df2["Regression"].iloc[0]=meanerror
							df2["Regression"].iloc[1]=mae
							df2["Regression"].iloc[2]=mape
							regp=pd.DataFrame(pred)
							ratio_incrr=[]
							ratio_incrr.append(0)
							for j in range(2,len(regp)+1):
									 Ra=regp.iloc[j-2]
									 Rb=regp.iloc[j-1]
									 ratio_incrr.append(int(((Rb-Ra)/Ra)*100))
					return pred,ratio_incrr
				monthlyRegression,ratio_incrr=regression(data,V,noofterms)
				r=pd.DataFrame(monthlyRegression)
				r.columns=["TotalDemand","Spain","Austria","Japan","Hungary","Germany","Polland","UK","France","Romania","Italy","Greece","Crotia","Holland","Finland","Hongkong"]
				r['Model']="Regression"
				r['Date']=Rdate
				r['RatioIncrease']=ratio_incrr
				r.astype(str)
				for index, i in r.iterrows():
					dat = (i['Model'],i['Date'],i['TotalDemand'],i['RatioIncrease'],i['Spain'],i['Austria'],i['Japan'],i['Hungary'],i['Germany'],i['Polland'],i['UK'],i['France'],i['Romania'],i['Italy'],i['Greece'],i['Crotia'],i['Holland'],i['Finland'],i['Hongkong'])
					cur.execute(sql,dat)
					con.commit()
			if exp==1:
				#Exponential Smoothing
				dates=pd.date_range(start_index1,end_index1,freq='M')
				lengthofprd=len(dates)
				dateofterm= pd.PeriodIndex(freq='M', start=start_index1, periods=lengthofprd+1)
				dateofterms=dateofterm.strftime("20%y-%m-%d")
				Edate=pd.DataFrame(dateofterms)
				predictonterm=len(Edate)
				
				def exponential_smoothing(series, alpha,predictonterm):
					result = [series[0]] # first value is same as series
					for i in range(1,len(series)):
						result.append(alpha * series[i] + (1 - alpha) * result[i-1])
					preds=result[len(series)-1]#pred
					actual=series[len(series)-1]#actual
					forecastlist=[]
					for i in range(0,predictonterm):
						forecast=(alpha*actual)+((1-alpha)*preds)
						forecastlist.append(forecast)
						actual=preds
						preds=forecast
					return result,forecastlist
				def Exponentialmooth(data,alpha,predicterm):
					predexp=list()
					forecaste=pd.DataFrame()
					m=len(data.columns.tolist())
					for i in range(0,m-5):
						pred,forecasts=exponential_smoothing(data[data.columns.tolist()[i]],0.5,predictonterm)
						ss=pd.DataFrame(forecasts)
						predexp.append(pred)
						forecaste=pd.concat([forecaste,ss],axis=1)
						if(i==0):
							meanerr=ME(len(data[data.columns.tolist()[i]]),predexp)
							meanaverr=MAE(data[data.columns.tolist()[i]],predexp)
							mperr=MAPE(data[data.columns.tolist()[i]],predexp)
							df2["Exponential Smoothing"].iloc[0]=meanerr
							df2["Exponential Smoothing"].iloc[1]=meanaverr
							df2["Exponential Smoothing"].iloc[2]=mperr
							Exponentials=pd.DataFrame(forecaste)
							ratio_incex=[]
							ratio_incex.append(0)
							for j in range(2,len(Exponentials)+1):
								 Ea=Exponentials.iloc[j-2]
								 Eb=Exponentials.iloc[j-1]
								 ratio_incex.append(int(((Eb-Ea)/Ea)*100))
					return forecaste,ratio_incex
				fore,ratio_incex=Exponentialmooth(data,0.5,predictonterm)
				skf=pd.DataFrame(fore)
				skf.columns=["TotalDemand","Spain","Austria","Japan","Hungary","Germany","Polland","UK","France","Romania","Italy","Greece","Crotia","Holland","Finland","Hongkong"]
				skf['Model']="Exponential Smoothing"
				skf['Date']=Edate
				skf['RatioIncrease']=ratio_incex
				skf.astype(str)
				for index, i in skf.iterrows():
					dat = (i['Model'],i['Date'],i['TotalDemand'],i['RatioIncrease'],i['Spain'],i['Austria'],i['Japan'],i['Hungary'],i['Germany'],i['Polland'],i['UK'],i['France'],i['Romania'],i['Italy'],i['Greece'],i['Crotia'],i['Holland'],i['Finland'],i['Hongkong'])
					cur.execute(sql,dat)
					con.commit()



			dates=pd.date_range(start_index1,end_index1,freq='M')
			lengthofprd=len(dates)
			dateofterm= pd.PeriodIndex(freq='M', start=start_index1, periods=lengthofprd+1)
			dateofterms=dateofterm.strftime("20%y-%m-%d")
			ss=pd.DataFrame(dateofterms,columns=['Date'])        
			dataframeforsum=pd.concat([ss])
					
			if mov==1:
				cur.execute("SELECT `TotalDemand` FROM `forecastoutput` WHERE `Model`= 'Moving Average'" ) 
				Xmdata = cur.fetchall()
				Xmadata = pd.DataFrame(Xmdata)
				movsummm=pd.DataFrame(Xmadata)
				movsummm.columns=['Moving Average']
				dataframeforsum=pd.concat([dataframeforsum,movsummm],axis=1)
				
				
			if ari==1:
				cur.execute("SELECT `TotalDemand` FROM `forecastoutput` WHERE `Model`= 'ARIMA'" ) 
				Xadata = cur.fetchall()
				Xardata = pd.DataFrame(Xadata)
				movsumma=pd.DataFrame(Xardata)
				movsumma.columns=['ARIMA']
				dataframeforsum=pd.concat([dataframeforsum,movsumma],axis=1)

			if exp==1:
				cur.execute("SELECT `TotalDemand` FROM `forecastoutput` WHERE `Model`= 'Exponential Smoothing'" ) 
				Xedata = cur.fetchall()
				Xesdata = pd.DataFrame(Xedata)
				exp=pd.DataFrame(Xesdata)
				exp.columns=['Exponential Smoothing']
				dataframeforsum=pd.concat([dataframeforsum,exp],axis=1)
				
			if reg==1:
				cur.execute("SELECT `TotalDemand` FROM `forecastoutput` WHERE `Model`= 'Regression'" ) 
				Xrdata = cur.fetchall()
				Xredata = pd.DataFrame(Xrdata)
				regr=pd.DataFrame(Xredata)
				regr.columns=['Regression']
				dataframeforsum=pd.concat([dataframeforsum,regr],axis=1)
				
				
			dataframeforsum.astype(str)

			from pandas.io import sql
			engine = create_engine("mysql+pymysql://{user}:{pw}@localhost/{db}".format(user="root",pw="",db="inventory_management"))
			dataframeforsum.to_sql(con=engine, name='summaryoutput',index=False, if_exists='replace')
			engine2 = create_engine("mysql+pymysql://{user}:{pw}@localhost/{db}".format(user="root",pw="",db="inventory_management"))
			df2.to_sql(con=engine2, name='summaryerror',index=False, if_exists='replace')
			con.commit()

			cnr=con.cursor()
			cnr.execute("SELECT * FROM `summaryoutput`")
			sdata = cnr.fetchall()
			summaryq = pd.DataFrame(sdata)

			con.close()
			return render_template('monthly.html',summaryq=summaryq.to_html(index=False),sayy=1,smt='Monthly',yr1=demandforecastfrm+' to ',yr2=demandforecasttoo,x=res11,y=r11,x1=tres11,y1=tr11,x2=ures11,y2=ur11,x3=vres11,y3=vr11,x4=wres11,y4=wr11)
		return render_template('monthly.html',sayy=1,smt='Monthly',yr1=demandforecastfrm+' to ',yr2=demandforecasttoo,x=res11,y=r11,x1=tres11,y1=tr11,x2=ures11,y2=ur11,x3=vres11,y3=vr11,x4=wres11,y4=wr11)
##quarterly
	
@app.route("/quarterlyforecast",methods = ['GET','POST'])
def quarterlyforecast():
		data = pd.DataFrame(Quaterdata)
		a1=data.sort_values(['GDP','TotalDemand'], ascending=[True,True])# container1
		a2=data.sort_values(['Pi_Exports','TotalDemand'], ascending=[True,True])# container2
		a3=data.sort_values(['Market_Share','TotalDemand'], ascending=[True,True])# container3
		a4=data.sort_values(['Advertisement_Expense','TotalDemand'], ascending=[True,True])# container4
		# container1
		df=a1[['GDP']]/3
		re11 = np.array([])
		res11 = np.append(re11,df)

		df1=a1[['TotalDemand']]
		r1 = np.array([]) 
		r11 = np.append(r1, df1)

		# top graph
		tdf=data['Date'].astype(str)
		tre11 = np.array([])
		tres11 = np.append(tre11,tdf)
		tr1 = np.array([]) 
		tr11 = np.append(tr1, df1)

		# container2
		udf=a2[['Pi_Exports']]
		ure11 = np.array([])
		ures11 = np.append(ure11,udf)
		ur1 = np.array([]) 
		ur11 = np.append(ur1, df1)

		# container3
		vdf=a3[['Market_Share']]/3
		vre11 = np.array([])
		vres11 = np.append(vre11,vdf)
		vr1 = np.array([]) 
		vr11 = np.append(vr1, df1)

		# container4
		wdf=a4[['Advertisement_Expense']]
		wre11 = np.array([])
		wres11 = np.append(wre11,wdf)
		wr1 = np.array([])
		wr11 = np.append(wr1, df1)

		if request.method == 'POST':
			mov=0
			exp=0
			reg=0
			ari=0
			arx=0
			till = request.form.get('till')
			if request.form.get('moving'):
				mov=1

			if request.form.get('ESPO'):
				exp=1
				
			if request.form.get('regression'):
				reg=1
				
			if request.form.get('ARIMA'):
				ari=1
				
			if request.form.get('ARIMAX'):
				arx=1
			
			con = pymysql.connect(host='localhost',user='root',password='',db='inventory_management',charset='utf8mb4',cursorclass=pymysql.cursors.DictCursor)
			cur = con.cursor()
			cur.execute("CREATE TABLE IF NOT EXISTS `ftech` (`mov` VARCHAR(1),`exp` VARCHAR(1), `reg` VARCHAR(1),`ari` VARCHAR(1),`arx` VARCHAR(1),`till` VARCHAR(10))")
			cur.execute("DELETE FROM `ftech`")
			con.commit()
			cur.execute("INSERT INTO `ftech` VALUES('"+str(mov)+"','"+str(exp)+"','"+str(reg)+"','"+str(ari)+"','"+str(arx)+"','"+str(till)+"')")
			con.commit()
			cur.execute("CREATE TABLE IF NOT EXISTS `forecastoutputq`(`Model` VARCHAR(25),`Date` VARCHAR(10),`TotalDemand` VARCHAR(10),`RatioIncrease` VARCHAR(10),`Spain` VARCHAR(10),`Austria` VARCHAR(10),`Japan` VARCHAR(10),`Hungary` VARCHAR(10),`Germany` VARCHAR(10),`Polland` VARCHAR(10),`UK` VARCHAR(10),`France` VARCHAR(10),`Romania` VARCHAR(10),`Italy` VARCHAR(10),`Greece` VARCHAR(10),`Crotia` VARCHAR(10),`Holland` VARCHAR(10),`Finland` VARCHAR(10),`Hongkong` VARCHAR(10))")
			con.commit()
			cur.execute("DELETE FROM `forecastoutputq`")
			con.commit()
			sql = "INSERT INTO `forecastoutputq` (`Model`,`Date`,`TotalDemand`,`RatioIncrease`,`Spain`,`Austria`,`Japan`,`Hungary`,`Germany`,`Polland`,`UK`,`France`,`Romania`,`Italy`,`Greece`,`Crotia`,`Holland`,`Finland`,`Hongkong`) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"


			#read the monthly file and index that with time
			df=data.set_index('Date')
			split_point =int(0.7*len(df))
			D, V = df[0:split_point],df[split_point:]

			data=pd.DataFrame(D)

			#Functions for ME, MAE, MAPE
			#ME
			def ME(y_true, y_pred):
				y_true, y_pred = np.array(y_true), np.array(y_pred)
				return np.mean(y_true - y_pred) 

			#MAE
			def MAE(y_true, y_pred):
				y_true, y_pred = np.array(y_true), np.array(y_pred)
				return np.mean(np.abs(y_true - y_pred))

			#MAPE 
			def MAPE(y_true, y_pred):
				y_true, y_pred = np.array(y_true), np.array(y_pred)
				return np.mean(np.abs((y_true - y_pred) / y_pred)) * 100 

			cur1=con.cursor()
			cur1.execute("SELECT * FROM `ftech`")
			ftech=pd.DataFrame(cur1.fetchall())
			ari=int(ftech['ari'])
			arx=int(ftech['arx'])
			exp=int(ftech['exp'])
			mov=int(ftech['mov'])
			reg=int(ftech['reg'])
			start_index1=str(D['GDP'].index[-1])
			end_index1=str(ftech['till'][0])
			#end_index1=indx[:4]

			df2 = pd.DataFrame(data=0,index=["ME","MAE","MAPE"],columns=["Moving Average","ARIMA","Exponential Smoothing","Regression"])

			if mov==1:
				#2---------------simple moving average-------------------------
				#################################MovingAverage#######################
				list1=list()
				def mavg(data):
					 m=len(data.columns.tolist())
					 for i in range(0,m-5):
						 #Arima Model Fitting
						 model1=ARIMA(data[data.columns.tolist()[i]].astype(float), order=(0,0,1))
						 results_ARIMA1=model1.fit(disp=0)   
			#             start_index1 = '2017-01-01'
			#             end_index1 = '2022-01-01' #4 year forecast
						 ARIMA_fit1= results_ARIMA1.fittedvalues
						 forecast2=results_ARIMA1.predict(start=start_index1, end=end_index1)
						 list1.append(forecast2)
						 if(i==0):
							 #ME
							 s=ME(data['TotalDemand'],ARIMA_fit1)
							 #MAE
							 so=MAE(data['TotalDemand'],ARIMA_fit1)
							 #MAPE 
							 son=MAPE(data['TotalDemand'],ARIMA_fit1)
							 df2["Moving Average"].iloc[0]=s
							 df2["Moving Average"].iloc[1]=so
							 df2["Moving Average"].iloc[2]=son
							 s=pd.DataFrame(forecast2)
							 ratio_inc=[]
							 ratio_inc.append(0)
							 for j in range(2,len(s)+1):
								 a=s.iloc[j-2]
								 b=s.iloc[j-1]
								 ratio_inc.append(int(((b-a)/a)*100))
					 return list1,ratio_inc
				print(data)
				Ma_Out,ratio_incma=mavg(data)
				dfs=pd.DataFrame(Ma_Out)
				tdfs=dfs.T
				print(tdfs)
				tdfs.columns=["TotalDemand","Spain","Austria","Japan","Hungary","Germany","Polland","UK","France","Romania","Italy","Greece","Crotia","Holland","Finland","Hongkong"]
				tdfs['Model']='Moving Average'
				tdfs['RatioIncrease']=ratio_incma
				tdfs['Date']=(tdfs.index).strftime("20%y-%m-%d")


				tdfs.astype(str)
				for index, i in tdfs.iterrows():
					dat = (i['Model'],i['Date'],i['TotalDemand'],i['RatioIncrease'],i['Spain'],i['Austria'],i['Japan'],i['Hungary'],i['Germany'],i['Polland'],i['UK'],i['France'],i['Romania'],i['Italy'],i['Greece'],i['Crotia'],i['Holland'],i['Finland'],i['Hongkong'])
					cur.execute(sql,dat)
					con.commit()
				
				
			if ari==1:
				##--------------min errors--ARIMA (1,0,0)----------------------------- 
				############################for Total Demand Monthly####################################
				list2=list()
				def AutoRimavg(data):
					 m=len(data.columns.tolist())
					 for i in range(0,m-5):
						 #Arima Model Fitting
						 model1=ARIMA(data[data.columns.tolist()[i]].astype(float), order=(1,0,0))
						 results_ARIMA1=model1.fit(disp=0)   
						 ARIMA_fit1= results_ARIMA1.fittedvalues
						 forecast2=results_ARIMA1.predict(start=start_index1, end=end_index1)
						 list2.append(forecast2)
						 if(i==0):
							  #ME
							 s=ME(data['TotalDemand'],ARIMA_fit1)
							 #MAE
							 so=MAE(data['TotalDemand'],ARIMA_fit1)
							 #MAPE 
							 son=MAPE(data['TotalDemand'],ARIMA_fit1)
							 df2["ARIMA"].iloc[0]=s
							 df2["ARIMA"].iloc[1]=so
							 df2["ARIMA"].iloc[2]=son
							 Ars=pd.DataFrame(forecast2)
							 ratio_inc=[]
							 ratio_inc.append(0)
							 for j in range(2,len(Ars)+1):
								 As=(Ars.iloc[j-2])
								 bs=(Ars.iloc[j-1])
								 ratio_inc.append(int(((As-bs)/As)*100))
					 return list1,ratio_inc
				
						
				Arimamodel,ratio_inc=AutoRimavg(data)
				Amodel=pd.DataFrame(Arimamodel)
				Results=Amodel.T
				Results.astype(str)
				Results.columns=["TotalDemand","Spain","Austria","Japan","Hungary","Germany","Polland","UK","France","Romania","Italy","Greece","Crotia","Holland","Finland","Hongkong"]
				Results['Model']="ARIMA"
				Results['RatioIncrease']=ratio_inc
				Results['Date']=Results.index.astype(str)
				
				for index, i in Results.iterrows():
					dat = (i['Model'],i['Date'],i['TotalDemand'],i['RatioIncrease'],i['Spain'],i['Austria'],i['Japan'],i['Hungary'],i['Germany'],i['Polland'],i['UK'],i['France'],i['Romania'],i['Italy'],i['Greece'],i['Crotia'],i['Holland'],i['Finland'],i['Hongkong'])
					cur.execute(sql,dat)
					con.commit()

			if reg==1:
				
				#Linear Regression
				#Regression Modeling
				dates=pd.date_range(start_index1,end_index1,freq='3M')
				lprd=len(dates)
				dateofterms= pd.PeriodIndex(freq='3M', start=start_index1, periods=lprd+1)
				dofterm=dateofterms.strftime("20%y-%m-%d")
				Rdate=pd.DataFrame(dofterm)
				noofterms=len(dofterm)
				def regression(data,V,noofterms):
					#Getting length of Data Frame
					lenofdf=len(data.columns.tolist())

					#Getting List Of Atributes in Data Frame
					listofatr=list()
					listofatr=data.columns.tolist()

					#making list of pred
					pred=pd.DataFrame()

					#now riun for each row
					for i in range(0,(lenofdf)-5):
						df=pd.DataFrame(data[data.columns.tolist()[i]].reset_index())
						xvar=list()
						for row in df[listofatr[i]]:
							xvar.append(row)
						df5=pd.DataFrame(xvar)
						yvar=list()
						for j in range(0,len(df[listofatr[i]])):
							yvar.append(j)
						dfss=pd.DataFrame(yvar)
						clf = linear_model.LinearRegression()
						clf.fit(dfss,df5)
						# Make predictions using the testing set

						dfv=pd.DataFrame(V[V.columns.tolist()[i]].reset_index())
						k=list()
						for l in range(len(df[listofatr[i]]),len(df[listofatr[i]])+len(dfv)):
							k.append(l)
						ks=pd.DataFrame(k)

						#Future prediction

						predlist=list()
						for j in range(len(df[listofatr[i]]),len(df[listofatr[i]])+noofterms):
							predlist.append(j)
						dataframeoflenofpred=pd.DataFrame(predlist)
						dateframeofpred=pd.DataFrame(clf.predict(dataframeoflenofpred))
						pred=pd.concat([pred,dateframeofpred],axis=1)

						#Accuracy Of the mODEL
						y_pred = clf.predict(ks)
						if(i==0):
							meanerror=ME(dfv[listofatr[i]], y_pred)
							mae=MAE(dfv[listofatr[i]], y_pred)
							mape=MAPE(dfv[listofatr[i]],y_pred)
							df2["Regression"].iloc[0]=meanerror
							df2["Regression"].iloc[1]=mae
							df2["Regression"].iloc[2]=mape
							regp=pd.DataFrame(pred)
							ratio_incrr=[]
							ratio_incrr.append(0)
							for j in range(2,len(regp)+1):
									 Ra=regp.iloc[j-2]
									 Rb=regp.iloc[j-1]
									 ratio_incrr.append(int(((Rb-Ra)/Ra)*100))
					return pred,ratio_incrr
				monthlyRegression,ratio_incrr=regression(data,V,noofterms)
				r=pd.DataFrame(monthlyRegression)
				r.columns=["TotalDemand","Spain","Austria","Japan","Hungary","Germany","Polland","UK","France","Romania","Italy","Greece","Crotia","Holland","Finland","Hongkong"]
				r['Model']="Regression"
				r['Date']=Rdate
				r['RatioIncrease']=ratio_incrr
				r.astype(str)
				for index, i in r.iterrows():
					dat = (i['Model'],i['Date'],i['TotalDemand'],i['RatioIncrease'],i['Spain'],i['Austria'],i['Japan'],i['Hungary'],i['Germany'],i['Polland'],i['UK'],i['France'],i['Romania'],i['Italy'],i['Greece'],i['Crotia'],i['Holland'],i['Finland'],i['Hongkong'])
					cur.execute(sql,dat)
					con.commit()
			if exp==1:
				#Exponential Smoothing
				dates=pd.date_range(start_index1,end_index1,freq='3M')
				lengthofprd=len(dates)
				dateofterm= pd.PeriodIndex(freq='3M', start=start_index1, periods=lengthofprd+1)
				dateofterms=dateofterm.strftime("20%y-%m-%d")
				Edate=pd.DataFrame(dateofterms)
				predictonterm=len(Edate)
				
				def exponential_smoothing(series, alpha,predictonterm):
					result = [series[0]] # first value is same as series
					for i in range(1,len(series)):
						result.append(alpha * series[i] + (1 - alpha) * result[i-1])
					preds=result[len(series)-1]#pred
					actual=series[len(series)-1]#actual
					forecastlist=[]
					for i in range(0,predictonterm):
						forecast=(alpha*actual)+((1-alpha)*preds)
						forecastlist.append(forecast)
						actual=preds
						preds=forecast
					return result,forecastlist
				def Exponentialmooth(data,alpha,predicterm):
					predexp=list()
					forecaste=pd.DataFrame()
					m=len(data.columns.tolist())
					for i in range(0,m-5):
						pred,forecasts=exponential_smoothing(data[data.columns.tolist()[i]],0.5,predictonterm)
						ss=pd.DataFrame(forecasts)
						predexp.append(pred)
						forecaste=pd.concat([forecaste,ss],axis=1)
						if(i==0):
							meanerr=ME(len(data[data.columns.tolist()[i]]),predexp)
							meanaverr=MAE(data[data.columns.tolist()[i]],predexp)
							mperr=MAPE(data[data.columns.tolist()[i]],predexp)
							df2["Exponential Smoothing"].iloc[0]=meanerr
							df2["Exponential Smoothing"].iloc[1]=meanaverr
							df2["Exponential Smoothing"].iloc[2]=mperr
							Exponentials=pd.DataFrame(forecaste)
							ratio_incex=[]
							ratio_incex.append(0)
							for j in range(2,len(Exponentials)+1):
								 Ea=Exponentials.iloc[j-2]
								 Eb=Exponentials.iloc[j-1]
								 ratio_incex.append(int(((Eb-Ea)/Ea)*100))
					return forecaste,ratio_incex
				fore,ratio_incex=Exponentialmooth(data,0.5,predictonterm)
				skf=pd.DataFrame(fore)
				skf.columns=["TotalDemand","Spain","Austria","Japan","Hungary","Germany","Polland","UK","France","Romania","Italy","Greece","Crotia","Holland","Finland","Hongkong"]
				skf['Model']="Exponential Smoothing"
				skf['Date']=Edate
				skf['RatioIncrease']=ratio_incex
				skf.astype(str)
				for index, i in skf.iterrows():
					dat = (i['Model'],i['Date'],i['TotalDemand'],i['RatioIncrease'],i['Spain'],i['Austria'],i['Japan'],i['Hungary'],i['Germany'],i['Polland'],i['UK'],i['France'],i['Romania'],i['Italy'],i['Greece'],i['Crotia'],i['Holland'],i['Finland'],i['Hongkong'])
					cur.execute(sql,dat)
					con.commit()



			dates=pd.date_range(start_index1,end_index1,freq='3M')
			lengthofprd=len(dates)
			dateofterm= pd.PeriodIndex(freq='3M', start=start_index1, periods=lengthofprd+1)
			dateofterms=dateofterm.strftime("20%y-%m-%d")
			ss=pd.DataFrame(dateofterms,columns=['Date'])        
			dataframeforsum=pd.concat([ss])
					
			if mov==1:
				cur.execute("SELECT `TotalDemand` FROM `forecastoutputq` WHERE `Model`= 'Moving Average'" ) 
				Xmdata = cur.fetchall()
				Xmadata = pd.DataFrame(Xmdata)
				movsummm=pd.DataFrame(Xmadata)
				movsummm.columns=['Moving Average']
				dataframeforsum=pd.concat([dataframeforsum,movsummm],axis=1)
				
				
			if ari==1:
				cur.execute("SELECT `TotalDemand` FROM `forecastoutputq` WHERE `Model`= 'ARIMA'" ) 
				Xadata = cur.fetchall()
				Xardata = pd.DataFrame(Xadata)
				movsumma=pd.DataFrame(Xardata)
				movsumma.columns=['ARIMA']
				dataframeforsum=pd.concat([dataframeforsum,movsumma],axis=1)

			if exp==1:
				cur.execute("SELECT `TotalDemand` FROM `forecastoutputq` WHERE `Model`= 'Exponential Smoothing'" ) 
				Xedata = cur.fetchall()
				Xesdata = pd.DataFrame(Xedata)
				exp=pd.DataFrame(Xesdata)
				exp.columns=['Exponential Smoothing']
				dataframeforsum=pd.concat([dataframeforsum,exp],axis=1)
				
			if reg==1:
				cur.execute("SELECT `TotalDemand` FROM `forecastoutputq` WHERE `Model`= 'Regression'" ) 
				Xrdata = cur.fetchall()
				Xredata = pd.DataFrame(Xrdata)
				regr=pd.DataFrame(Xredata)
				regr.columns=['Regression']
				dataframeforsum=pd.concat([dataframeforsum,regr],axis=1)
				
				
			dataframeforsum.astype(str)

			from pandas.io import sql
			engine = create_engine("mysql+pymysql://{user}:{pw}@localhost/{db}".format(user="root",pw="",db="inventory_management"))
			dataframeforsum.to_sql(con=engine, name='summaryoutputq',index=False, if_exists='replace')
			engine2 = create_engine("mysql+pymysql://{user}:{pw}@localhost/{db}".format(user="root",pw="",db="inventory_management"))
			df2.to_sql(con=engine2, name='summaryerror',index=False, if_exists='replace')
			con.commit()

			cnr=con.cursor()
			cnr.execute("SELECT * FROM `summaryoutputq`")
			sdata = cnr.fetchall()
			summaryq = pd.DataFrame(sdata)

			con.close()
			return render_template('quarterly.html',summaryq=summaryq.to_html(index=False),sayy=1,smt='Quarterly',yr1=demandforecastfrm+' to ',yr2=demandforecasttoo,x=res11,y=r11,x1=tres11,y1=tr11,x2=ures11,y2=ur11,x3=vres11,y3=vr11,x4=wres11,y4=wr11)
		return render_template('quarterly.html',sayy=1,smt='Quarterly',yr1=demandforecastfrm+' to ',yr2=demandforecasttoo,x=res11,y=r11,x1=tres11,y1=tr11,x2=ures11,y2=ur11,x3=vres11,y3=vr11,x4=wres11,y4=wr11)

##yearly	

@app.route("/yearlyforecast",methods = ['GET','POST'])
def yearlyforecast():
		data = pd.DataFrame(Yeardata)
		a1=data.sort_values(['GDP','TotalDemand'], ascending=[True,True])# container1
		a2=data.sort_values(['Pi_Exports','TotalDemand'], ascending=[True,True])# container2
		a3=data.sort_values(['Market_Share','TotalDemand'], ascending=[True,True])# container3
		a4=data.sort_values(['Advertisement_Expense','TotalDemand'], ascending=[True,True])# container4
		# container1
		df=a1[['GDP']]/12
		re11 = np.array([])
		res11 = np.append(re11,df)

		df1=a1[['TotalDemand']]
		r1 = np.array([]) 
		r11 = np.append(r1, df1)

		# top graph
		tdf=data['Date']
		vari=[]
		for var in tdf:
			vari.append(var[:4])
		tres11 = vari
		tr1 = np.array([]) 
		tr11 = np.append(tr1, df1)

		# container2
		udf=a2[['Pi_Exports']]
		ure11 = np.array([])
		ures11 = np.append(ure11,udf)
		ur1 = np.array([]) 
		ur11 = np.append(ur1, df1)

		# container3
		vdf=a3[['Market_Share']]/12
		vre11 = np.array([])
		vres11 = np.append(vre11,vdf)
		vr1 = np.array([]) 
		vr11 = np.append(vr1, df1)

		# container4
		wdf=a4[['Advertisement_Expense']]
		wre11 = np.array([])
		wres11 = np.append(wre11,wdf)
		wr1 = np.array([])
		wr11 = np.append(wr1, df1)

		if request.method == 'POST':
			mov=0
			exp=0
			reg=0
			ari=0
			arx=0
			till = request.form.get('till')
			if request.form.get('moving'):
				mov=1

			if request.form.get('ESPO'):
				exp=1
				
			if request.form.get('regression'):
				reg=1
				
			if request.form.get('ARIMA'):
				ari=1
				
			if request.form.get('ARIMAX'):
				arx=1
			
			con = pymysql.connect(host='localhost',user='root',password='',db='inventory_management',charset='utf8mb4',cursorclass=pymysql.cursors.DictCursor)
			cur = con.cursor()
			cur.execute("CREATE TABLE IF NOT EXISTS `ftech` (`mov` VARCHAR(1),`exp` VARCHAR(1), `reg` VARCHAR(1),`ari` VARCHAR(1),`arx` VARCHAR(1),`till` VARCHAR(10))")
			cur.execute("DELETE FROM `ftech`")
			con.commit()
			cur.execute("INSERT INTO `ftech` VALUES('"+str(mov)+"','"+str(exp)+"','"+str(reg)+"','"+str(ari)+"','"+str(arx)+"','"+str(till)+"')")
			con.commit()
			cur.execute("CREATE TABLE IF NOT EXISTS `forecastoutputy`(`Model` VARCHAR(25),`Date` VARCHAR(10),`TotalDemand` VARCHAR(10),`RatioIncrease` VARCHAR(10),`Spain` VARCHAR(10),`Austria` VARCHAR(10),`Japan` VARCHAR(10),`Hungary` VARCHAR(10),`Germany` VARCHAR(10),`Polland` VARCHAR(10),`UK` VARCHAR(10),`France` VARCHAR(10),`Romania` VARCHAR(10),`Italy` VARCHAR(10),`Greece` VARCHAR(10),`Crotia` VARCHAR(10),`Holland` VARCHAR(10),`Finland` VARCHAR(10),`Hongkong` VARCHAR(10))")
			con.commit()
			cur.execute("DELETE FROM `forecastoutputy`")
			con.commit()
			sql = "INSERT INTO `forecastoutputy` (`Model`,`Date`,`TotalDemand`,`RatioIncrease`,`Spain`,`Austria`,`Japan`,`Hungary`,`Germany`,`Polland`,`UK`,`France`,`Romania`,`Italy`,`Greece`,`Crotia`,`Holland`,`Finland`,`Hongkong`) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"


			#read the monthly file and index that with time
			df=data.set_index('Date')
			split_point =int(0.7*len(df))
			D, V = df[0:split_point],df[split_point:]
			
			data=pd.DataFrame(D)

			#Functions for ME, MAE, MAPE
			#ME
			def ME(y_true, y_pred):
				y_true, y_pred = np.array(y_true), np.array(y_pred)
				return np.mean(y_true - y_pred) 

			#MAE
			def MAE(y_true, y_pred):
				y_true, y_pred = np.array(y_true), np.array(y_pred)
				return np.mean(np.abs(y_true - y_pred))

			#MAPE 
			def MAPE(y_true, y_pred):
				y_true, y_pred = np.array(y_true), np.array(y_pred)
				return np.mean(np.abs((y_true - y_pred) / y_pred)) * 100 

			cur1=con.cursor()
			cur1.execute("SELECT * FROM `ftech`")
			ftech=pd.DataFrame(cur1.fetchall())
			ari=int(ftech['ari'])
			arx=int(ftech['arx'])
			exp=int(ftech['exp'])
			mov=int(ftech['mov'])
			reg=int(ftech['reg'])
			start_index1=str(D['GDP'].index[-1])
			end_index1=str(ftech['till'][0])
			#end_index1=indx[:4]

			df2 = pd.DataFrame(data=0,index=["ME","MAE","MAPE"],columns=["Moving Average","ARIMA","Exponential Smoothing","Regression"])

			if mov==1:
				#2---------------simple moving average-------------------------
				#################################MovingAverage#######################
				list1=list()
				def mavg(data):
					 m=len(data.columns.tolist())
					 for i in range(0,m-5):
						 #Arima Model Fitting
						 model1=ARIMA(data[data.columns.tolist()[i]].astype(float), order=(0,0,1))
						 results_ARIMA1=model1.fit(disp=0)   
			#             start_index1 = '2017-01-01'
			#             end_index1 = '2022-01-01' #4 year forecast
						 ARIMA_fit1= results_ARIMA1.fittedvalues
						 forecast2=results_ARIMA1.predict(start=start_index1, end=end_index1)
						 list1.append(forecast2)
						 if(i==0):
							 #ME
							 s=ME(data['TotalDemand'],ARIMA_fit1)
							 #MAE
							 so=MAE(data['TotalDemand'],ARIMA_fit1)
							 #MAPE 
							 son=MAPE(data['TotalDemand'],ARIMA_fit1)
							 df2["Moving Average"].iloc[0]=s
							 df2["Moving Average"].iloc[1]=so
							 df2["Moving Average"].iloc[2]=son
							 s=pd.DataFrame(forecast2)
							 ratio_inc=[]
							 ratio_inc.append(0)
							 for j in range(2,len(s)+1):
								 a=s.iloc[j-2]
								 b=s.iloc[j-1]
								 ratio_inc.append(int(((b-a)/a)*100))
					 return list1,ratio_inc
				print(data)
				Ma_Out,ratio_incma=mavg(data)
				dfs=pd.DataFrame(Ma_Out)
				tdfs=dfs.T
				print(tdfs)
				tdfs.columns=["TotalDemand","Spain","Austria","Japan","Hungary","Germany","Polland","UK","France","Romania","Italy","Greece","Crotia","Holland","Finland","Hongkong"]
				tdfs['Model']='Moving Average'
				tdfs['RatioIncrease']=ratio_incma
				dindex=(tdfs.index).strftime("20%y")
				tdfs['Date']=(dindex)


				tdfs.astype(str)
				for index, i in tdfs.iterrows():
					dat = (i['Model'],i['Date'],i['TotalDemand'],i['RatioIncrease'],i['Spain'],i['Austria'],i['Japan'],i['Hungary'],i['Germany'],i['Polland'],i['UK'],i['France'],i['Romania'],i['Italy'],i['Greece'],i['Crotia'],i['Holland'],i['Finland'],i['Hongkong'])
					cur.execute(sql,dat)
					con.commit()
				
				
			if ari==1:
				##--------------min errors--ARIMA (1,0,0)----------------------------- 
				############################for Total Demand Monthly####################################
				list2=list()
				def AutoRimavg(data):
					 m=len(data.columns.tolist())
					 for i in range(0,m-5):
						 #Arima Model Fitting
						 model1=ARIMA(data[data.columns.tolist()[i]].astype(float), order=(1,0,0))
						 results_ARIMA1=model1.fit(disp=0)   
						 ARIMA_fit1= results_ARIMA1.fittedvalues
						 forecast2=results_ARIMA1.predict(start=start_index1, end=end_index1)
						 list2.append(forecast2)
						 if(i==0):
							  #ME
							 s=ME(data['TotalDemand'],ARIMA_fit1)
							 #MAE
							 so=MAE(data['TotalDemand'],ARIMA_fit1)
							 #MAPE 
							 son=MAPE(data['TotalDemand'],ARIMA_fit1)
							 df2["ARIMA"].iloc[0]=s
							 df2["ARIMA"].iloc[1]=so
							 df2["ARIMA"].iloc[2]=son
							 Ars=pd.DataFrame(forecast2)
							 ratio_inc=[]
							 ratio_inc.append(0)
							 for j in range(2,len(Ars)+1):
								 As=(Ars.iloc[j-2])
								 bs=(Ars.iloc[j-1])
								 ratio_inc.append(int(((As-bs)/As)*100))
					 return list1,ratio_inc
				
						
				Arimamodel,ratio_inc=AutoRimavg(data)
				Amodel=pd.DataFrame(Arimamodel)
				Results=Amodel.T
				Results.astype(str)
				Results.columns=["TotalDemand","Spain","Austria","Japan","Hungary","Germany","Polland","UK","France","Romania","Italy","Greece","Crotia","Holland","Finland","Hongkong"]
				Results['Model']="ARIMA"
				Results['RatioIncrease']=ratio_inc
				Results['Date']=Results.index.astype(str)
				
				for index, i in Results.iterrows():
					dat = (i['Model'],i['Date'],i['TotalDemand'],i['RatioIncrease'],i['Spain'],i['Austria'],i['Japan'],i['Hungary'],i['Germany'],i['Polland'],i['UK'],i['France'],i['Romania'],i['Italy'],i['Greece'],i['Crotia'],i['Holland'],i['Finland'],i['Hongkong'])
					cur.execute(sql,dat)
					con.commit()

			if reg==1:
				
				#Linear Regression
				#Regression Modeling
				dates=pd.date_range(start_index1,end_index1,freq='A')
				lprd=len(dates)
				dateofterms= pd.PeriodIndex(freq='A', start=start_index1, periods=lprd+1)
				dofterm=dateofterms.strftime("20%y")
				Rdate=pd.DataFrame(dofterm)
				noofterms=len(dofterm)
				def regression(data,V,noofterms):
					#Getting length of Data Frame
					lenofdf=len(data.columns.tolist())

					#Getting List Of Atributes in Data Frame
					listofatr=list()
					listofatr=data.columns.tolist()

					#making list of pred
					pred=pd.DataFrame()

					#now riun for each row
					for i in range(0,(lenofdf)-5):
						df=pd.DataFrame(data[data.columns.tolist()[i]].reset_index())
						xvar=list()
						for row in df[listofatr[i]]:
							xvar.append(row)
						df5=pd.DataFrame(xvar)
						yvar=list()
						for j in range(0,len(df[listofatr[i]])):
							yvar.append(j)
						dfss=pd.DataFrame(yvar)
						clf = linear_model.LinearRegression()
						clf.fit(dfss,df5)
						# Make predictions using the testing set

						dfv=pd.DataFrame(V[V.columns.tolist()[i]].reset_index())
						k=list()
						for l in range(len(df[listofatr[i]]),len(df[listofatr[i]])+len(dfv)):
							k.append(l)
						ks=pd.DataFrame(k)

						#Future prediction

						predlist=list()
						for j in range(len(df[listofatr[i]]),len(df[listofatr[i]])+noofterms):
							predlist.append(j)
						dataframeoflenofpred=pd.DataFrame(predlist)
						dateframeofpred=pd.DataFrame(clf.predict(dataframeoflenofpred))
						pred=pd.concat([pred,dateframeofpred],axis=1)

						#Accuracy Of the mODEL
						y_pred = clf.predict(ks)
						if(i==0):
							meanerror=ME(dfv[listofatr[i]], y_pred)
							mae=MAE(dfv[listofatr[i]], y_pred)
							mape=MAPE(dfv[listofatr[i]],y_pred)
							df2["Regression"].iloc[0]=meanerror
							df2["Regression"].iloc[1]=mae
							df2["Regression"].iloc[2]=mape
							regp=pd.DataFrame(pred)
							ratio_incrr=[]
							ratio_incrr.append(0)
							for j in range(2,len(regp)+1):
									 Ra=regp.iloc[j-2]
									 Rb=regp.iloc[j-1]
									 ratio_incrr.append(int(((Rb-Ra)/Ra)*100))
					return pred,ratio_incrr
				monthlyRegression,ratio_incrr=regression(data,V,noofterms)
				r=pd.DataFrame(monthlyRegression)
				r.columns=["TotalDemand","Spain","Austria","Japan","Hungary","Germany","Polland","UK","France","Romania","Italy","Greece","Crotia","Holland","Finland","Hongkong"]
				r['Model']="Regression"
				r['Date']=Rdate
				r['RatioIncrease']=ratio_incrr
				r.astype(str)
				for index, i in r.iterrows():
					dat = (i['Model'],i['Date'],i['TotalDemand'],i['RatioIncrease'],i['Spain'],i['Austria'],i['Japan'],i['Hungary'],i['Germany'],i['Polland'],i['UK'],i['France'],i['Romania'],i['Italy'],i['Greece'],i['Crotia'],i['Holland'],i['Finland'],i['Hongkong'])
					cur.execute(sql,dat)
					con.commit()
			if exp==1:
				#Exponential Smoothing
				dates=pd.date_range(start_index1,end_index1,freq='A')
				lengthofprd=len(dates)
				dateofterm= pd.PeriodIndex(freq='A', start=start_index1, periods=lengthofprd+1)
				dateofterms=dateofterm.strftime("20%y")
				Edate=pd.DataFrame(dateofterms)
				predictonterm=len(Edate)
				
				def exponential_smoothing(series, alpha,predictonterm):
					result = [series[0]] # first value is same as series
					for i in range(1,len(series)):
						result.append(alpha * series[i] + (1 - alpha) * result[i-1])
					preds=result[len(series)-1]#pred
					actual=series[len(series)-1]#actual
					forecastlist=[]
					for i in range(0,predictonterm):
						forecast=(alpha*actual)+((1-alpha)*preds)
						forecastlist.append(forecast)
						actual=preds
						preds=forecast
					return result,forecastlist
				def Exponentialmooth(data,alpha,predicterm):
					predexp=list()
					forecaste=pd.DataFrame()
					m=len(data.columns.tolist())
					for i in range(0,m-5):
						pred,forecasts=exponential_smoothing(data[data.columns.tolist()[i]],0.5,predictonterm)
						ss=pd.DataFrame(forecasts)
						predexp.append(pred)
						forecaste=pd.concat([forecaste,ss],axis=1)
						if(i==0):
							meanerr=ME(len(data[data.columns.tolist()[i]]),predexp)
							meanaverr=MAE(data[data.columns.tolist()[i]],predexp)
							mperr=MAPE(data[data.columns.tolist()[i]],predexp)
							df2["Exponential Smoothing"].iloc[0]=meanerr
							df2["Exponential Smoothing"].iloc[1]=meanaverr
							df2["Exponential Smoothing"].iloc[2]=mperr
							Exponentials=pd.DataFrame(forecaste)
							ratio_incex=[]
							ratio_incex.append(0)
							for j in range(2,len(Exponentials)+1):
								 Ea=Exponentials.iloc[j-2]
								 Eb=Exponentials.iloc[j-1]
								 ratio_incex.append(int(((Eb-Ea)/Ea)*100))
					return forecaste,ratio_incex
				fore,ratio_incex=Exponentialmooth(data,0.5,predictonterm)
				skf=pd.DataFrame(fore)
				skf.columns=["TotalDemand","Spain","Austria","Japan","Hungary","Germany","Polland","UK","France","Romania","Italy","Greece","Crotia","Holland","Finland","Hongkong"]
				skf['Model']="Exponential Smoothing"
				skf['Date']=Edate
				skf['RatioIncrease']=ratio_incex
				skf.astype(str)
				for index, i in skf.iterrows():
					dat = (i['Model'],i['Date'],i['TotalDemand'],i['RatioIncrease'],i['Spain'],i['Austria'],i['Japan'],i['Hungary'],i['Germany'],i['Polland'],i['UK'],i['France'],i['Romania'],i['Italy'],i['Greece'],i['Crotia'],i['Holland'],i['Finland'],i['Hongkong'])
					cur.execute(sql,dat)
					con.commit()



			dates=pd.date_range(start_index1,end_index1,freq='A')
			lengthofprd=len(dates)
			dateofterm= pd.PeriodIndex(freq='A', start=start_index1, periods=lengthofprd+1)
			dateofterms=dateofterm.strftime("20%y")
			ss=pd.DataFrame(dateofterms,columns=['Date'])        
			dataframeforsum=pd.concat([ss])
					
			if mov==1:
				cur.execute("SELECT `TotalDemand` FROM `forecastoutputy` WHERE `Model`= 'Moving Average'" ) 
				Xmdata = cur.fetchall()
				Xmadata = pd.DataFrame(Xmdata)
				movsummm=pd.DataFrame(Xmadata)
				movsummm.columns=['Moving Average']
				dataframeforsum=pd.concat([dataframeforsum,movsummm],axis=1)
				
				
			if ari==1:
				cur.execute("SELECT `TotalDemand` FROM `forecastoutputy` WHERE `Model`= 'ARIMA'" ) 
				Xadata = cur.fetchall()
				Xardata = pd.DataFrame(Xadata)
				movsumma=pd.DataFrame(Xardata)
				movsumma.columns=['ARIMA']
				dataframeforsum=pd.concat([dataframeforsum,movsumma],axis=1)

			if exp==1:
				cur.execute("SELECT `TotalDemand` FROM `forecastoutputy` WHERE `Model`= 'Exponential Smoothing'" ) 
				Xedata = cur.fetchall()
				Xesdata = pd.DataFrame(Xedata)
				exp=pd.DataFrame(Xesdata)
				exp.columns=['Exponential Smoothing']
				dataframeforsum=pd.concat([dataframeforsum,exp],axis=1)
				
			if reg==1:
				cur.execute("SELECT `TotalDemand` FROM `forecastoutputy` WHERE `Model`= 'Regression'" ) 
				Xrdata = cur.fetchall()
				Xredata = pd.DataFrame(Xrdata)
				regr=pd.DataFrame(Xredata)
				regr.columns=['Regression']
				dataframeforsum=pd.concat([dataframeforsum,regr],axis=1)
				
				
			dataframeforsum.astype(str)

			from pandas.io import sql
			engine = create_engine("mysql+pymysql://{user}:{pw}@localhost/{db}".format(user="root",pw="",db="inventory_management"))
			dataframeforsum.to_sql(con=engine, name='summaryoutputy',index=False, if_exists='replace')
			engine2 = create_engine("mysql+pymysql://{user}:{pw}@localhost/{db}".format(user="root",pw="",db="inventory_management"))
			df2.to_sql(con=engine2, name='summaryerror',index=False, if_exists='replace')
			con.commit()

			cnr=con.cursor()
			cnr.execute("SELECT * FROM `summaryoutputy`")
			sdata = cnr.fetchall()
			summaryq = pd.DataFrame(sdata)

			con.close()
			return render_template('yearly.html',summaryq=summaryq.to_html(index=False),sayy=1,smt='Yearly',yr1=demandforecastfrm+' to ',yr2=demandforecasttoo,x=res11,y=r11,x1=tres11,y1=tr11,x2=ures11,y2=ur11,x3=vres11,y3=vr11,x4=wres11,y4=wr11)
		return render_template('yearly.html',sayy=1,smt='Yearly',yr1=demandforecastfrm+' to ',yr2=demandforecasttoo,x=res11,y=r11,x1=tres11,y1=tr11,x2=ures11,y2=ur11,x3=vres11,y3=vr11,x4=wres11,y4=wr11)


	
#############################Dashboard#######################################
#yearly
@app.route('/youtgraph', methods = ['GET','POST'])
def youtgraph():
		con = pymysql.connect(host='localhost',user='root',password='',db='inventory_management',charset='utf8mb4',cursorclass=pymysql.cursors.DictCursor)
		cur = con.cursor()
		cur.execute("SELECT `Model` FROM `forecastoutputy` GROUP BY `Model`")
		sfile=cur.fetchall()
		global yqst
		qlist=pd.DataFrame(sfile)
		qlst=qlist['Model'].astype(str)
		yqst=qlst.values
		con.close()
		return render_template('ydashboard.html',qulist=yqst)

@app.route('/youtgraph1', methods = ['GET', 'POST'])
def youtgraph1():
		if request.method=='POST':
			value=request.form['item']
		qconn = pymysql.connect(host='localhost',user='root',password='',db='inventory_management',charset='utf8mb4',cursorclass=pymysql.cursors.DictCursor)
		qcur = qconn.cursor()
		qcur.execute("SELECT * FROM `demandforecastinputdata")
		qsdata = qcur.fetchall()
		qdata = pd.DataFrame(qsdata)

		#graph1
		adata=qdata['TotalDemand']
		x_axis=qdata['Date'].astype(str)

		#predictedgraph1
		pcur = qconn.cursor()
		pcur.execute("SELECT * FROM `forecastoutputy` WHERE `Model`='"+value+"'")
		psdata = pcur.fetchall()
		edata = pd.DataFrame(psdata)
		eedata=edata['TotalDemand'].astype(float)
		ldata=eedata.values
		
		nur = qconn.cursor()
		nur.execute("SELECT MIN(`Date`) AS 'MIN' FROM `forecastoutputy` WHERE `Model`='"+value+"'")
		MIN=nur.fetchone()
		pdata=[]
		i=0
		k=0
		a="null"
		while(x_axis[i]<MIN['MIN']):
			pdata.append(a)
			i=i+1
			k=k+1
		ata=np.concatenate((pdata,ldata),axis=0)
		
		#x axis
		fcur = qconn.cursor()
		fcur.execute("SELECT `Date` FROM `demandforecastinputdata` WHERE `Date`<'"+MIN['MIN']+"'")
		fsdata = fcur.fetchall()
		indx = pd.DataFrame(fsdata)
		indx=indx['Date']
		index=np.concatenate((indx,edata['Date'].values),axis=0)
		yindx=[]
		for var in index:
			var1 = var[:4]
			yindx.append(var1)
		#bargraph
		bcur = qconn.cursor()
		bcur.execute("SELECT * FROM `forecastoutputy` WHERE `Model`='"+value+"'")
		bsdata = bcur.fetchall()
		bdata = pd.DataFrame(bsdata)
		
		btdf=bdata['Date'].astype(str)
		btre11 = np.array([])
		btres11 = np.append(btre11,btdf)

		b1tdf1=bdata[['Spain']]	#spain
		b1tr1 = np.array([]) 
		b1tr11 = np.append(b1tr1, b1tdf1)
		
		b2tdf1=bdata[['Austria']]	#austria
		b2tr1 = np.array([]) 
		b2tr11 = np.append(b2tr1, b2tdf1)
		
		b3tdf1=bdata[['Japan']]	#japan
		b3tr1 = np.array([]) 
		b3tr11 = np.append(b3tr1, b3tdf1)
		
		b4tdf1=bdata[['Hungary']]	#hungry
		b4tr1 = np.array([]) 
		b4tr11 = np.append(b4tr1, b4tdf1)
		
		b5tdf1=bdata[['Germany']]	#germany
		b5tr1 = np.array([]) 
		b5tr11 = np.append(b5tr1, b5tdf1)

		b6tdf1=bdata[['TotalDemand']]	#total
		b6tr1 = np.array([]) 
		b6tr11 = np.append(b6tr1, b6tdf1)

		#comparisonbar
		ccur = qconn.cursor()
		ccur.execute("SELECT * FROM `forecastoutputy` WHERE `Model`='"+value+"'")
		csdata = ccur.fetchall()
		cdata = pd.DataFrame(csdata)
		
		ctdf=cdata['Date'].astype(str)
		ctre11 = np.array([])
		ctres11 = np.append(ctre11,ctdf)

		c1tdf1=cdata[['RatioIncrease']]	#ratioincrease
		c1tr1 = np.array([]) 
		c1tr11 = np.append(c1tr1, c1tdf1)	
		
		qcur.execute("SELECT * FROM `summaryerror`")
		sdata = qcur.fetchall()
		mape = pd.DataFrame(sdata)
		qconn.close()
		return render_template('ydashboard.html',mon=value,qulist=yqst,mape=mape.to_html(index=False),say=1,pdata=ata,adata=adata.values,x_axis=yindx,frm=len(qdata)-1,to=k,x13=btres11,x14=ctres11,y13=b1tr11,y14=b2tr11,y15=b3tr11,y16=b4tr11,y17=b5tr11,y18=b6tr11,y19=c1tr11)

#monthly	
@app.route('/moutgraph', methods = ['GET','POST'])
def moutgraph():
		con = pymysql.connect(host='localhost',user='root',password='',db='inventory_management',charset='utf8mb4',cursorclass=pymysql.cursors.DictCursor)
		cur = con.cursor()
		cur.execute("SELECT `Model` FROM `forecastoutput` GROUP BY `Model`")
		sfile=cur.fetchall()
		global mqst
		qlist=pd.DataFrame(sfile)
		qlst=qlist['Model'].astype(str)
		mqst=qlst.values
		con.close()
		return render_template('mdashboard.html',qulist=mqst)

@app.route('/moutgraph1', methods = ['GET', 'POST'])
def moutgraph1():
		if request.method=='POST':
			value=request.form['item']
		qconn = pymysql.connect(host='localhost',user='root',password='',db='inventory_management',charset='utf8mb4',cursorclass=pymysql.cursors.DictCursor)
		qcur = qconn.cursor()
		qcur.execute("SELECT * FROM `demandforecastinputdata")
		qsdata = qcur.fetchall()
		qdata = pd.DataFrame(qsdata)

		#graph1
		adata=qdata['TotalDemand']
		x_axis=qdata['Date'].astype(str)

		#predictedgraph1
		pcur = qconn.cursor()
		pcur.execute("SELECT * FROM `forecastoutput` WHERE `Model`='"+value+"'")
		psdata = pcur.fetchall()
		edata = pd.DataFrame(psdata)
		eedata=edata['TotalDemand'].astype(float)
		ldata=eedata.values
		
		nur = qconn.cursor()
		nur.execute("SELECT MIN(`Date`) AS 'MIN' FROM `forecastoutput` WHERE `Model`='"+value+"'")
		MIN=nur.fetchone()
		pdata=[]
		i=0
		k=0
		a="null"
		while(x_axis[i]<MIN['MIN']):
			pdata.append(a)
			i=i+1
			k=k+1
		ata=np.concatenate((pdata,ldata),axis=0)
		
		#x axis
		fcur = qconn.cursor()
		fcur.execute("SELECT `Date` FROM `demandforecastinputdata` WHERE `Date`<'"+MIN['MIN']+"'")
		fsdata = fcur.fetchall()
		indx = pd.DataFrame(fsdata)
		indx=indx['Date'].astype(str).values
		index=np.concatenate((indx,edata['Date'].values),axis=0)
		
		#bargraph
		bcur = qconn.cursor()
		bcur.execute("SELECT * FROM `forecastoutput` WHERE `Model`='"+value+"'")
		bsdata = bcur.fetchall()
		bdata = pd.DataFrame(bsdata)
		
		btdf=bdata['Date'].astype(str)
		btre11 = np.array([])
		btres11 = np.append(btre11,btdf)

		b1tdf1=bdata[['Spain']]	#spain
		b1tr1 = np.array([]) 
		b1tr11 = np.append(b1tr1, b1tdf1)
		
		b2tdf1=bdata[['Austria']]	#austria
		b2tr1 = np.array([]) 
		b2tr11 = np.append(b2tr1, b2tdf1)
		
		b3tdf1=bdata[['Japan']]	#japan
		b3tr1 = np.array([]) 
		b3tr11 = np.append(b3tr1, b3tdf1)
		
		b4tdf1=bdata[['Hungary']]	#hungry
		b4tr1 = np.array([]) 
		b4tr11 = np.append(b4tr1, b4tdf1)
		
		b5tdf1=bdata[['Germany']]	#germany
		b5tr1 = np.array([]) 
		b5tr11 = np.append(b5tr1, b5tdf1)

		b6tdf1=bdata[['TotalDemand']]	#total
		b6tr1 = np.array([]) 
		b6tr11 = np.append(b6tr1, b6tdf1)

		#comparisonbar
		ccur = qconn.cursor()
		ccur.execute("SELECT * FROM `forecastoutput` WHERE `Model`='"+value+"'")
		csdata = ccur.fetchall()
		cdata = pd.DataFrame(csdata)
		
		ctdf=cdata['Date'].astype(str)
		ctre11 = np.array([])
		ctres11 = np.append(ctre11,ctdf)

		c1tdf1=cdata[['RatioIncrease']]	#ratioincrease
		c1tr1 = np.array([]) 
		c1tr11 = np.append(c1tr1, c1tdf1)	
		
		qcur.execute("SELECT * FROM `summaryerror`")
		sdata = qcur.fetchall()
		mape = pd.DataFrame(sdata)
		qconn.close()
		return render_template('mdashboard.html',mon=value,qulist=mqst,mape=mape.to_html(index=False),say=1,pdata=ata,adata=adata.values,x_axis=index,frm=len(qdata)-1,to=k,x13=btres11,x14=ctres11,y13=b1tr11,y14=b2tr11,y15=b3tr11,y16=b4tr11,y17=b5tr11,y18=b6tr11,y19=c1tr11)


#quarterly
@app.route('/qoutgraph', methods = ['GET','POST'])
def qoutgraph():
		con = pymysql.connect(host='localhost',user='root',password='',db='inventory_management',charset='utf8mb4',cursorclass=pymysql.cursors.DictCursor)
		cur = con.cursor()
		cur.execute("SELECT `Model` FROM `forecastoutputq` GROUP BY `Model`")
		sfile=cur.fetchall()
		global qst
		qlist=pd.DataFrame(sfile)
		qlst=qlist['Model'].astype(str)
		qst=qlst.values
		con.close()
		return render_template('qdashboard.html',qulist=qst)

@app.route('/qoutgraph1', methods = ['GET', 'POST'])
def qoutgraph1():
		if request.method=='POST':
			value=request.form['item']
		qconn = pymysql.connect(host='localhost',user='root',password='',db='inventory_management',charset='utf8mb4',cursorclass=pymysql.cursors.DictCursor)
		qcur = qconn.cursor()
		qcur.execute("SELECT * FROM `demandforecastinputdata")
		qsdata = qcur.fetchall()
		qdata = pd.DataFrame(qsdata)

		#graph1
		adata=qdata['TotalDemand']
		x_axis=qdata['Date'].astype(str)

		#predictedgraph1
		pcur = qconn.cursor()
		pcur.execute("SELECT * FROM `forecastoutputq` WHERE `Model`='"+value+"'")
		psdata = pcur.fetchall()
		edata = pd.DataFrame(psdata)
		eedata=edata['TotalDemand'].astype(float)
		ldata=eedata.values
		
		nur = qconn.cursor()
		nur.execute("SELECT MIN(`Date`) AS 'MIN' FROM `forecastoutputq` WHERE `Model`='"+value+"'")
		MIN=nur.fetchone()
		pdata=[]
		i=0
		k=0
		a="null"
		while(x_axis[i]<MIN['MIN']):
			pdata.append(a)
			i=i+1
			k=k+1
		ata=np.concatenate((pdata,ldata),axis=0)
		
		#x axis
		fcur = qconn.cursor()
		fcur.execute("SELECT `Date` FROM `demandforecastinputdata` WHERE `Date`<'"+MIN['MIN']+"'")
		fsdata = fcur.fetchall()
		indx = pd.DataFrame(fsdata)
		indx=indx['Date'].astype(str).values
		index=np.concatenate((indx,edata['Date'].values),axis=0)
		
		#bargraph
		bcur = qconn.cursor()
		bcur.execute("SELECT * FROM `forecastoutputq` WHERE `Model`='"+value+"'")
		bsdata = bcur.fetchall()
		bdata = pd.DataFrame(bsdata)
		
		btdf=bdata['Date'].astype(str)
		btre11 = np.array([])
		btres11 = np.append(btre11,btdf)

		b1tdf1=bdata[['Spain']]	#spain
		b1tr1 = np.array([]) 
		b1tr11 = np.append(b1tr1, b1tdf1)
		
		b2tdf1=bdata[['Austria']]	#austria
		b2tr1 = np.array([]) 
		b2tr11 = np.append(b2tr1, b2tdf1)
		
		b3tdf1=bdata[['Japan']]	#japan
		b3tr1 = np.array([]) 
		b3tr11 = np.append(b3tr1, b3tdf1)
		
		b4tdf1=bdata[['Hungary']]	#hungry
		b4tr1 = np.array([]) 
		b4tr11 = np.append(b4tr1, b4tdf1)
		
		b5tdf1=bdata[['Germany']]	#germany
		b5tr1 = np.array([]) 
		b5tr11 = np.append(b5tr1, b5tdf1)

		b6tdf1=bdata[['TotalDemand']]	#total
		b6tr1 = np.array([]) 
		b6tr11 = np.append(b6tr1, b6tdf1)

		#comparisonbar
		ccur = qconn.cursor()
		ccur.execute("SELECT * FROM `forecastoutputq` WHERE `Model`='"+value+"'")
		csdata = ccur.fetchall()
		cdata = pd.DataFrame(csdata)
		
		ctdf=cdata['Date'].astype(str)
		ctre11 = np.array([])
		ctres11 = np.append(ctre11,ctdf)

		c1tdf1=cdata[['RatioIncrease']]	#ratioincrease
		c1tr1 = np.array([]) 
		c1tr11 = np.append(c1tr1, c1tdf1)	
		
		qcur.execute("SELECT * FROM `summaryerror`")
		sdata = qcur.fetchall()
		mape = pd.DataFrame(sdata)
		qconn.close()
		return render_template('qdashboard.html',mon=value,qulist=qst,mape=mape.to_html(index=False),say=1,pdata=ata,adata=adata.values,x_axis=index,frm=len(qdata)-1,to=k,x13=btres11,x14=ctres11,y13=b1tr11,y14=b2tr11,y15=b3tr11,y16=b4tr11,y17=b5tr11,y18=b6tr11,y19=c1tr11)

@app.route("/yearlysimulation",methods = ['GET','POST'])
def yearlysimulation():
		if request.method == 'POST':
			gdp=0
			pi=0
			ms=0
			adv=0
			
			gdp_dis=request.form.get('gdp_dis')
			pi_dis=request.form.get('pi_dis')
			ms_dis=request.form.get('ms_dis')
			adv_dis=request.form.get('adv_dis')
			
			min=request.form.get('min')
			max=request.form.get('max')
			mue=request.form.get('mue')
			sig=request.form.get('sig')
			cval=request.form.get('cval')
			
			
			min1=request.form.get('min1')
			max1=request.form.get('max1')
			mue1=request.form.get('mue1')
			sig1=request.form.get('sig1')
			cval1=request.form.get('cval1')
			
			min2=request.form.get('min2')
			max2=request.form.get('max2')
			mue2=request.form.get('mue2')
			sig2=request.form.get('sig2')
			cval2=request.form.get('cval2')
			
			min3=request.form.get('min3')
			max3=request.form.get('max3')
			mue3=request.form.get('mue3')
			sig3=request.form.get('sig3')
			cval3=request.form.get('cval3')
			
			itr= int(request.form.get('itr'))
			frm = request.form.get('from')
			sfrm=int(frm[:4])
			to = request.form.get('to')
			sto=int(to[:4])
			
			kwargs={}
			atrtable=[]
			
			if request.form.get('gdp'):
				gdp=1
				atrtable.append('Gdp')
				if gdp_dis == 'gdp_dis1':
					min=request.form.get('min')
					max=request.form.get('max')
					kwargs['Gdp_dis']='Uniform'
					kwargs['gdpvalues']=[min,max]
				if gdp_dis == 'gdp_dis2':
					mue=request.form.get('mue')
					sig=request.form.get('sig')
					kwargs['Gdp_dis']='Normal'
					kwargs['gdpvalues']=[mue,sig]
				if gdp_dis == 'gdp_dis3':
					kwargs['Gdp_dis']='Random'
					pass
				if gdp_dis == 'gdp_dis4':
					cval=request.form.get('cval')
					kwargs['Gdp_dis']='Constant'
					kwargs['gdpvalues']=[cval]

			if request.form.get('pi'):
				pi=1
				atrtable.append('Pi')
				if pi_dis == 'pi_dis1':
					min1=request.form.get('min1')
					max1=request.form.get('max1')
					kwargs['Pi_dis']='Uniform'
					kwargs['pivalues']=[min1,max1]
				if pi_dis == 'pi_dis2':
					mue1=request.form.get('mue1')
					sig1=request.form.get('sig1')
					kwargs['Pi_dis']='Normal'
					kwargs['pivalues']=[mue1,sig1]
				if pi_dis == 'pi_dis3':
					kwargs['Pi_dis']='Random'
					pass
				if pi_dis == 'pi_dis4':
					cval1=request.form.get('cval1')
					kwargs['Pi_dis']='Constant'
					kwargs['pivalues']=[cval1]
				
			if request.form.get('ms'):
				ms=1
				atrtable.append('Ms')
				if ms_dis == 'ms_dis1':
					min=request.form.get('min2')
					max=request.form.get('max2')
					kwargs['Ms_dis']='Uniform'
					kwargs['msvalues']=[min2,max2]
				if ms_dis == 'ms_dis2':
					mue=request.form.get('mue2')
					sig=request.form.get('sig2')
					kwargs['Ms_dis']='Normal'
					kwargs['msvalues']=[mue2,sig2]
				if ms_dis == 'ms_dis3':
					kwargs['Ms_dis']='Random'
					pass
				if ms_dis == 'ms_dis4':
					cval=request.form.get('cval2')
					kwargs['Ms_dis']='Constant'
					kwargs['msvalues']=[cval2]
				
			if request.form.get('adv'):
				adv=1
				atrtable.append('Adv')
				if adv_dis == 'adv_dis1':
					min=request.form.get('min3')
					max=request.form.get('max3')
					kwargs['Adv_dis']='Uniform'
					kwargs['advvalues']=[min3,max3]
				if adv_dis == 'adv_dis2':
					mue=request.form.get('mue3')
					sig=request.form.get('sig3')
					kwargs['Adv_dis']='Normal'
					kwargs['advvalues']=[mue3,sig3]
				if adv_dis == 'adv_dis3':
					kwargs['Adv_dis']='Random'
					pass
				if adv_dis == 'adv_dis4':
					cval=request.form.get('cval3')
					kwargs['Adv_dis']='Constant'
					kwargs['advvalues']=[cval3]

			#print(kwargs)
			#print(atrtable)
			
			con = pymysql.connect(host='localhost',user='root',password='',db='inventory_management',charset='utf8mb4',cursorclass=pymysql.cursors.DictCursor)
			cur = con.cursor()
			cur.execute("CREATE TABLE IF NOT EXISTS `stech` (`gdp` VARCHAR(1),`pi` VARCHAR(1), `ms` VARCHAR(1),`adv` VARCHAR(1),`itr` VARCHAR(5),`sfrm` VARCHAR(10),`sto` VARCHAR(10))")
			cur.execute("DELETE FROM `stech`")
			con.commit()
			cur.execute("INSERT INTO `stech` VALUES('"+str(gdp)+"','"+str(pi)+"','"+str(ms)+"','"+str(adv)+"','"+str(itr)+"','"+str(sfrm)+"','"+str(sto)+"')")
			con.commit()
			
			
			
			
			data = pd.DataFrame(Yeardata)
			#print(data)
			data.columns 
			xvar=pd.concat([data['GDP'],data['Pi_Exports'],data['Market_Share'],data['Advertisement_Expense']],axis=1)
			yvar=pd.DataFrame(data['TotalDemand'])




			regr = linear_model.LinearRegression()
			regr.fit(xvar,yvar)
	#		predict=regr.predict(xvar)



			#Error Measures
			def ME(y_true, y_pred):
				y_true, y_pred = np.array(y_true), np.array(y_pred)
				return np.mean(y_true - y_pred) 
			#MAE
			def MAE(y_true, y_pred):
				y_true, y_pred = np.array(y_true), np.array(y_pred)
				return np.mean(np.abs(y_true - y_pred))
			#MAPE 
			def MAPE(y_true, y_pred):
				 y_true, y_pred = np.array(y_true), np.array(y_pred)
				 return np.mean(np.abs((y_true - y_pred) / y_pred)) * 100 



			def sim(iteration,data,startyear,endyear,atrtable,Gdp_dis=None,gdpvalues=None,Adv_dis=None,advvalues=None,Ms_dis=None,msvalues=None,Pi_dis=None,pivalues=None):
				preddata=pd.DataFrame()
				simdata=pd.DataFrame()
				#Errordf=pd.DataFrame()
				Errormsr=pd.DataFrame()
				date=pd.date_range(start=pd.datetime(startyear, 1, 1), end=pd.datetime(endyear+1, 1, 1),freq='A')
				date=pd.DataFrame(date.strftime("%Y"))
				 
				 #Fetching The Orignal Data Of Available Years of the Orignal Data That We Have Actually
				m=len(date)
				Arrayofdates=data['Date']
				vari=[] 
				for var in Arrayofdates:
					vari.append(var[:4])
				Arrayofdates=pd.DataFrame(vari)
				dates=[]
				Fetchdata=[]
				for i in range(0,m):
					years=date.loc[i]
				for j in range(0,len(Arrayofdates)):
					if int(Arrayofdates.loc[j])==int(years):
						da=data['TotalDemand'].loc[j]
						Fetchdata.append(da)  #Gives Data In the Given Range That we have actually
						dates.extend(years) #Gives Years that we have data
				
				for i in range(0,iteration):
					df=pd.DataFrame()
					#for The Gdp
					S='flag'
					for row in atrtable:
						if row=='Gdp':
							S='Gdp'
					if S=='Gdp':
						for row in Gdp_dis:
							if row=='Normal':
							   gdpdf=pd.DataFrame(np.random.normal(gdpvalues[0],gdpvalues[1],m))
							elif row=='Uniform':
							   gdpdf=pd.DataFrame(np.random.normal(gdpvalues[0],gdpvalues[1],m))
							elif row=='Constant': 
							   gdpdf=pd.DataFrame(np.random.choice([gdpvalues[0]],m))
							else:
							   gdpdf=pd.DataFrame(np.random.uniform(-4,4,m))
					else:
					   gdpdf=pd.DataFrame(np.random.uniform(0,0,m))
					# for the pi dataframe
					O='flag'
					for row in atrtable:
						  if row=='Pi':
							  O='Pi'
					if O=='Pi':
						for row in Pi_dis:
							if row=='Normal':
							   pidf=pd.DataFrame(np.random.normal(pivalues[0],pivalues[1],m))
							elif row=='Uniform':
							   pidf=pd.DataFrame(np.random.normal(pivalues[0],pivalues[1],m))
							elif row=='Constant': 
							   pidf=pd.DataFrame(np.random.choice([pivalues[0]],m))
							else:
							   pidf=pd.DataFrame(np.random.random_integers(80,120,m))
					else:
					   pidf=pd.DataFrame(np.random.uniform(0,0,m))
					
					
					#for the Adv Dataframe
					N='flag'
					for row in atrtable:
						if row=='Adv':
							N='Adv'
					if N=='Adv':
						for row in Adv_dis:
							if row=='Normal':
							   advdf=pd.DataFrame(np.random.normal(advvalues[0],advvalues[1],m))
							elif row=='Uniform':
							   advdf=pd.DataFrame(np.random.normal(advvalues[0],advvalues[1],m))
							elif row=='Constant': 
							   advdf=pd.DataFrame(np.random.choice([advvalues[0]],m))
							else:
							   advdf=pd.DataFrame(np.random.random_integers(500000,1000000,m))
					else:
					   advdf=pd.DataFrame(np.random.uniform(0,0,m))
					#for the Ms dataframe
					U='flag'
					for row in atrtable:
						if row=='Ms':
							U='Ms'
					if U=='Ms':
						for row in Ms_dis:
							if row=='Normal':
							   msdf=pd.DataFrame(np.random.normal(msvalues[0],msvalues[1],m))
							elif row=='Uniform':
							   msdf=pd.DataFrame(np.random.normal(msvalues[0],msvalues[1],m))
							elif row=='Constant': 
							   msdf=pd.DataFrame(np.random.choice([msvalues[0]],m))
							else:
							   msdf=pd.DataFrame(np.random.uniform(0.1,0.5,m))
					else:
					   msdf=pd.DataFrame(np.random.uniform(0,0,m))
					
				#Concatenating All the dataframes for Simulation Data
					df=pd.concat([gdpdf,pidf,msdf,advdf],axis=1)
					simid=pd.DataFrame(np.random.choice([i+1],m))
					dd=pd.concat([simid,gdpdf,pidf,advdf,msdf],axis=1)
					dd.columns=['Year','Gdp','Pi','Adv','Ms']
					simdata=pd.concat([simdata,dd],axis=0)
					
				#Predicting the Data And store in pred data through onhand Regression Method
					
					dfs=pd.DataFrame(regr.predict(df))
					datatable=pd.concat([simid,date,dfs],axis=1)
					datatable.columns=['simid','Year','Total_Demand(Tonnes)']
					preddata=pd.concat([datatable,preddata],axis=0)
					
					
					datas=list()
			  #Geting Data With Respective Dates
			#        print(datatable)
			  
					for row in dates:
			#            print(dates)
						datas.extend(datatable.loc[datatable['Year'] ==row, 'Total_Demand(Tonnes)'])
					
					kkk=pd.DataFrame(datas)
					me=ME(Fetchdata,kkk)
					mae=MAE(Fetchdata,kkk)
					mape=MAPE(Fetchdata,kkk)
					dfe=pd.DataFrame([me,mae,mape],index=['ME','MAE','MAPE']).T    
					Errormsr=pd.concat([Errormsr,dfe],axis=0).reset_index(drop=True)
				return preddata,simdata,Errormsr


			preddata,simdata,Errormsr=sim(itr,data,sfrm,sto,atrtable,**kwargs)
			engine = create_engine("mysql+pymysql://{user}:{pw}@localhost/{db}".format(user="root",pw="",db="inventory_management"))
			preddata.to_sql(con=engine, name='predicteddata',index=False, if_exists='replace')
			engine2 = create_engine("mysql+pymysql://{user}:{pw}@localhost/{db}".format(user="root",pw="",db="inventory_management"))
			simdata.to_sql(con=engine2, name='simulationdata',index=False, if_exists='replace')
			con.commit()
			engine3 = create_engine("mysql+pymysql://{user}:{pw}@localhost/{db}".format(user="root",pw="",db="inventory_management"))
			Errormsr.to_sql(con=engine3, name='simerror',index=False, if_exists='replace')
			con.commit()
			
			cnr=con.cursor()
			cnr.execute("SELECT * FROM `simerror`")
			sdata = cnr.fetchall()
			simerror = pd.DataFrame(sdata)
			
			
			con.close()
			return render_template('ysimulation.html',sayy=1,simerror=simerror.to_html(index=False))
		return render_template('ysimulation.html')
##PROCURMENT PLANNING
@app.route('/procurementplanning')
def procurementplanning():

		return render_template('vendorselection_criterianumberask.html')


@app.route("/criteriagenerate", methods=['GET','POST'])
def criteriagenerate():
		if request.method == 'POST':
			global cnmbr
			global vnmbr
			cnmbr = int(request.form['cnmbr'])
			vnmbr = int(request.form['vnmbr'])
			if cnmbr == 0 or vnmbr==0:
				return render_template('criterianumberask.html',warning='Data Invalid')
			cmainlist=[]
			global cnames
			cnames = []
			for i in range (1,cnmbr+1):
				lst=[]
				name='cname'+str(i)
				lst.append(i)
				lst.append(name)
				cmainlist.append(lst)
				cnames.append(name)
			vmainlist=[]
			global vnames
			vnames = []
			for i in range (1,vnmbr+1):
				lst=[]
				name='vname'+str(i)
				lst.append(i)
				lst.append(name)
				vmainlist.append(lst)
				vnames.append(name)

			return render_template('vendorselection_criteriagenerate.html',cmainlist=cmainlist,vmainlist=vmainlist)
		return render_template('vendorselection_criterianumberask.html')

@app.route("/criteriagenerated", methods=['GET','POST'])
def criteriagenerated():
		if request.method == 'POST':
			global criterianames
			criterianames=[]
			for name in cnames:
				criterianame = request.form[name]
				criterianames.append(criterianame)
			global vendornames
			vendornames=[]
			for name in vnames:
				vendorname = request.form[name]
				vendornames.append(vendorname)
			
			mcrlst=[]
			cn=len(criterianames)
			k=1
			global maincriteriaoption
			maincriteriaoption=[]
			global maincritriacri
			maincritriacri=[]
			for i in range(cn-1):
				for j in range (i+1,cn):
					cri='criteriaorder'+str(k)
					opt='coption'+str(k)
					crlst=[k,cri,criterianames[i],criterianames[j],opt]
					mcrlst.append(crlst)
					k=k+1
					maincriteriaoption.append(opt)
					maincritriacri.append(cri)
			
			mvrlst=[]
			vn=len(vendornames)
			k=1
			global mainvendoroption
			mainvendoroption=[]
			global mainvendorcri
			mainvendorcri=[]
			for z in criterianames:
				mvrlst1=[]
				vcri=[]
				vopt=[]
				for i in range(vn-1):
					for j in range (i+1,vn):
						cri='vendororder'+z+str(k)
						opt='voption'+z+str(k)
						vrlst=[k,cri,vendornames[i],vendornames[j],opt]
						mvrlst1.append(vrlst)
						k=k+1
						vcri.append(cri)
						vopt.append(opt)
				mvrlst.append(mvrlst1)
				mainvendorcri.append(vcri)
				mainvendoroption.append(vopt)

			return render_template('vendorselection_maincriteria.html',mcrlst=mcrlst,mvrlst=mvrlst)
		return render_template('vendorselection_criteriagenerated.html')

def tablecreator(imp,val,crit):
	n=len(imp)
	for i in range(n):
		if imp[i]==1:
			val[i]=float(1/val[i])
	fdata=pd.DataFrame(columns=[crit],index=[crit])
	i=0
	k=0
	for index in fdata.index:
		j=0
		for columns in fdata.columns:
			if i==j:
				fdata[index][columns]=1
			if i<j:
				fdata[index][columns]=round((float(val[k])),2)
				fdata[columns][index]=round((1/val[k]),2)
				k=k+1
			j=j+1
		i=i+1
	return fdata
@app.route("/criteriaread", methods=['GET','POST'])
def criteriaread():
		if request.method == 'POST':
			importances = []
			values = []
			for name1 in maincritriacri:
				imp = int(request.form[name1])
				importances.append(imp)
			for name2 in maincriteriaoption:
				val = int(request.form[name2])
				values.append(val)
			#global maincriteriadata
			maincriteriadata=tablecreator(importances,values,criterianames)
			
			mainimportances=[]
			for crioption in mainvendorcri:
				importance=[]
				for option1 in crioption:
					impc = int(request.form[option1])
					importance.append(impc)
				mainimportances.append(importance)
			
			mainvalues=[]
			for vendoroption in mainvendoroption:
				vvalues=[]
				for option2 in vendoroption:
					valuev = int(request.form[option2])
					vvalues.append(valuev)
				mainvalues.append(vvalues)
			maindf=[]
			for z in range(len(criterianames)):
				df=tablecreator(mainimportances[z],mainvalues[z],vendornames)
				maindf.append(df)

			dictmain={'crit':maincriteriadata}
			names=criterianames
			dfs=maindf

			dictionary=dict((n,d) for (n,d) in zip(names,dfs))

			def ahpmain(dictmain):
				global wt_Crit
				wt_Crit=[]
				key=[]
				key=list(dictmain.keys())
				for i in key:
					Crit=np.dot(dictmain[i],dictmain[i])
					row_sum=[]
					for j in range(len(Crit)):
						row_sum.append(sum(Crit[j]))
					wt_Crit.append([s/sum(row_sum) for s in row_sum])
					Crit=[]
				return wt_Crit

			def ahp(dictmain,dictionary):
				global output
				main= ahpmain(dictmain)   
				submain= ahpmain(dictionary)
				dd=pd.DataFrame(submain).T
				df=pd.DataFrame(main).T
				output=np.dot(dd,df)
				return output,dd

			yaxis,dd=ahp(dictmain,dictionary)
			yax=pd.DataFrame(yaxis,index=vendornames,columns=['Score']).sort_values('Score',ascending=False).T
			ynames=yax.columns
			yval=yax.T.values
			dd.index=vendornames
			dd.columns=names
			dd=dd.T
			opq23=[]
			for column in dd.columns:
				opq21=[]
				opq22=[]
				opq21.append(column)
				for val in dd[column]:
					opq22.append(val)
				opq21.append(opq22)
				opq23.append(opq21)

			return render_template('vendorselection_ahp_final_output.html',ynames=ynames,yval=yval,dd=opq23,names=names)
		return render_template('vendorselection_criteriagenerated.html')

#DETERMINISTIC STARTS
@app.route("/spt")
def spt():
		return render_template('SinglePeriod.html')

@app.route("/ppbreak")
def ppbreak():
		return render_template('pbreak.html')

@app.route('/pbrk', methods=['GET','POST'])
def pbrk():
		return render_template('pbrk.html')

@app.route('/eoq', methods=['GET','POST'])
def eoq():
		##setUpCost::setting up cost prior(>>setUpCost;<<moving rate)  
		AnnulaUnitsDemand=100##purchase demand of product per year
		FixedCost=500 ##cost fixed for the product
		AnnHoldingcost=0.25 ##remaining goods cost
		UnitCost=445 ##purchasing cost
		LeadTime=10 ##time b/w initiation and completion of a production process.
		SafetyStock=100##extra stock
		
		if request.method == 'POST':
			AnnulaUnitsDemand= request.form['AnnulaUnitsDemand']
			FixedCost=request.form['FixedCost']
			AnnHoldingcost=request.form['AnnHoldingcost'] 
			UnitCost=request.form['UnitCost']
			LeadTime=request.form['LeadTime']
			SafetyStock=request.form['SafetyStock']
			
			AnnulaUnitsDemand=float(AnnulaUnitsDemand)
			FixedCost=float(FixedCost)
			AnnHoldingcost=float(AnnHoldingcost)
			UnitCost=float(UnitCost)
			LeadTime=float(LeadTime)
			SafetyStock=float(SafetyStock)        
			
		sgap=1 
		pgap=1
		HoldingCost=AnnHoldingcost*UnitCost
		EOQ=round((math.sqrt((2*AnnulaUnitsDemand*FixedCost)/(HoldingCost*pgap))*sgap),2)
		REOQ=round((math.sqrt((2*AnnulaUnitsDemand*FixedCost)/(HoldingCost*pgap))*sgap),0)  
		totOrderCost=round((FixedCost*AnnulaUnitsDemand/EOQ),2) 
		totHoldCost=round(((HoldingCost*EOQ*pgap)/2),2) 
		TotalCost=round((totOrderCost+totHoldCost),2)
		
		NumOrders=round((AnnulaUnitsDemand/EOQ),2)
		OrderTime=round((365/NumOrders),2)
		ReorderPoint=round((((AnnulaUnitsDemand/365)*LeadTime)+SafetyStock),0)
		
		count=round((EOQ*.75),0)
		qtylist1=[]
		hclist=[]
		sclist=[]
		mtlist=[]
		tclist=[] 
		
		while (count < EOQ):
			qtylist1.append(count)
			hclist.append(round((count/2*HoldingCost),2))
			sclist.append(round((AnnulaUnitsDemand/count*FixedCost),2))
			mtlist.append(round((AnnulaUnitsDemand*UnitCost),2))
			tclist.append(round((count/2*HoldingCost+AnnulaUnitsDemand/count*FixedCost),2))
			count +=2
		
		qtylist1.append(EOQ) 
		hclist.append(totHoldCost) 
		sclist.append(totOrderCost)
		tclist.append(totHoldCost+totOrderCost)
		
		while (count < (EOQ*2)):
			qtylist1.append(count)
			hclist.append(round((count/2*HoldingCost),2))
			sclist.append(round((AnnulaUnitsDemand/count*FixedCost),2))
			mtlist.append(round((AnnulaUnitsDemand*UnitCost),2))
			tclist.append(round((count/2*HoldingCost+AnnulaUnitsDemand/count*FixedCost),2))
			count +=2
		val=0
		for i in range(len(tclist)):
			if(EOQ==qtylist1[i]):
				val=i

	#    sstock=int(math.sqrt((LeadTime^2)+(int(ReorderPoint)^2)))            
		return render_template('eoq.html',NumOrders=NumOrders,OrderTime=OrderTime,
							   ReorderPoint=ReorderPoint,HoldCost=totHoldCost,TotalCost=TotalCost,
							   EOQ=EOQ,REOQ=REOQ,
							   sclist=sclist,hclist=hclist,tclist=tclist,val=val,qtylist1=qtylist1,
							   AnnulaUnitsDemand=AnnulaUnitsDemand,FixedCost=FixedCost,
							   AnnHoldingcost=AnnHoldingcost,UnitCost=UnitCost,LeadTime=LeadTime,
							   SafetyStock=SafetyStock)
########################EEEEppppppppppQQQQQQ############
########################EEEEppppppppppQQQQQQ############
@app.route('/eproduction', methods=['GET','POST'])
def eproduction():
		AnnulaUnitsDemand=100
		Prodrate=125
		FixedCost=500
		AnnHoldingcost=0.1
		UnitCost=25000
		LeadTime=10
		SafetyStock=100
		
		if request.method == 'POST':
			AnnulaUnitsDemand= request.form['AnnulaUnitsDemand']
			Prodrate=request.form['Prodrate']
			FixedCost=request.form['FixedCost']
			AnnHoldingcost=request.form['AnnHoldingcost'] 
			UnitCost=request.form['UnitCost']
			LeadTime=request.form['LeadTime']
			SafetyStock=request.form['SafetyStock']
			
			AnnulaUnitsDemand=int(AnnulaUnitsDemand)
			Prodrate=int(Prodrate)
			FixedCost=int(FixedCost)
			AnnHoldingcost=float(AnnHoldingcost)
			UnitCost=int(UnitCost)
			LeadTime=int(LeadTime)
			SafetyStock=int(SafetyStock)
		if(Prodrate<=AnnulaUnitsDemand):
			return render_template('eproduction.html',warning='Production date should not be least than Annual Demand',
								   AnnulaUnitsDemand=AnnulaUnitsDemand,FixedCost=FixedCost,
								   AnnHoldingcost=AnnHoldingcost,UnitCost=UnitCost,Prodrate=Prodrate,
								   LeadTime=LeadTime,SafetyStock=SafetyStock
								   )

		pgap=round((1-(AnnulaUnitsDemand/Prodrate)),2) 

		HoldingCost=float(AnnHoldingcost*UnitCost)
		EOQ=round((math.sqrt((2*AnnulaUnitsDemand*FixedCost)/(HoldingCost*pgap))),2)
		REOQ=round((math.sqrt((2*AnnulaUnitsDemand*FixedCost)/(HoldingCost*pgap))),0)  
		totOrderCost=round((FixedCost*AnnulaUnitsDemand/EOQ),2) 
		totHoldCost=round(((HoldingCost*EOQ*pgap)/2),2) 
		TotalCost=round((totOrderCost+totHoldCost),2)

		NumOrders=round((AnnulaUnitsDemand/EOQ),2)
		OrderTime=round((365/NumOrders),2)
		ReorderPoint=round((((AnnulaUnitsDemand/365)*LeadTime)+SafetyStock),0)
		
		count=EOQ*.75
		qtylist1=[]
		hclist=[]
		sclist=[]
		mtlist=[]
		tclist=[] 
		
		while (count < EOQ):
			qtylist1.append(int(count))
			hclist.append(round((count/2*HoldingCost*pgap),2))
			sclist.append(round((AnnulaUnitsDemand/count*FixedCost),2))
			mtlist.append(round((AnnulaUnitsDemand*UnitCost),2))
			tclist.append(round(((count/2*HoldingCost*pgap+AnnulaUnitsDemand/count*FixedCost)),2))
			count +=2
		
		qtylist1.append(EOQ) 
		hclist.append(totHoldCost) 
		sclist.append(totOrderCost)
		tclist.append(totOrderCost+totHoldCost)
		
		while (count < (EOQ*1.7)):
			qtylist1.append(int(count))
			hclist.append(round((count/2*HoldingCost*pgap),2))
			sclist.append(round((AnnulaUnitsDemand/count*FixedCost),2))
			mtlist.append(round((AnnulaUnitsDemand*UnitCost),2))
			tclist.append(round(((count/2*HoldingCost*pgap+AnnulaUnitsDemand/count*FixedCost)),2))
			count +=2      

		val=0
		for i in range(len(tclist)):
			if(EOQ==qtylist1[i]):
				val=i

		return render_template('eproduction.html',NumOrders=NumOrders,OrderTime=OrderTime,
							   ReorderPoint=ReorderPoint,HoldCost=totHoldCost,TotalCost=TotalCost,
							   EOQ=EOQ,REOQ=REOQ,
							   sclist=sclist,hclist=hclist,tclist=tclist,val=val,qtylist1=qtylist1,
							   AnnulaUnitsDemand=AnnulaUnitsDemand,FixedCost=FixedCost,
							   AnnHoldingcost=AnnHoldingcost,UnitCost=UnitCost,Prodrate=Prodrate,
							   LeadTime=LeadTime,SafetyStock=SafetyStock
							   )

######################EEEEppppppppppQQQQQQ############
######################EEEEppppppppppQQQQQQ############
@app.route('/eoq_backorders', methods=['GET','POST'])
def eoq_backorders():
		AnnulaUnitsDemand=12000
		shortcost=1.1
		FixedCost=8000
		AnnHoldingcost=0.3
		UnitCost=1
		LeadTime=10
		SafetyStock=100
		
		if request.method == 'POST':
			AnnulaUnitsDemand= request.form['AnnulaUnitsDemand']
			shortcost=request.form['shortcost']
			FixedCost=request.form['FixedCost']
			AnnHoldingcost=request.form['AnnHoldingcost'] 
			UnitCost=request.form['UnitCost']
			LeadTime=request.form['LeadTime']
			SafetyStock=request.form['SafetyStock']
			
			AnnulaUnitsDemand=int(AnnulaUnitsDemand)
			shortcost=int(shortcost)
			FixedCost=int(FixedCost)
			AnnHoldingcost=float(AnnHoldingcost)
			UnitCost=int(UnitCost)
			LeadTime=int(LeadTime)
			SafetyStock=int(SafetyStock)
		HoldingCost=float(AnnHoldingcost*UnitCost) 
		sgap=(shortcost+HoldingCost)/shortcost     

		EOQ=round((math.sqrt((2*AnnulaUnitsDemand*FixedCost)/HoldingCost))*(math.sqrt(sgap)),2) 
		REOQ=round(math.sqrt((2*AnnulaUnitsDemand*FixedCost)/(HoldingCost)*sgap),0) 

		totbackorder=EOQ*(HoldingCost/(shortcost+HoldingCost))     
		totOrderCost=round(((FixedCost*AnnulaUnitsDemand)/EOQ),2) 
		totHoldCost=round(((HoldingCost*((EOQ-totbackorder)**2))/(2*EOQ)),2) 
		totshortcost=round((shortcost*(totbackorder**2)/(2*EOQ)),2)     
		TotalCost=round((totOrderCost+totHoldCost+totshortcost),2)     

		NumOrders=round((AnnulaUnitsDemand/EOQ),2) 
		OrderTime=round((365/NumOrders),2) 
		ReorderPoint=round((((AnnulaUnitsDemand/365)*LeadTime)+SafetyStock),0) 

		count= EOQ*.75         
		qtylist1=[] 
		hclist=[] 
		sclist=[] 
		mtlist=[] 
		shlist=[] 
		tclist=[] 
				
		while (count < EOQ): 
			qtylist1.append(int((count))) 
			hclist.append(round(((HoldingCost*((count-totbackorder)**2))/(2*count)),2)) 
			sclist.append(round((AnnulaUnitsDemand/count*FixedCost),2)) 
			mtlist.append(round((AnnulaUnitsDemand*UnitCost),2)) 
			shlist.append(round((shortcost*((totbackorder)**2)/(2*count)),2)) 
			tclist.append(round(((((HoldingCost*((count-totbackorder)**2))/(2*count))+AnnulaUnitsDemand/count*FixedCost)+shortcost*((totbackorder)**2)/(2*count)),2)) 
			count +=2 
			
		qtylist1.append(EOQ) 
		hclist.append(totHoldCost) 
		sclist.append(totOrderCost) 
		shlist.append(totshortcost) 
		tclist.append(totOrderCost+totshortcost+totHoldCost)     
		
		while (count < (EOQ*1.7)): 
			qtylist1.append(int((count))) 
			hclist.append(round(((HoldingCost*((count-totbackorder)**2))/(2*count)),2)) 
			sclist.append(round((AnnulaUnitsDemand/count*FixedCost),2)) 
			mtlist.append(round((AnnulaUnitsDemand*UnitCost),2)) 
			shlist.append(round((shortcost*((totbackorder)**2)/(2*count)),2)) 
			tclist.append(round(((((HoldingCost*((count-totbackorder)**2))/(2*count))+AnnulaUnitsDemand/count*FixedCost)+shortcost*((totbackorder)**2)/(2*count)),2)) 
			count +=2 

		val=0
		for i in range(len(tclist)):
			if(EOQ==qtylist1[i]):
				val=i

		return render_template('eoq_backorders.html',NumOrders=NumOrders,OrderTime=OrderTime,
							   ReorderPoint=ReorderPoint,HoldCost=totHoldCost,TotalCost=TotalCost,
							   EOQ=EOQ,REOQ=REOQ,
							   shlist=shlist,sclist=sclist,hclist=hclist,tclist=tclist,val=val,qtylist1=qtylist1,
							   AnnulaUnitsDemand=AnnulaUnitsDemand,FixedCost=FixedCost,
							   AnnHoldingcost=AnnHoldingcost,UnitCost=UnitCost,shortcost=shortcost,
							   LeadTime=LeadTime,SafetyStock=SafetyStock)

#################pbreak######################
@app.route("/pbreak_insert", methods=['GET','POST'])
def pbreak_insert():
		if request.method == 'POST':
			quantity = request.form.getlist("quantity[]")
			price = request.form.getlist("price[]")
			conn = pymysql.connect(host='localhost',user='root',password='',db='inventory_classification',charset='utf8mb4',cursorclass=pymysql.cursors.DictCursor)
			curr = conn.cursor()
			curr.execute("CREATE TABLE IF NOT EXISTS `pbreaktable` (quantity int(8),price int(8))")
			curr.execute("DELETE FROM `pbreaktable`")
			conn.commit()
			say=1
			for i in range(len(quantity)):
				quantity_clean = quantity[i]
				price_clean = price[i]
				if quantity_clean and price_clean:
					curr.execute("INSERT INTO `pbreaktable`(`quantity`,`price`) VALUES('"+quantity_clean+"','"+price_clean+"')")
					conn.commit()
				else:
					say=0
		if say==0:
			message="Some values were not inserted!"
		else:
			message="All values were inserted!"
		return(message)

@app.route('/view', methods=['GET','POST'])
def view():
		if request.method == 'POST':
			conn = pymysql.connect(host='localhost',user='root',password='',db='inventory_classification',charset='utf8mb4',cursorclass=pymysql.cursors.DictCursor)
			curr = conn.cursor()
			curr.execute("SELECT * FROM `pbreaktable`")
			res = curr.fetchall()
			ress=pd.DataFrame(res)
		return render_template('pbrk.html',username=username,ress =ress.to_html())

@app.route('/pbreakcalculate', methods=['GET','POST'])
def pbreakcalculate():
		AnnulaUnitsDemand=10
		FixedCost=1
		AnnHoldingcost=0.1
		UnitCost=445
		LeadTime=10
		SafetyStock=100

		if request.method == 'POST':
			if request.form['AnnulaUnitsDemand']:
				AnnulaUnitsDemand= request.form['AnnulaUnitsDemand']
				AnnulaUnitsDemand=float(AnnulaUnitsDemand)
			if request.form['FixedCost']:
				FixedCost=request.form['FixedCost']
				FixedCost=float(FixedCost)
			if request.form['AnnHoldingcost']:
				AnnHoldingcost=request.form['AnnHoldingcost']
				AnnHoldingcost=float(AnnHoldingcost)

		conn = pymysql.connect(host='localhost',user='root',password='',db='inventory_classification',charset='utf8mb4',cursorclass=pymysql.cursors.DictCursor)
		curr = conn.cursor()
		curr.execute("SELECT * FROM `pbreaktable`")
		res = curr.fetchall()
		ress=pd.DataFrame(res)
		conn.close()
		datatable=pd.DataFrame(columns=['Quantity','Price','EOQ','TotalCost'])
		mainlist=[]
		Qu=ress['quantity']
		Qm=0
		for index, i in ress.iterrows():
			tcl=[]
			quantity = i['quantity']
			price = i['price']
			HoldingCost1=AnnHoldingcost*price
			eoq1=round((math.sqrt((2*AnnulaUnitsDemand*FixedCost)/(HoldingCost1))),2)
			REOQ=round(eoq1,0)
			totOrderCost1=round((FixedCost*AnnulaUnitsDemand/eoq1),2)
			totHoldCost1=round(((HoldingCost1*eoq1)/2),2)
			totalcost1=float(round((totOrderCost1+totHoldCost1),2))
			lst=[quantity,price,eoq1,totalcost1]
			a=pd.DataFrame(lst).T
			a.columns=['Quantity','Price','EOQ','TotalCost']
			datatable=pd.concat([datatable,a],ignore_index=True)
			name='TotalCost (Price='+str(a['Price'][0])+')'
			tcl.append(name)
			Qmin=1
			Qmax=Qu[Qm]
			qtylist2=[]
			tclist1=[]

			while (Qmin < Qmax):
				qtylist2.append(Qmin)
				tclist1.append(round((Qmin/2*totHoldCost1+AnnulaUnitsDemand/Qmin*FixedCost),2))
				Qmin +=2  
				
			Qmin=Qmax+1		        
			qtylist2.append(eoq1) 
			tclist1.append(totalcost1)               

			tcl.append(tclist1)       
			mainlist.append(tcl)

		Eu=datatable['EOQ']
		Qu=datatable['Quantity']
		Tu=datatable['TotalCost']
		minlst=[]    
		for i in range(len(Eu)):
			if i ==0:
				if Eu[i]<=Qu[i]:
					minlst.append(i)
			else:
				if Eu[i]<=Qu[i] and Eu[i]>Qu[i-1]:
					minlst.append(i)
		if len(minlst)==0:
			minnval='Solution not feasible'
		else:
			minval=Tu[minlst[0]]
			minnval=Eu[minlst[0]]
			for j in minlst:
				if Tu[j]<minval:
					minval=Tu[j]
					minnval=Eu[j]
			val1=0
			for i in range(len(tclist1)):
				if (round(minnval))==qtylist2[i]:
					val1=i

			minival=round(minval)
			minnival=round(minnval)
			NumOrders=round((AnnulaUnitsDemand/minnval),2)
			OrderTime=round((365/NumOrders),2)
			ReorderPoint=round((((AnnulaUnitsDemand/365)*LeadTime)+SafetyStock),0) 	

		return render_template('pbreak.html',  
			NumOrders=NumOrders,OrderTime=OrderTime,REOQ=REOQ,ReorderPoint=ReorderPoint,
			AnnulaUnitsDemand=AnnulaUnitsDemand,FixedCost=FixedCost,
			AnnHoldingcost=AnnHoldingcost,UnitCost=UnitCost,LeadTime=LeadTime,
			SafetyStock=SafetyStock,minnval=minnval,minval=minval,minival=minival,minnival=minnival,
		  datatable=datatable.to_html(index=False),mainlist=mainlist,
		  val1=val1,tclist1=tclist1,qtylist2=qtylist2)
#################Demand  problalstic######################
@app.route('/demand', methods=['GET', 'POST'])
def demand():
		cost=10
		price=12
		salvage=2
		if request.method == 'POST':
			cost=request.form['cost']
			price=request.form['price']
			salvage=request.form['salvage']   
			
			cost=int(cost)
			price=int(price)
			salvage=int(salvage)    
			
		data=pd.read_csv(localpath+"\\Demand.csv")    
		data = pd.DataFrame(data)    
		cdf=[]
		sum=0
		for row in data['Prob']:
			sum=sum+row
			cdf.append(sum)
		cumm_freq=(pd.DataFrame(cdf)).values##y-axis    
		overcost=cost-salvage
		undercost=price-cost
		CSl=undercost/(undercost+overcost)
		k=[row>CSl for row in cumm_freq]
		count=1
		for row in k:
			if row==False:
				count=count+1    
		demand=(data['Demand']).values    
		w=data['Demand'].loc[count]##line across x-axis
		val=0
		for i in range(len(cumm_freq)):
			if(w==demand[i]):
				val=i                             

		return render_template('demand.html',cost=cost,price=price,salvage=salvage,
								   cumm_freq=cumm_freq,demand=demand,val=val)
@app.route('/normal', methods=['GET', 'POST'])
def normal():
		cost=10
		price=12
		salvage=9
		sd=2
		
		if request.method == 'POST':
			cost=request.form['cost']
			price=request.form['price']
			salvage=request.form['salvage']

			cost=int(cost)
			price=int(price)
			salvage=int(salvage)
		
		data=pd.read_csv(localpath+"\\Demand.csv")    
		data = pd.DataFrame(data)    
		overcost1=cost-salvage
		undercost1=price-cost
		CSl=undercost1/(undercost1+overcost1)
		zz=st.norm.ppf(CSl)##x-line
		z=float(format(zz, '.2f'))
		
	#    Expecteddemand=round(mea+(z*sd))
		mean = 0; sd = 1; variance = np.square(sd)
		x = np.arange(-4,4,.01)##x-axis
		f =(np.exp(-np.square(x-mean)/2*variance)/(np.sqrt(2*np.pi*variance)))##y-axis
		val=0
		for i in range(len(f)):
			if(z==round((x[i]),2)):
				val=i

		return render_template('normal.html',x=x,f=f,val=val,cost=cost,price=price,salvage=salvage)

@app.route('/utype', methods=['GET','POST'])
def utype():
		cost=10
		price=12
		salvage=2
		mini=1
		maxi=10
		
		if request.method == 'POST':
			cost=request.form['cost']
			price=request.form['price']
			salvage=request.form['salvage']
			mini=request.form['mini']
			maxi=request.form['maxi']
			
			cost=int(cost)
			price=int(price)
			salvage=int(salvage)
			mini=int(mini)
			maxi=int(maxi)
			
		data=pd.read_csv(localpath+"\\Demand.csv")    
		data = pd.DataFrame(data)    
		overcost=cost-salvage
		undercost=price-cost
		CSl=undercost/(undercost+overcost)
		expdemand1=round(mini+((maxi-mini)*CSl))
	#    a=[mini,0]
	#    b=[mini,100]
	#    c=[maxi,0]
	#    d=[maxi,100]
	#    width = c[0] - b[0]
	#    height = d[1] - a[1]
		lims = np.arange(0,maxi,1)
		val=0
		for i in range(len(lims)):
			if(expdemand1==lims[i]):
				val=i

		return render_template('utype.html',x=lims,f=lims,val=val,cost=cost,price=price,salvage=salvage,mini=mini,maxi=maxi)
@app.route('/outputx', methods=['GET', 'POST'])
def outputx():
		conn = pymysql.connect(host='localhost',user='root',password='',db='inventory_classification',charset='utf8mb4',cursorclass=pymysql.cursors.DictCursor)
		cur = conn.cursor()
		cur.execute("SELECT * FROM `abc`")
		all_data = cur.fetchall()
		all_data = pd.DataFrame(all_data)
		
		A_ccat=.8
		B_ccat=.95
		
		A_ucat=.1
		B_ucat=.25
		
		tot_cost=all_data['Cost'].sum()
		tot_usage=all_data['Annual Usage'].sum()
		
		all_data['perc_cost']=all_data['Cost']/tot_cost
		all_data['perc_usage']=all_data['Annual Usage']/tot_usage

		all_data.sort_values(by=['perc_cost'], inplace=True, ascending=False)
		
		sort_data=all_data.reset_index()
	   
		sort_data['cum_cperc']=np.nan
		sort_data['cum_uperc']=np.nan
		sort_data['Class']=''

		for i in range(len(sort_data)):
			if(i==0):
				sort_data.set_value(i, 'cum_cperc', sort_data['perc_cost'][i])
				sort_data.set_value(i, 'cum_uperc', sort_data['perc_usage'][i])
		#        cperc_data.append(all_data['perc_cost'][i])
				sort_data.set_value(i,'Class','A')
			else:
				sort_data.set_value(i, 'cum_cperc', sort_data['perc_cost'][i]+sort_data['cum_cperc'][i-1])
				sort_data.set_value(i, 'cum_uperc', sort_data['perc_usage'][i]+sort_data['cum_uperc'][i-1])
				
				if(sort_data['cum_cperc'][i]<=A_ccat and sort_data['cum_uperc'][i]<=A_ucat):
					sort_data.set_value(i,'Class','A')
				elif(sort_data['cum_cperc'][i]<=B_ccat and sort_data['cum_uperc'][i]<=B_ucat):
					sort_data.set_value(i,'Class','B')
				else: 
					sort_data.set_value(i,'Class','C')

		x7=sort_data[['cum_cperc']]
		x1=x7*100
		x3=np.round(x1)
		x2=np.array([])
		x5 = np.append(x2,x3)
		y7= sort_data[['cum_uperc']]
		y1=y7*100
		y3=np.round(y1)
		y2=np.array([])
		y5 = np.append(y2,y3)
		
	###############% of Total cost//
		a= sort_data[(sort_data['Class']=='A')][['perc_cost']]
		j=a.sum()
		k=j*100
		pd.DataFrame(k) 
		kf=k[0]
	 
		b= sort_data[(sort_data['Class']=='B')][['perc_cost']]
		n=b.sum()
		m=n*100
		pd.DataFrame(m) 
		mf=m[0]
		
		c= sort_data[(sort_data['Class']=='C')][['perc_cost']]
		o=c.sum()
		p=o*100
		pd.DataFrame(p)
		pf=p[0]
		
		tes=k,m,p    
		t2 = np.array([])
		te2 = np.append(t2,tes)
	###################Items // Annual Usage 
	#    z=sort_data[['Product number']]
	#    z1=z.sum()
		f= sort_data[(sort_data['Class']=='A')][['Product number']]
		v=f.sum()
		pd.DataFrame(v)
		vif=v[0]
		
		
		f1= sort_data[(sort_data['Class']=='B')][['Product number']]
		u=f1.sum()
		pd.DataFrame(u)
		uif=u[0]
		
		f2= sort_data[(sort_data['Class']=='C')][['Product number']]
		vf=f2.sum()
		pd.DataFrame(vf)
		kif=vf[0]
		
	#################% of Total units //  Annual Usage 
		t= sort_data[(sort_data['Class']=='A')][['perc_usage']]
		i=t.sum()
		p1=i*100
		pd.DataFrame(p1)
		nf=p1[0]
	 
		l= sort_data[(sort_data['Class']=='B')][['perc_usage']]
		t=l.sum()
		q1=t*100
		pd.DataFrame(q1)
		qf=q1[0]
		
		u= sort_data[(sort_data['Class']=='C')][['perc_usage']]
		w=u.sum()
		s1=w*100
		pd.DataFrame(s1)
		sf=s1[0]
		
		test=p1,q1,s1
		tt2 = np.array([])
		tte2 = np.append(tt2,test)

	#############values//Cost*Annual Usage    
		sort_data['Value'] = sort_data['Cost'] * sort_data['Annual Usage']
		
		fz= sort_data[(sort_data['Class']=='A')][['Value']]
		vz=fz.sum()
		pd.DataFrame(vz)
		vzz=vz[0]
		
		
		fz1= sort_data[(sort_data['Class']=='B')][['Value']]
		uz=fz1.sum()
		pd.DataFrame(uz)
		uzf=uz[0]
		
		fz2= sort_data[(sort_data['Class']=='C')][['Value']]
		vzf=fz2.sum()
		pd.DataFrame(vzf)
		kzf=vzf[0]
		
		h=[{'Scenario':'A','Values':vzz,'product number':vif,'perc_usage':nf,'perc_cost ':kf},
		   {'Scenario':'B','Values':uzf,'product number':uif,'perc_usage':qf,'perc_cost ':mf},
		   {'Scenario':'C','Values':kzf,'product number':kif,'perc_usage':sf,'perc_cost ':pf}]
		df = pd.DataFrame(h)
		lo=sort_data[['Product Description','Product number','Cost','Annual Usage','Class']]
		
		cur = conn.cursor()
		cur.execute("SELECT * FROM `abc1`")
		all_data4 = cur.fetchall()
		all_data4 = pd.DataFrame(all_data4)
		
		lolz=all_data4[['Product number','Product Description','Cost','Annual Usage','Average Stay','Average Consumption','Criticality']]

	######################FFFFFFFFSSSSSSSSSNNNNNNNNNNNN#########################
	######################FFFFFFFFSSSSSSSSSNNNNNNNNNNNN#########################
	######################FFFFFFFFSSSSSSSSSNNNNNNNNNNNN#########################

		curr = conn.cursor()
		curr.execute("SELECT * FROM `fsn`")
		all_data1 = curr.fetchall()
		all_data1 = pd.DataFrame(all_data1)
		F_cat=.2
		S_cat=.5
			
		tot_stay=all_data1['Average Stay'].sum()
		tot_consupt=all_data1['Average Consumption'].sum()
		
		
		all_data1['perc_stay']=all_data1['Average Stay']/tot_stay
		all_data1['perc_cons']=all_data1['Average Consumption']/tot_consupt
		
		all_data1.sort_values(by=['perc_stay'], inplace=True, ascending=True)
		
		sort_data1=all_data1.reset_index()
		
		sort_data1['cum_stay']=np.nan
		sort_data1['cum_cons']=np.nan
		sort_data1['Class']=''
		
		
		for i in range(len(sort_data1)):
			if(i==0):
				sort_data1.set_value(i, 'cum_stay', sort_data1['perc_stay'][i])
				sort_data1.set_value(i, 'cum_cons', sort_data1['perc_cons'][i])
				sort_data1.set_value(i,'Class','F')
			else:
				sort_data1.set_value(i, 'cum_stay', sort_data1['perc_stay'][i]+sort_data1['cum_stay'][i-1])
				sort_data1.set_value(i, 'cum_cons', sort_data1['perc_cons'][i]+sort_data1['cum_cons'][i-1])
				
				if(sort_data1['cum_stay'][i]<=F_cat) :
					sort_data1.set_value(i,'Class','F')
				elif(sort_data1['cum_stay'][i]<=S_cat):
					sort_data1.set_value(i,'Class','S')
				else: 
					sort_data1.set_value(i,'Class','N')
				
		x71=sort_data1[['cum_stay']]
		x11=x71*100
		x31=np.round(x11)
		x21=np.array([])
		x51 = np.append(x21,x31)
		y71= sort_data1[['cum_cons']]
		y11=y71*100
		y31=np.round(y11)
		y21=np.array([])
		y51 = np.append(y21,y31)
		
	###############% of Total cost//
		a1= sort_data1[(sort_data1['Class']=='F')][['perc_stay']]
		j1=a1.sum()
		k1=j1*100
		pd.DataFrame(k1) 
		kf1=k1[0]
	 
		b1= sort_data1[(sort_data1['Class']=='S')][['perc_stay']]
		n1=b1.sum()
		m1=n1*100
		pd.DataFrame(m1) 
		mf1=m1[0]
		
		c1= sort_data1[(sort_data1['Class']=='N')][['perc_stay']]
		o1=c1.sum()
		p1=o1*100
		pd.DataFrame(p1)
		pf1=p1[0]
		
		tes1=k1,m1,p1    
		t21 = np.array([])
		te21 = np.append(t21,tes1)
	###################Items // Annual Usage 
	#    z=sort_data[['Product number']]
	#    z1=z.sum()
		f1= sort_data1[(sort_data1['Class']=='F')][['Product number']]
		v1=f1.sum()
		pd.DataFrame(v1)
		vif1=v1[0]
		
		
		f11= sort_data1[(sort_data1['Class']=='S')][['Product number']]
		u1=f11.sum()
		pd.DataFrame(u1)
		uif1=u1[0]
		
		f21= sort_data1[(sort_data1['Class']=='N')][['Product number']]
		vf1=f21.sum()
		pd.DataFrame(vf1)
		kif1=vf1[0]
		
	#################% of Total units //  Annual Usage 
		t1= sort_data1[(sort_data1['Class']=='F')][['perc_cons']]
		i1=t1.sum()
		p11=i1*100
		pd.DataFrame(p11)
		nf1=p11[0]
	 
		l1= sort_data1[(sort_data1['Class']=='S')][['perc_cons']]
		t1=l1.sum()
		q11=t1*100
		pd.DataFrame(q11)
		qf1=q11[0]
		
		u1= sort_data1[(sort_data1['Class']=='N')][['perc_cons']]
		w1=u1.sum()
		s11=w1*100
		pd.DataFrame(s11)
		sf1=s11[0]
		
		test1=p11,q11,s11
		tt21 = np.array([])
		tte21 = np.append(tt21,test1)

	#############values//Cost*Annual Usage    
		sort_data1['Value'] = sort_data1['Average Stay'] * sort_data1['Average Consumption']
		
		fz1= sort_data1[(sort_data1['Class']=='F')][['Value']]
		vz1=fz1.sum()
		pd.DataFrame(vz1)
		vzz1=vz1[0]
		
		
		fz11= sort_data1[(sort_data1['Class']=='S')][['Value']]
		uz1=fz11.sum()
		pd.DataFrame(uz1)
		uzf1=uz1[0]
		
		fz21= sort_data1[(sort_data1['Class']=='N')][['Value']]
		vzf1=fz21.sum()
		pd.DataFrame(vzf1)
		kzf1=vzf1[0]
		
		h1=[{'Scenario':'F','Values':vzz1,'product number':vif1,'perc_cons':nf1,'perc_stay ':kf1},
		   {'Scenario':'S','Values':uzf1,'product number':uif1,'perc_cons':qf1,'perc_stay ':mf1},
		   {'Scenario':'N','Values':kzf1,'product number':kif1,'perc_cons':sf1,'perc_stay ':pf1}]
		df1 = pd.DataFrame(h1)

		lo1=sort_data1[['Product Description','Product number','perc_stay','perc_cons','Class']]
	##############VVVVVVVVVEEEEEEEEEEEEDDDDDDDDD#########
	##############VVVVVVVVVEEEEEEEEEEEEDDDDDDDDD######### 
		cur1 = conn.cursor()
		cur1.execute("SELECT * FROM `ved`")
		all_data2 = cur1.fetchall()
		all_data2 = pd.DataFrame(all_data2)
		all_data2['values']=all_data2['Class'] + all_data2["Criticality"]
		
		AV= all_data2[(all_data2['values']=='AV')]
		AV=AV.index.max()
		
		AE= all_data2[(all_data2['values']=='AE')]
		AE= AE.index.max()
		AE=np.nan_to_num(AE)
		
		AD= all_data2[(all_data2['values']=='AD')]
		AD=AD.index.max()
		AD=np.nan_to_num(AD)
		
		BV=all_data2[(all_data2['values']=='BV')]
		BV=BV.index.max()
		
		BE=all_data2[(all_data2['values']=='BE')]
		BE=BE.index.max()
		
		BD=all_data2[(all_data2['values']=='BD')]
		BD=BD.index.max()
		BD=np.nan_to_num(BD)
		
		CV=all_data2[(all_data2['values']=='CV')]
		CV=CV.index.max()
		CV=np.nan_to_num(CV)
		
		CE=all_data2[(all_data2['values']=='CE')]
		CE=CE.index.max()
		
		CD=all_data2[(all_data2['values']=='CD')]
		CD=CD.index.max()
	 ############################################### 
		xx71=all_data2[['cum_cperc']]
		xx71=xx71.astype(float)
		xx11=xx71*100
		xx31=xx11.round()
		xx21=np.array([])
		xx51 = np.append(xx21,xx31)

		yy71= all_data2[['cum_uperc']]
		yy71=yy71.astype(float)
		yy11=yy71*100
		yy31=yy11.round(0)
		yy21=np.array([])
		yy51 = np.append(yy21,yy31)  

	###############% of Total cost//
		aa= all_data2[(all_data2['Criticality']=='V')][['perc_cost']]
		jj=aa.sum()
		kk=jj*100
		#k=pd.DataFrame(k)
		kkf=kk[0]
	 
		bb= all_data2[(all_data2['Criticality']=='E')][['perc_cost']]
		nn=bb.sum()
		mm=nn*100
	#    m=pd.DataFrame(m) 
		mmf=mm[0]
		
		cc= all_data2[(all_data2['Criticality']=='D')][['perc_cost']]
		oo=cc.sum()
		pp=oo*100
	#    p=pd.DataFrame(p)
		ppf=pp[0]
		
		ttes=[kk,mm,pp]
		ttes=pd.concat(ttes)
		th2 = np.array([])
		the2 = np.append(th2,ttes)
	###################Items // Annual Usage 
	#    z=sort_data[['Product number']]
	#    z1=z.sum()
		ff= all_data2[(all_data2['Criticality']=='V')][['Product number']]
		vv=ff.sum()
		pd.DataFrame(vv)
		vvif=vv[0]
		
		
		ff1= all_data2[(all_data2['Criticality']=='E')][['Product number']]
		uu=ff1.sum()
		pd.DataFrame(uu)
		uuif=uu[0]
		
		ff2= all_data2[(all_data2['Criticality']=='D')][['Product number']]
		vvf=ff2.sum()
		pd.DataFrame(vvf)
		kkif=vvf[0]
		
	#################% of Total units //  Annual Usage 
		tt= all_data2[(all_data2['Criticality']=='V')][['perc_usage']]
		ii=tt.sum()
		pp1=ii*100
		pd.DataFrame(pp1)
		nnf=pp1[0]
	 
		ll= all_data2[(all_data2['Criticality']=='E')][['perc_usage']]
		tq=ll.sum()
		qq1=tq*100
		pd.DataFrame(qq1)
		qqf=qq1[0]
		
		uw= all_data2[(all_data2['Criticality']=='D')][['perc_usage']]
		wu=uw.sum()
		sc1=wu*100
		pd.DataFrame(sc1)
		ssf=sc1[0]
		
		testt=[pp1,qq1,sc1]
		testt=pd.concat(testt)
		ttt2 = np.array([])
		ttte2 = np.append(ttt2,testt)

	#############values//Cost*Annual Usage    
		all_data2['Value'] = all_data2['Cost'] * all_data2['Annual Usage']
		
		fzz= all_data2[(all_data2['Criticality']=='V')][['Value']]
		vzz=fzz.sum()
		pd.DataFrame(vzz)
		vzzz=vzz[0]
		
		
		fzz1= all_data2[(all_data2['Criticality']=='E')][['Value']]
		uzz=fzz1.sum()
		pd.DataFrame(uzz)
		uzzf=uzz[0]
		
		fzz2= all_data2[(all_data2['Criticality']=='D')][['Value']]
		vzzf=fzz2.sum()
		pd.DataFrame(vzzf)
		kzzf=vzzf[0]
		
		hh=[{'Scenario':'V','Values':vzzz,'product number':vvif,'perc_usage':nnf,'perc_cost ':kkf},
		   {'Scenario':'E','Values':uzzf,'product number':uuif,'perc_usage':qqf,'perc_cost ':mmf},
		   {'Scenario':'D','Values':kzzf,'product number':kkif,'perc_usage':ssf,'perc_cost ':ppf}]
		dff = pd.DataFrame(hh)
		

	   
		return render_template('inventoryclassification.html',
							   x=y5,y=x5,
							   barcost=te2 ,barusage=tte21,
							   s=df.to_html(index=False),
							   sam=lo.to_html(index=False),
							   tale=lolz.to_html(index=False),
							   
							   x1=x51,y1=y51,
							   bar1=te21 ,bar2=tte2,
							   s1=df1.to_html(index=False),
							   sam1=lo1.to_html(index=False),
							   
							   xx1=AV,xx2=AE,xx3=AD,
							   yy1=BV,yy2=BE,yy3=BD,
							   zz1=CV,zz2=CE,zz3=CD,
							   bb1=the2 ,bb2=ttte2,
							   zone1=yy51,zone2=xx51,
							   sammy=dff.to_html(index=False))

@app.route('/vendormanagement')
def vendormanagement():
		return render_template('vendormanagement.html')

@app.route('/vendormanagementimport',methods=['POST','GET'])
def vendormanagementimport():
		global vendordata
		global vendordataview
		db = pymysql.connect(host='localhost',user='root',password='',db='inventory_management',charset='utf8mb4',cursorclass=pymysql.cursors.DictCursor)
		vendordata = pd.read_sql("SELECT * from vendor_management", con=db)
		db.close()
		vendordata['POdate']=pd.to_datetime(vendordata['POdate'])
		vendordata['POdate_year']=vendordata['POdate'].dt.year
		vendordataview=vendordata.head(50)
		return render_template('vendormanagementview.html',vendordataview=vendordataview.to_html(index=False))

@app.route('/vendormanagementview',methods=['POST','GET'])
def vendormanagementview():
		return render_template('vendormanagementview.html',vendordataview=vendordataview.to_html(index=False))

@app.route('/vndrmngmnt1',methods=['POST','GET'])
def vndrmngmnt1():
		VENDORID=sorted(vendordata['Vendorid'].unique())
		if request.method=='POST':
			vendorin=request.form['name1']
			def Vendor(VendorId):
				datasetcomb34=vendordata[['Vendorid','Vendor_name','Vendor_address','Vendormin_order']][vendordata['Vendorid']== VendorId]
				return datasetcomb34.iloc[0,:]
			snglvw=Vendor(vendorin)
			singleview=pd.DataFrame(snglvw).T
			return render_template('vendormanagement1.html',say=1,vendorin=vendorin,VENDORID=VENDORID,singleview=singleview.to_html(index=False))
		return render_template('vendormanagement1.html',VENDORID=VENDORID)

@app.route('/vndrmngmnt2',methods=['POST','GET'])
def vndrmngmnt2():
		pouyear=sorted(vendordata['POdate_year'].unique())
		if request.method == 'POST':
			SelectedYear = int(request.form['name1'])
			SelectedTop = int(request.form['name2'])
			def top10vendorspend(year,top_value):
				x=[]
				y=[]
				gg1=vendordata[(vendordata['POdate_year']==year)].groupby(['POdate_year','Vendorid'])['PO_Value'].sum()
				x=gg1.nlargest(top_value).index.get_level_values(1)
				y=gg1.nlargest(top_value).values
				df=pd.DataFrame({'VendorID':x,'Total':y})
				return df
			vndrvspnd=top10vendorspend(SelectedYear,SelectedTop)
			def top10vendoravgspend(top):
				gg3=vendordata.groupby(['POdate_year','Vendorid'])['PO_Value'].mean()
				xxx=gg3.nlargest(top).index.get_level_values(1)
				yyy=round(gg3.nlargest(top),2).values
				df=pd.DataFrame({'VendorID':xxx,'Mean':yyy})
				return df
			vndrvavgspnd=top10vendoravgspend(SelectedTop)
			return render_template('vendormanagement2.html',say=1,SelectedYear=SelectedYear,pouyear=pouyear,vndrval=vndrvspnd.values,vndrvavg=vndrvavgspnd.values)
		return render_template('vendormanagement2.html',pouyear=pouyear)

@app.route('/vndrmngmnt3',methods=['POST','GET'])
def vndrmngmnt3():
		pouyear=sorted(vendordata['POdate_year'].unique())
		if request.method == 'POST':
			SelectedYear = int(request.form['name1'])
			SelectedTop = int(request.form['name2'])
			def top10POvendorvalue(year,top_value):
				x=[]
				y=[]
				gg1=vendordata[(vendordata['POdate_year']==year)].groupby(['POdate_year','Vendorid'])['Inventoryreplenished'].sum()
				x=gg1.nlargest(top_value).index.get_level_values(1)
				y=gg1.nlargest(top_value).values
				df=pd.DataFrame({'VendorId':x,'Total':y})
				return df
			vndrval=top10POvendorvalue(SelectedYear,SelectedTop)
			def top10POvendoravg(top):
				gg3=vendordata.groupby(['POdate_year','Vendorid'])['Inventoryreplenished'].mean()
				xxx=gg3.nlargest(top).index.get_level_values(1)
				yyy=round(gg3.nlargest(top),2).values
				df=pd.DataFrame({'VendorID':xxx,'Mean':yyy})
				return df
			vndrvavg=top10POvendoravg(SelectedTop)
			return render_template('vendormanagement3.html',say=1,SelectedYear=SelectedYear,pouyear=pouyear,vndrval=vndrval.values,vndrvavg=vndrvavg.values)
		return render_template('vendormanagement3.html',pouyear=pouyear)

@app.route('/vndrmngmnt4',methods=['POST','GET'])
def vndrmngmnt4():
		pouyear=sorted(vendordata['POdate_year'].unique())
		if request.method == 'POST':
			SelectedYear = int(request.form['name1'])
			SelectedTop = int(request.form['name2'])
			def top10vendorPOcnt(year,top):
				x=[]
				y=[]
				gg1=vendordata[(vendordata['POdate_year']==year)].groupby(['POdate_year','Vendorid'])['POdate_year'].count()
				x=gg1.nlargest(top).index.get_level_values(1)
				y=gg1.nlargest(top).values
				df=pd.DataFrame({'MatID':x,'Total_count':y})
				return df
			vndrvavgpoacnt=top10vendorPOcnt(SelectedYear,SelectedTop)
			def top10vendorPOavg(top):
				g=vendordata.groupby('Vendorid')['POdate_year'].size()
				xx=g.nlargest(top).index.get_level_values(0)
				yy=g.nlargest(top).values
				dfexp7=pd.DataFrame({'VendorID':xx,'Average_count':yy})
				return dfexp7
			vndrvavgpoavg=top10vendorPOavg(SelectedTop)
			return render_template('vendormanagement4.html',say=1,SelectedYear=SelectedYear,pouyear=pouyear,vndrval=vndrvavgpoacnt.values,vndrvavg=vndrvavgpoavg.values)
		return render_template('vendormanagement4.html',pouyear=pouyear)

@app.route('/vendorperformanceanalysis')
def vendorperformanceanalysis():
		return render_template('vendorperformanceanalysis.html',say=0)

@app.route('/vendorperformanceanalysisdata',methods=['POST','GET'])
def vendorperformanceanalysisdata():
		if request.method=='POST':
			global wdata
			global wtdata
			file1 = request.files['file1'].read()
			file2 = request.files['file2'].read()
			if len(file1)==0 or len(file2)==0:
				return render_template('vendorperformanceanalysis.html',say=0,warning='Data Invalid')
			data1=pd.read_csv(io.StringIO(file1.decode('utf-8')))
			wdata=pd.DataFrame(data1)
			data2=pd.read_csv(io.StringIO(file2.decode('utf-8')))
			wtdata=pd.DataFrame(data2)
			return render_template('vendorperformanceanalysis.html',say=1,data1=data1.to_html(index=False),data2=data2.to_html(index=False))

@app.route('/vendorperformanceanalys',methods=['POST','GET'])
def vendorperformanceanalys():
		wt=[]
		for ds in wtdata['Weight']:
			wt.append(round((float(ds)),2))
		treatment=[]
		for ds in wtdata['Positive Attribute']:
			if ds=='Yes':
				treatment.append('+')
			else:
				treatment.append('-')
		def normalize(df,alpha,treatment):
			y=df.iloc[:,1:len(list(df))]
			for i, j in zip(list(y),treatment):
				if j== '-':
					y[i]=y[i].min()/y[i]
				elif j== '+':
					y[i]=y[i]/y[i].max()
			for i, t in zip(list(y),wt):
				y[i]=y[i]*t
			df['Score'] = y.sum(axis=1)
			df=df.sort_values('Score', ascending=False)
			df['Rank']=df['Score'].rank(ascending=False)
			df['Rank']=df['Rank'].astype(int)
			return df[['Rank','Vendor']]
		dff=normalize(wdata,wt,treatment)
		return render_template('vendorperformanceanalysisview.html',say=1,data=dff.to_html(index=False))

@app.route('/purchaseorderallocation')
def purchaseorderallocation():
		return render_template('purchaseorderallocation.html')

@app.route('/purchaseorderallocationimport',methods=['POST','GET'])
def purchaseorderallocationimport():
		global ddemand1
		global dsupply1
		global maxy1
		global miny1
		global Vcost1
		global Vrisk1
		db = pymysql.connect(host='localhost',user='root',password='',db='inventory_management',charset='utf8mb4',cursorclass=pymysql.cursors.DictCursor)
		ddemand1 = pd.read_sql("SELECT * from opt_demand", con=db)
		dsupply1 = pd.read_sql("SELECT * from opt_supply", con=db)
		maxy1 = pd.read_sql("SELECT * from opt_maxcapacity", con=db)
		miny1 = pd.read_sql("SELECT * from opt_mincapacity", con=db)
		Vcost1 = pd.read_sql("SELECT * from opt_vcost", con=db)
		Vrisk1 = pd.read_sql("SELECT * from opt_vrisk", con=db)
		db.close()
		return render_template('purchaseorderallocationimport.html',ddemand=ddemand1.to_html(index=False),dsupply=dsupply1.to_html(index=False),
		maxy=maxy1.to_html(index=False),miny=miny1.to_html(index=False),Vcost=Vcost1.to_html(index=False),Vrisk=Vrisk1.to_html(index=False))

@app.route('/purchaseorderallocationanalyse',methods=['POST','GET'])
def purchaseorderallocationanalyse():
		ddemand=ddemand1.set_index("Product")
		dsupply=dsupply1.set_index("Vendor")
		maxy=maxy1.set_index("Vendors\Product List")
		miny=miny1.set_index("Vendors\Product List")
		Vcost =Vcost1.set_index("Vendors\Product List")
		Vrisk = Vrisk1.set_index("Vendors\Product List")
		demand=dict(zip(list(ddemand.index),ddemand.iloc[:,0].values))
		supply=dict(zip(list(dsupply.index),dsupply.iloc[:,0].values))
		max1=maxy.to_dict()
		min1=miny.to_dict()
		Vendors=list(dsupply.index)
		Products=list(ddemand.index)

		VcostNorm = Vcost.copy()
		VriskNorm = Vrisk.copy()
		if request.method=='POST':
			CostWeight=float(request.form['CostWeight'])
			RiskWeight=float(request.form['RiskWeight'])
			Total=[]
			for i in list(list(VcostNorm)):
				Tot = VcostNorm[i].sum()
				Total.append(Tot)
			for i, j in zip(list(VcostNorm),Total):
				VcostNorm[i]=VcostNorm[i]/j

			Total=[]
			for i in list(list(VriskNorm)):
				Tot = VriskNorm[i].sum()
				Total.append(Tot)
			for i, j in zip(list(VriskNorm),Total):
				VriskNorm[i]=VriskNorm[i]/j

			risk=VriskNorm.to_dict()
			cost=VcostNorm.to_dict()
			Total_cost=defaultdict(dict)
			Total_Risk=defaultdict(dict)
			Total_Cost=pd.DataFrame(CostWeight*pd.DataFrame(cost))
			Total_Risk=pd.DataFrame(RiskWeight*pd.DataFrame(risk))
			Decision_var=(Total_Cost+Total_Risk).to_dict()

			prob = pulp.LpProblem("Optimization", pulp.LpMinimize)
			routes = [(w,b) for w in Products for b in Vendors]
			x = LpVariable.dicts("route", (Products, Vendors), cat = 'LpInteger')
			prob += lpSum([x[w][b] * Decision_var[w][b] for (w,b) in routes]),"Objective function"

			for w in Products:
				prob += lpSum([x[w][b] for b in Vendors]) == demand[w]

			for b in Vendors:
				prob += lpSum([x[w][b] for w in Products]) <= supply[b]

			for w in Products:
				for b in Vendors:
					prob += x[w][b] <= max1[w][b]

			for w in Products:
				for b in Vendors:
					prob += x[w][b] >= min1[w][b]
			prob.writeLP("SO.lp")
			prob.solve()
			opt_status=pulp.LpStatus[prob.status]
			if opt_status=='Optimal':
			#print (pulp.value(prob.objective))
				re=[]
				res=[]
				ress=[]
				i=0
				for variable in prob.variables():
					re.append(variable.varValue)
					res.append(variable.varValue)
					i=i+1
					if (i==len(Total_Cost)):
						i=0
						ress.append(re)
						re=[]
				Optimal_quantity1=pd.DataFrame(ress,columns=Vendors,index=Products).astype(int)
				opq13=[]
				for column in Optimal_quantity1.columns:
					opq11=[]
					opq12=[]
					opq11.append(column)
					for val in Optimal_quantity1[column]:
						opq12.append(val)
					opq11.append(opq12)
					opq13.append(opq11)
				Optimal_quantity2=Optimal_quantity1.T
				opq23=[]
				for column in Optimal_quantity2.columns:
					opq21=[]
					opq22=[]
					opq21.append(column)
					for val in Optimal_quantity2[column]:
						opq22.append(val)
					opq21.append(opq22)
					opq23.append(opq21)
				VCran=[]
				for column in Vcost.columns:
					for val in Vcost[column].values:
						VCran.append(val)
				VRran=[]
				for column in Vrisk.columns:
					for val in Vrisk[column].values:
						VRran.append(val)
				Costproduct=[i*j for (i,j) in zip(res,VCran)]
				sumCostproduct=sum(Costproduct)
				Riskproduct=[i*j for (i,j) in zip(res,VRran)]
				optrisk=sum(Riskproduct)/sum(res)
				return render_template('purchaseorderallocationoutput.html',username=username,say=1,optrisk=optrisk,sumCostproduct=sumCostproduct,Optimal_quantity1=opq13,
				Optimal_quantity2=opq23,grpi1=Optimal_quantity1.index,grpi2=Optimal_quantity2.index,warning2="The obtained solution was "+opt_status)
			
			return render_template('purchaseorderallocationoutput.html',warning1="The obtained solution was "+opt_status)
		return render_template('purchaseorderallocationoutput.html')

@app.route('/purchaseordermanagement')
def purchaseordermanagement():
		return render_template('purchaseordermanagement.html')

@app.route('/poimport',methods=['POST','GET'])
def poimport():
		global podata
		global podatahead
		db = pymysql.connect(host='localhost',user='root',password='',db='inventory_management',charset='utf8mb4',cursorclass=pymysql.cursors.DictCursor)
		podata = pd.read_sql("SELECT * from po_management", con=db)
		db.close()
		podata['POdate']=pd.to_datetime(podata['POdate'])
		podata['PO_year']=podata['POdate'].dt.year
		podata['Orderreceiveddate']=pd.to_datetime(podata['Orderreceiveddate'])
		podata['Orderreceivedyear']=podata['Orderreceiveddate'].dt.year
		podatahead=podata.head(50)
		return render_template('purchaseordermanagementview.html',podatahead=podatahead.to_html(index=False))

@app.route('/purchaseordermanagementview')
def purchaseordermanagementview():
		return render_template('purchaseordermanagementview.html',podatahead=podatahead.to_html(index=False))

@app.route('/pomtype1',methods=['POST','GET'])
def pomtype1():
		PONO=sorted(podata['POno'].unique())
		if request.method=='POST':
			SelectedPOno=int(request.form['name1'])
			def POSingle(POno):
				podat=podata[['POno','POammendmentdate','POdate','POverificationdate','PO_Value']][podata['POno']== POno]
				return podat.iloc[0,:]
			snglvw=POSingle(SelectedPOno)
			svpodata=pd.DataFrame(snglvw).T
    
			return render_template('purchaseordermanagement1.html',say=1,sayy=1,PONO=PONO,svpodata=svpodata.to_html(index=False),SelectedPOno=SelectedPOno)
		return render_template('purchaseordermanagement1.html',say=1,PONO=PONO)

@app.route('/pomtype2',methods=['POST','GET'])
def pomtype2():
		uyear=sorted(podata['PO_year'].unique())
		if request.method=='POST':
			SelectedYear=int(request.form['name1'])
			podata.loc[(podata.PO_Value >= 0) & (podata.PO_Value < 10000), 'PO_Group'] = '0-10K'
			podata.loc[(podata.PO_Value >= 10000) & (podata.PO_Value < 50000), 'PO_Group'] = '10K-50K'
			podata.loc[(podata.PO_Value >= 50000) & (podata.PO_Value < 100000), 'PO_Group'] = '50K-100K'
			podata.loc[(podata.PO_Value >= 100000) & (podata.PO_Value < 500000), 'PO_Group'] = '100K-500K'
			podata.loc[(podata.PO_Value >= 500000) & (podata.PO_Value < 1000000), 'PO_Group'] = '500K-1M'
			podata.loc[podata.PO_Value >= 1000000, 'PO_Group'] = '>1M'
			podata.loc[podata.PO_Group == '0-10K', 'PO_GroupNo'] = 1
			podata.loc[podata.PO_Group == '10K-50K', 'PO_GroupNo'] = 2
			podata.loc[podata.PO_Group == '50K-100K', 'PO_GroupNo'] = 3
			podata.loc[podata.PO_Group == '100K-500K', 'PO_GroupNo'] = 4
			podata.loc[podata.PO_Group == '500K-1M', 'PO_GroupNo'] = 5
			podata.loc[podata.PO_Group == '>1M', 'PO_GroupNo'] = 6
			def top10POyrcount(year):
				x=[]
				y=[]
				gg1=podata[(podata['PO_year']==year)].groupby(['PO_year','PO_GroupNo','PO_Group'])['PO_year'].size()
				x=gg1.index.get_level_values(2)
				z=gg1.index.get_level_values(1)
				y=gg1.values
				df=pd.DataFrame({'z':z, 'PO Value':x,'Total Count':y})
				df=df.sort_values('z')
				df=df.drop('z',axis=1)
				return df
			df=top10POyrcount(SelectedYear)
			return render_template('purchaseordermanagement2.html',say=1,sayy=1,uyear=uyear,data=df.values,SelectedYear=SelectedYear)
		return render_template('purchaseordermanagement2.html',say=1,uyear=uyear)

@app.route('/pomtype3',methods=['POST','GET'])
def pomtype3():
		uyear=sorted(podata['PO_year'].unique())
		if request.method=='POST':
			SelectedYear=int(request.form['name1'])
			podata.loc[(podata.Inventoryreplenished >= 0) & (podata.Inventoryreplenished < 100), 'Inventory_Group'] = '0-100'
			podata.loc[(podata.Inventoryreplenished >= 100) & (podata.Inventoryreplenished < 200), 'Inventory_Group'] = '100-200'
			podata.loc[(podata.Inventoryreplenished >= 200) & (podata.Inventoryreplenished < 300), 'Inventory_Group'] = '200-300'
			podata.loc[(podata.Inventoryreplenished >= 300) & (podata.Inventoryreplenished < 400), 'Inventory_Group'] = '300-400'
			podata.loc[(podata.Inventoryreplenished >= 400) & (podata.Inventoryreplenished < 500), 'Inventory_Group'] = '400-500'
			podata.loc[podata.Inventoryreplenished >= 500,'Inventory_Group'] = '>500'
			def top10poinvyrcount(year):
				x=[]
				y=[]
				gg1=podata[(podata['PO_year']==year)].groupby(['PO_year','Inventory_Group'])['Inventory_Group'].size()
				x=gg1.index.get_level_values(1)
				y=gg1.values
				df=pd.DataFrame({'Inventory Value':x,'Total Count':y})
				df=df.sort_values('Inventory Value')
				return df
			df=top10poinvyrcount(SelectedYear)
			return render_template('purchaseordermanagement3.html',say=1,sayy=1,uyear=uyear,data=df.values,SelectedYear=SelectedYear)
		return render_template('purchaseordermanagement3.html',say=1,uyear=uyear)
@app.route('/pomtype5',methods=['POST','GET'])
def pomtype5():
		uyear=sorted(podata['PO_year'].unique())
		if request.method=='POST':
			SelectedYear=int(request.form['name1'])
			podata['date_diff']=podata['Orderreceiveddate']-podata['POdate']
			podata.loc[(podata.date_diff >= '15 days') & (podata.date_diff < '18 days'), 'date_diff_Group'] = '15-18'
			podata.loc[(podata.date_diff >= '18 days') & (podata.date_diff < '21 days'), 'date_diff_Group'] = '18-20'
			podata.loc[(podata.date_diff >= '21 days') & (podata.date_diff <= '23 days'), 'date_diff_Group'] = '20-23'
			def topleadyear(year):
				x=[]
				y=[]
				gg1=podata[(podata['PO_year']==year)].groupby(['PO_year','date_diff_Group'])['date_diff_Group'].size()
				x=gg1.index.get_level_values(1)
				y=gg1.values
				df=pd.DataFrame({'Lead_Time':x,'Total Count':y})
				return df
			df=topleadyear(SelectedYear)
			return render_template('purchaseordermanagement5.html',say=1,sayy=1,uyear=uyear,data=df.values,SelectedYear=SelectedYear)
		return render_template('purchaseordermanagement5.html',say=1,uyear=uyear)

@app.route('/pomtype4',methods=['POST','GET'])
def pomtype4():

		pocdata=podata.groupby('PO_year')['PO_year'].size()
		year=pocdata.index.get_level_values(0)
		count=pocdata.values.astype(int)
		df=pd.DataFrame({'Year':year,'PO_Count':count})
		return render_template('purchaseordermanagement4.html',data=df.values)
#Aggregate Planning
@app.route("/aggregate",methods = ['GET','POST'])
def aggregate():
    if request.method== 'POST':
        from_date=request.form['from']
        to_date=request.form['to']
        factory=request.form['typedf']
        connection = pymysql.connect(host='localhost',
             user='user',
             password='',
             db='test',
             charset='utf8mb4',
             cursorclass=pymysql.cursors.DictCursor)

        x=connection.cursor()
        x.execute("select * from `agggendata`")
        connection.commit()
        data=pd.DataFrame(x.fetchall())
        
        fromdifftodata= data[(data['Month'] > from_date) & (data['Month'] < to_date )]


        datas=fromdifftodata[fromdifftodata['Factory']==factory]
        global forecastedplaniingdata
        forecastedplaniingdata=pd.concat([datas['Month'],datas['Demand_Forecast']],axis=1)
        dataforecast=pd.concat([datas['Month'],datas['Factory'],datas['Demand_Forecast']],axis=1)

        return render_template('aggregatedataview.html',datafile=dataforecast.to_html(index=False),graphdata=datas.values)
    return render_template('aggregate.html')

@app.route('/optimize',methods=["GET","POST"])
def optimize():
    if request.method=="POST":
        formDate_val=request.form['formDate']
        ToDate_val=request.form['ToDate']
        InitialWorkforce_val =request.form['InitialWorkforce']
        InitialInventory_val=request.form['InitialInventory']
        InitialStockouts_val=request.form['InitialStockouts']
        LaborHours_val=request.form['LaborHours']
        MaterialCost_val=request.form['MaterialCost']
        InventoryHoldingCost_val=request.form['InventoryHoldingCost'] 
        MarginalCostStockOut_val=request.form['MarginalCostStockOut']
        HTCost_val=request.form['HTCost']
        LayoffCost_val=request.form['LayoffCost']
        RegularTimeCost_val=request.form['RegularTimeCost']
        OverTimeCost_val=request.form['OverTimeCost']
        CostSubcontracting_val=request.form['CostSubcontracting']
        # =============================================================================
        # #Wr = workforce size for Month t, t = 1, ... , 6
        # #Rt = number of employees hired at the beginning of Month t, t = 1, ... , 6
        # #Lr =number of employees laid off at the beginning of Month t, t = 1, ... , 6
        # #Pt = number of units produced in Month t, t = 1, ... , 6
        # #It = inventory at the end of Month t, t = 1, ... , 6
        # #St = number of units stocked out/backlogged at the end of Month t, t = 1, ... , 6
        # #Ct = number of units subcontracted for Month t, t = 1, ... , 6
        # #Ot =number of overtime hours worked in Month t, t = 1, ... , 6 
        # =============================================================================
        # Assign spreadsheet filename to `file`
        forcast = forecastedplaniingdata[(forecastedplaniingdata['Month']>formDate_val) & (forecastedplaniingdata['Month']<ToDate_val )]
        datas=pd.concat([forcast['Month'],forcast['Demand_Forecast']],axis=1).reset_index(drop=True)
        dat=datas['Month'].astype(str)
        dta=pd.concat([dat,datas['Demand_Forecast']],axis=1)
            

        # Print the sheet names
        Dem_forecast=dta
        period = []
        for x in range(len(dta)): 
            period.append(x)
        Ini_Workforce=int(InitialWorkforce_val)
        Ini_Inventory=int(InitialInventory_val)
        Ini_Stock_Out=int(InitialStockouts_val)
        #Regular-time labor cost
#        RC=Parameters['Cost'][5]
        RC=int(RegularTimeCost_val)
        
        #Overtime labor cost

        OC=int(OverTimeCost_val)
        
        #Cost of hiring and layoffs
#        HR=Parameters['Cost'][3]
        HR=int(HTCost_val)
        
#        LC=Parameters['Cost'][4]
        LC=int(LayoffCost_val)
        #Cost of holding inventory
        
#        HC=Parameters['Cost'][1]
        HC=int(InventoryHoldingCost_val)
        #Cost of stocking out
#        SC=Parameters['Cost'][2]
        SC=int(MarginalCostStockOut_val)
        #Cost of subcontracting
#        SCC=Parameters['Cost'][7]
        SCC=int(CostSubcontracting_val)
        #Material cost 
#        MC=Parameters['Cost'][0]
        MC=int(MaterialCost_val)
        #Production Rate
        kk=int(LaborHours_val)
        PR=(1/kk)
        # Create the 'prob' variable to contain the problem data
        model = LpProblem("Min Cost Aggregate Planning problem",LpMinimize)
        Workforce= pulp.LpVariable.dict("Workforce",(time for time in period),lowBound=0,cat='Integer')   
        Hired = pulp.LpVariable.dict("Hired",(time for time in period),lowBound=0,cat='Integer')       
        Laid_off = pulp.LpVariable.dict("Laid_off",(time for time in period),lowBound=0,cat='Integer')        
        Production = pulp.LpVariable.dict("Production",(time for time in period),lowBound=0,cat='Integer')
        Inventory = pulp.LpVariable.dict("Inventory",(time for time in period),lowBound=0,cat='Integer')
        Stock_Out = pulp.LpVariable.dict("Stock_Out",(time for time in period),lowBound=0,cat='Integer')
        Subcontract = pulp.LpVariable.dict("Subcontract",(time for time in period),lowBound=0,cat='Integer')
        Overtime_Hrs = pulp.LpVariable.dict("Overtime_Hrs",(time for time in period),lowBound=0,cat='Integer')
        model += pulp.lpSum(
            [RC * Workforce[time] for time in period]
            + [HR * Hired[time] for time in period]
            + [LC * Laid_off[time] for time in period]
            + [MC * Production[time] for time in period]
            + [HC * Inventory[time] for time in period]
            + [SC * Stock_Out[time] for time in period]
            + [SCC * Subcontract[time] for time in period]
            + [OC * Overtime_Hrs[time] for time in period]
            )        
        for time in period:
            if(time==0):
                model += pulp.lpSum(Workforce[time]-Ini_Workforce-Hired[time]+Laid_off[time])==0
                model += pulp.lpSum(Ini_Inventory+Production[time]+Subcontract[time]\
                 -Dem_forecast['Demand_Forecast'][time]-Ini_Stock_Out-Inventory[time]+Stock_Out[time])==0
            else:
                model += pulp.lpSum(Workforce[time]-Workforce[time-1]-Hired[time]+Laid_off[time])==0
                model += pulp.lpSum(Inventory[time-1]+Production[time]+Subcontract[time]\
                 -Dem_forecast['Demand_Forecast'][time]-Stock_Out[time-1]-Inventory[time]+Stock_Out[time])==0
                
            model += pulp.lpSum(Production[time]-40*Workforce[time]+(Overtime_Hrs[time]*PR))<=0
            model += pulp.lpSum(Overtime_Hrs[time]-10*Workforce[time])<=0
        model.solve()
        print("Status:", LpStatus[model.status])
        for v in model.variables():
            print(v.name, "=", v.varValue)
        print("Total Cost of Ingredients per can = ", value(model.objective))
        #Storing Name and Values
        
        Name=[]
        values=[]
        for v in model.variables():
            Name.append(v.name)
            values.append(v.varValue)
        #counting no of hired   
        count=0    
        for k in range(0,len(Name)):
            val=Name[k]
            if val[0:5]=='Hired':
                count=count+1
        
        Name_df=pd.DataFrame(Name)
        valdf=pd.DataFrame(values)
        
        Namearray=pd.DataFrame(Name_df.values.reshape(count, int(len(Name)/count), order='F'))
        
        Valuesarray=pd.DataFrame(valdf.values.reshape(count, int(len(Name)/count), order='F'))
        
        kk=pd.DataFrame(Namearray.iloc[0])
        kk.columns=['val']
        Namesofcol = kk['val'].map(lambda x: x.lstrip('+-').rstrip('_0'))
        
        Valuesarray.columns = [Namesofcol]
        
        opt = pd.DataFrame(Valuesarray)
        
        datasor = pd.concat([opt['Inventory'],opt['Stock_Out'],opt['Subcontract'],opt['Production'],opt['Hired'],opt['Laid_off'],opt['Workforce'],opt['Overtime_Hrs']],axis=1)  
        dd = pd.DataFrame(Dem_forecast)
        
        dfss = pd.concat([dd,datasor],axis=1)
        
        inventoryhold = opt['Inventory'].sum()
        
        overtime = opt['Overtime_Hrs'].sum()
        
        subcontract = opt['Subcontract'].sum()
        
        Hired = opt['Hired'].sum()
        
        layoff = opt['Laid_off'].sum()
        
        invent = opt['Inventory'].iloc[-1]
        
        stockoutval=opt['Stock_Out'].sum()
        
        con = pymysql.connect(host='localhost',user='root',password='',db='test',charset='utf8mb4')
        
        engine = create_engine("mysql+pymysql://{user}:{pw}@localhost/{db}".format(user="root",pw="",db="test"))
        dfss.to_sql(con=engine, name='optimizedallocations', if_exists='replace')
        con.close()
        
        cost_total=value(model.objective)  
       
        piedata=dd.drop(dd.index[0])
        
        tableofcost=[cost_total,(HR*Hired),(subcontract*SCC),(overtime*OC),(inventoryhold*HC),(stockoutval*SC)]
        tableofname=['Total Cost','Hiring Cost','Subcontract Cost','Overtime Cost','Inventory Holding Cost','Stockout Cost']
        dataoftable=pd.concat([pd.DataFrame(tableofname),pd.DataFrame(tableofcost)],axis=1)
        dataoftable.columns=['Cost_Component','Value']
        piedata=dataoftable.drop(dataoftable.index[0])
        
        
        return render_template("Optimizer-dataview.html",stockoutval=stockoutval,cost_total=cost_total,piedata=piedata.values,fraju=dataoftable.to_html(index=False),invent=invent,layoff=layoff,Hired=Hired,dfile=dfss.values,dfss=dfss.to_html(index=False),formDate_val=formDate_val,ToDate_val=ToDate_val,InitialWorkforce_val=InitialWorkforce_val,InitialInventory_val=InitialInventory_val,InitialStockouts_val=InitialStockouts_val,
            LaborHours_val=LaborHours_val,MaterialCost_val=MaterialCost_val,InventoryHoldingCost_val=InventoryHoldingCost_val,MarginalCostStockOut_val=MarginalCostStockOut_val,HTCost_val=HTCost_val, 
            LayoffCost_val= LayoffCost_val,RegularTimeCost_val=RegularTimeCost_val,OverTimeCost_val=OverTimeCost_val,CostSubcontracting_val=CostSubcontracting_val)

