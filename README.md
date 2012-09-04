pyder - Python/Mako static website generate
==========

[Pyder](https://github.com/von/pyder) is a simple Python and
[Mako](http://www.makotemplates.org/) based static website generator
(a "python spider").

Pyder is "simple" which means it does exactly what I want, how I want
it. Maybe you will find it the same; if not, there are a number of
alternatives.

## Overview ##

You create your website with files named as they will be in your
website. As discussed subsequently, you can have some of these files
processed by Mako as they are copied over.

## The _site_config.py Configuration File##

In addition to your website files you create a configuration file
*_site_config.py* in the root directory of your website. This file
specifies what files should be copied over without processing and what
files should be processed by Mako.

Example portion of *_site_config.py*:

    # Files to process
    process = [ "*.html", "*.txt" ]

    # Files to copy without processing
    copy = [ "*.php", "*.css", "*.asc", "*.jpg", "*.ico" ]

    # Files to rename while copying
    rename = { "current" : "new" }

The *process* and *copy* lists are lists of globs. The *rename* list
is a dictionary mapping current names to new names.

Typically you will create a *_templates* directory to hold your Mako
templates. You specify this with the *site_template_dir* variable in
*_site_config.py*:

    # Where site templates are stored
    site_template_dir = "_templates"

You can specify directories to be ignored using
*dirs_to_skip*:

    # Directories to skip
    dirs_to_skip = [ "_*" ]

You can specify extra variables to subsitute in your templates using
*variables*:

    variables = {
        "myname" : "J. Webmaster",
        "email" : "webmaster@example.com",
        }

## The pyderweb script ###

The script to convert your templates to the final product is
*pyderweb*. The usage is:

    pyderweb generate <template directory> <output directory>

*pyderweb* reads *_site_config.py* and processes based on its directives.

*pyderweb* can also serve the resulting website, for example:

    pyderweb serve <output directory>

Will serve the website on localhost:8000 for testing.

## Example ##

For a simple example, see
[pyder/example](https://github.com/von/pyder/tree/master/example).
