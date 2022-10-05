from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse
from urllib.parse import unquote
import json
import hashlib
import threading
import time

class MCClassicServer:
    def __init__(self, id, ip, port, version, salt, name, public, users, maxusers):
        self.id = id
        self.to_clean = False
        self.ip = ip
        self.port = port
        self.version = version
        self.salt = salt
        self.name = name
        self.public = public
        self.users = users
        self.maxusers = maxusers
        
    def to_html(self):
        html = (
            "<li>" + 
                "<p> ID: " + str(self.id) + " - " + self.name + " (" + self.ip + ":" + str(self.port) + ") (" + 
                str(self.users) + "/" + 
                str(self.maxusers) + ") (Version: " + 
                str(self.version) + ")" + "</p>" + 
            "</li>")
        return html
        
    def to_html_full(self):
        html = (
            "<div>" +
                "<h3>" + self.name + " (" + str(self.id) + ")</h3>" +
                "<p>Players: " + str(self.users) + "/" + str(self.maxusers) + "</p>" +
                "<p>Version: " + str(self.version) + "</p>" +
                "<p>Join at: " + self.ip + ":" + str(self.port) + "</p>" +
            "</div>")
        return html

listenip = "0.0.0.0"
listenport = 80
clean_timeout = 120
url = "http://localhost"
name = "MCClassicServerList"
version = 1.0
webserver = None
is_running = False
registered_servers = [ ]
registered_accounts = { }

def update_servers():
    server_id = 0
    for server in registered_servers:
        server_id += 1
        server.id = server_id

def get_server_by_id(id):
    server_id = 0
    for server in registered_servers:
        server_id += 1
        if server_id == id:
            return server
    return None

