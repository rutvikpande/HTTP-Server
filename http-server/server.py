import config as cfg
from socket import *
from client_Threading import client_Thread

clients = [] #list to store connected users
#Server class
class Server():
    '''
        Server 
    '''
    def __init__(self):
        self.server_config = cfg.ServerConfig
        self.server_config["ServerPort"] = 7677
        self.server_auth = cfg.ServerAuth
        self.default_loc = cfg.DefaultLoc 
    
    def closeServer(self):
        for thread in clients:
            thread.join()

    def run_server(self):
        server_socket = socket(AF_INET, SOCK_STREAM)
        server_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1) # to continue connecting on same port
        server_socket.bind(('', self.server_config["ServerPort"]))
        server_socket.listen(self.server_config["ListenConnection"])
        print("server started on port {}".format(self.server_config["ServerPort"]))
        while True:
            try:
                client_socket, client_address = server_socket.accept()
                if(len(clients) == self.server_config["MaxConnections"]):
                    print("Closing. Max limit reached for connections.")
                    client_socket.close()
                    break
                print("server connected to {}".format(client_address))
                New_Client =client_Thread(client_socket, client_address, self) 
                New_Client.start()
                clients.append(New_Client)
            except(KeyboardInterrupt):
                break
        self.closeServer()
        print("\nThank You !\n")


if __name__ == "__main__":
    server_instance = Server()
    server_instance.run_server()
