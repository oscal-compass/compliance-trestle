# Trestle author jinja - output templating support for oscal documents.

Unfortunately OSCAL documents are not yet universally accepted. Therefore to support various OSCAL and non-OSCAL compliance workflows `trestle author jinja` is designed to provide end users with the ability to use jinja to produce customized output. This complements the more structured commands `trestle author catalog-{assemble|generate}`, `trestle author profile-{assemble|generate}` and `trestle author ssp-{assemble|generate}` and allows arbitrary use of jinja.

## Jinja and jinja extensions provided by trestle.

[Jinja](https://jinja.palletsprojects.com/en/3.0.x/) is a powerful templating engine that is both more flexible that pure 'Moustache' approaches, and not coupled to a particular web application server (as an example Django templates). Users are encouraged to review the [template designer documentation](https://jinja.palletsprojects.com/en/3.0.x/templates/) for jinja as all core functionality is exposed.

Trestle's implementation of the Jinja command works in the following way:

1. The template search space, by default, is relative to the current working directory.
1. Trestle can inject a lookup table, into the jinja variables to contain booleans / substitutions required by end users using Moustache style variable substitutions.
1. Trestle can provide a number of interfaces to OSCAL objects, currently a resolved catalog and a SSP, into jinja.
1. Trestle supports custom jinja tags for importing.
1. The jinja templating is recursive, to ensure all jinja tags are resolved as appropriate.

More details will be on each of these points below.

## CLI invocation

Note the examples here use markdown, however, jinja can quite easily target xml or html if used w/o specific markdown content.
`trestle author jinja -i input_template.md.jinja -o output_file.md -ssp SSP_NAME -p PROFILE_NAME -lut lookup_table.yaml -elp lut.prefix`

- `-i` input file path, relative to cwd. Users are encouraged to use the `file_name.target_extension.jinja` best practice as it helps mitigate issues, however is not required.
- `-o` final output path, relative to cwd.
- `-ssp` (optional) ssp name (in the trestle project). When used the jinja template will have a `ssp_md_writer` variable exposed to use.
- `-p` (optional) profile name (in the trestle project). When used the jinja template will have `resolved_catalog` and `catalog_interface` variables to use.
- `-lut` (optional) loads yaml into a dictionary in python for which each (top level) variable is available in jinja.
- `-elp` (optional) a period separated prefix for the variables in the lookup table. E.g. if the lut contained `banana: yellow` and the prefix was `fruit.tropical` using `{{ fruit.tropical.banana }}` would print out `yellow` in the jinja template.

## Sample jinja templates

Note in addition to these templates some testing examples are available [here](https://github.com/IBM/develop)

| template                                          | Description                                                                                          | Optional args required                                                                                          |
| ------------------------------------------------- | ---------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------- |
| [Simple SSP template](assets/sample_ssp.md.jinja) | Sample ssp jinja template which prints out all control responses and includes a front-matter section | `-ssp` and `-p` for the ssp json and corresponding profile, respectively. Also requires a `frontmatter.md` file |

## Variable availability in the jinja template.

### LUT

The lookup table is primarily used for string substitution and to provide variables for basic logic operations in jinja e.g.

The LUT:

```yaml
names:
  OSCAL: Open Security Compliance Assessment Language
  trestle_pip: compliance-trestle
  trestle_module: trestle
variables:
  mac_os: true
```

The Jinja template:

```jinja

Install via pip install {{ names.trestle_pip }} and invoke at the python REPL by import {{ names.trestle_module }}

{% if variables.mac_os %}
Users are recommended to use homebrew to install the latest python 3 and then install python within a venv.
{% endif %}
```

The output:

```text

Install via pip install compliance-trestle and invoke at the python REPL by import trestle

Users are recommended to use homebrew to install the latest python 3 and then install python within a venv.
```

Users are free to use the LUT to inject more complex variables (arrays of data etc) to use at their own will using standard jinja templating.

### Resolved catalog interface (profile)

Passing `-p` exposes a catalog, resolved from the profile, at `catalog` and a `trestle.core.catalog_interface.CatalogInterface` at `catalog_interface`.

This allows user to perform various task such as iterating ove reach group and printing the group title.

```jinja
{% for group in catalog_interface.get_all_groups_from_catalog() +%}
## {{ group.title }} {{ group.class }} \({{ group.id|upper }}\)
```

### SSP interface.

If `-ssp` is passed a variable within the jinja template called `ssp_md_writer` is made available which is an instance of `trestle.core.ssp_io.SSPMarkdownWriter`.
`-ssp` requires that `-p` has also been set.

This as allows users, as an example to print out a control response, as markdown

```jinja
#### What is the solution and how is it implemented?
{{ ssp_md_writer.get_control_response('my_control_id', 3)}}
```

## Custom Jinja tags.

Trestle provides to custom jinja tags for use specifically with markdown: `mdsection_include` and `md_clean_include`.

`md_clean_include` is similar to the native `{% include 'sub_template' %}` that jinja provides except for the following:

1. `md_clean_include` will look for yaml headers in the markdown content and exclude it from the template
1. `md_clean_include` can be used with an optional keyword argument `heading_level` argument
   1. `{% md_clean_include 'path_to_file.md' heading_level=2 %}`
   1. The heading level argument adjusts to (based on the number of hashes) the most significant heading in the document, if headings exist.

`mdsection_include` is similar to the native `md_clean_include` except that.:

1. `mdsection_include` requires an second positional argument which is the title of a heading, from a markdown file, which you want the cotent from.
   1. E.g:  `{% mdsection_include 'test_markdown.md' '# Header we want' %}`
1. `mdsection_include` can be used with an optional keyword argument `heading_level` argument similar to `md_clean_include`
   1. `{% mdsection_include 'test_markdown.md' '# Header we want' %}`
   1. The heading level argument adjusts to (based on the number of hashes) the most significant heading in the chosen section, if headings exist.
