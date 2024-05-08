# Import the required libraries
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler

# Set the server address and port
address = '127.0.0.1'
port = 8080

# Initialize the server
server = ThreadingHTTPServer((address, port), SimpleHTTPRequestHandler)

# Start the server functioning
server.serve_forever()