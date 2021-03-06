"""TemplateProcessor: Wrapper around Mako to process templates"""

import os
import os.path

from mako.template import Template
from mako.lookup import TemplateLookup

import markdown

class TemplateProcessor(object):
    """Wrapper around Mako to proecess templates"""

    def __init__(self, output_base, template_dirs, variables):
        """Initial TemplateProcessor

        output_base is path to base of output directory.
        template_dirs is list of directories to search for templates.
        variables is a dictionary of extra variables to substitute."""
        self.output_base = output_base
        self.template_dirs = template_dirs
        self.variables = variables

    def process_file(self, path):
        """Process the given file"""
        dirname = os.path.dirname(path)
        filename = os.path.basename(path)
        out_filepath = os.path.join(self.output_base, dirname, filename)
        template_dirs = self.template_dirs[:]
        template_dirs.append(dirname)
        template_lookup = TemplateLookup(directories=template_dirs,
                                  input_encoding='utf-8',
                                  output_encoding='utf-8')
        with open(path) as template_file:
            template_string = "".join(template_file.readlines())
        # Handle Markdown files with .md extension
        # Do this before processing mako to avoid Markdown doing
        # weird things to html.
        if os.path.splitext(filename)[1] == ".md":
            template_string = markdown.markdown(template_string)
            out_filepath=os.path.splitext(out_filepath)[0] + ".html"
        # Process template
        template = Template(template_string,
                     lookup=template_lookup,
                     input_encoding='utf-8',
                     output_encoding='utf-8')
        url_path = os.path.join(dirname, filename)
        if url_path.startswith("."):
            url_path = url_path[1:]
        substitutions = {
            "dirname" : os.path.dirname(url_path),
            "filename" : os.path.basename(url_path),
            "relative_url" : url_path
            }
        substitutions.update(self.variables)
        output = template.render(**substitutions)
        # utf-8 decoding from template.render() apparently
        # not working, hence decode() here
        self._write_out_file(out_filepath, output.decode())

    def _write_out_file(self, filename, contents):
        """Write contents to filename, creating directories as needed."""
        self._check_output_directory(filename)
        with open(filename, "w") as out_file:
            out_file.write(contents)

    def _check_output_directory(self, filename):
        """Make sure the directory for filename exists."""
        path = os.path.dirname(filename)
        if not os.path.exists(path):
            os.makedirs(path)
