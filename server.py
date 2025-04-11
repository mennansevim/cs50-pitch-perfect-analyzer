import http.server
import socketserver

PORT = 8000

Handler = http.server.SimpleHTTPRequestHandler

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"Web sunucusu http://localhost:{PORT} adresinde başlatıldı")
    httpd.serve_forever() 