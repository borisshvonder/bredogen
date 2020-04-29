#!/usr/bin/env python3

import http.server
import socketserver
import ssl
import http.client
import urllib.parse
import socket
from shutil import copyfileobj
from lxml import etree
from io import StringIO, BytesIO
import bredogen
import random
import argparse
import sys

# Try to use gevent for light threading (improve performance)
import gevent
from gevent import monkey
monkey.patch_all()

class MyHTTPRequestHandler(http.server.BaseHTTPRequestHandler):
    #protocol_version = 'HTTP/1.1' # allow HTTP/1.1 features

    def handle_one_request(self):
        try:
            self.raw_requestline = self.rfile.readline(65537)
            if len(self.raw_requestline) > 65536:
                self.requestline = ''
                self.request_version = ''
                self.command = ''
                self.send_error(HTTPStatus.REQUEST_URI_TOO_LONG)
                return
            if not self.raw_requestline:
                self.close_connection = True
                return
            if not self.parse_request():
                # An error code has been sent, just exit
                return

            self.custom_handle_request()

            self.wfile.flush() #actually send the response if not already done.
        except socket.timeout as e:
            #a read or a write timed out.  Discard this connection
            self.log_error("Request timed out: %r", e)
            self.close_connection = True
            return

    # Handle all http methods in one function
    def custom_handle_request(self):
        # Get site hostname
        self.sitehost = self.server.sitehost

        # Send request to upstream
        upstream_conn = http.client.HTTPSConnection(self.sitehost)
        upstream_conn.putrequest(self.command, self.path, skip_host=False, skip_accept_encoding=False)
        upstream_connection_close = False
        request_hostname = self.sitehost
        for k,v in list(self.headers.items()):
            if k.lower() == "host":
                request_hostname = v
                continue # skip the Host header
            elif k.lower() == "server":
                self.server_version = v
                continue # skip the Server header too
            elif k.lower() == "connection" and v.lower() == "close":
                upstream_connection_close = True
            upstream_conn.putheader(k, v)
        if not upstream_connection_close:
            # force connection-close for upstream
            upstream_conn.putheader("Connection", "close")
        upstream_conn.endheaders()

        # Receive response headers from upstream
        upstream_resp = upstream_conn.getresponse()
        response_content_length = -1
        response_chunked = False
        response_content_type = ""
        response_content_encoding = None
        upstream_headers = []
        for k,v in upstream_resp.getheaders():
            if k.lower().strip() == 'connection' and v.lower().strip() == 'close':
                self.close_connection = True
            elif k.lower().strip() == 'content-length':
                response_content_length = int(v)
                continue # filter this
            elif k.lower().strip() == "transfer-encoding" and "chunked" in v.lower():
                response_chunked = True
                continue # filter this too
            elif k.lower().strip() == 'content-encoding':
                response_content_encoding = v
                continue # filter this too
            elif k.lower().strip() == 'content-type':
                response_content_type = v
            upstream_headers.append((k,v))

        body = None
        if upstream_resp.status == 200 and "html" in response_content_type.lower():
            if response_chunked:
                body = self.process_html(upstream_resp.read(), request_hostname) # python already implements dechunking internally
                response_content_length = len(body)
                response_content_encoding = None
            elif response_content_length >= 0:
                body = self.process_html(upstream_resp.read(response_content_length), request_hostname)
                response_content_length = len(body)
                response_content_encoding = None

        # Send response headers to the client
        self.send_response(upstream_resp.status, upstream_resp.reason)

        for k,v in upstream_headers:
            self.send_header(k, v)
        # send (possibly updated) content-length to upstream
        if response_content_length >= 0:
            self.send_header("Content-Length", str(response_content_length))
        if response_content_encoding != None:
            self.send_header("Content-Encoding", response_content_encoding)
        self.end_headers()

        if body != None:
            # Send modified body response
            self.wfile.write(body)
        else:
            # Path-through unmodified response body
            copyfileobj(upstream_resp, self.wfile)

    def process_html(self, body, request_hostname):
        parser = etree.HTMLParser()
        tree = etree.parse(BytesIO(body), parser)

        # URL rewriting
        for a in tree.getroot().xpath(".//a"):
            url = a.get('href')
            if url and self.sitehost in url:
                url = url.replace(self.sitehost, request_hostname)
                a.set('href', url)

        for t in tree.getroot().xpath(".//text()"):
            if t.getparent().tag in ("span", "div", "strong", "a", "h1", "h2", "h3", "h4", "p"):
                if t.getparent().text and len(t.getparent().text.strip()) > 0:
                    src = t.getparent().text
                    # Skip all-digit strings
                    if src.lower().strip().replace(':','').replace('.','').replace(';','').isdigit():
                        continue
                    t.getparent().text = bredogen.process(src)

        return etree.tostring(tree.getroot(), pretty_print=True, method="html")

# TODO: use this after logic works with normal http server
class MyHTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True

def main():
    parser = argparse.ArgumentParser(description='Bredogen HTTP(S) proxy (courtesy Borisich)')
    parser.add_argument('-l', '--listen', type=str, default='443', help='listen in the form [ip:]port (default 443)')
    parser.add_argument('-c', '--certfile', type=str, help='')
    parser.add_argument('hostname', type=str, help='site hostname')
    args = parser.parse_args()

    if args.certfile == None:
        sys.stderr.write("error: You must specify --certfile!\n")
        parser.print_usage(sys.stderr)
        sys.exit()

    if ':' in args.listen:
        addr, port = args.listen.split(':', 1)
    else:
        addr, port = '', args.listen
    port = int(port)

    print("Starting HTTPS Server listening on {addr}:{port} certfile='{certfile}' upstream '{hostname}' ...".format(
        addr=addr, port=port, certfile=args.certfile, hostname=args.hostname)
    )

    httpd = MyHTTPServer((addr, port), MyHTTPRequestHandler)
    httpd.socket = ssl.wrap_socket(httpd.socket, certfile = args.certfile, server_side = True, cert_reqs=ssl.CERT_OPTIONAL)
    # Store site hostname on the "server" object, so it is available for request handlers
    httpd.sitehost = args.hostname
    httpd.serve_forever()

if __name__ == '__main__':
        main()

