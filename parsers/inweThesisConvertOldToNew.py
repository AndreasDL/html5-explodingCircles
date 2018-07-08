"""
Eerst database.sql uitvoeren voor de structuur.
Dan definitions.py uitvoeren om de testdefinities toe te voegen.
Dit uitvoeren voegt testbeds dubbel toe (bv vwall1 en vwall1-am3)
"""
import re
import pprint #debug
import os
import psycopg2
import psycopg2.extras
import sys
import urllib.request
import xml.etree.ElementTree as etree

#############################################################################settings#############################################################################
#baseDir  = "/home/drew/masterproef/f4ftestsuite/trunk/monitor_site/work/monitoring/contexts/"
baseDir  = "/home/drew/masterproef/playground/scripts/overzetten/bvermeul/"
firstDir = ["fls","international"] #dirs for ping, getVersion & list resources
loginDir = "login_scenarios"
stitchingDir = "stitching_scenarios"
#resultDir    = "/home/drew/masterproef/f4ftestsuite/trunk/monitor_site/db_dump_scenarios.sql"
resultDir    = "/home/drew/masterproef/playground/scripts/overzetten/db_dump_scenarios.sql"

resultsDir   = "/home/drew/masterproef/site/results/"
certDir      = "/home/drew/.ssl/"

dbname = "testdb"
user  = ""
dpass = ""
durl  = "localhost"
pingFreq   = 300
listFreq   = 900
getVerFreq = 900
loginFreq  = 43200
stitchFreq = 43200
nextRun = "2014-1-7T12:00:00"
enabled = True
convert = True

if (len(sys.argv) > 1):
	dbname = str(sys.argv[1])
	if (len(sys.argv) > 2):
		convert = False

print("Connecting to database")
con = psycopg2.connect(database=dbname,user=user,password=dpass,host=durl)
cur = con.cursor()

###############################################################################Parsing###############################################################################

users = {} #mapped on username
testbeds = {} #maped on testbedname
testbedurns = {} #we need also to know which urns are already in the database
tests = {} #keep track of simple tests user => test
stitchpathids  = {} #contextfilename => {id nieuw , id old}
stitchpath = {} #old id => filename

addUserQ = "INSERT INTO users (username,userAuthorityUrn,passwordFilename,pemKeyAndCertFilename) VALUES(%s,%s,%s,%s)"
addBedQ  = "INSERT INTO testbeds (testbedname,url,urn) VALUES(%s,%s,%s)"
addTestQ = "INSERT INTO testinstances (testname,testDefinitionName,frequency,nextrun,enabled) VALUES(%s,%s,%s,%s,%s) RETURNING testinstanceid"
addParQ  = "INSERT INTO parameterInstances (testinstanceId,parameterName,parametervalue) VALUES (%s,%s,%s)"
addResQ  = "INSERT INTO results (testinstanceid,log,timestamp) VALUES(%s,%s,%s) RETURNING resultid"
addSubResQ = "INSERT INTO subresults (resultid,returnname,returnvalue) VALUES(%s,%s,%s)"

def addUser(map,cur):
	cur.execute(addUserQ,(\
		map['username'],\
		map['userAuthorityUrn'],\
		certDir+"pass",\
		#map['passwordFilename'],\
		certDir+"cert.pem"\
		#map['pemKeyAndCertFilename']\
	))
	users[map['username']] = map
	tests[map['username']] = {"simple" : {}, "login" : {}, 'stitch' : {}} #user testtype testbedname testid
def addTestbed(map,cur):
	cur.execute(addBedQ,
		(map['testbedname'],
		map['pinghost'],
		map['testedAggregateManagerUrn'],
		)) #add testbed
	testbedurns[map['testedAggregateManagerUrn']] = map
	testbeds[map['testbedname']] = map

def addpingTest(map,cur):
	cur.execute(addTestQ,(map['testbedname']+"ping","ping",pingFreq,nextRun,enabled))
	cur.execute(addParQ,(cur.fetchone()[0],"testbed",map['testbedname']))
