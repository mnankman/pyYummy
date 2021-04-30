from http.server import HTTPServer, BaseHTTPRequestHandler

HOSTNAME= "localhost"
PORT = 8000

BASIC_STYLE = """
body {
    color: black;
    background-color: white;
}
"""

YUMMY_STYLE = """
body {
    font-family: Arial, Helvetica, sans-serif;
    color: blue;
    background-color: #cccccc;
}
h1   {color: blue;}
table, th, td {
    border-collapse: collapse;
    border: 1px solid black;
}
"""


data = {}

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

class YummyHTTPRequestHandler(BaseHTTPRequestHandler, HtmlComposer):

    def do_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def render_form(self, hostname, port):
        html = """
        <form action="http://{hostname}:{port}" method="POST">
        <input type="text" name="data" value="mydata" />
        <input type="submit" />
        </form>
        """
        return html.format(hostname = hostname, port = port)

    def render_home(self):
        self.wfile.write(
            self.html("YummyServer Home", 
                self.tag("H1", "Yummy!")
                + "<br/>" 
                + self.render_form(HOSTNAME, PORT)
                + "<br/>" 
                + self.render_dict(data),
                YUMMY_STYLE
            )
        )

    def add_input(self, post_data):
        k = len(data)+1
        items = post_data.split("=")
        data[k] = items[1]

    def do_GET(self):
        self.do_headers()
        self.render_home()

    def do_POST(self):
        self.do_headers()
        content_len = int(self.headers['content-length'])
        post_data = self.rfile.read(content_len)
        self.add_input(post_data.decode("utf-8"))
        self.render_home()

    def do_PUT(self):
        self.do_POST()


httpd = HTTPServer((HOSTNAME, PORT), YummyHTTPRequestHandler)
httpd.serve_forever()