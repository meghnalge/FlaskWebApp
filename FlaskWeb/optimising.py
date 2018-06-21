import pymysql
import os
import numpy as np 
import pandas as pd 
from pandas.api.types import is_string_dtype 
from pulp import * 
import math 
import time 
import warnings 
#import cplex

localaddress="D:\\home\\site\\wwwroot\\FlaskWeb"

def grpbatchInitialmap(grpname, batchInitchar):
    global dctGrpBatch
    grp = dctGrpBatch[grpname]
    for a in grp:
        if batchInitchar in a:
            return a[0]

def createRuleGrpsdct(rulestr):
    a2 = rulestr.split(';')
    Slocnameslist = []
    dctinitialofbatch = {}
    listoflist = []
    for a in a2:
        Slocnames = a.split('-', 1)[0]
        batchinitialsgrps = a.split('-', 1)[1].split(',')
        for b in batchinitialsgrps:
            temp = list(b)
            listoflist.append(temp)
        dctinitialofbatch[Slocnames] = listoflist
        listoflist = []
        Slocnameslist.append(Slocnames)
    return dctinitialofbatch, Slocnameslist

def scenarioReader(scenariodf, scenario_num):
    global MET_HELD
    global Test_Cut
    global customer_proir_flag
    global SW_flag
    global prod_dt
    global cm01_cons
    global max_wagon_wt
    global min_wagon_wt
    global max_width
    global dctGrpBatch
    global Slocnameslist
#    if (isDefaultScenario == 0):
#        MET_HELD = 0
#        Test_Cut = 0
#        customer_proir_flag = 0
#        SW_flag = 0
#        prod_dt = 0
#        cm01_cons = 0
#        max_wagon_wt = 205000
#        min_wagon_wt = 175000
#        max_width = 370

    if (scenariodf['customer_priority'].iloc[scenario_num] == 0):
        customer_proir_flag = 0
    else:
        customer_proir_flag = 1

    if (scenariodf['oldest_sw'].iloc[scenario_num] == 0):
        SW_flag = 0
    else:
        SW_flag = 1

    if (scenariodf['production_date'].iloc[scenario_num] == 0):
        prod_dt = 0
    else:
        prod_dt = 1

    if (pd.notnull(scenariodf['load_lower_bounds'].iloc[scenario_num])):
        min_wagon_wt = scenariodf['load_lower_bounds'].iloc[scenario_num]
    else:
        min_wagon_wt = 175000

    if (pd.notnull(scenariodf['load_upper_bounds'].iloc[scenario_num])):
        max_wagon_wt = scenariodf['load_upper_bounds'].iloc[scenario_num]
    else:
        max_wagon_wt = 205000

    if (pd.notnull(scenariodf['width_bounds'].iloc[scenario_num])):
        max_width = scenariodf['width_bounds'].iloc[scenario_num]
    else:
        max_width = 370

    if (scenariodf['met_held_group'].iloc[scenario_num] == 0):
        MET_HELD = 0
    else:
        MET_HELD = 1

    if (scenariodf['test_cut_group'].iloc[scenario_num] == 0):
        Test_Cut = 0
    else:
        Test_Cut = 1

    if (scenariodf['Sub-grouping rules'].iloc[scenario_num] == 1):
        cm01_cons = 1

        if (pd.notnull(scenariodf['Rule'].iloc[scenario_num])):
            dctGrpBatch, Slocnameslist = createRuleGrpsdct(scenariodf['Rule'].iloc[scenario_num])
        else:
            print("Rule not given")
    else:
        cm01_cons = 0

    print("config is- customer_proir_flag=", customer_proir_flag, " SW_flag=", SW_flag, " prod_dt=", prod_dt)


