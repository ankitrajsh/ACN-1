# Import the required libraries
from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
from _thread import start_new_thread
import ssl
from urllib.parse import urlparse
import re

# Set the global variables
SERVER_IP = '127.0.0.1'
SERVER_PORT = 8081

# Define the Proxy Server class
class ProxySever():

    '''
    Name        : __init__()
    Description : Initiates the Proxy Server by defining the TCP socket 
    Arguments   : None
    Return      : None
    '''
    def __init__(self):
        self.proxyServer = socket(AF_INET, SOCK_STREAM)
        self.proxyServer.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.proxyServer.bind((SERVER_IP, SERVER_PORT))
        self.proxyServer.listen(5)
        pass

    '''
    Name        : forwardRequest()
    Description : Modifies the Client HTTP Request if required and forwards it to the server 
    Arguments   : The Client HTTP Request
    Return      : The HTTP Response
    '''
    def forwardRequest(self, request):

        # Create a TCP Socket and connect to the server
        server = socket(AF_INET, SOCK_STREAM)
        server.connect((request['server_host'], request['server_port']))

        # Handle the case of https
        if request['server_port'] == 443:
            context =ssl.create_default_context()
            server = context.wrap_socket(server, server_hostname = request['server_host'])

        # Frame the GET Request and send it through the socket
        url = 'GET {} HTTP/1.0\r\nHOST: {}\r\n\r\n'.format(request['server_path'], request['server_host'])
        server.sendall(url.encode())
        server.settimeout(5)
        
        # Receieve the response from the socket
        response = b''
        try:
            while True:
                data = server.recv(4096)
                response += data
                if not data:
                    server.close()
                    break
            
            # Decode and analyse the header of the response received
            header = response.split(b"\r\n\r\n")[0]
            decoded_header = header.decode()
            status_code = decoded_header.split("\r\n")[0].split(" ")[1]
            
            # Handle the cases of unsuccessful responses
            if status_code == '404' or status_code == '304' or (300 >=  int(status_code) and int(status_code) < 400):
               pass

            # Modify the response
            body = response[len(header) + 4 :]
            decoded_header = decoded_header + '\r\nproxy_ip_addr: {}\r\nproxy_port: {}\r\n\r\n'.format(SERVER_IP, SERVER_PORT)
            modified_response = decoded_header.encode() + body 
        
        # Handle the exception occurred while receiving the response 
        except Exception as e:
            print('Exception {}'.format(e))
            server.settimeout(0)
            modified_response = b'HTTP/1.0 404 File not found\r\n' 
        
        # Return the response
        return modified_response

    '''
    Name        : parseRequest()
    Description : Parses the Client HTTP Request
    Arguments   : The Client HTTP Request
    Return      : The parsed details of the Client HTTP Request
    '''
    def parseRequest(self, request):

        # Define the URL Details
        urlDetails = {'server_host' : '', 'server_port' : 0, 'server_path' : '/', 'is_valid' : 0}
        
        # Extract the URL
        url_arr = request.split('\r\n')
        server_url_str = url_arr[0].split(" ")
        url = server_url_str[1][1:]

        # Handle the case of https
        if url.split(':')[-1] == '443' and url[:4] != 'http':
            url = url[:4] + 's' + url[4:]
        
        # Parse the URL using the urlparse module and store the details
        parsedURL = urlparse(url)
        if parsedURL.scheme and parsedURL.netloc:
            urlDetails['server_host'] = parsedURL.hostname
            urlDetails['server_port'] = 80
            if parsedURL.scheme == "https":
                urlDetails['server_port'] = 443
            if parsedURL.path:
                urlDetails['server_path'] =  parsedURL.path
            urlDetails['is_valid'] = 1
            get_port_regex =re.findall(r':\d+', url)
            if(get_port_regex):
                if(get_port_regex[0][0]==':' and get_port_regex[0][1:].isdigit()):
                    urlDetails['server_port'] = int(get_port_regex[0][1:])
        
        # Return the URL Details
        return urlDetails

    '''
    Name        : handleClient()
    Description : Handles the Client Request in a separate thread
    Arguments   : The Client Connection and Request
    Return      : None
    '''
    def handleClient(self, connection, request):

        # Parse the Client request
        parsedRequest = self.parseRequest(request)
        
        # Forward the Client request to Server and get the response
        response = self.forwardRequest(parsedRequest)

        # Send the response to the client through the socket connection and close the connection
        connection.sendall(response)
        connection.close()

        # Return
        return

    '''
    Name        : listenClient()
    Description : Listens to the proxy server socket and creates a new thread for every client request
    Arguments   : None
    Return      : None
    '''
    def listenClient(self):
        while True:
            connection, address = self.proxyServer.accept()
            request = connection.recv(4096).decode('latin-1')
            start_new_thread(self.handleClient, (connection, request))

# Program Execution begins from here
if __name__== '__main__':
    httpProxy = ProxySever()
    httpProxy.listenClient()