from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib

class MyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # This will be called, when the radio tries to retrieve the m3u from p.flowlive.com
        # after finishing the handshake and everything with radio.thelounge.com.
        # It will be answered, no matter which m3u it requests with hochschulradio-aachen m3u for me
        parsed = urllib.urlparse(self.path)
        query_string = parsed.query
        path = parsed.path
        print(f"query_string: {query_string}, path: {path}")
        if 'm3u' in path: #'/r/27/84/8427.m3u':
            # send 200 response
            self.send_response(200)
            # add our own custom header
            self.send_header("myheader", "myvalue") # superfluous?
            # send response headers
            self.end_headers()
            # send the body of the response
            self.wfile.write(bytes("#EXTM3U\n", "utf-8"))
            self.wfile.write(bytes("#EXT-IMG-INF:IS-PLAYLIST=TRUE,StreamFormat=SHOUTCAST/SHOUTCAST,AudioFormat=MP3,Bitrate=128\n", "utf-8"))
            self.wfile.write(bytes("http://evans.hochschulradio.rwth-aachen.de:8000/hoeren/high.m3u\n", "utf-8"))

    def do_POST(self):
        # read the content-length header
        content_length = int(self.headers.get("Content-Length"))
        # read that many bytes from the body of the request
        post_data = self.rfile.read(content_length)
        print(f"post_data: {post_data}")
        post_data_str = urllib.parse.unquote(post_data) # decode url byte str to str
        credential, register = None, None
        if 'X_Login' in post_data_str:
            try:
                credential = post_data_str.split('pure:CredentialObject=')[1]
                credential = credential.split('&pure:MAC=')[0].strip()
                print(f'credential: {credential} len(credential): {len(credential)}')
            except IndexError:
                print("Credential is not in POST, Skip")
        elif 'X_RegisterDevice' in post_data_str:
            #deviceobject = post_data.split('pure:DeviceObject=')[1]
            pass # TODO: unclear what this action does, just saw that request from the radio when the key/credential was not working
        else:
            print(f'Unknown action, please add this to the code:{post_data_str}')
        #self._set_headers()

        # construct header:
        self.send_response(200)
        self.send_header("Content-type", 'text/xml; charset=UTF-8')
        #self.send_header("Content-Length", 427), #content_length)
        self.send_header("Connection", "keep-alive")
        self.send_header("Cache-Control", "private")
        self.send_header("Accept-Ranges", "bytes")
        self.send_header("Ext", "")
        self.send_header("X-Powered-By", "ASP.NET")
        self.end_headers()

        data = []
        if credential is not None:
            if len(credential) == 128:
                 # first phase of key handshake, where the radio sends us a 128 char key
                 static_key = 'k+suO3y/h9YhWx9rYsfCNDKh3KXFceUkiSsuGzcf6nW9cfqWVCpPioqGqDOmntTS' # respond with static key 64 chars long: it is not getting accepted by Siesta Flow for now. needs to be calculated via the right (yet to determine) method
                 self.send_header("Content-Length", 427), #TODO: replace static length
                 data.append(b'<?xml version="1.0"  encoding="utf-8" ?>')
                 data.append(b'<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/" xmlns:pure="http://pure.com/portal/soap">')
                 data.append(b'<s:Body>')
                 data.append(b'<u:X_LoginResponse xmlns:u="urn:schemas-upnp-org:service:ContentDirectory:1">')
                 #data.append(b'<pure:Response>k+suO3y/h9YhWx9rYsfCNDKh3KXFceUkiSsuGzcf6nW9cfqWVCpPioqGqDOmntTS</pure:Response>')
                 data.append(b'<pure:Response>{0}</pure:Response>'.format(static_key))
                 data.append(b'</u:X_LoginResponse>')
                 data.append(b'</s:Body>')
                 data.append(b'</s:Envelope>')
            elif len(credential) == 140:
                 # second phase of key handshake, just respond with something which looks like a simple "OK"
                 self.send_header("Content-Length", 312), #TODO: replace static length
                 data.append(b'<?xml version="1.0"  encoding="utf-8" ?>')
                 data.append(b'<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/" xmlns:pure="http://pure.com/portal/soap">')
                 data.append(b'<s:Body>')
                 data.append(b'<u:X_LoginResponse xmlns:u="urn:schemas-upnp-org:service:ContentDirectory:1">')
                 data.append(b'</u:X_LoginResponse>')
                 data.append(b'</s:Body>')
                 data.append(b'</s:Envelope>')
        if data:
            for elem in data:
                self.wfile.write(bytes(elem))

        # echo the body in the response
        #self.wfile.write(body)

httpd = HTTPServer(('127.0.0.1', 80), MyHandler) # or replace with your internal IP
httpd.serve_forever()