def optPulpCaller(df, dictWidth, dictLoad, numRailGuess, GrpKey, Add_HeatNo_Cons, listRail, listCoil, absRails, fracGap, maxSecs, grpnum, cbc_flag):
    global pass2runs
    num_rail = len(listRail)
    probName = "Grp_" + ''.join(GrpKey)
    prob = LpProblem(probName, LpMinimize)
    x_vars = LpVariable.dicts("x_", (listCoil, listRail), 0, 1, LpInteger)
    df_index_list = df.index.tolist()
    rail_vars = LpVariable.dicts("rail_var_", (listRail), 0, 1, LpInteger)

    obj_part_a = LpAffineExpression()
    obj_part_a = sum(
        [-(maincoilwt + (math.ceil(float(dictLoad[i]) / load_scale_factor))) * x_vars[i][j] for i in listCoil for j in
         listRail] + [(obj_wt_wagon + enu) * rail_vars[k] for enu, k in enumerate(listRail)])
    obj_part_proddate = LpAffineExpression()
    obj_part_sw = LpAffineExpression()
    obj_part_sameHeatRail = LpAffineExpression()
    obj_part_sameHeatRailSlack = LpAffineExpression()
    obj_part_nonmetBoost = LpAffineExpression()
    obj_part_nontcBoost = LpAffineExpression()
    obj_part_TestCut = LpAffineExpression()
    obj_part_TestCutSlack = LpAffineExpression()
    obj_part_cm01Rail = LpAffineExpression()
    obj_part_cm01RailSlack = LpAffineExpression()
    obj_part_nonmet = LpAffineExpression()
    obj_part_nonmetSlack = LpAffineExpression()
    if (df['SLoc'].iloc[0] in Slocnameslist and cm01_cons == 1):
        df['BatchStart'] = df['Batch'].str[:1]
        df['cmgrp'] = df.apply(lambda x: grpbatchInitialmap(x['SLoc'], x['BatchStart']), axis=1)
        cmgrpd = df.groupby('cmgrp')
        maxcoilspresent = len(listCoil)
        cmGrpslackVar = LpVariable.dicts('cmGrpslackVar_', (range(0, 2), listRail), 0, maxcoilspresent, LpInteger)
        cmGrpIndVar = LpVariable.dicts('cmGrpIndVar_', (range(0, 2), listRail), 0, 1, LpInteger)
        slack_cmGrpIndVar = LpVariable.dicts('slack_cmGrpIndVar_', range(0, 2), 0, num_rail, LpInteger)
        i = 0
        for key, grp in cmgrpd:
            if (key == ''):
                continue
            else:
                index_list = grp.index.tolist()
                rel_req1 = int(math.ceil((float(grp['Delivery Qty'].sum()) / min_wagon_wt)))
                tot_coils1 = len(grp)
                prob += sum(
                    [cmGrpIndVar[i][j] for j in listRail] + [slack_cmGrpIndVar[i]]) == rel_req1, "IndSlackcmgrp_" + str(
                    key)
                obj_part_cm01RailSlack += sum([cm_wt1 * slack_cmGrpIndVar[i]])
                for j in listRail:
                    prob += sum(
                        [x_vars[df.index.get_loc(k)][j] for k in index_list] + [cmGrpslackVar[i][j]]) == tot_coils1 * \
                            cmGrpIndVar[i][j], 'cmGrp_' + ''.join(key) + '_RAil_' + str(j)
                    obj_part_cm01Rail += sum([cm_wt2 * cmGrpslackVar[i][j]])
                i = i + 1
    df['Prod DtRank'] = df['Prod Dt'].rank(ascending=1, method='dense').astype(int)
    if (prod_dt == 1 and df['Prod DtRank'].max() > 1):
        for j in listRail:
            obj_part_proddate += sum([prod_wt * x_vars[i][j] * df['Prod DtRank'].iloc[i] for i in listCoil])
    if (SW_flag == 1):
        print("++++HERE+++++")
        sw_grp = df.groupby(['SW'])  # got groups
        max_week = df['SW'].max()
        for key, grp in sw_grp:
            if (key == max_week):
                weekdiff = 1
            else:
                weekdiff = (max_week - key) + 1
            if (grpnum == 7):
                print("key=", key, " weekdiff=", weekdiff, " swwt=", sw_wt * weekdiff)
            index_list = grp.index.tolist()
            for i in listRail:
                obj_part_sw += sum([-sw_wt * weekdiff * x_vars[df.index.get_loc(j)][i] for j in index_list])
    if (flag_boostmetclr == 1):
        non_metindex = df[df['Met Held'] != 'Y'].index.values.tolist()
        for i in listRail:
            obj_part_nonmetBoost += sum([-mboost * x_vars[df.index.get_loc(k)][i] for k in non_metindex])
    non_tcindex = df[df['Test Cut'] != 'Y'].index.values.tolist()
    for i in listRail:
        obj_part_nontcBoost += sum([-tboost * x_vars[df.index.get_loc(k)][i] for k in non_tcindex])
    if (MET_HELD == 1):
        if(is_string_dtype(df['Met Held'])!=True):
            df['Met Held']=df['Met Held'].astype(str)
        temp_grp = df[df['Met Held'] == 'Y'].groupby('Heat No').filter(lambda x: len(x) > 1)
        same_heat_grp = temp_grp.groupby('Heat No')
        metindx = df[df['Met Held'] == 'Y'].index.values.tolist()
        non_metindex = df[df['Met Held'] != 'Y'].index.values.tolist()
        num_of_same_heat_grp = len(same_heat_grp)
        SameHeatRailVar = LpVariable.dicts('SameHeatRail_', (range(len(same_heat_grp)), listRail), 0, 10, LpInteger)
        sameHeatIndVar = LpVariable.dicts('sameHeatInd_', (range(len(same_heat_grp)), listRail), 0, 1, LpInteger)
        slack_sameHeatIndVar = LpVariable.dicts('SlacksameHeatInd_', range(len(same_heat_grp)), 0, num_rail, LpInteger)
        i = 0
        for key, grp in same_heat_grp:
            index_list = grp.index.tolist()
            rel_req = int(math.ceil((float(grp['Delivery Qty'].sum()) / min_wagon_wt)))
            tot_coils = len(grp)
            prob += sum([sameHeatIndVar[i][j] for j in listRail] + [
                slack_sameHeatIndVar[i]]) == rel_req, "IndSameHeatConswithSlack_" + str(i)
            obj_part_sameHeatRailSlack += sum([(met_wt1) * slack_sameHeatIndVar[i]])
            for j in listRail:
                prob += sum(
                    [x_vars[df.index.get_loc(k)][j] for k in index_list] + [SameHeatRailVar[i][j]]) == tot_coils * \
                        sameHeatIndVar[i][j], 'SameHeatCons' + ''.join(key) + 'RAil_' + str(j)
                obj_part_sameHeatRail += sum([(met_wt2) * SameHeatRailVar[i][j]])
            i = i + 1
    if (Test_Cut == 1 and df[df['Test Cut'] == 'Y'].shape[0] > 1 and df[df['Met Held'] == 'Y'].shape[0] > 1):
        test_cut_grp = df[df['Test Cut'] == 'Y']
        index_list = test_cut_grp.index.tolist()
        tot_coils = test_cut_grp.shape[0]
        slacktestCutRailVar = LpVariable.dicts('slacktestCutRailVar_', (listRail), 0, 10, LpInteger)
        testCutIndVar = LpVariable.dicts('testCutIndVar_', (listRail), 0, 1, LpInteger)
        slacktestCutIndVar = LpVariable.dicts('slacktestCutIndVar_', range(0, 1), 0, num_rail, LpInteger)
        rel_req1 = int(math.ceil(( float(test_cut_grp['Delivery Qty'].sum()) / min_wagon_wt))) + 1
        prob += sum(
            [testCutIndVar[j] for j in listRail] + [slacktestCutIndVar[0]]) == rel_req1, "IndTestCutConswithSlack_"
        obj_part_TestCutSlack += sum([test_wt1 * slacktestCutIndVar[0]])
        for j in listRail:
            prob += sum([x_vars[df.index.get_loc(k)][j] for k in index_list] + [slacktestCutRailVar[j]]) == tot_coils * \
                    testCutIndVar[j], 'TestCutCons' + ' ' + str(j)
            obj_part_TestCut += sum([(test_wt2 + j) * slacktestCutRailVar[j]])
    if (cltmet_testtype == 1 and df[df['Met Held'] == 'Y'].shape[0] > 1 and df[df['Met Held'] != 'Y'].shape[0] > 1):
        non_met_grp = df[df['Met Held'] != 'Y']
        index_list = non_met_grp.index.tolist()
        tot_coils = non_met_grp.shape[0]
        slacknonmetRailVar = LpVariable.dicts('slacknonmetRailVar_', (listRail), 0, 40, LpInteger)
        nonmetIndVar = LpVariable.dicts('nonmetIndVar_', (listRail), 0, 1, LpInteger)
        slacknonmetIndVar = LpVariable.dicts('slacknonmetIndVar_', range(0, 1), 0, num_rail, LpInteger)
        rel_req1 = int(math.ceil(( float(non_met_grp['Delivery Qty'].sum()) / min_wagon_wt)))
        prob += sum([nonmetIndVar[j] for j in listRail] + [slacknonmetIndVar[0]]) == rel_req1, "IndnonmetConswithSlack_"
        obj_part_nonmetSlack += sum([nonmet_wt1 * slacknonmetIndVar[0]])
        for j in listRail:
            prob += sum([x_vars[df.index.get_loc(k)][j] for k in index_list] + [slacknonmetRailVar[j]]) == tot_coils * \
                    nonmetIndVar[j], 'nonmetCons' + ' ' + str(j)
            obj_part_nonmet += sum([(nonmet_wt2 + j * 1) * slacknonmetRailVar[j]])
    prob += obj_part_cm01Rail + obj_part_cm01RailSlack + obj_part_sw + obj_part_proddate + obj_part_a + obj_part_sameHeatRail + obj_part_sameHeatRailSlack + obj_part_TestCut + obj_part_TestCutSlack + obj_part_nonmetBoost + obj_part_nonmet + obj_part_nonmetSlack+obj_part_nontcBoost
    for j in listRail:
        prob += sum([x_vars[i][j] * dictLoad[i] for i in listCoil]) <= max_wagon_wt * rail_vars[
            j], "maxLoadConstraint_" + str(j)
        prob += sum([x_vars[i][j] * dictLoad[i] for i in listCoil]) >= min_wagon_wt * rail_vars[
            j], "minLoadConstraint_" + str(j)
        prob += sum([x_vars[i][j] * dictWidth[i] for i in listCoil]) <= max_width * rail_vars[j], "maxWidthConstraint_" + str(
            j)
        for i in listCoil:
            prob += x_vars[i][j] <= rail_vars[j], "x_true_" + str(i) + "_" + str(j)
    for i in listCoil:
        if (customer_proir_flag == 1 and df['Customer Priority'].iloc[i] == 'Y'):
            prob += sum([x_vars[i][j] for j in listRail]) == 1, "CustPriorityassgntConst_" + str(i)
        else:
            prob += sum([x_vars[i][j] for j in listRail]) <= 1, "assignmentConstraint_" + str(i)
    filename = afilename + str(grpnum) + '_' + add_comment + '_' + currentscenarioname + '.lp'
    filename = filename.replace("/", "")
    filename = filename.replace("*", "")
    if (time_flag == 1):
        start = time.time()
        if (grpnum == 100):
            #a11=prob.solve(pulp.PULP_CBC_CMD(msg=1))
            #a11 = prob.solve(pulp.CPLEX_PY(mip=True, msg=True, epgap=defaultfracGap))
            print("h")
            #a11=prob.solve(pulp.PULP_CBC_CMD(msg=1, fracGap=fracGap,maxSeconds=maxSecs))
            #a11 = prob.solve(pulp.CPLEX_PY(mip=True, msg=True))
            a11=prob.solve(pulp.PULP_CBC_CMD(msg=1, fracGap=fracGap))
        else:
            print("**")
            a11=prob.solve(pulp.PULP_CBC_CMD(msg=1, fracGap=fracGap,maxSeconds=maxSecs))
            #prob.writeLP(filename)
            #a11 = prob.solve(pulp.CPLEX_PY(mip=True, msg=True, epgap=defaultfracGap))
            #a11=prob.solve(pulp.PULP_CBC_CMD(msg=1))
        # a11=prob.solve(pulp.PULP_CBC_CMD(msg=1, fracGap=fracGap,threads=3))
        # a11=prob.solve(pulp.PULP_CBC_CMD(msg=1))
        end = time.time()
        time_required = end - start
        if (time_required >= maxSecs):
            print("stariting Pass 2")
            start = time.time()
            a11 = prob.solve(pulp.PULP_CBC_CMD(msg=1, fracGap=.05, maxSeconds=maxSecs))
            pass2runs = pass2runs + 1
            end = time.time()
            print("Pass 2 ends, Group number is=", grpnum)
            print("pass2runs=", pass2runs)
            if (end - start >= maxSecs):
                print("Going for pass 3")
                all = prob.solve(pulp.PULP_CBC_CMD(msg=1, fracGap=.1, maxSeconds=maxSecs))
                print("pass 3 ends")
    else:
        a11 = prob.solve(pulp.PULP_CBC_CMD(msg=1, fracGap=fracGap))
    ans = []
    rails = []
    df['Wagon-No'] = np.nan
    df['RailCarAllotment'] = np.nan
    df['ProblemStatus'] = np.nan
    df['GrpKey'] = np.nan
    df['Total Coils'] = np.nan
    global solnStatusdf
    global coilsAlloted
    global opt_unallocatedcoils
    a = 0
    if (prob.status == 1):
        df.loc[:, 'GrpKey'] = str(GrpKey)
        df['Comment'] = add_comment
        df['ObjValue'] = pulp.value(prob.objective)
        df['ProblemStatus'] = LpStatus[prob.status]
        c = 0
        a1 = [0] * len(listCoil)
        a = 0
        for j in listRail:
            k = 0
            if (int(value(rail_vars[j])) == 1):
                rails.append(1)
                a = a + 1
            else:
                rails.append(0)
            for i in listCoil:
                if (float(value(x_vars[i][j])) > 1.14033782417e-9):
                    coilsAlloted = coilsAlloted + 1
                    k = 1
                    if (j == 0):
                        c = 1
                    df.loc[df_index_list[i], 'Wagon-No'] = a + absRails
                    a1[i] = a
            if (k == 1):
                c = c + 1
        for i in listCoil:
            if (a1[i] == 0):
                df.loc[df_index_list[i], 'Wagon-No'] = 'Not Allocated'
                opt_unallocatedcoils = opt_unallocatedcoils + 1
        total_width_unalctd = df[df['Wagon-No'].astype(str) == 'Not Allocated']['Width'].sum()
        total_load_unalctd = df[df['Wagon-No'].astype(str) == 'Not Allocated']['Delivery Qty'].sum()
        correct_commentld = ''
        if (total_load_unalctd <= min_wagon_wt):
            correct_commentld = "Leftover Wt Less Than Load Lower Bound"
        correct_commentwtd = ''
        if (total_width_unalctd >= max_width):
            correct_commentwtd = "Width exceeding the Max width allowed"
        df.loc[df['Wagon-No'].astype(str) == 'Not Allocated', 'Comment'] = correct_commentld + '  ' + correct_commentwtd
        print(
        "Group num is ", df['Group-Number'].iloc[0], " and Wagons Required are ", a, " Total Wagons till now are ",
        absRails + a)
        a = absRails + a
        c = absRails + c
        df1=pd.DataFrame(df)
        df1['Prod Dt']=df1['Prod Dt'].astype(object)
        df1['Wagon-No']=df1['Wagon-No'].replace("Not Allocated",0)
        df1['Wagon-No'] = df1['Wagon-No'].astype(int)
        for index, i in df1.iterrows():
            data = (i['Scenario'],i['Group-Number'],i['Route'],i['SLoc'],i['Ship-to Abb'],i['Primary Equipment'],i['Batch'],i['SW'],i['Met Held'],i['Heat No'],i['Delivery Qty'],i['Width'],i['Length'],i['Test Cut'],i['Customer Priority'],i['Wagon-No'],i['Comment'])
            curs.execute(sql,data)
            conn.commit()
        return df, a
    else:
        global not_solved
        not_solved += 1
        opt_unallocatedcoils = opt_unallocatedcoils + df.shape[0]
        df.loc[:, 'GrpKey'] = str(GrpKey)
        df['Wagon-No'] = 'Not Allocated'
        if (prob.status == -1 or prob.status == -3):
            df['Comment'] = 'Infeasible Problem'
        elif (prob.status == -2):
            df['Comment'] = 'Unbounded Problem'
        elif (prob.status == -3):
            df['Comment'] = 'Infeasible Problem'
        elif (prob.status == 0):
            df['Comment'] = 'Problem Not Solved due to timeout'
        else:
            df['Comment'] = 'TimeOut'
        df1=pd.DataFrame(df)
        df1['Prod Dt'] =df1['Prod Dt'].astype(object)
        df1['Wagon-No']=df1['Wagon-No'].replace("Not Allocated",0)
        df1['Wagon-No'] = df1['Wagon-No'].astype(int)
        for index, i in df1.iterrows():
            data = (i['Scenario'],i['Group-Number'],i['Route'],i['SLoc'],i['Ship-to Abb'],i['Primary Equipment'],i['Batch'],i['SW'],i['Met Held'],i['Heat No'],i['Delivery Qty'],i['Width'],i['Length'],i['Test Cut'],i['Customer Priority'],i['Wagon-No'],i['Comment'])
            curs.execute(sql,data)
            conn.commit()
        return df, absRails
