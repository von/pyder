# Example _site_config.py configuration file for pyderweb

# Files to process
process = [ "*.html", "*.txt", "*.md" ]

# Files to copy without processing
copy = [ "*.php", "*.css", "*.asc", "*.jpg", "*.ico" ]

# Files to rename when copying
rename = { "current_name" : "new_name" }

# Directories to skip
dirs_to_skip = [ "_*" ]

# Where site templates are stored
site_template_dir = "_templates"

# Extra variables to substitute in scripts
variables = {
    "admin_name" : "J. Webmaster",
    "admin_email" : "admin@example.com",
    }
