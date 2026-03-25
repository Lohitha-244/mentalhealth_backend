from http.server import HTTPServer, BaseHTTPRequestHandler

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Pong")

print("Starting pure python ping server on port 8000...")
httpd = HTTPServer(('127.0.0.1', 8000), SimpleHTTPRequestHandler)
httpd.serve_forever()
