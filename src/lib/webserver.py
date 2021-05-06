from http.server import HTTPServer, BaseHTTPRequestHandler

BASIC_STYLE = """
body {
    color: black;
    background-color: white;
}
"""

class HtmlComposer:
    def html(self, title, body, style=BASIC_STYLE):
        html = """
        <html>
            <head><style>{style}</style></head>
            <body title='{title}'>{body}</body>
        </html>
        """
        return bytes(html.format(style=style, title=title, body=body), "utf-8")

    def tag(self, tag, content):
        html = "<{tag}>{content}</{tag}>"
        return html.format(tag=tag, content=content)

    def render_dict(self, dict):
        html = "<table>"
        for k,v in dict.items():
            row = "<tr><td>{}</td><td>{}</td></tr>"
            html += row.format(k, v)
        html += "</table>"
        return html

class HTTPRequestHandler(BaseHTTPRequestHandler, HtmlComposer):

    def get_hostname(self):
        return self.server.server_address[0]

    def get_port(self):
        return self.server.server_address[1]

    def do_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def render_home(self):
        self.wfile.write(
            self.html("Title", self.tag("H1", "Home")))

    def get_data(self, post_data):
        items = post_data.split("=")
        return (items[0],items[1])

    def do_GET(self):
        self.do_headers()
        self.render_home()

    def do_POST(self):
        self.do_headers()
        content_len = int(self.headers['content-length'])
        post_data = self.rfile.read(content_len)
        key, value = self.get_data(post_data.decode("utf-8"))
        output = "{} = {}"
        self.wfile.write(
            self.html("Title", self.tag("H1", "Home") + "<br/>" + output.format(key, value)))

    def do_PUT(self):
        self.do_POST()

DEFAULT_HOSTNAME= "localhost"
DEFAULT_PORT = 8000

def start_server(handler_class=HTTPRequestHandler, hostname=DEFAULT_HOSTNAME, port=DEFAULT_PORT):
    httpd = HTTPServer((hostname, port), handler_class)
    httpd.serve_forever()

if __name__ == '__main__':
    start_server(HTTPRequestHandler)
