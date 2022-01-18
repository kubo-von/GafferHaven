import os, pathlib
import ssl
import urllib.request
import json

#library stores both local and web assets
class Library:
	def __init__(self):
		self.lib_path = key = os.getenv('HAVENLIBRARY')
		self.local_hdris_path = os.path.join(self.lib_path,"hdris/downloaded")
		self.local_cache_path = os.path.join(self.lib_path,"hdris/cache")
		self.assets = dict()
		self.assets["local_hdris"] = []
		self.assets["web_hdris"] = []
		self.categories = dict()
		self.categories["local_hdris"] = []
		self.categories["web_hdris"] = []
		make_folder(self.local_hdris_path)
		make_folder(self.local_cache_path)
		self.reload_local()
	
	def reload_local(self):
		self.assets["local_hdris"] = []
		dirs = os.listdir(self.local_hdris_path)
		for d in dirs:
			raw_info = dict()
			hdri = Hdri(d,self,True,raw_info)
			self.assets["local_hdris"].append(hdri)
			self.categories["local_hdris"] = merge_into_list(self.categories["local_hdris"],hdri.categories)

	def reload_web(self):
		self.assets["web_hdris"] = []
		data = haven_api_query("assets?t=hdris")
		for key,raw_info in data.items():
			hdri = Hdri(key,self,False,raw_info)
			self.assets["web_hdris"].append(hdri)
			self.categories["web_hdris"] = merge_into_list(self.categories["local_hdris"],hdri.categories)

class Hdri:
	def __init__(self,hdri_id,lib,local,raw_info):
		self.local = local
		self.id = hdri_id
		self.lib = lib
		self.info = raw_info
		self.resolutions_downloaded = []

		if local:
			self.thumbnail = os.path.join(lib.local_hdris_path,self.id,self.id+".webp")
			self.info = load_json_dict( os.path.join(self.lib.local_hdris_path, self.id, self.id+".json") )
		else:
			self.thumbnail = self.cache_thumbnail()

		self.get_resolutions_dowloaded()

		if ("categories" in self.info.keys()):
			self.categories = self.info["categories"]
		else:
			self.categories = []

	def get_file_path(self,res):
		return os.path.join(self.lib.local_hdris_path, self.id, self.id+"_"+res+".exr")

	def get_resolutions_dowloaded(self):
		local_folder = self.lib.local_hdris_path+"/"+self.id+"/"
		if os.path.isdir(local_folder):
			for file in os.listdir(local_folder):
				if file.endswith(".exr"):
					self.resolutions_downloaded.append(file.rsplit("_")[-1].rsplit(".")[0])

	def get_resolutions_available(self):
		data = haven_api_query("files/"+self.id)
		result = dict()
		for res, files in data["hdri"].items():
			if ("exr" in files.keys()):
				result[res]= files["exr"]["url"]
		return result
	
	def use(self,res,node):
		# Set map path and resolution on the light node in Gaffer
		node_type = node.typeName()
		# Cycles
		if (node_type == "GafferCycles::CyclesLight"):
			node['parameters']['image'].setValue( self.get_file_path(res).replace(self.lib.local_hdris_path,"${HAVENLIBRARY}/hdris/downloaded")) 
			node['parameters']['map_resolution'].setValue(self.get_map_resolution(res))
		# Arnold
		elif (node_type == "GafferArnold::ArnoldShader"):
			node['parameters']['filename'].setValue( self.get_file_path(res).replace(self.lib.local_hdris_path,"${HAVENLIBRARY}/hdris/downloaded")) 

	def download_and_use(self,res,node,dowload_link):
		# Download .exr
		target_exr_path = self.get_file_path(res)
		make_folder( os.path.join(self.lib.local_hdris_path,self.id) )
		dowload_file(dowload_link, target_exr_path)
		# Dwonload Thumbnail
		thumb_path = os.path.join(self.lib.local_hdris_path, self.id, self.id+".webp")
		if not os.path.isfile(thumb_path):
			dowload_file("https://cdn.polyhaven.com/asset_img/thumbs/"+self.id+".png?height=480", thumb_path)
		# Store info dict
		json_path = os.path.join(self.lib.local_hdris_path, self.id, self.id+".json")
		dump_to_json(json_path,self.info)
		# Set map path and resolution on the light node in Gaffer
		self.use(res,node)

	def cache_thumbnail(self):
		cached_path = os.path.join(self.lib.local_cache_path,self.id+".webp")
		if not os.path.isfile(cached_path):
			dowload_file("https://cdn.polyhaven.com/asset_img/thumbs/"+self.id+".png?height=180", cached_path)
		return cached_path

	def get_map_resolution(self,res):
		resolutions = {
		  "1k": 1024,
		  "2k": 2048,
		  "4k": 4096,
		  "8k": 8192,
		  "16k": 16384
		}
		if res not in resolutions.keys():
			return 1024
		else:
			return resolutions[res]

# == Utils ==
	
# Query the Polyhaven api https://github.com/Poly-Haven/Public-API
def haven_api_query(arguments):
	# Setting headers to prevent 403 error
	user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
	url = "https://api.polyhaven.com/"+arguments
	headers={'User-Agent':user_agent,} 
	# Query the api
	request=urllib.request.Request(url,None,headers)
	response = urllib.request.urlopen(request)
	# Store the json response as dict
	data = response.read() 
	jdata = json.loads(data)
	return jdata

# Make all folders in the path unless they already exist
def make_folder(path):
	if os.path.exists(path):
		pass
	else:
		os.makedirs(path, mode=0o777, exist_ok=True)

# Download file from web
def dowload_file(source,target):
	try:
		headers={'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'}
		request_=urllib.request.Request(source,None,headers) #The assembled request
		response = urllib.request.urlopen(request_)# store the response
		#create a new file and write the image
		with open(target, 'wb') as out_file:
			out_file.write(response.read())
	except Exception as e:
		print( "Failed to download {} to {}".format(source,target) )
		print( e.__class__)
		print( e.reason )

# save dict as json file
def dump_to_json(filepath,dictonary):
	with open(filepath,"w") as f:
		json.dump(dictonary,f)

# Load json file as dict
def load_json_dict(file_path):
	try:
		with open(file_path, 'r') as j:
			return json.loads(j.read())
	except Exception as e:
		print("could not load {}, {}".format(filepath),e)
		return dict()

# Adds item from 2nd lists to the 1st one except if they already exist there
def merge_into_list(target_list,source_list):
	out = target_list
	for i in source_list:
		if i not in target_list:
			out.append(i)
	return out