warnings.filterwarnings("ignore") 
write_summary = 1 
Add_HeatNo_Cons = 1  # no use of this flag 
afilename = 'demodata' 
add_comment = '' 

DefaultScenario = 0 
# scenario settings 

customer_proir_flag = 1 
flag_boostmetclr = 1 
mboost = 2000 
tboost = 100 
cltmet_testtype = 1 
SW_flag = 0 
prod_dt = 0 
cm01_cons = 0 


# cbc settings 
cbc_flag=0 
defaultfracGap = 0 
maxSecs = 4800 
time_flag = 1 
# global variables to count coils 
absRails = 0 
coilsAlloted = 0 
smallgrpcoils = 0 
inputcoils = 0 
opt_unallocatedcoils = 0 
time_required = 0 
pass2runs = 0 
# weights for opt 
load_scale_factor = 10000 

obj_wt_wagon = 10 
maincoilwt = 400 
prod_wt = 1 
# sw_wt=200 
sw_wt = 25 
# met wt as of fri a246pm 
# met_wt1=75,40 for results4,2 for bgrp 
# met_wt2=50,20 
met_wt1 = 5 
met_wt2 = 2 

nonmet_wt1 = 50 
nonmet_wt2 = 10 

test_wt1 = 20 
test_wt2 = 10 

