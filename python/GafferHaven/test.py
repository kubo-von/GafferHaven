import ssl
import urllib.request
import json

# import GafferHaven
# import importlib
# importlib.reload(GafferHaven)

def havenApiQuery(arguments):
	user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'

	url = "https://api.polyhaven.com/"+arguments
	headers={'User-Agent':user_agent,} 

	request=urllib.request.Request(url,None,headers) #The assembled request
	response = urllib.request.urlopen(request)
	data = response.read() # The data u need
	#print(data)
	jdata = json.loads(data)
	print(type(jdata))
	for h in jdata.keys():
		print(jdata[h])


#print(havenApiQuery("assets?t=hdris"))
#print(havenApiQuery("files/abandoned_church"))
#print(havenApiQuery("info/muddy_autumn_forest"))
#print(havenApiQuery("categories/hdris"))

import havenAssetLibrary
l = havenAssetLibrary.library()