# Import the required libraries
import json
from socket import socket,AF_INET,SOCK_STREAM,SOL_SOCKET,SO_REUSEADDR
from _thread import start_new_thread
import ssl
from urllib.parse import urlparse
import re
from englisttohindi.englisttohindi import EngtoHindi
from bs4 import BeautifulSoup
import os
from datetime import datetime,date,timedelta
import matplotlib.pyplot as plt

# Set the global variables
SERVER_IP = "127.0.0.1"
SERVER_PORT = 8081
json_file_path = "data.json"

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
    Name        : saveUserData()
    Description : Saves the User activity in a .json file with the format
                    {
                        "server_host": "localhost",
                        "server_port": 8080,
                        "server_path": "/hello.html",
                        "is_valid": 1,
                        "date_time": "2023-11-04 19:17:45.616163"
                    }
    Arguments   : The Client Address Details and the request
    Return      : None
    '''
    def saveUserData(self, address, request):

        # Prepare the data to be saved and store it to access using the ip address of the user as the key
        ip, port = address
        date_time = datetime.now()
        request['date_time'] = str(date_time)
        json_data = {}
        key = f'{ip}'

        # Check for existence of file
        if os.path.exists('data.json'):

            # Open the .json file in read mode
            with open('data.json', 'r') as json_file:
                new_data = json.load(json_file)

                # Get data using ip from the previous data and append data to the existing ip data
                get_data = new_data.get(key)
                if get_data:
                    get_data.append(request)
                else:
                    get_data = request
                new_data[key] = get_data

            # Save the new data to the json file
            with open(json_file_path, 'w') as json_file:
                json.dump(new_data, json_file, indent=4)
        
        # Create a new json file and add first data when the file do not exists
        else:
            json_data = {key:[request]}
            with open(json_file_path, 'w') as json_file:
                json.dump(json_data, json_file, indent=4)
        
        # Return
        return

    '''
    Name        : plotGraph()
    Description : Plots and saves User activity in a Graph
    Arguments   : The X and Y axes and the Graph name
    Return      : None
    '''
    def plotGraph(self,x_axis,y_axis,name):
        
        # Plot the graph and set the attributes
        plt.bar(x_axis, y_axis)
        plt.xticks(rotation = 20, ha = 'right')
        plt.savefig(name, dpi = 400)
        plt.close()

        # Return
        return

    '''
    Name        : createGraphData()
    Description : Creates the data to plot User activity in a Graph and invokes plotGraph function
    Arguments   : None
    Return      : None
    '''
    def createGraphData(self):

        # Initialize the required variables
        total_no_of_request, request_made_today, request_made_this_week, request_made_this_month = 0, 0, 0, 0
        today, today_day, one_week, one_month = date.today(), today.day, timedelta(days=7), timedelta(days=30)
        request_by_day = { 'Sunday': 0, 'Monday': 0, 'Tuesday':0, 'Wednesday':0, 'Thursday':0, 'Friday':0, 'Saturday':0 }
        month_names = { 
                        1: "January", 2: "February", 3: "March", 4: "April",
                        5: "May", 6: "June", 7: "July", 8: "August",
                        9: "September", 10: "October", 11: "November", 12: "December"
        }
        request_by_month = {
            'January': 0, 'February': 0, 'March': 0, 'April': 0, 'May': 0, 'June': 0,
            'July': 0, 'August': 0, 'September': 0, 'October': 0, 'November': 0, 'December': 0
        }

        # Check for existence of the file
        if not os.path.exists(json_file_path):
            return
        
        with open(json_file_path, 'r') as json_file:
            
            # Load the json data
            data = json.load(json_file)
            
            for values in data.values():

                # Loop over the requested data in the json file
                for req in values:
                    
                    # Read the variables
                    total_no_of_request += 1
                    get_date = req['date_time'].split(' ')[0]
                    get_day_arr = get_date.split('-')
                    get_day_no = get_day_arr[2]
                    get_month_no = get_day_arr[1]
                    date_time = datetime.strptime(req['date_time'], '%Y-%m-%d %H:%M:%S.%f')
                    
                    # Check if the date in within one week
                    is_within_week = -(date_time.date()-today) < one_week

                    # Check if the date in within one month
                    is_within_month = -(date_time.date()-today) < one_month

                    # If date is of today then increment request_made_today
                    if today_day == int(get_day_no):
                        request_made_today += 1

                    # If date is of within one week then increment request_by_day
                    if is_within_week:
                        request_made_this_week += 1
                        day_of_week = date_time.strftime('%A') 
                        request_by_day[day_of_week] += 1

                    current_month_name = month_names[int(get_month_no)] 
                    request_by_month[current_month_name]+=1

                    # if date is of within one week then increment request_made_this_month
                    if(is_within_month):
                        request_made_this_month+= 1
                
            # call plotGraph function to create graph
            my_axis = list(request_by_month.values())
            mx_axis = list(request_by_month.keys())
            self.plotGraph(mx_axis,my_axis,"request_by_month.png")

            dy_axis = list(request_by_day.values())
            dx_axis = list(request_by_day.keys())
            self.plotGraph(dx_axis,dy_axis,"request_by_day.png")

            tx_axis = ["Today"]
            ty_axis = [request_made_today]
            self.plotGraph(tx_axis,ty_axis,"request_made_today.png")
        
        # Return
        return

    '''
    Name        : convertLanguageInHtml()
    Description : Converts the english language in the html file to hindi
    Arguments   : The HTML Content
    Return      : The translated HTML content
    '''
    def translate(self, html):

        # Create BeautifulSoup object for the html
        soup=BeautifulSoup(html,"html.parser")
        
        # List the tags to be scanned for text conversion
        tag = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'td', 'th', 'span']

        # Get the html element tag
        for headingElemenet in soup.find_all(tag):

            # Get the string from the html tag
            string_value = headingElemenet.string 

            # Convert the english to hindi
            trans = EngtoHindi(message=string_value)
            
            # Replace the english to hindi
            headingElemenet.string = trans.convert

        # Return the translated HTML content
        return str(soup)

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
    def handleClient(self, connection, address, request):

        # Parse the Client request
        parsedRequest = self.parseRequest(request)

        # Save the data to a json file
        self.saveUserData(address, parsedRequest)

        # Forward the Client request to Server and get the response
        response = self.forwardRequest(parsedRequest)

        # Decode the headers
        decoded_headers = response.split(b"\r\n\r\n")[0].decode()
        headers_arr = decoded_headers.split("\r\n")
        headers_content_type = ''
        for element in headers_arr:
            if element:
                if 'content-type:' in element.lower():
                    headers_content_type = element

        # Prepare the translated response
        new_response = response

        # If the response is an html file, then translate from English to Hindi
        if headers_content_type:
            if 'text/html' in headers_content_type:
                body = response[len(decoded_headers) + 4 :].decode()
                body_arr = body.split('\n')
                modified_html = ''
                if body_arr[0].lower() == '<!doctype html>':
                    modified_html = self.translate(body)
                    new_response = (decoded_headers+modified_html).encode()
        
        # Send the translated response to the client through the socket
        connection.sendall(new_response)
        connection.close()

        # Recored the activity
        self.createGraphData()

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
            start_new_thread(self.handleClient, (connection, address, request))
            
# Program Execution begins from here
if __name__== '__main__':
    httpProxy = ProxySever()
    httpProxy.listenClient()