cm_wt1 = 10 
cm_wt2 = 10 
# nonmetboost=25 

outputfiledir = localaddress+"\\static"
os.chdir(outputfiledir)
##global variables for solutionstatus df 
dctGrpBatch = {} 
Slocnameslist = [] 

conn = pymysql.connect(host='scdemoserver.mysql.database.azure.com',
		user='myadmin@scdemoserver',password='Megh@4420',
		db='inventory_management',charset='utf8mb4',
		cursorclass=pymysql.cursors.DictCursor, ssl = {'ssl': {'ca': '/var/www/html/BaltimoreCyberTrustRoot.crt.pem'}})

cur = conn.cursor()
curs = conn.cursor()
curr = conn.cursor()

cur.execute("SELECT * FROM scenario")
result = cur.fetchall()
scenariod = pd.DataFrame(result)
scenariod = scenariod.replace('Yes',1)
scenariod = scenariod.replace('No',0)
scenariodf = pd.DataFrame(scenariod)
scenario_length=len(scenariodf)

curr.execute("SELECT * FROM `input`")
result1 = curr.fetchall()
all_data = pd.DataFrame(result1)
all_data.dtypes
all_data['Width'] = all_data['Width'].convert_objects(convert_numeric=True)

req_cols = ['Route', 'SLoc', 'Ship-to Abb', 'Primary Equipment', 'Batch', 'Prod Dt', 'SW', 'Met Held', 'Heat No', 
            'Delivery Qty', 'Width', 'Length', 'Test Cut', 'Customer Priority'] 

