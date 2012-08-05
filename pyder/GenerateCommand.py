"""GenerateCommand: Implements 'generate' command to generate website."""
import fnmatch
import os
import os.path
import shutil

from . import CommandBase, TemplateProcessor

import mako


class GenerateCommand(CommandBase):
    """Generate the website from input files"""

    _name = "generate"

    def __init__(self, args):
        super(GenerateCommand, self).__init__(args)
        self.dest_dir = os.path.abspath(self.args.dest_dir)
        self.site_config = self.process_config_file(
            os.path.join(self.args.source_dir, self.args.site_config))
        template_dir = os.path.abspath(
            os.path.join(self.args.source_dir,
                         self.site_config["site_template_dir"]))
        self.debug("Template directory is {}".format(template_dir))
        self.processor = TemplateProcessor(
            output_base=self.dest_dir,
            template_dirs=[template_dir])

    def run(self):
        """Generate website."""
        self.debug("Parsing source starting at \"{}\"".format(
                self.args.source_dir))
        os.chdir(self.args.source_dir)
        for dirname, subdirs, filenames in os.walk("."):
            self._filter_dirs(subdirs)  # Filters in place
            self.process_dir(dirname, filenames)

    def handle_exception(self, ex):
        """Handle exceptions, particularly from Mako"""
        print mako.exceptions.text_error_template().render()
        return(1)

    def process_dir(self, dirname, filenames):
        """Process given directory."""
        self.debug("Processing directory \"{}\"".format(dirname))
        dir_config_file = os.path.join(dirname, "_config.py")
        if os.path.exists(dir_config_file):
            self.dir_config = self.process_config_file(dir_config_file,
                                                       self.site_config)
        for filename in filenames:
            if self.should_process(filename):
                self.process_file(dirname, filename)
            elif self.should_copy(filename):
                self.copy_file(dirname, filename)
            elif self.should_rename(filename):
                self.rename_file(dirname, filename)

    def process_file(self, dirname, filename):
        """Process given file."""
        in_filepath = os.path.join(dirname, filename)
        self.debug("Processing {}".format(in_filepath))
        self.processor.process_file(in_filepath)

    def copy_file(self, dirname, filename):
        """Copy file without processing it"""
        in_filepath = os.path.join(dirname, filename)
        out_filepath = os.path.join(self.dest_dir, dirname, filename)
        self.debug("Copying {} to {}".format(in_filepath, out_filepath))
        self._check_output_directory(out_filepath)
        shutil.copyfile(in_filepath, out_filepath)

    def rename_file(self, dirname, filename):
        """Copy file without processing it"""
        in_filepath = os.path.join(dirname, filename)
        new_name = self.site_config["rename"][filename]
        out_filepath = os.path.join(self.dest_dir, dirname, new_name)
        self.debug("Copying {} to {}".format(in_filepath, out_filepath))
        self._check_output_directory(out_filepath)
        shutil.copyfile(in_filepath, out_filepath)

    def process_config_file(self, config_filename, config=None):
        """Process configuration file, returning configuration.

        If config is given, configuration is added to a copy of it and
        returned."""
        config = config.copy() if config else {}
        if not os.path.exists(config_filename):
            raise IOError("Configuration file \"{}\" does not exist"
                          "".format(config_filename))
        self.debug(
            "Processing configuration file \"{}\"".format(config_filename))
        try:
            # We pass config as locals so it doesn't get filled up
            # with python stuff.
            execfile(config_filename, {}, config)
        except Exception as ex:
            self.warning(
                "Error processing configuration \"{}\": {}".format(
                    config_filename, str(ex)))
        return config

    def _check_output_directory(self, filename):
        """Make sure the directory for filename exists."""
        path = os.path.dirname(filename)
        if not os.path.exists(path):
            os.makedirs(path)

    def should_process(self, filename):
        """Should the given file be processed, based on 'process'?"""
        return any(map(lambda pattern: fnmatch.fnmatch(filename, pattern),
                       self.site_config["process"]))

    def should_copy(self, filename):
        """Should the given file be processed, based on 'copy'?"""
        return any(map(lambda pattern: fnmatch.fnmatch(filename, pattern),
                       self.site_config["copy"]))

    def should_rename(self, filename):
        """Should the given file be rename, based on 'rename'?"""
        return any(map(lambda rename: filename == rename,
                       self.site_config["rename"].keys()))

    def _filter_dirs(self, dirnames):
        """Given a list of directory names, filter it in place.

        Does so based on 'dirs_to_skip' configuration."""
        # Replace contents of list with filtered list
        # Kudos: http://stackoverflow.com/a/4639748/197789
        skip = lambda dirname: any(
            map(lambda pattern: fnmatch.fnmatch(dirname, pattern),
                self.site_config["dirs_to_skip"]))
        dirnames[:] = (dirname for dirname in dirnames
                       if not skip(dirname))

    @classmethod
    def add_arguments(cls, parser):
        parser.add_argument("-c", "--site_config",
                            default="_site_config.py",
                            help="configuration file", metavar="FILENAME")
        parser.add_argument("source_dir",
                            help="Source directory", metavar="PATH")
        parser.add_argument("dest_dir",
                            help="Destination directory", metavar="PATH")
