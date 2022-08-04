#Server config file
import os
#Server configuration
ServerConfig = {
	"ServerName" : "Sagar_Rutvik",
	"ServerIP" : "127.0.0.1",
	"Connection" : "close",
	"ListenConnection" : 5,
	"Methods" : [ "GET",  "POST",  "PUT" ,  "DELETE",  "HEAD" ],
	"max_bytes" : 1048576,
	"MaxConnections" : 100
}

#Authorization
ServerAuth = {
	"type"	   : "Basic",	
	"username" : "Sagar",
	"password" : "compNet"
}

#locations to the server asssets
DefaultLoc ={

	"ServerResources" : os.getcwd() ,
	"ServerRoot" : os.getcwd(),
}