def addListTest(map,cur):
	cur.execute(addTestQ,(map['testbedname']+"list","listResources",listFreq,nextRun,enabled))
	testinstanceid = cur.fetchone()[0]
	cur.execute(addParQ,(testinstanceid,"testbed",map['testbedname']))	
	cur.execute(addParQ,(testinstanceid,"user",map['username']))
def addGetVersionTest(map,cur):
	if ("amversion" in map and map['amversion']== 3):
		cur.execute(addTestQ,(map['testbedname']+"getVerv3","getVersion3",getVerFreq,nextRun,enabled))
		testinstanceid = cur.fetchone()[0]
		cur.execute(addParQ,(testinstanceid,"testbed",map['testbedname']))	
		cur.execute(addParQ,(testinstanceid,"user",map['username']))
	else :
		cur.execute(addTestQ,(map['testbedname']+"getVerv2","getVersion2",getVerFreq,nextRun,enabled))
		testinstanceid = cur.fetchone()[0]
		cur.execute(addParQ,(testinstanceid,"testbed",map['testbedname']))	
		cur.execute(addParQ,(testinstanceid,"user",map['username']))
def addLoginTest(map,cur):
	if ("amversion" in map and map['amversion']== 3):
		cur.execute(addTestQ,(map['testbedname']+"login3","login3",loginFreq,nextRun,enabled))
		testinstanceid = cur.fetchone()[0]
		cur.execute(addParQ,(testinstanceid,"testbed",map['testbedname']))	
		cur.execute(addParQ,(testinstanceid,"user",map['username']))
	else :
		cur.execute(addTestQ,(map['testbedname']+"login2","login2",loginFreq,nextRun,enabled))
		testinstanceid = cur.fetchone()[0]
		cur.execute(addParQ,(testinstanceid,"testbed",map['testbedname']))	
		cur.execute(addParQ,(testinstanceid,"user",map['username']))
def addStitchingTest(map,cur):
	testname = ""
	for urn in map["stitchedAuthorityUrns"]:
		testname += testbedurns[urn]['testbedname']
	testname += "stitch"

	cur.execute(addTestQ,(testname,"stitch",stitchFreq,nextRun,enabled))
	testinstanceid = cur.fetchone()[0]

	cur.execute(addParQ,(testinstanceid,"user",map['username']))
	for urn in map["stitchedAuthorityUrns"]:
		cur.execute(addParQ,(testinstanceid,'stitchedAuthorities',testbedurns[urn]['testbedname']))
	if "scsUrl" not in map : map['scsUrl'] = "http://geni.maxgigapop.net:8081/geni/xmlrpc"
	cur.execute(addParQ,(testinstanceid,'scsUrl',map['scsUrl']))
	cur.execute(addParQ,(testinstanceid,'testedAggregateManager',testbedurns[map['testedAggregateManagerUrn']]['testbedname']))

	return testinstanceid

def getUrlFromUrn(urn):
	return urn.split("+")[1]	
def getNameFromUrn(urn):
	name = getUrlFromUrn(urn).split('.')[0]
	print("\t!Warn testbed with urn: %s Added with name: %s" % (urn,name))
	return name

def addStitchResult(map,cur):
	#makedir
	dates = map['date_start'].split()
	hours = dates[1]
	dates = dates[0].split("-")
	newid = stitchpathids[stitchpath[map['context_id']]]['newid']
	path = resultsDir + "stitch/" + str(newid) + "/" + str(dates[0]) + "/" + str(dates[1]) + "/" + str(dates[2]) + "/" + str(hours) + "/"
	#print(path)
	if not os.path.exists(path) : os.makedirs(path)
	try: 
		#get & save html
		urllib.request.urlretrieve(map["detail_url"], path + "result.html")
		#save xml
		urllib.request.urlretrieve(map['detail_xml'], path + "result-overview.xml")
		#load & parse xml
		#put in database
		cur.execute(addResQ,(newid,"",map["date_start"]+"+02"))
		resultid = cur.fetchone()[0]
		for method in etree.parse(path+"result-overview.xml").getroot().iter("method") :
			cur.execute(addSubResQ,(resultid,method.find("methodName").text,method.find("state").text))
		cur.execute(addSubResQ,(resultid,"log",""))
		print(map['id'] ,"added stitchingResult", resultid," with id",newid," date: " , map['date_start'])
		con.commit();
	except :
		print ("toevoegen van result met (old) id " , map['id'], " is mislukt, ophalen van result.html of result-overview.xml is niet gelukt");
		con.rollback();


