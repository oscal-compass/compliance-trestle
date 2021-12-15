# A markdown file with jinja objects.


# This should pull content in only if the var is correct
{% md_clean_include 'test_markdown.md' heading_level=2 %}