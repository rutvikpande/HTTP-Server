from threading import Thread
import mimetypes
import webbrowser
import random
import requests
import time
import json
import os


#setting up the default locations for testing files
curr_path = os.getcwd()
test_path = curr_path + "/testing/"
put_path = curr_path + "/testing/PUT/"

class Tester(Thread):
	'''
        The Tester class tests the multi threaded server
        GET request - Get the request ,opens the request in the browser.
        PUT request - creates the resource and makes request
        HEAD request - give all headers 
        DELETE request - deletes the resource.
    '''
	def __init__(self, urls, f):
		Thread.__init__(self)
		self.urls = urls
		self.flag = f

	def run(self):
		current_urls = []
		for method, url in self.urls.items():
			if method == "GET":
				get_obj = GET(url, self.flag)
				current_urls.append(get_obj)
				get_obj.start()
				
			elif method == "PUT":
				put_obj = PUT(url,self.flag)
				current_urls.append(put_obj)
				put_obj.start()


			elif method == "DELETE":
				delete_obj = DELETE(url, self.flag)
				current_urls.append(delete_obj)
				delete_obj.start()

			elif method == "HEAD":
				head_obj = HEAD(url, self.flag)
				current_urls.append(head_obj)
				head_obj.start()
				
class GET(Thread):
	def __init__(self, url, flag):
		Thread.__init__(self)
		self.url = url
		self.flag = flag

	def run(self):
    	
		if self.flag == 1:
			index = 0 #random.randint(0,3)
			print("GET - requested resource opened up in browser. url :" + self.url[index])
			webbrowser.open_new_tab(self.url[index])
		
		elif self.flag == 2:
			url = self.url["url"]
			print("GET- request opened via browser. url :" + url)
			webbrowser.open_new_tab(url)


class PUT(Thread):
	def __init__(self, url, flag):
		Thread.__init__(self)
		self.url = url
		self.flag = flag
		
	def run(self):
		if self.flag == 1:
			index = random.randint(0, len(self.url) -1 )
			file_name = self.url[index].split('http://localhost:7677/')[1]
			file_name = put_path + file_name 
			guess = mimetypes.MimeTypes().guess_type(file_name)[0]
			file_data = open(file_name, "rb").read()

			#make a put request 
			req = requests.put(self.url[index], data = file_data, headers={"Connection": "close", "Content-Type": guess })
			print("PUT-" + self.url[index] + " : " + str(req.status_code) + " " + req.reason + "\n" )

			#opens the uploaded resource into browser
			webbrowser.open_new_tab(self.url[index])
	
		

class DELETE(Thread):
	def __init__(self, url, flag):
		Thread.__init__(self)
		self.url = url
		self.flag = flag

	def run(self):
		if self.flag == 1:
			#make a delete request 
			index = random.randint(0, len(self.url) -1 )
			res = requests.delete(self.url[index], headers={"Connection": "close"})
			print("DELETE url :" + self.url[index] + " " +  str(res.status_code) + " " + res.reason + "\n")

		
class HEAD(Thread):
	def __init__(self, url, flag):
		Thread.__init__(self)
		self.url = url
		self.flag = flag

	def run(self):
		if self.flag == 1:
			#making a head request
			res = requests.head(self.url, headers={"Connection": "close"})
			requests.session().close()
			print("HEAD request to" + self.url + " : " + str(res.status_code) + " " + res.reason + "\nHeaders:")
			for key, value in res.headers.items():
				print(key + ":" + value )
			print("\n")




if __name__ == "__main__":

	print(Tester.__doc__)

	#testing the basic requests methods
	print("--" * 50  + "\n")
	print("Testing the basic request methods")
	print("--" * 50  + "\n")

	with open(test_path + "test1.json", 'r') as f_in:
		urls = json.load(f_in)
	test1 = Tester(urls, 1) 
	test1.start()
	test1.join()
	time.sleep(2)
	
	#testing multiple clients with the same access url
	print("--" * 50  + "\n")
	print("Testing many clients simultaniously ")
	print("--" * 50  + "\n")

	current_clients = []
	with open(test_path + "test2.json", 'r') as f_in:
		urls = json.load(f_in)

	for _ in range(urls['GET']["max_client"]):
		obj = Tester(urls, 2)
		current_clients.append(obj)
		obj.start()
	for client in current_clients:
    		client.join()

	















