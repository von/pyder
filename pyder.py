#!/usr/bin/env python

from __future__ import print_function

import argparse
import fnmatch
import os
import os.path
import re
import sys

import mako
from mako.template import Template
from mako.lookup import TemplateLookup

######################################################################
#
# Output functions

def _debug_noop(*args, **kwargs):
    """Do nothing. For non-debug mode."""
    pass

def _debug(*args, **kwargs):
    """Print debug message."""
    print(*args, **kwargs)
    
debug = _debug_noop

def warning(*args, **kwargs):
    """Handle a warning message"""
    kwargs["file"] = sys.stderr
    print(*args, **kwargs)
    
######################################################################

# Must inherit from object for __subclasses__() to work
class CommandBase(object):
    """Base class for all script commands"""

    # Command line string that match this command
    _names = [ "base" ]

    def __init__(self, args):
        self.args = args
        
    def run(self):
        """Called when its time to do its thing."""
        pass

    @classmethod
    def add_subparser(cls, subparsers):
        """Add subparser for this command.

        subparsers is parser from add_subparses() method."""
        parser = subparsers.add_parser(cls._name, help=cls.__doc__)
        parser.set_defaults(command_class=cls)
        cls.add_arguments(parser)
    
    @classmethod
    def add_arguments(cls, parser):
        """Given an ArgumentParser (or subparser) add any arguments this command needs."""
        pass

######################################################################
    
class GenerateCommand(CommandBase):
    """Generate the website from input files"""

    _name = "generate"

    def run(self):
        debug("Parsing source starting at \"{}\"".format(self.args.source_dir))
        self.dest_dir = os.path.abspath(self.args.dest_dir)
        os.chdir(self.args.source_dir)
        self.site_config = self.process_config_file(self.args.site_config)
        template_dir = os.path.abspath(self.site_config["site_template_dir"])
        debug("Template directory is {}".format(template_dir))
        self.template_lookup = TemplateLookup(directories=[template_dir])
        for dirname,subdirs,filenames in os.walk("."):
            # Filter out any names we should skip
            self._filter_names(subdirs)  # Filters in place
            self._filter_names(filenames)  # Filters in place
            self.process_dir(dirname, filenames)

    def process_dir(self, dirname, filenames):
        debug("Processing directory \"{}\"".format(dirname))
        dir_config_file = os.path.join(dirname, "_config.py")
        self.dir_config = self.process_config_file(dir_config_file,
                                                   self.site_config)
        for filename in filenames:
            self.process_file(dirname, filename)
            
    def process_file(self, dirname, filename):
        in_filepath = os.path.join(dirname, filename)
        out_filepath = os.path.join(self.dest_dir, dirname, filename)
        debug("Processing {} to {}".format(in_filepath, out_filepath))
        template = self._read_template(in_filepath)
        substitutions = {
            "dirname" : dirname,
            "filename" : filename,
            "config" : self.dir_config,
            }
        try:
            output = template.render(**substitutions)
        except Exception as e:
            warning("Error processing \"{}\":".format(filename))
            warning(mako.exceptions.text_error_template().render())
            return
        self._write_out_file(out_filepath, output)

    def process_config_file(self, config_filename, config=None):
        """Process configuration file, returning configuration.

        If config is given, configuration is added to a copy of it and returned."""
        config = config.copy() if config else {}
        if os.path.exists(config_filename):
            debug(
                "Processing configuration file \"{}\"".format(config_filename))
            try:
                # We pass config as locals so it doesn't get filled up
                # with python stuff.
                execfile(config_filename, {}, config)
            except Exception as e:
                warning("Error processing configuration \"{}\": {}".format(
                    config_filename, str(e)))
        return config

    def _read_template(self, filename):
        """Read a file and return a mako.template.Template object"""
        with open(filename) as f:
            template_string = "".join(f.readlines())
        return Template(template_string, lookup=self.template_lookup)

    def _write_out_file(self, filename, contents):
        """Write contents to filename, creating directories as needed."""
        path = os.path.dirname(filename)
        if not os.path.exists(path):
            os.makedirs(path)
        with open(filename, "w") as f:
            f.write(contents)

    def _skip_name(self, name):
        """Should a given fir/directory be skiped, based on 'skip'?"""
        return any(map(lambda pattern: fnmatch.fnmatch(name, pattern),
                       self.site_config["skip"]))
    
    def _filter_names(self, list):
        """Given a list of file/directory names, filter it in place.

        Does so based on 'skip' configuration."""
        # Replace contents of list with filtered list
        # Kudos: http://stackoverflow.com/a/4639748/197789
        list[:] = (name for name in list if not self._skip_name(name))
            
    @classmethod
    def add_arguments(cls, parser):
        parser.add_argument("-c", "--site_config",
                            default="_site_config.py",
                            help="configuration file", metavar="FILENAME")
        parser.add_argument("source_dir",
                            help="Source directory", metavar="PATH")
        parser.add_argument("dest_dir",
                            help="Destination directory", metavar="PATH")

######################################################################

def parse_args(argv):
    """Parse commandline arguments returns args object."""
    parser = argparse.ArgumentParser(
        # print script description with -h/--help
        description=__doc__,
        # Don't mess with format of description
        formatter_class=argparse.RawDescriptionHelpFormatter,
        )
    parser.add_argument("-d", "--debug",
                        dest="debug", action='store_const', const=True,
                        help="Turn on debugging")

    subparsers = parser.add_subparsers(title="Commands",
                                       description="valid commands")

    # Each subclass of CommandBase represents a command
    for cls in CommandBase.__subclasses__():
        cls.add_subparser(subparsers)

    args = parser.parse_args()
    return args

######################################################################

def main(argv=None):
    # Do argv default this way, as doing it in the functional
    # declaration sets it at compile time.
    if argv is None:
        argv = sys.argv

    args = parse_args(argv)

    if args.debug:
        global debug
        debug = _debug
        debug("Debugging enabled")

    cmd_class = args.command_class(args)
    status = cmd_class.run()
    
    return(status)

if __name__ == "__main__":
    sys.exit(main())
