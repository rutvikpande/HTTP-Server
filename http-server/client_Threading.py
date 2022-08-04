#References used for this project

#https://developer.mozilla.org/en-US/docs/Web/HTTP
#http://foss.coep.org.in/coepwiki/index.php/Computer_Networks_2020 
#https://bhch.github.io/posts/2017/11/writing-an-http-server-from-scratch/
#https://github.com/sarvesh-bodakhe/http-server
#https://datatracker.ietf.org/doc/html/rfc2616

from threading import Thread
import time
from socket import *
import mimetypes
import os

class client_Thread(Thread):
    '''
        Client Thread 
    '''
    def __init__(self, client_socket, client_address ,server_obj):
        Thread.__init__(self)
        self.client_socket = client_socket
        self.client_ip, self.client_port = client_address
        #server configuration
        self.server_config = server_obj.server_config
        #authentication of server  
        self.server_auth = server_obj.server_auth
        self.default_loc = server_obj.default_loc

    headers = {
        'Server': 'http-server',
        'Content-Type': 'text/html',
    }

    status_codes = {
        200: 'OK',
        404: 'Not Found',
        501: 'Not Implemented',
        400: "Bad Request",
        201: "Created",
        500: "Internal Server Error",
        415: "Unsupported Media Type",
        405 : "Method Not Allowed",
        204 : "No Content",
        505 : "Http Version Not Supported",
        501 : "Not Implemented",
        304 : "Not modified",
        403 : "Access to Resource is Forbidden",
        401 : "Unauthorized",
        503 : "Service unavailable",

    }
    bin_data_flag = 0
    #function to recv the entire message body  
    def recv_all(self):
        chunk = self.client_socket.recv(self.server_config['max_bytes'])
        return chunk

    def run(self):
        request = self.recv_all()
        if request:
            try:
                request = request.decode("utf-8")	
                        
            except(UnicodeDecodeError):  		
                self.bin_data_flag = 1
            # print(request)
        try:
            response = self.request_handler(request)
        except:
            response = self.send_error(500)
            self.client_socket.sendall(response)
            # terminate_thread			
            self.client_socket.close()
        # print(response)
        self.client_socket.sendall(response)
        self.client_socket.close()

    #extacts headers from the request
    def header_parser(self, request):
        data = ""
        dflag = 0
        headers = {}
        for header in request[ 1 : ]:
            if header != "" and dflag == 0:
                try:
                    token, value = header.strip().split(':', 1)
                    token = token.strip().lower()
                    if token == "Authorization":
                        headers[token] = value.strip()
                    else:
                        headers[token] = value.strip().lower()
                    if token == "content-length":
                        data_len = int(value.strip())
                except(ValueError):
                    return self.send_error(400)
            else:
                dflag = 1
                data += header + "\n"
        return (headers, data)
    
    def request_handler(self, request):
        # print(request)
        if self.bin_data_flag == 0:
            request = request.strip().split('\r\n')
        
        #extracting the headers and message body from the request
        self.headers, data = self.header_parser(request)	
        # print(data)
        #error checking on request line 
        try:
            method, resource, version = request[0].split()
        
        except(ValueError):
            return self.send_error(400)

        if method not in self.server_config["Methods"] or resource == "":
            return self.send_error(400)
        elif version == "HTTP/1.1":
            path = resource.strip('/')
            if(method == "GET"):
                return self.GET(path)

            elif(method == "PUT"):
                return self.PUT(path, data)

            elif(method == "DELETE"):
                return self.DELETE(path)

            # elif(method == "POST"):
            #     return self.POST(path, data)

            elif(method == "HEAD"):
                return self.HEAD(path)

            else:
                return self.send_error(405)
        else:
            return self.send_error(505)

    def response_headers(self, extra_headers=None):
        """Returns headers (as bytes).

        The `extra_headers` can be a dict for sending 
        extra headers with the current response
        """
        headers_copy = self.headers.copy() # make a local copy of headers
        # print(headers_copy)
        if extra_headers:
            headers_copy.update(extra_headers)

        headers = ''

        for h in headers_copy:
            headers += '%s: %s\r\n' % (h, headers_copy[h])
        # print(headers)
        return headers.encode() # convert str to bytes

    def response_line(self, status_code):
        """Returns response line (as bytes)"""
        reason = self.status_codes[status_code]
        response_line = 'HTTP/1.1 %s %s\r\n' % (status_code, reason)

        return response_line.encode() # convert from str to bytes

    #headers common to all the request methods
    def common_header(self):
	
        headers = {}
        headers['Server'] = self.server_config["ServerName"]
        headers['Date'] = self.current_time()
        headers['Connection'] = 'close'
        return headers

	#GET speciifc response headers
    def server_get_header(self, path=None):
        # print(path)
        headers = self.common_header()
        headers['Content-Type'] = mimetypes.guess_type(path)[0] or 'text/html'
        headers['Accept-Ranges'] = 'bytes'
        headers['Accept-Language'] = 'en-US'
        return headers
	
	#PUT specific response headers
    def server_put_header( self, path):
        headers = self.common_header()
        if os.path.isdir(path):
            slash = "/"
        else:
            slash = ""
        headers['Content-Location: '] = slash + path.split(self.default_loc["ServerResources"])[1] + "\n\n"
        return headers

	#DELETE specific response headers
    def server_delete_header(self, status_code):

        if status_code == 401:
            headers = self.server_get_header()
            headers['WWW-Authenticate'] = 'Basic, charset = "UTF-8"\n\n'
        else:
            headers = self.server_get_header()
        return headers


    def GET(self, path):
        if not path:
            path = 'index.html'
        if os.path.exists(path) and not os.path.isdir(path): # don't serve directories
            response_line = self.response_line(200)
            extra_headers = self.server_get_header(path)
            response_headers = self.response_headers(extra_headers)

            with open(path, 'rb') as f:
                response_body = f.read()
        else:
            return self.send_error(404)

        blank_line = b'\r\n'

        response = b''.join([response_line, response_headers, blank_line, response_body])
        return response

    #PUT implementation
    def PUT(self, resource_path, data ): 

        response_line = self.response_line(200)
        extra_headers = self.server_put_header(resource_path)
        response_headers = self.response_headers(extra_headers)
        #basic error checking
        if not data:
            return self.send_error(400)
        else:
            if resource_path == "index.html":
                return self.send_error(405)

        content_type = self.headers['content-type'].split(';')[0]

        #file exsistence
        if os.path.isfile(resource_path):

            if(mimetypes.guess_type(resource_path)[0] in content_type):
                extra_headers = self.server_put_header(resource_path)
                response_headers = self.response_headers(extra_headers)
            else:
                #error - unsupported Media Types
                return self.send_error(415)

        if self.bin_data_flag == 1:
            mode = "wb"
        else:
            mode = "w"
        blank_line = b'\r\n'
        response = b''.join([response_line, response_headers, blank_line])
        #check for exsistence and write permissions
        if self.check_permissions(resource_path, "write"):
            self.write_file(resource_path, data, mode)
            return response
        else:
            return self.send_error(403)

    #DELETE -implementation
    def DELETE(self, resource_path):
		
        a = []
        a.append('<html>\n<body>')
        a.append('<h1> File deleted </h1>')
        a.append('</body>\n</html>')
        message = ("\n").join(a)
        response_body = message.encode()

        #status code 401 - unauthorised
        try:
            if(self.headers['Authorization']):

                auth_type, credentials  =  self.headers['authorization'].split(" ")
                #send only headers don't delete file 
                if auth_type != self.server_auth['type']:
                    response_line = self.response_line(401)
                    extra_headers = self.server_delete_header(401)
                    response_headers = self.response_headers(extra_headers)
                    blank_line = b'\r\n'
                    response = b''.join([response_line, response_headers, blank_line])
                    return response
            
        except(KeyError):
            response_line = self.response_line(401)
            extra_headers = self.server_delete_header(401)
            response_headers = self.response_headers(extra_headers)
            blank_line = b'\r\n'
            response = b''.join([response_line, response_headers, blank_line])
            return response	

        if resource_path == "/":
            if os.path.isfile(self.default_loc["ServerResources"]+ "/" + "index.html"):
                resource_path += "index.html"

        if not os.path.exists(resource_path):
            return self.send_error(404)

        try:
            #deletes the resource
            os.remove(resource_path)

        except(OSError):
            return self.send_error(404)

        response_line = self.response_line(200)
        extra_headers = self.server_delete_header(200)
        response_headers = self.response_headers(extra_headers)
        blank_line = b'\r\n'
        response = b''.join([response_line, response_headers, blank_line,response_body])
        return response	
    
    #HEAD implemntation 
	#sends on the response headers
    def HEAD(self, resource_path):
        response_line = self.response_line(200)
        extra_headers = self.server_get_header(resource_path)
        response_headers = self.response_headers(extra_headers)
        blank_line = b'\r\n'
        response = b''.join([response_line, response_headers, blank_line])
        return response
    
    def send_error(self , status_code):
        response_line = self.response_line(status_code)
        response_headers = self.response_headers()
        body = '<h1>{} {}</h1>'.format(status_code,self.status_codes[status_code])
        response_body = body.encode()
        blank_line = b'\r\n'
        response = b''.join([response_line, response_headers, blank_line, response_body])
        return response

    def current_time(self):
        return time.strftime("%a, %d %b %Y %I:%M:%S", time.gmtime()) + " GMT"

    def write_file(self, resourceURI, data, mode="w"):
        with open(resourceURI, mode) as myfile:
            myfile.write(data)

    #checks for the file permissions	
    def check_permissions(self, resource_path, permission="read"):

        if os.access(resource_path, os.F_OK):
            if(permission == "read-write"):
                return os.access(resource_path, os.R_OK) and os.access(resource_path, os.W_OK)
            if(permission == "read"):
                return 	os.access(resource_path, os.R_OK)
            if(permission == "write"):
                return os.access(resource_path, os.W_OK)
            if(permission == "excecute"):
                return os.access(resource_path, os.X_OK)

