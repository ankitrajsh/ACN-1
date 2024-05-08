# Import the required libraries
import sys, os
import webbrowser
import requests
from bs4 import BeautifulSoup
from http.client import HTTPConnection

# Initialize global variables
HTTPConnection._http_vsn_str = 'HTTP/1.0'
files = []

'''
When the client is contacting the server directly, this string is null. When the client is contacting 
the proxy sever, the client formats the address and port of the origin server in this string and attaches 
to the filePath as a prefix. The proxy server extracts them from this prefix string.
'''
prefix = ''

'''
Name        : makeGetRequest()
Description : Frames an appropriate HTTP GET request and retreives the object from the server 
Arguments   : Address and port of the server to be contacted and the path of the object to be retreived, in that order
Return      : The received HTTP response
'''
def makeGetRequest(address, port, filePath):
    
    # Declare use of global variable
    global prefix

    # Set the ip type according to the port number
    if port == 443:
        type = 'https'
    else:
        type = "http"
    
    # Format the url of the HTTP GET Request and retreive it
    url = '{}://{}:{}/{}'.format(type, address, port, prefix + filePath)
    response = requests.get(url)

    # Return the HTTP response
    return response

'''
Name        : parseArguments()
Description : Parses the command line arguments and determines the server address, port and the path of the object to be retreived
Arguments   : The list of command line arguments
Return      : The server address, server port and the path to the object, in that order
'''
def parseArguments(arguments):

    # Declare use of global variable
    global prefix

    # If there are only two arguments, they are:
    # a) the address of the origin server
    # b) the port of the origin server
    if len(arguments) == 2:
        address, port, filePath = arguments[0], int(arguments[1]), ''
    
    # If there are three arguments, they are:
    # a) the address of the origin server
    # b) the port of the origin server
    # c) the path to the object to be retreived
    elif len(arguments) == 3:
        address, port, filePath = arguments[0], int(arguments[1]), arguments[2]
    
    # If there are four arguments, they are:
    # a) the address of the proxy server
    # b) the port of the proxy server
    # c) the address of the origin server
    # d) the port of the origin server
    elif len(arguments) == 4:
        if arguments[3] == 443:
            prefix = 'https'
        else:
            prefix = 'http'
        prefix += '://{}:{}'.format(arguments[2], arguments[3])
        address, port, filePath = arguments[0], int(arguments[1]), ''
    
    # If there are five arguments, they are:
    # a) the address of the proxy server
    # b) the port of the proxy server
    # c) the address of the origin server
    # d) the port of the origin server
    # e) the path to the object to be retreived
    elif len(arguments) == 5:
        if arguments[3] == 443:
            prefix = 'https'
        else:
            prefix = 'http'
        prefix += '://{}:{}/'.format(arguments[2], arguments[3])
        address, port, filePath = arguments[0], int(arguments[1]), arguments[4]
    
    # Handle the invalid input format case
    else:
        address, port, filePath = None, None, None
    
    # Return the address and port of the host to be contacted and the file path
    return address, port, filePath

'''
Name        : parseHTML()
Description : Saves the HTML response, parses it for further references and retreives them through non-persistent HTTP connection
Arguments   : The path where the HTML response is to be saved as a file and the HTML response, in that order
Return      : None
'''
def parseHTML(filePath, response):

    # Save the HTML Response in an HTML File
    with open(filePath, 'w') as file:
        file.write(response.content.decode())
        files.append(filePath)
    
    # Parse the HTML file
    with open(filePath, 'r') as file:
        soup = BeautifulSoup(file, 'html.parser')

        # Extract the stylesheets and request the css files
        allCss = soup.findAll('link', href=True)
        for link in allCss:
            stylePath = link.get('href')
            if stylePath.find('.') > -1:
                styleResponse = makeGetRequest(address, port, stylePath)
                local_css_name = stylePath.split("/").pop()
                with open(local_css_name, 'w') as file:
                    file.write(styleResponse.text)
                    files.append(local_css_name)
        
        # Extract the scripts and request the script files
        allScripts = soup.findAll('script')
        for jsTag in allScripts:
            jsSrc = jsTag.get("src")
            if(jsSrc):
                scriptResponse = makeGetRequest(address, port, jsSrc)
                local_js_name = jsSrc.split("/").pop()
                with open(local_js_name, 'w') as file:
                    file.write(scriptResponse.text)
                    files.append(local_js_name)
        
        # Extract the images and request the image files
        if soup.find('img'):
            for imageObject in soup.find_all('img'):
                imagePath = imageObject.get('src')
                imageResponse = makeGetRequest(address, port, imagePath)
                local_img_name = imagePath.split("/").pop()
                with open(local_img_name, 'wb') as file:
                    file.write(imageResponse.content)
                    files.append(local_img_name)
    
    # Return
    return

# Program Execution begins from here
if __name__ == '__main__':

    # Extract the command line arguments and parse them
    arguments = sys.argv[1:]
    address, port, filePath = parseArguments(arguments)

    # Handle the case of inappropriate input format
    if address == None or port == None or filePath == None:
        print('Input not in the expected format. Please go through README.md for reference...!!!')

    else:

        # Retreieve the object using HTTP GET request and store the response
        response = makeGetRequest(address, port, filePath)

        # Set the default HTML file name, if not provided
        if filePath == '':
            filePath = 'index.html'

        # If the HTTP Request is a success, save the response into a file and parse further
        if response.status_code == 200:

            # If the requested file is an HTML object, call the subroutine to parse the response further
            if filePath.endswith('.html'):
                parseHTML(filePath, response)

            # Else, directly save the response into a file
            else:
                with open(filePath, 'wb') as file:
                    file.write(response.content)
                    files.append(filePath)

        # Else, create a file to store the error messae
        else:
            with open('error.html', 'wb') as file:
                file.write(response.content)
                files.append('error.html')
                filePath = 'error.html'

        # Open the response file in a web browser
        webbrowser.open(filePath)

        # Finally, delete all the files created before terminating the program
        for file in files:
            os.remove(file)