Print_cols = ['Group-Number', 'Route', 'SLoc', 'Ship-to Abb', 'Primary Equipment', 'Batch', 
              'Prod Dt', 'SW', 'Met Held', 'Heat No', 'Delivery Qty', 'Width', 'Length',
              'Test Cut', 'Customer Priority', 'Wagon-No', 'Comment'] 

req_data = all_data.loc[:, req_cols] 
req_data['Group-Number'] = np.nan 
req_data['Prod Dt'] = pd.to_datetime(req_data['Prod Dt']) 
inputcoils = req_data.shape[0] 
scen_time = str(time.time()).replace('.', '') 
svalue = 0
sql = "INSERT INTO `output` (`Scenario`,`Group-Number`,`Route`,`SLoc`,`Ship-to Abb`,`Primary Equipment`,`Batch`,`SW`,`Met Held`,`Heat No`,`Delivery Qty`,`Width`,`Length`,`Test Cut`,`Customer Priority`,`Wagon-No`,`Comment`) VALUES( %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
for scenario in range(0, len(scenariodf)): 
    scenarioReader(scenariodf, scenario) 
    currentscenarioname = scenariodf['scenario'].iloc[scenario] 
    svalue = svalue + 1
    if scenariodf['sub_grouping_rules'][scenario] == "SLoc,Route,ShipToAbb,PrimaryEqpt":
        group_rule = ['SLoc', 'Route', 'Ship-to Abb', 'Primary Equipment']

    elif scenariodf['sub_grouping_rules'][scenario] == "SLoc,Route,ShipToAbb":
        group_rule = ['SLoc', 'Route', 'Ship-to Abb']

    elif scenariodf['sub_grouping_rules'][scenario] == "SLoc,Route":
        group_rule = ['SLoc', 'Route']

    elif scenariodf['sub_grouping_rules'][scenario] == "Route,ShipToAbb,PrimaryEqpt":
        group_rule = ['Route', 'Ship-to Abb', 'Primary Equipment']

    elif scenariodf['sub_grouping_rules'][scenario] == "Route,ShipToAbb":
        group_rule = ['Route', 'Ship-to Abb']

    else:
        group_rule = ['Ship-to Abb','Primary Equipment']


    grouped_data = req_data.groupby(group_rule)
