from http.server import HTTPServer, BaseHTTPRequestHandler

hostname= "localhost"
port = 8000
postform = """
<form action="http://{hostname}:{port}" method="POST">
  <input type="text" name="data" value="mydata" />
  <input type="submit" />
</form>
"""
data = {}


class YummyHTTPRequestHandler(BaseHTTPRequestHandler):

    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
    
    def _html(self, content):
        html = "<html><body>{}</body></html>"
        return bytes(html.format(content), "utf-8")

    def _tag(self, tag, content):
        html = "<{tag}>{content}</{tag}>"
        return html.format(tag=tag, content=content)

    def _data(self):
        html = "<table>"
        for k,v in data.items():
            row = "<tr><td>{}</td><td>{}</td></tr>"
            html += row.format(k, v)
        html += "</table>"
        return html

    def _home(self):
        return self._html(
            self._tag("H1", "Yummy!")
            + "</br></br>" 
            + postform.format(hostname = hostname, port = port)
            + "</br></br>" 
            + self._data()
        )

    def _add_input(self, post_data):
        k = len(data)+1
        items = post_data.split("=")
        data[k] = items[1]
        print("post_data = ", post_data)

    def do_GET(self):
        print ("do_GET")
        self._set_headers()
        self.wfile.write(self._home())

    def do_POST(self):
        print ("do_POST")
        self._set_headers()
        content_len = int(self.headers['content-length'])
        post_data = self.rfile.read(content_len)
        self._add_input(post_data.decode("utf-8"))
        self.wfile.write(self._home())

    def do_PUT(self):
        self.do_POST()


httpd = HTTPServer((hostname, port), YummyHTTPRequestHandler)
httpd.serve_forever()