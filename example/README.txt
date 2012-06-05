<%inherit file="README.base" />

<%
# All files are processed by mako, and his is python code
name = "World's Greatest Example"
%>

<%block name="content">
This is an example website.

End of README for "${name}".
</%block>