################################################################################################################################
#####################								Parse data
################################################################################################################################

print("Parsing existing data")
print("\tParsing fls monitoring & flsmonitoring_international")
for dir in firstDir:
	print("Dir:", dir)

	for file in os.listdir(baseDir+dir):
		if file.endswith(".properties"):
			f = open(baseDir+dir+"/"+file,'r')
		
			map = {"testbedname" : (file.split("=")[2]).split(".")[0]}
			for line in f:
				arr = line.split("=");
				if (len(arr) > 1): map[arr[0].strip()] = arr[1].strip()

			if len(map) >= 7:
				if map['testbedname'] not in testbeds : addTestbed(map,cur)
				if map['username'] not in users: addUser(map,cur)
				if map['testbedname'] not in tests[map['username']]["simple"]:
					addpingTest(map,cur)
					addListTest(map,cur)
					addGetVersionTest(map,cur)
					tests[map['username']]["simple"][map['testbedname']] = True #id haalt hier niet uit
			else :
				print("\t!!Adding testbed & ping & list & getVersion failed for %s" % map['testbedname'])
			f.close()
		con.commit() #commit after each file

print("\tParsing login tests")
print("Dir:", loginDir)
for file in os.listdir(baseDir+loginDir):
	if file.endswith(".properties"):
		f = open(baseDir+loginDir+'/'+file,'r')

		map = {"testbedname" : (file.split("=")[2]).split(".")[0]}
		for line in f:
			arr = line.split("=");
			if (len(arr) > 1): map[arr[0].strip()] = arr[1].strip()

		if len(map) >= 7:
			if map['testbedname'] not in testbeds :	addTestbed(map,cur)
			if map['username'] not in users : addUser(map,cur)
			if map["testbedname"] not in tests[map['username']]["login"] : 
				addLoginTest(map,cur)
				tests[map['username']]["login"][map['testbedname']] = True #haalt hier niet uit
		else :
			print("\t!!Adding testbed & logintest failed for %s" % map['testbedname'])
con.commit()

print("\tParing Stitching tests")
print("Dir:", stitchingDir)
for file in os.listdir(baseDir+stitchingDir):
	if file.endswith(".properties"):
		f = open(baseDir+stitchingDir+'/'+file,'r')

		map = {}
		for line in f:
			arr = line.split("=");
			if (len(arr) > 1): map[arr[0].strip()] = arr[1].strip()
		map['stitchedAuthorityUrns'] = map['stitchedAuthorityUrns'].split()
		for i in range(len(map['stitchedAuthorityUrns'])): 
			map['stitchedAuthorityUrns'][i] = map['stitchedAuthorityUrns'][i].strip()

		if len(map) >= 7:
			if map['username'] not in users: addUser(map,cur)
			for urn in map['stitchedAuthorityUrns']:
				if urn not in testbedurns :
					bedmap = {'testbedname' : getNameFromUrn(urn), 'pinghost' : getUrlFromUrn(urn), 'testedAggregateManagerUrn' : urn}
					addTestbed(bedmap,cur)

			testinstanceid = addStitchingTest(map,cur)
			tests[map['username']]['stitch'][map['testname']] = testinstanceid
			stitchpathids[file] = {'newid' : testinstanceid , "oldid" : ""}
			#print("\tadded",map['testname'])
		else:
			print("\t!!Adding testbed & stitchingTest failed for %s" % map['testbedname'])
con.commit()


