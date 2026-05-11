"""
WebApp — lightweight web server framework for MicroPython (ESP32).

Hides all the HTTP / socket complexity so you can focus on your
robot logic.  Just create an app, register routes, and call run().

Example
-------
    from web_server import WebApp
    import machine, json

    app = WebApp("control.html")      # HTML file served at "/"

    motor = machine.PWM(machine.Pin(5))

    @app.route("/motor")
    def set_motor(params):
        speed = int(params.get("speed", "0"))
        motor.duty(speed)
        return {"speed": speed}         # ← sent back as JSON

    app.run()                            # blocks forever
"""

import socket
import json


class WebApp:
    """Tiny web-application server for MicroPython.

    Parameters
    ----------
    html_file : str
        Path to the HTML page served at ``/`` (and ``/index.html``).
        Resolved relative to the *calling script* when you pass a plain
        filename like ``"control.html"`` — just keep the HTML next to your
        ``.py`` file.
    port : int
        TCP port to listen on (default 80).
    """

    def __init__(self, html_file, port=80):
        self._html_file = html_file
        self._port = port
        self._routes = {}

    # ── route registration ──────────────────────────────────────

    def route(self, path):
        """Decorator – register *func* as the handler for *path*.

        The handler receives a ``dict`` of query-string parameters and
        must return a ``dict`` (sent as JSON), a ``str`` (sent as plain
        text), or ``None`` (empty 200 OK).

        Example::

            @app.route("/led")
            def led(params):
                state = params.get("state", "off")
                pin.value(1 if state == "on" else 0)
                return {"on": state == "on"}
        """
        def _decorator(func):
            self._routes[path] = func
            return func
        return _decorator

    def add_route(self, path, handler):
        """Register a route handler without decorator syntax.

        Useful when defining handlers in a loop or from a data structure.
        """
        self._routes[path] = handler

    # ── response helpers (class methods so handlers can use them) ─

    @staticmethod
    def send_json(cl, data, code="200 OK"):
        """Send a dict as a JSON response."""
        body = json.dumps(data)
        cl.send("HTTP/1.1 {}\r\nContent-Type: application/json\r\nAccess-Control-Allow-Origin: *\r\nConnection: close\r\n\r\n".format(code))
        cl.send(body)

    @staticmethod
    def send_text(cl, text, code="200 OK"):
        """Send a plain-text response."""
        cl.send("HTTP/1.1 {}\r\nContent-Type: text/plain\r\nConnection: close\r\n\r\n".format(code))
        cl.send(text)

    @staticmethod
    def send_file(cl, filepath):
        """Stream a file to the client in 1 KB chunks (saves RAM)."""
        cl.send("HTTP/1.1 200 OK\r\nContent-Type: text/html\r\nConnection: close\r\n\r\n")
        with open(filepath, "r") as f:
            while True:
                chunk = f.read(1024)
                if not chunk:
                    break
                cl.send(chunk)

    # ── internal helpers ────────────────────────────────────────

    @staticmethod
    def _parse_qs(qs):
        """Parse a query string into a dict."""
        params = {}
        if not qs:
            return params
        for part in qs.split("&"):
            if "=" in part:
                k, v = part.split("=", 1)
                params[k] = v
        return params

    # ── main loop ───────────────────────────────────────────────

    def run(self):
        """Start the web server — **blocks forever**.

        Listens for HTTP requests, matches the path against registered
        routes, and calls the appropriate handler.  ``/`` and
        ``/index.html`` always serve the HTML file passed to the
        constructor.
        """
        addr = socket.getaddrinfo("0.0.0.0", self._port)[0][-1]
        s = socket.socket()
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(addr)
        s.listen(3)
        print("WebApp listening on :{}".format(self._port))

        while True:
            cl = None
            try:
                cl, _remote = s.accept()
                cl.settimeout(5)
                request = cl.recv(1024).decode("utf-8")
                if not request:
                    cl.close()
                    continue

                first_line = request.split("\r\n")[0]
                method, path_full = first_line.split()[:2]
                path = path_full.split("?")[0]
                qs = path_full.split("?")[1] if "?" in path_full else ""
                params = self._parse_qs(qs)

                print("{} {}".format(method, path_full))

                # ── Serve the HTML page ─────────────────────────
                if path == "/" or path == "/index.html":
                    self.send_file(cl, self._html_file)

                # ── Registered API routes ───────────────────────
                elif path in self._routes:
                    result = self._routes[path](params)
                    if isinstance(result, dict):
                        self.send_json(cl, result)
                    elif isinstance(result, str):
                        self.send_text(cl, result)
                    else:
                        cl.send("HTTP/1.1 200 OK\r\nConnection: close\r\n\r\n")

                # ── 404 ─────────────────────────────────────────
                else:
                    self.send_text(cl, "Not Found", "404 Not Found")

            except Exception as e:
                print("Error:", e)
                if cl:
                    try:
                        self.send_text(cl, str(e), "500 Internal Server Error")
                    except:
                        pass
            finally:
                if cl:
                    try:
                        cl.close()
                    except:
                        pass
