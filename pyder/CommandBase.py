from __future__ import print_function

import sys

import mako


# Must inherit from object for __subclasses__() to work
class CommandBase(object):
    """Base class for all script commands"""

    # Print debug messages
    _show_debug = False

    # Command line string that match this command
    _name = "base"

    def __init__(self, args):
        self.args = args

    def doit(self):
        """Invoke run() method, handling exceptions."""
        try:
            status = self.run()
        except KeyboardInterrupt as ex:
            status = self.handle_keyboard_interrupt(ex)
        except Exception as ex:
            status = self.handle_exception(ex)
        return(status)

    def run(self):
        """Called when its time to do its thing."""
        pass

    @classmethod
    def add_subparsers(cls, subparsers):
        """Add subparses for all child classes.

        subparsers is parser from add_subparses() method."""
        for child_cls in cls.__subclasses__():
            child_cls.add_subparser(subparsers)

    @classmethod
    def add_subparser(cls, subparsers):
        """Add subparser for this command.

        subparsers is parser from add_subparses() method."""
        parser = subparsers.add_parser(cls._name, help=cls.__doc__)
        parser.set_defaults(command_class=cls)
        cls.add_arguments(parser)

    @classmethod
    def add_arguments(cls, parser):
        """Add needed argements to given ArgumentParser or subparser."""
        pass

    def handle_keyboard_interrupt(self, ex):
        """Called when a keyboard interrupt is caught running command.

        Return code is exit status."""
        return(1)

    def handle_exception(self, ex):
        """Called when an unhandled exception from run() is caught.

        Return code is exit status."""
        print(mako.exceptions.text_error_template().render())
        return(1)

    @classmethod
    def show_debug(cls, value):
        """Turn on or off debugging based on value."""
        cls._show_debug = value

    def debug(self, *args, **kwargs):
        """Handle debug message"""
        if self._show_debug:
            print(*args, **kwargs)

    def output(self, *args, **kwargs):
        """Handle output message"""
        print(*args, **kwargs)

    def warning(self, *args, **kwargs):
        """Handle warning message"""
        kwargs["file"] = sys.stderr
        print(*args, **kwargs)
