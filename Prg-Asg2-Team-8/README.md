
# Programming Assignment 2 : World Wide Web

The purpose of this WWW assignment is to learn about Web clients, Web servers, Web proxies and the HyperText Transfer Protocol (HTTP).

## Aim :

* To develop a Simple Web Client which will connect to the web server directly or through the intermediate web proxy using a TCP connection, send HTTP GET requests to the server and display the server responses as output.
* To implement and test a Simple Web Proxy that is able to parse, understand and forward to the Web server a (possibly modified) version of the client request. Similarly, the proxy should be able to parse, understand, and return to the client a (possibly modified) version of the response that the Web server provided to the proxy.
* To develop a multi-threaded web server that handles multiple HTTP requests simultaneously from your own web client(s), web browsers and proxy server.
* To develop an Extended Proxy Server that accepts URL requests from the web browser, get the response from the respective web server, translate the response message to Hindi and send the translated page to the web browser.
## Features

* The Server accepts multiple HTTP requests from various clients and serves them through threads
* The Client can request html files, pdf files, image files and text files from Server and open it in a browser
* When the client receives a html file, it parses the file and retrieves all further references using non-persistent HTTP connection
* The Proxy Server can accept multiple requests from various clients, parse it, modify it and forward it to the origin server. After receiving the response from the origin server, it modifies it and returns back to the client
* The Extended Proxy Server can translate the text inside an HTML file from English to Hindi before returning the response back to client. 
* Also, the Extended Proxy Server can keep track of the users that request various files from various servers through this extended proxy server and represent it using plots.
## Pre-Execution Steps :

Execute the following commands before running the program.

1. Create a virtual environment in python (assuming python 3 is installed)
```bash
python3 -m venv .venv
```

2. Install the requests module
```bash
pip install requests
```

3. Install the Beautiful Soup module
```bash
pip install beautifulsoup4
```

4. Install the englisttohindi module
```bash
pip install englisttohindi
```

5. Install the ssl module
```bash
pip install ssl
```

6. Install the matplotlib module
```bash
pip install matplotlib
```
## Execution Steps :

1. If the file is to be fetched from Server, run Server.py in a new terminal
```bash
python3 Server.py
```

2. If the file is to be fetched through Proxy Server as intermediate, run Proxy.py in a new terminal
```bash
python3 Proxy.py
```

3. If the file is to be fetched through Extended Proxy Server as intermediate, run ExtendedProxy.py in a new terminal
```bash
python3 ExtendedProxy.py
```

4. If the file is to be fetched from external website directly, run Client.py in a new terminal
```bash
python3 Client.py <website_address> 80
```

5. If the file is to be fetched from Server directly, run Client.py in a new terminal
```bash
python3 Client.py 127.0.0.1 8080 <file_path>
```

6. If the file is to be fetched from external website through Proxy or Extended Proxy, run Client.py in a new terminal
```bash
python3 Client.py 127.0.0.1 8081 <website_address> 80
```

7. If the file is to be fetched from Server through Proxy or Extended Proxy, run Client.py in a new terminal
```bash
python3 Client.py 127.0.0.1 8081 127.0.0.1 8080 <file_path>
```

### Note :
* Replace *<website_address>* and *<file_path>* with input of your choice.
* Make sure that the input falls into one of the above cases.