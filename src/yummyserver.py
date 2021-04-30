from lib import webserver

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


class YummyHTTPRequestHandler(webserver.HTTPRequestHandler):

    def render_form(self):
        html = """
        <form action="http://{hostname}:{port}" method="POST">
        <input type="text" name="data" value="mydata" />
        <input type="submit" />
        </form>
        """
        return html.format(hostname = self.get_hostname(), port = self.get_port())

    def render_home(self):
        self.wfile.write(
            self.html("YummyServer Home", 
                self.tag("H1", "Yummy!")
                + "<br/>" 
                + self.render_form()
                + "<br/>" 
                + self.render_dict(data),
                YUMMY_STYLE
            )
        )

    def add_input(self, post_data):
        k = len(data)+1
        items = post_data.split("=")
        data[k] = items[1]

    def do_POST(self):
        self.do_headers()
        content_len = int(self.headers['content-length'])
        post_data = self.rfile.read(content_len)
        self.add_input(post_data.decode("utf-8"))
        self.render_home()


if __name__ == '__main__':
    webserver.start_server(YummyHTTPRequestHandler)
