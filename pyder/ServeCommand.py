"""ServeCommand: Implements "serve" command"""

import os
import SimpleHTTPServer
import SocketServer

from . import CommandBase


class ServeCommand(CommandBase):
    """Serve the website"""

    _name = "serve"

    def run(self):
        self.debug("Serving website from {} on port {}".format(
                self.args.dest_dir,
                self.args.port))
        os.chdir(self.args.dest_dir)
        handler = SimpleHTTPServer.SimpleHTTPRequestHandler
        SocketServer.allow_reuse_address = True
        server = SocketServer.TCPServer(("", self.args.port), handler)
        server.serve_forever()

    @classmethod
    def add_arguments(cls, parser):
        parser.add_argument("-p", "--port",
                            default=8000,
                            help="port", metavar="PORT")
        parser.add_argument("dest_dir",
                            help="Destination directory", metavar="PATH")