#######################################################################Convert Results################################################################
if (convert):
	print("Parsing Results")
	print("Dir:", resultDir)
	f = open(resultDir,'r')
	header = ""
	#skip stuffs above
	for line in f:
		if line.startswith("COPY test_context") : 
			header = [ colname.strip() for colname in line.split("(")[1].split(")")[0].split(",")]
			break
	#pprint.pprint(header)

	#parse testcontexts here & add if needed
	for line in f:
		if line.startswith("\\.") : break
		map = { header[i] : line.split("\t")[i] for i in range(len(header)) }
		filename =map["contextfilename"].split("/")[-1] 
		if map["contextfilename"].split("/")[-1] in stitchpathids:
			stitchpathids[filename]["oldid"] = map["id"]
			stitchpath[map['id']] = filename

	#skip stuffs in between
	for line in f:
		if line.startswith("COPY test_results") : 
			header = [ colname.strip() for colname in line.split("(")[1].split(")")[0].split(",")]
			break

	#parse results and link to contexts
	for line in f:
		if line.startswith("\\.") : break
		ll = [ col.strip() for col in line.split("\t") ]
		result = {header[i] : ll[i] for i in range(len(header)) }
		result['detail_xml'] = result['detail_url'][0:-5] +  "-overview.xml"
		if result['context_id'] in stitchpath :
			addStitchResult(result,cur)
			#con.commit() nu in functie


####################################################################dubbels verwijderen
dubbelQuery = "select * from testbeds X where X.urn = any(select urn from testbeds group by urn having count(1) > 1) order by urn DESC,testbedname;"
getTypes = "select testinstanceid,testdefinitionname,testname from testinstances where testinstanceid = ANY(select testinstanceid from parameterinstances where parametervalue = %s)"
changeTestType = "update testinstances set testdefinitionname = %s where testinstanceid = %s"
changeTestName = "update testinstances set testname = %s where testinstanceid = %s"
changePar = "update parameterinstances set parametervalue = %s where parametervalue = %s"

deletePar = "delete from parameterinstances where testinstanceid = %s"
deleteTest = "delete from testinstances where testinstanceid = %s"

deleteTestbed = "delete from testbeds where testbedname = %s;"

dict_cur = con.cursor(cursor_factory=psycopg2.extras.DictCursor)
dict_cur.execute(dubbelQuery)
r = dict_cur.fetchone()
while (r != None):
	old_name = r['testbedname'];
	old_urn = r['urn'];
	old_url = r['url'];
	print("Double testbed: {", old_name, ",",old_urn, ",", old_url,"}")

	#dubbels eruithalen
	r= dict_cur.fetchone()
	while ( r != None and old_urn == r['urn']):
		print("\ttestbed: {", r['testbedname'], ",", r['urn'], ",", r['url'], "}")
		
		#testen ophalen
		cur.execute(getTypes,(r['testbedname'],))
		tests = cur.fetchall()
		#pprint.pprint(tests)

		#alles behalve stitching verzetten naar amv3
		for test in tests:
			if (test[1][-1] == "2"):
				#amv verzetten
				cur.execute(changeTestType,(test[1][0:-1] + "3", test[0]))
				cur.execute(changeTestName,(old_name + test[1][0:-1] + "3", test[0]))
			elif (test[1] == 'listResources'): 
				cur.execute(deletePar,(test[0],))
				cur.execute(deleteTest,(test[0],))#deze zal anders dubbel zijn
		#tesbednaam verzetten
		cur.execute(changePar,(old_name,r['testbedname']))
		#testbed verwijderen
		cur.execute(deleteTestbed,(r['testbedname'],))
		con.commit()
		
		r = dict_cur.fetchone()
con.commit()

#########################################################namen van stitch hernoemen (zonder am3)
cur.execute(changeTestName,("vwall1vwall2Stitch",177))
cur.execute(changeTestName,("vwall1utahStitch",178))
cur.execute(changeTestName,("vwall2utahStitch",179))


#########################################################testen van ftestple disablen
print("disable tests with ftestple")
disableTest = "update testinstances set enabled='f' where testinstanceid = %s"
cur.execute(getTypes,("ftestple",))

tests = cur.fetchall()
for test in tests:
	cur.execute(disableTest,(test[0],))
con.commit()

#########################################################specifieke testen disablen
print("disable other tests")
disableTestUrn = "update testinstances set enabled = 'f'\
	where testinstanceid = ANY(select testinstanceid from parameterinstances \
		where parametervalue = ANY(select testbedname from testbeds where urn = %s))"

cur.execute(disableTestUrn,("urn:publicid:IDN+fuseco.fokus.fraunhofer.de+authority+cm",))
con.commit()