#    outputfilename = afilename + '_' + scenariodf['scenario'].iloc[scenario] + '_' + scen_time + '.csv' 
    outputfilename = afilename + '.txt' 
    absRails = 0 
    coilsAlloted = 0 
    smallgrpcoils = 0 
    opt_unallocatedcoils = 0 

    absStartTime = time.time() 
    total_num_of_grps = len(grouped_data) 
    print("Total number of groups:", len(grouped_data)) 
    small_grps = 0 
    large_grps = 0 
    not_solved = 0 
    group_number = 1 
    min_wagon_wt = scenariodf['load_lower_bounds'][scenario]
    for key, grp in grouped_data: 
        df = grouped_data.get_group(key)
        df['Scenario'] = svalue
        df['Group-Number'] = group_number 
        group_number = group_number + 1 
        if (df['Delivery Qty'].sum() < min_wagon_wt): 
            small_grps += 1 
            smallgrpcoils = smallgrpcoils + len(grp) 
            df['ProblemStatus'] = 'Infeasible Due to Insufficient Load' 
            df['Wagon-No'] = 'Not Allocated' 
            df['Comment'] = 'Infeasible Due to Insufficient Load' 
            df.loc[:, 'GrpKey'] = str(key) 
            df1=pd.DataFrame(df)
            df1['Prod Dt'] =df1['Prod Dt'].astype(object)
            df1['Wagon-No']=df1['Wagon-No'].replace("Not Allocated",0)
            df1['Wagon-No'] = df1['Wagon-No'].astype(int)
            for index, i in df1.iterrows():
                data = (i['Scenario'],i['Group-Number'],i['Route'],i['SLoc'],i['Ship-to Abb'],i['Primary Equipment'],i['Batch'],i['SW'],i['Met Held'],i['Heat No'],i['Delivery Qty'],i['Width'],i['Length'],i['Test Cut'],i['Customer Priority'],i['Wagon-No'],i['Comment'])
                curs.execute(sql,data)
                conn.commit()
            continue 
        large_grps += 1 
        numRailGuess = int(math.ceil((df['Delivery Qty'].sum() / min_wagon_wt)))
        GrpKey = key 
        numRailCars = numRailGuess 
        numCoils = df.shape[0] 
        listCoil = range(numCoils) 
        listRail = range(numRailCars) 
        dictWidth = dict(enumerate(df.Width)) 
        dictLoad = dict(enumerate(df['Delivery Qty']))
        if (numCoils >= 50): 
           print("") 
        else: 
            fracGap = defaultfracGap 
            opt_obj, absRails = optPulpCaller(df, dictWidth, dictLoad, numRailGuess, GrpKey, Add_HeatNo_Cons, listRail, listCoil, absRails, fracGap, maxSecs, group_number - 1, cbc_flag) 
        print("absRails=", absRails) 
        print("--------------------\n")
    print("total num of grps =", len(grouped_data)) 
    print("total num of large grps=", large_grps) 
    print("total num of small gprs=", small_grps) 
    print("total num of notsolved=", not_solved) 
    print("absrail=", absRails, "Coils Supplied=", inputcoils, "Coils Alloted=", coilsAlloted, "Unallocated after opt=", 
          opt_unallocatedcoils, "SmallgrpCoils=", smallgrpcoils) 
    absEndTime = time.time() 
    print("+++++++++++++++++++++") 
    print("Time required for total run is :-", absEndTime - absStartTime) 
    time_required = time_required + absEndTime - absStartTime 
    print("Time till now= :-", time_required) 
    print("pass number=", scenario, "pass 2 runs=", pass2runs) 
    if (write_summary == 1): 
        writetext = []
        writetext.append("\n")
        writetext.append(" Scenario " + str(svalue))
        writetext.append(" Total num of clusters : " + str(len(grouped_data)))
        writetext.append(" Total num of large clusters : " + str((large_grps)))
        writetext.append(" Total num of small clusters : " + str((small_grps)))
        writetext.append(" Total num of not solved clusters : " + str(not_solved))
        writetext.append(" Total num of Wagons : " + str(absRails))
        writetext.append(" Total num of Coils Alloted : " + str(coilsAlloted))
        writetext.append(" Total num of Coils unAlloted after opt : " + str(opt_unallocatedcoils))
        writetext.append(" Total num of Small cluster Coils : " + str(smallgrpcoils))
        writetext.append(" Time for run : " + str(absEndTime - absStartTime))
        writetext.append(" Time till now : " + str(time_required))
        writetext.append(" Pass 2 runs till now : " + str(pass2runs))
        with open(os.path.join(outputfiledir, outputfilename), 'a') as f: 
            for l in writetext: 
                f.write(l) 
                f.write('\n')
        f.close()