class MCClassicServerList(BaseHTTPRequestHandler):
    def do_GET(self):
        request = urlparse(self.path)
        request_query = {}
        
        for query_entry in request.query.split("&"):
            if (len(query_entry.split("=")) < 2):
                continue
            query_entry_key = query_entry.split("=")[0]
            query_entry_value = query_entry.split("=")[1]
            request_query[query_entry_key] = unquote(query_entry_value)
        
        if request.path == "/":
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(bytes(
                "<!Doctype HTML>" +
                "<html>" +
                "<body>", "utf-8"))
            
            self.wfile.write(bytes(
                "<div>" +
                "<h3>" + name + " (" + str(version) + ")</h3>" +
                "</div>", "utf-8"))
            
            if len(registered_servers) >= 1:
                self.wfile.write(bytes("<p>There are " + str(len(registered_servers)) + " servers available</p>", "utf-8"))
                self.wfile.write(bytes("<ul>", "utf-8"))
                for server in registered_servers:
                    if server.public:
                        self.wfile.write(bytes(server.to_html(), "utf-8"))
                self.wfile.write(bytes("</ul>", "utf-8"))
            else:
                self.wfile.write(bytes("<p>There are no servers available</p>", "utf-8"))
                
            self.wfile.write(bytes(
                "</body>" +
                "</html>",
                "utf-8"))
        elif "/view" in request.path and not "/api" in request.path:
            display_invalid_request_page = False
            display_gone_page = False
            display_forbidden_page = False
        
            try:
                server_id = request.path.replace("/view", "", 1).replace("/", "", 1)
            
                if not server_id or not server_id.isdigit():
                    display_invalid_request_page = True
                    display_gone_page = False
                    display_forbidden_page = False
                    raise Exception()
            
                server = get_server_by_id(int(server_id))
                if server == None:
                    display_invalid_request_page = False
                    display_gone_page = True
                    display_forbidden_page = False
                    raise Exception()
            
                if not server.public:
                    display_invalid_request_page = False
                    display_gone_page = False
                    display_forbidden_page = True
                    raise Exception()
            
                self.send_response(200)
                self.send_header("Content-Type", "text/html")
                self.end_headers()
                
                self.wfile.write(bytes(
                    "<!Doctype HTML>" +
                    "<html>" +
                    "<body>" +
                    server.to_html_full() +
                    "</body>" +
                    "</html>",
                    "utf-8"))
            except:
                if display_invalid_request_page:
                    self.send_response(400)
                    self.send_header("Content-Type", "text/html")
                    self.end_headers()
                    self.wfile.write(bytes(
                        "<!Doctype HTML>" +
                        "<html>" +
                        "<body>" +
                        "<h1>400 Bad Request</h1>" +
                        "<p>The performed request could not be understood properly</p>" +
                        "</body>" +
                        "</html>",
                        "utf-8"))
                elif display_gone_page:
                    self.send_response(410)
                    self.send_header("Content-Type", "text/html")
                    self.end_headers()
                    self.wfile.write(bytes(
                        "<!Doctype HTML>" +
                        "<html>" +
                        "<body>" +
                        "<h1>410 Gone</h1>" +
                        "<p>The requested page is no longer available</p>" +
                        "</body>" +
                        "</html>",
                        "utf-8"))
                elif display_forbidden_page:
                    self.send_response(403)
                    self.send_header("Content-Type", "text/html")
                    self.end_headers()
                    self.wfile.write(bytes(
                        "<!Doctype HTML>" +
                        "<html>" +
                        "<body>" +
                        "<h1>403 Forbidden</h1>" +
                        "<p>You are not authorized to view this page</p>" +
                        "</body>" +
                        "</html>",
                        "utf-8"))
                else:
                    self.send_response(500)
                    self.send_header("Content-Type", "text/html")
                    self.end_headers()
                    self.wfile.write(bytes(
                        "<!Doctype HTML>" +
                        "<html>" +
                        "<body>" +
                        "<h1>500 Internal Server Error</h1>" +
                        "<p>The performed request could not be served due to an internal error</p>" +
                        "</body>" +
                        "</html>",
                        "utf-8"))
        elif request.path == "/heartbeat":
            self.protocol_version = "HTTP/0.9"
            display_invalid_request_page = False
        
            try:
                if (not "port" in request_query or 
                    not "version" in request_query or 
                    not "salt" in request_query or
                    not "name" in request_query or
                    not "public" in request_query or
                    not "users" in request_query or
                    not "max" in request_query):
                    display_invalid_request_page = True
                    raise Exception()
            
                ip = self.address_string()
                port = request_query["port"]
                srvversion = request_query["version"]
                salt = request_query["salt"]
                srvname = request_query["name"]
                public = request_query["public"].lower()
                users = request_query["users"]
                maxusers = request_query["max"]
                srvid = len(registered_servers) + 1

                if (not port.isdigit() or
                    not srvversion.isdigit() or
                    not (public == "true" or public == "false") or
                    not users.isdigit() or 
                    not maxusers.isdigit()):
                    display_invalid_request_page = True
                    raise Exception()
                else:
                    updated_existing_entry = False
                    for server in registered_servers:
                        if server.name == srvname:
                            if not server.ip == ip:
                                updated_existing_entry = True
                                self.wfile.write(bytes("You are not allowed to perform this request!", "utf-8"))
                            else:
                                server.to_clean = False
                                server.port = int(port)
                                server.version = int(srvversion)
                                server.salt = salt
                                server.public = True if (public == "true") else False
                                server.users = int(users)
                                server.maxusers = int(maxusers)
                                
                                updated_existing_entry = True
                                update_servers()
                                srvid = server.id
                                self.wfile.write(bytes(url + "/view/" + str(srvid), "utf-8"))
                            break
                
                    if not updated_existing_entry:
                        registered_servers.append(MCClassicServer(srvid, ip, 
                            int(port), 
                            int(srvversion), 
                            salt, 
                            srvname, 
                            True if (public == "true") else False, 
                            int(users), 
                            int(maxusers)))
                        update_servers()
                        self.wfile.write(bytes(url + "/view/" + str(srvid), "utf-8"))
                    print("Heartbeat from " + 
                        ip + ":" + port + 
                        " (ID: " + 
                        str(srvid) + 
                        ", Name: " + 
                        srvname + 
                        ", Version: " + 
                        srvversion + 
                        ", Public: " + 
                        public + 
                        ", Users: " + 
                        users + 
                        ", MaxUsers: " + 
                        maxusers + ")")
            except:
                if display_invalid_request_page:
                    self.wfile.write(bytes("The performed request is invalid!", "utf-8"))
                else:
                    self.wfile.write(bytes("An internal error has occured!", "utf-8"))
        elif request.path == "/api/create_account":
            display_invalid_request_page = False
        
            try:
                if (not "username" in request_query or
                    not "password" in request_query):
                    display_invalid_request_page = True
                    raise Exception()
            
                username = request_query["username"]
                password = request_query["password"]

                if (not username in registered_accounts.keys()):
                    registered_accounts[username] = password
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self.end_headers()
                    self.wfile.write(bytes(json.dumps({ "result": "OK" }), "utf-8"))
                else:
                    self.send_response(403)
                    self.send_header("Content-Type", "application/json")
                    self.end_headers()
                    self.wfile.write(bytes(json.dumps({ "error": { "message": "Forbidden", "code": 403 } }), "utf-8"))
            except Exception as ex:
                if display_invalid_request_page:
                    self.send_response(400)
                    self.send_header("Content-Type", "application/json")
                    self.end_headers()
                    self.wfile.write(bytes(json.dumps({ "error": { "message": "Invalid Request", "code": 400 } }), "utf-8"))
                else:
                    self.send_response(500)
                    self.send_header("Content-Type", "application/json")
                    self.end_headers()
                    self.wfile.write(bytes(json.dumps({ "error": { "message": "Internal Error", "code": 500 } }), "utf-8"))
        elif request.path == "/api/delete_account":
            display_invalid_request_page = False
        
            try:
                if (not "username" in request_query or
                    not "password" in request_query):
                    display_invalid_request_page = True
                    raise Exception()
            
                username = request_query["username"]
                password = request_query["password"]

                if (username in registered_accounts.keys() and 
                    registered_accounts[username] == password):
                    del registered_accounts[username]
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self.end_headers()
                    self.wfile.write(bytes(json.dumps({ "result": "OK" }), "utf-8"))
                else:
                    self.send_response(403)
                    self.send_header("Content-Type", "application/json")
                    self.end_headers()
                    self.wfile.write(bytes(json.dumps({ "error": { "message": "Forbidden", "code": 403 } }), "utf-8"))
            except Exception as ex:
                if display_invalid_request_page:
                    self.send_response(400)
                    self.send_header("Content-Type", "application/json")
                    self.end_headers()
                    self.wfile.write(bytes(json.dumps({ "error": { "message": "Invalid Request", "code": 400 } }), "utf-8"))
                else:
                    self.send_response(500)
                    self.send_header("Content-Type", "application/json")
                    self.end_headers()
                    self.wfile.write(bytes(json.dumps({ "error": { "message": "Internal Error", "code": 500 } }), "utf-8"))
        elif request.path == "/api/mppass":
            display_invalid_request_page = False
        
            try:
                if (not "username" in request_query or
                    not "password" in request_query or
                    not "serverip" in request_query or
                    not "serverport" in request_query):
                    display_invalid_request_page = True
                    raise Exception()
            
                username = request_query["username"]
                password = request_query["password"]
                serverip = request_query["serverip"]
                serverport = request_query["serverport"]
                
                if not serverport.isdigit():
                    display_invalid_request_page = True
                    raise Exception()
                
                targetserver = None
                for server in registered_servers:
                    if server.ip == serverip and server.port == int(serverport):
                        targetserver = server
                        break
                
                if targetserver == None:
                    display_invalid_request_page = True
                    raise Exception()
                
                if (not username in registered_accounts.keys() or 
                    not password == registered_accounts[username]):
                    self.send_response(403)
                    self.send_header("Content-Type", "application/json")
                    self.end_headers()
                    self.wfile.write(bytes(json.dumps({ "error": { "message": "Forbidden", "code": 403 } }), "utf-8"))
                else:
                    mpass = hashlib.md5(bytes(targetserver.salt + username, "utf-8")).hexdigest()
                    
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self.end_headers()
                    self.wfile.write(bytes(json.dumps({ "result": mpass }), "utf-8"))
            except Exception as ex:
                if display_invalid_request_page:
                    self.send_response(400)
                    self.send_header("Content-Type", "application/json")
                    self.end_headers()
                    self.wfile.write(bytes(json.dumps({ "error": { "message": "Invalid Request", "code": 400 } }), "utf-8"))
                else:
                    self.send_response(500)
                    self.send_header("Content-Type", "application/json")
                    self.end_headers()
                    self.wfile.write(bytes(json.dumps({ "error": { "message": "Internal Error", "code": 500 } }), "utf-8"))
        elif "/api/view" in request.path:
            display_invalid_request_page = False
            display_gone_page = False
            display_forbidden_page = False
        
            try:
                server_id = request.path.replace("/api/view", "", 1).replace("/", "", 1)
            
                if not server_id or not server_id.isdigit():
                    display_invalid_request_page = True
                    display_gone_page = False
                    display_forbidden_page = False
                    raise Exception()
            
                server = get_server_by_id(int(server_id))
                if server == None:
                    display_invalid_request_page = False
                    display_gone_page = True
                    display_forbidden_page = False
                    raise Exception()
            
                if not server.public:
                    display_invalid_request_page = False
                    display_gone_page = False
                    display_forbidden_page = True
                    raise Exception()
            
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                
                self.wfile.write(bytes(json.dumps({ "result": { 
                    "name": server.name, 
                    "users": server.users, 
                    "maxusers": server.maxusers,
                    "version": server.version,
                    "ip": server.ip,
                    "port": server.port } }), "utf-8"))
            except:
                if display_invalid_request_page:
                    self.send_response(400)
                    self.send_header("Content-Type", "application/json")
                    self.end_headers()
                    self.wfile.write(bytes(json.dumps({ "error": { "message": "Invalid Request", "code": 400 } }), "utf-8"))
                elif display_gone_page:
                    self.send_response(410)
                    self.send_header("Content-Type", "application/json")
                    self.end_headers()
                    self.wfile.write(bytes(json.dumps({ "error": { "message": "Page no longer exists", "code": 410 } }), "utf-8"))
                elif display_forbidden_page:
                    self.send_response(403)
                    self.send_header("Content-Type", "application/json")
                    self.end_headers()
                    self.wfile.write(bytes(json.dumps({ "error": { "message": "Forbidden", "code": 403 } }), "utf-8"))
                else:
                    self.send_response(500)
                    self.send_header("Content-Type", "application/json")
                    self.end_headers()
                    self.wfile.write(bytes(json.dumps({ "error": { "message": "Internal Error", "code": 500 } }), "utf-8"))
        else:
            self.send_response(404)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(bytes(
                "<!Doctype HTML>" +
                "<html>" +
                "<body>" +
                "<h1>404 Not Found</h1>" +
                "<p>The requested page was not found</p>" +
                "</body>" +
                "</html>",
                "utf-8"))
        
        self.wfile.flush()
        self.close_connection = True
    def do_POST(self):
        request = urlparse(self.path)
        request_data = self.rfile.read(int(self.headers["Content-Length"]))
        request_query = {}
        
        for query_entry in request_data.decode("utf-8").split("&"):
            if (len(query_entry.split("=")) < 2):
                continue
            query_entry_key = query_entry.split("=")[0]
            query_entry_value = query_entry.split("=")[1]
            request_query[query_entry_key] = unquote(query_entry_value)
            
        if request.path == "/heartbeat":
            display_invalid_request_page = False
        
            try:
                if (not "port" in request_query or 
                    not "version" in request_query or 
                    not "salt" in request_query or
                    not "name" in request_query or
                    not "public" in request_query or
                    not "users" in request_query or
                    not "max" in request_query):
                    display_invalid_request_page = True
                    raise Exception()
            
                ip = self.address_string()
                port = request_query["port"]
                srvversion = request_query["version"]
                salt = request_query["salt"]
                srvname = request_query["name"]
                public = request_query["public"].lower()
                users = request_query["users"]
                maxusers = request_query["max"]
                srvid = len(registered_servers) + 1

                if (not port.isdigit() or
                    not srvversion.isdigit() or
                    not (public == "true" or public == "false") or
                    not users.isdigit() or 
                    not maxusers.isdigit()):
                    display_invalid_request_page = True
                    raise Exception()
                else:
                    updated_existing_entry = False
                    for server in registered_servers:
                        if server.name == srvname:
                            if not server.ip == ip:
                                updated_existing_entry = True
                                self.send_response(403)
                                self.send_header("Content-Type", "text/html")
                                self.end_headers()
                                self.wfile.write(bytes(
                                    "<!Doctype HTML>" +
                                    "<html>" +
                                    "<body>" +
                                    "<h1>403 Forbidden</h1>" +
                                    "<p>You are not authorized to view this page</p>" +
                                    "</body>" +
                                    "</html>",
                                    "utf-8"))
                            else:
                                server.to_clean = False
                                server.port = int(port)
                                server.version = int(srvversion)
                                server.salt = salt
                                server.public = True if (public == "true") else False
                                server.users = int(users)
                                server.maxusers = int(maxusers)
                                
                                updated_existing_entry = True
                                update_servers()
                                srvid = server.id
                                self.send_response(200)
                                self.send_header("Content-Type", "text/plain")
                                self.end_headers()
                                self.wfile.write(bytes(url + "/view/" + str(srvid), "utf-8"))
                            break
                
                    if not updated_existing_entry:
                        registered_servers.append(MCClassicServer(srvid, ip, 
                            int(port), 
                            int(srvversion), 
                            salt, 
                            srvname, 
                            True if (public == "true") else False, 
                            int(users), 
                            int(maxusers)))
                        update_servers()
                        self.send_response(200)
                        self.send_header("Content-Type", "text/plain")
                        self.end_headers()
                        self.wfile.write(bytes(url + "/view/" + str(srvid), "utf-8"))
                    print("Heartbeat from " + 
                        ip + ":" + port + 
                        " (ID: " + 
                        str(srvid) + 
                        ", Name: " + 
                        srvname + 
                        ", Version: " + 
                        srvversion + 
                        ", Public: " + 
                        public + 
                        ", Users: " + 
                        users + 
                        ", MaxUsers: " + 
                        maxusers + ")")
            except:
                if display_invalid_request_page:
                    self.send_response(400)
                    self.send_header("Content-Type", "text/html")
                    self.end_headers()
                    self.wfile.write(bytes(
                        "<!Doctype HTML>" +
                        "<html>" +
                        "<body>" +
                        "<h1>400 Bad Request</h1>" +
                        "<p>The performed request could not be understood properly</p>" +
                        "</body>" +
                        "</html>",
                        "utf-8"))
                else:
                    self.send_response(500)
                    self.send_header("Content-Type", "text/html")
                    self.end_headers()
                    self.wfile.write(bytes(
                        "<!Doctype HTML>" +
                        "<html>" +
                        "<body>" +
                        "<h1>500 Internal Server Error</h1>" +
                        "<p>The performed request could not be served due to an internal error</p>" +
                        "</body>" +
                        "</html>",
                        "utf-8"))
        else:
            self.send_response(404)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(bytes(
                "<!Doctype HTML>" +
                "<html>" +
                "<body>" +
                "<h1>404 Not Found</h1>" +
                "<p>The requested page was not found</p>" +
                "</body>" +
                "</html>",
                "utf-8"))
        
        self.wfile.flush()
        self.close_connection = True
def cleanup_thread_func():
    while is_running:
        for i in range(int(round(clean_timeout / 2))):
            if is_running:
                time.sleep(1)
            else:
                return

        print("Cleaning inactive servers...")
        for server in registered_servers:
            if not server.to_clean:
                server.to_clean = True
            else:
                print("Removed " + server.ip + ":" + str(server.port) + " due to no update in " + str(clean_timeout) + "s")
                registered_servers.remove(server)
                update_servers()
        print("Cleaned inactive servers!")
if __name__ == "__main__":
    print("Starting...")
    webserver = HTTPServer((listenip, listenport), MCClassicServerList)
    cleanup_thread = threading.Thread(target=cleanup_thread_func)
    
    is_running = True
    cleanup_thread.start()
    print("Started!")
    print("Listening on " + listenip + ":" + str(listenport))
    
    try:
        webserver.serve_forever()
    except KeyboardInterrupt:
        pass

    print("Exiting...")
    is_running = False
    webserver.server_close()
