# CHANGELOG

## v3.5.0 (2024-10-23)

### Build

* build(deps): bump python-semantic-release/upload-to-gh-release (#1717)

Bumps [python-semantic-release/upload-to-gh-release](https://github.com/python-semantic-release/upload-to-gh-release) from 9.8.8 to 9.8.9.
- [Release notes](https://github.com/python-semantic-release/upload-to-gh-release/releases)
- [Changelog](https://github.com/python-semantic-release/upload-to-gh-release/blob/main/releaserc.toml)
- [Commits](https://github.com/python-semantic-release/upload-to-gh-release/compare/v9.8.8...v9.8.9)

---
updated-dependencies:
- dependency-name: python-semantic-release/upload-to-gh-release
  dependency-type: direct:production
  update-type: version-update:semver-patch
...

Signed-off-by: dependabot[bot] &lt;support@github.com&gt;
Co-authored-by: dependabot[bot] &lt;49699333+dependabot[bot]@users.noreply.github.com&gt; ([`5e15a03`](https://github.com/oscal-compass/compliance-trestle/commit/5e15a035fc4e60b4f450f609d924813565b2b354))

* build(deps): bump python-semantic-release/upload-to-gh-release (#1683)

Bumps [python-semantic-release/upload-to-gh-release](https://github.com/python-semantic-release/upload-to-gh-release) from 9.8.0 to 9.8.8.
- [Release notes](https://github.com/python-semantic-release/upload-to-gh-release/releases)
- [Changelog](https://github.com/python-semantic-release/upload-to-gh-release/blob/main/releaserc.toml)
- [Commits](https://github.com/python-semantic-release/upload-to-gh-release/compare/v9.8.0...v9.8.8)

---
updated-dependencies:
- dependency-name: python-semantic-release/upload-to-gh-release
  dependency-type: direct:production
  update-type: version-update:semver-patch
...

Signed-off-by: dependabot[bot] &lt;support@github.com&gt;
Co-authored-by: dependabot[bot] &lt;49699333+dependabot[bot]@users.noreply.github.com&gt;
Co-authored-by: Chris Butler &lt;chris.butler@redhat.com&gt;
Co-authored-by: Jennifer Power &lt;barnabei.jennifer@gmail.com&gt; ([`01332d3`](https://github.com/oscal-compass/compliance-trestle/commit/01332d3e7c73fd645788b67e4d5b81cec6ab8576))

* build(deps): Bump python-semantic-release/python-semantic-release (#1682)

Bumps [python-semantic-release/python-semantic-release](https://github.com/python-semantic-release/python-semantic-release) from 9.8.0 to 9.8.8.
- [Release notes](https://github.com/python-semantic-release/python-semantic-release/releases)
- [Changelog](https://github.com/python-semantic-release/python-semantic-release/blob/master/CHANGELOG.md)
- [Commits](https://github.com/python-semantic-release/python-semantic-release/compare/v9.8.0...v9.8.8)

---
updated-dependencies:
- dependency-name: python-semantic-release/python-semantic-release
  dependency-type: direct:production
  update-type: version-update:semver-patch
...

Signed-off-by: dependabot[bot] &lt;support@github.com&gt;
Co-authored-by: dependabot[bot] &lt;49699333+dependabot[bot]@users.noreply.github.com&gt;
Co-authored-by: Chris Butler &lt;chris.butler@redhat.com&gt;
Co-authored-by: Jennifer Power &lt;barnabei.jennifer@gmail.com&gt; ([`56b019c`](https://github.com/oscal-compass/compliance-trestle/commit/56b019c1e8f5bf404d6c69bf3c2c00422f293d66))

* build(deps): bump artifact actions from 2 to 4 (#1679)

Signed-off-by: Jennifer Power &lt;barnabei.jennifer@gmail.com&gt; ([`2e81958`](https://github.com/oscal-compass/compliance-trestle/commit/2e81958fe69b57455844006e98bf2cffe24a61bf))

### Chore

* chore: adds initial triaging process and stale issue handling (#1712)

* chore: adds triaging process and stale workflow

Signed-off-by: Jennifer Power &lt;barnabei.jennifer@gmail.com&gt;

* docs: fix working in ROADMAP around stale issues

Signed-off-by: Jennifer Power &lt;barnabei.jennifer@gmail.com&gt;

* fix: fixes md formatting

Signed-off-by: Jennifer Power &lt;barnabei.jennifer@gmail.com&gt;

* chore: reword ROADMAP.md section on stale issues

Signed-off-by: Jennifer Power &lt;barnabei.jennifer@gmail.com&gt;

* fix: fixes markdown formatting

Signed-off-by: Jennifer Power &lt;barnabei.jennifer@gmail.com&gt;

---------

Signed-off-by: Jennifer Power &lt;barnabei.jennifer@gmail.com&gt; ([`0350791`](https://github.com/oscal-compass/compliance-trestle/commit/035079112490086964094a59159e333a8b4b467a))

* chore: add html validation to build process (#1659)

Adds link validation to all links within the documentation ([`810f4e7`](https://github.com/oscal-compass/compliance-trestle/commit/810f4e7c1de7d0284ca970f225c47081fcc4bdaf))

* chore: Merge back version tags and changelog into develop. ([`dfe8929`](https://github.com/oscal-compass/compliance-trestle/commit/dfe892936e5960ad64f6f387dbe5918314049e89))

### Ci

* ci: updates GH credential strategy in the python-push.yml (#1726)

* ci: updates python-push.yml to use a GitHub app for commit work

Signed-off-by: Jennifer Power &lt;barnabei.jennifer@gmail.com&gt;

* fix: removes extra &#34;&gt;&#34; character

Signed-off-by: Jennifer Power &lt;barnabei.jennifer@gmail.com&gt;

---------

Signed-off-by: Jennifer Power &lt;barnabei.jennifer@gmail.com&gt; ([`c69511a`](https://github.com/oscal-compass/compliance-trestle/commit/c69511a134d540b4e443a69f07e36caaa6321ec9))

### Documentation

* docs: update the compliance-trestle-fedramp plugin usage (#1517)

Signed-off-by: Jennifer Power &lt;barnabei.jennifer@gmail.com&gt; ([`e3aeb95`](https://github.com/oscal-compass/compliance-trestle/commit/e3aeb959aac761432e21908be86ee37b426e0d2e))

### Feature

* feat(author-jinja): load jinja extensions from plugins (#1710)

* Implement new helpers as jinja filters loaded via an extension

Signed-off-by: Ryan Ahearn &lt;ryan.ahearn@gsa.gov&gt;

* auto-load plugins with jinja extensions

Signed-off-by: Ryan Ahearn &lt;ryan.ahearn@gsa.gov&gt;

* Refactor jinja organization for ease of reuse

Signed-off-by: Ryan Ahearn &lt;ryan.ahearn@gsa.gov&gt;

* Document plugins including jinja extensions

Signed-off-by: Ryan Ahearn &lt;ryan.ahearn@gsa.gov&gt;

* Rename first_array_entry filter for clarity

fix some other random typos

Signed-off-by: Ryan Ahearn &lt;ryan.ahearn@gsa.gov&gt;

* Update api docs

Signed-off-by: Ryan Ahearn &lt;ryan.ahearn@gsa.gov&gt;

* Add docs for new built-in jinja filters

Signed-off-by: Ryan Ahearn &lt;ryan.ahearn@gsa.gov&gt;

* Correct the copyright line for new files

Signed-off-by: Ryan Ahearn &lt;ryan.ahearn@gsa.gov&gt;

* Remove inherited dangling comment

Signed-off-by: Ryan Ahearn &lt;ryan.ahearn@gsa.gov&gt;

---------

Signed-off-by: Ryan Ahearn &lt;ryan.ahearn@gsa.gov&gt; ([`f7b63ad`](https://github.com/oscal-compass/compliance-trestle/commit/f7b63ad77347532ed42585ff402ca5a7db512712))

### Fix

* fix(build): installs required build dependencies during semantic release build (#1736)

Semantic release is running in a container that does
not have access to the dependencies installed in `make
develop` step

Signed-off-by: Jennifer Power &lt;barnabei.jennifer@gmail.com&gt; ([`4dbdf7d`](https://github.com/oscal-compass/compliance-trestle/commit/4dbdf7d0f330ef980e5ba19f445c9568004f5e85))

* fix: support rule overlap for checks and target components (#1730)

* fix: support rule overlap for checks and target components

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;

* Fix type specification

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;

* Fix typing, second try.

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;

* remove extraneous logging statement

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;

---------

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt; ([`11ab516`](https://github.com/oscal-compass/compliance-trestle/commit/11ab516a1cda022ea349d1dadae4179709486834))

* fix(refactor): clean up timezone deprecations (#1722)

* fix(refactor): remove deprecated datetime functionality

Signed-off-by: Chris Butler &lt;chris.butler@redhat.com&gt;


---------

Signed-off-by: Chris Butler &lt;chris.butler@redhat.com&gt; ([`7b8b353`](https://github.com/oscal-compass/compliance-trestle/commit/7b8b3537dc8d4edfb0bab554be32e53a6fd5ad2a))

* fix: add testing policy to contributing.md (#1697)

* add testing policy to contributing.md

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;

* Add sonar cloud info.

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;

---------

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt; ([`8744cee`](https://github.com/oscal-compass/compliance-trestle/commit/8744cee2beb966e99b338e71ccf723b805b9b4d7))

* fix(markdown): writes component data for markdown without rules (#1695)

* test: adds failing test to confirm component definition bug

Signed-off-by: Jennifer Power &lt;barnabei.jennifer@gmail.com&gt;

* feat: adds implemented requirement and statement description information

The comp_dict is populated with the information from the OSCAL JSON
and logic on when to write parts left to the ControlWriter.

Signed-off-by: Jennifer Power &lt;barnabei.jennifer@gmail.com&gt;

* fix: assemble component responses with and without rules

Signed-off-by: Jennifer Power &lt;barnabei.jennifer@gmail.com&gt;

* fix: updates control_rules logic to fix test failure

Signed-off-by: Jennifer Power &lt;barnabei.jennifer@gmail.com&gt;

* feat: centralizes logic for component inclusion in control writer

To ensure parts are written out for component definitions without
rules in a way that is not too verbose, parts will only be included
if they have rules attached or non-empty prose.

Signed-off-by: Jennifer Power &lt;barnabei.jennifer@gmail.com&gt;

* fix: updates formatting to make tests pass

Signed-off-by: Jennifer Power &lt;barnabei.jennifer@gmail.com&gt;

* docs: updates docs to reflect component authoring behavior

Signed-off-by: Jennifer Power &lt;barnabei.jennifer@gmail.com&gt;

---------

Signed-off-by: Jennifer Power &lt;barnabei.jennifer@gmail.com&gt; ([`25dbc7a`](https://github.com/oscal-compass/compliance-trestle/commit/25dbc7a4ae823c8645e8861f3763883e855b44af))

* fix(docs): add cookie consent popup (#1690)



---------

Signed-off-by: Chris Butler &lt;chris.butler@redhat.com&gt; ([`e67f73c`](https://github.com/oscal-compass/compliance-trestle/commit/e67f73c7cc3203037dd4d83b92ac317cd6e70978))

* fix(docs): correct build status icon is displayed in docs (#1689)

Signed-off-by: Chris Butler &lt;chris.butler@redhat.com&gt; ([`5385092`](https://github.com/oscal-compass/compliance-trestle/commit/53850920bede72f40104cd2d70b80b06f994660a))

* fix: add Python coding standards info (#1686)

* Add Python coding standards info

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;

* correct english

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;

* address reviewer suggestion on PEP8 link location

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;

* Trestle updating and release logistics

Inspired by need to address OpenSSF requirement:

To enable collaborative review, the project&#39;s source repository MUST
include interim versions for review between releases; it MUST NOT
include only final releases.

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;

* Fix contributing copyright.

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;

* add semantic release &amp; tags info

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;

---------

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt; ([`1fe8457`](https://github.com/oscal-compass/compliance-trestle/commit/1fe8457b27cb87b537ba806dd7862c729e1e1ab8))

* fix: lf footer website guidelines (#1678)

* LF footer website guidelines

https://github.com/cncf/foundation/blob/main/website-guidelines.md

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;

* make mdformat

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;

* Trestle created

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;

* fix maintainers link

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;

* &lt;hr&gt;

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;

* remove hr

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;

* fix maintainers reference

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;

* And license.

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;

* add cncf logo

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;

* fix trestle website too

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;

* restore maintainers.md

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;

* remove Red Hat from footer, per Red Hat request

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;

---------

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt; ([`40b2880`](https://github.com/oscal-compass/compliance-trestle/commit/40b2880ed9c0f9f7ff1fae71b17371306b57d4f6))

### Unknown

* Merge pull request #1737 from oscal-compass/develop

chore: Trestle release ([`7d3ee4c`](https://github.com/oscal-compass/compliance-trestle/commit/7d3ee4c71780d314eaf27f8f0a5ca90d94375987))

* Merge pull request #1735 from oscal-compass/develop

chore: Trestle release ([`26b7734`](https://github.com/oscal-compass/compliance-trestle/commit/26b77343b9bafd3c696f5586cf0e9beaf983dece))

* fix(profile-resolve):handle unspecified aggregate parameters (#1709)

Signed-off-by: Michael Davie &lt;mldavie@amazon.com&gt;
Co-authored-by: Alejandro Leiva &lt;alejandro.leiva.palomo@ibm.com&gt; ([`bc6f510`](https://github.com/oscal-compass/compliance-trestle/commit/bc6f51025bb29ae8f7828cee5f1803817574e322))

## v3.4.0 (2024-08-23)

### Chore

* chore: Merge back version tags and changelog into develop. ([`724ac16`](https://github.com/oscal-compass/compliance-trestle/commit/724ac169389e4d80cca4c336e17fbd5bed4cedff))

### Documentation

* docs: update maintainers list to reflect active maintainers (#1638)

Signed-off-by: Jennifer Power &lt;barnabei.jennifer@gmail.com&gt;
Co-authored-by: mrgadgil &lt;49280244+mrgadgil@users.noreply.github.com&gt; ([`f8daaae`](https://github.com/oscal-compass/compliance-trestle/commit/f8daaae2e57c9a582b9a94bd5128ed55a890a3bf))

* docs: updates CODE_OF_CONDUCT urls in README and website (#1635)

Signed-off-by: Jennifer Power &lt;barnabei.jennifer@gmail.com&gt; ([`08f387a`](https://github.com/oscal-compass/compliance-trestle/commit/08f387a074734a5ddd079d5f613220aa6b44242c))

* docs: adds ROADMAP.md with high level roadmap description (#1626)

* docs: adds ROADMAP.md with high level roadmap description

Signed-off-by: Jennifer Power &lt;barnabei.jennifer@gmail.com&gt;

* chore: refines working in ROADMAP.md for clarity

Signed-off-by: Jennifer Power &lt;barnabei.jennifer@gmail.com&gt;

* docs: updates ROADMAP.md with timeline information

Signed-off-by: Jennifer Power &lt;barnabei.jennifer@gmail.com&gt;

* docs: rewords section on iterations

Adds more clarity around what takes place in
the 12-week period. No changes to the overall plan.

Signed-off-by: Jennifer Power &lt;barnabei.jennifer@gmail.com&gt;

---------

Signed-off-by: Jennifer Power &lt;barnabei.jennifer@gmail.com&gt; ([`ed10dad`](https://github.com/oscal-compass/compliance-trestle/commit/ed10dadee72ac2bedf07c71095e598dc6f95b5bf))

### Feature

* feat: add parameter aggregation support for SSP (#1668)

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt; ([`b2611d1`](https://github.com/oscal-compass/compliance-trestle/commit/b2611d1382c6ff1e9e1864e7fa1726dd7ad07eb5))

* feat: adds dependabot configuration for continous updates (#1647)

Signed-off-by: Jennifer Power &lt;barnabei.jennifer@gmail.com&gt; ([`4862c4a`](https://github.com/oscal-compass/compliance-trestle/commit/4862c4ac0ec9ce06988f1b6d75ad5986acbd3b78))

* feat: adds implementation parts to This System component in markdown (#1536)

* feat: adds implementation part prompts for This System

Changes in assembly are due to changes in the markdown breaking the unit tests
because the This System component is associated with each statement

Signed-off-by: Jennifer Power &lt;barnabei.jennifer@gmail.com&gt;

* fix: removes this system comp prose and status duplication

The process_main_component was overwriting the first prose
response to all the parts

Signed-off-by: Jennifer Power &lt;barnabei.jennifer@gmail.com&gt;

* chore: removes TODO comment for bug review

Signed-off-by: Jennifer Power &lt;barnabei.jennifer@gmail.com&gt;

* chore: updates workding in comments in control_writer.py

Signed-off-by: Jennifer Power &lt;barnabei.jennifer@gmail.com&gt;

* chore: moves part_a_text_edited into applicable unit tests

Signed-off-by: Jennifer Power &lt;barnabei.jennifer@gmail.com&gt;

* refactor: add include-all-parts to make part responses optional

To ensure the default markdown is not overly verbose, writing all
implementation parts and the inclusion of This System is optional.

Signed-off-by: Jennifer Power &lt;barnabei.jennifer@gmail.com&gt;

* docs: updates documentation with include-all-parts description

Signed-off-by: Jennifer Power &lt;barnabei.jennifer@gmail.com&gt;

* chore: updates comments and docstring in control_writer.py updates

The goal is to increase the usefulness of the comments

Signed-off-by: Jennifer Power &lt;barnabei.jennifer@gmail.com&gt;

* fix: updates docstring in control_writer.py to improve clarity

Signed-off-by: Jennifer Power &lt;barnabei.jennifer@gmail.com&gt;

---------

Signed-off-by: Jennifer Power &lt;barnabei.jennifer@gmail.com&gt; ([`54706af`](https://github.com/oscal-compass/compliance-trestle/commit/54706af0f9d428d10451823aa7d8d0f92a86e3eb))

### Fix

* fix: cis benchmarks to catalog task, which mistakenly does not see all columns (#1657)

* fix: allow sheet specification

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;

* fix: number of columns is too small by 1

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;

* Fix: examine all columns

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;

---------

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt; ([`6c2d3f3`](https://github.com/oscal-compass/compliance-trestle/commit/6c2d3f3bd8d6eeaf04e0a931ce39b8b52646e95a))

* fix: skips sonar scans for dependabot updates (#1656)

* fix: skips sonar scans for dependabot updates

Dependabot updates only include third party dependency updates

Signed-off-by: Jennifer Power &lt;barnabei.jennifer@gmail.com&gt;

* fix: updates workflow if statement formatting

Signed-off-by: Jennifer Power &lt;barnabei.jennifer@gmail.com&gt;

---------

Signed-off-by: Jennifer Power &lt;barnabei.jennifer@gmail.com&gt; ([`050c425`](https://github.com/oscal-compass/compliance-trestle/commit/050c425771ccb52bd263b011e37e128a1eb8205f))

* fix: updates invalid dependabot configuation (#1650)

Signed-off-by: Jennifer Power &lt;barnabei.jennifer@gmail.com&gt; ([`e27f0cd`](https://github.com/oscal-compass/compliance-trestle/commit/e27f0cda76a89c7fe60e425916e8b85c3cb1fc30))

* fix: correct logo redirection for PyPi page (#1644)

* fix: correct logo redirection for PyPi page

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;

* fix: change develop to main branch in the logo link

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;

---------

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt; ([`2c4899a`](https://github.com/oscal-compass/compliance-trestle/commit/2c4899a809cb28855943f4f3e89f3e9d771aaf1e))

* fix: default value for optional string params should be None (#1621)

* fix: default value for optional string params should be None

Signed-off-by: George Vauter &lt;gvauter@redhat.com&gt;

* pin setuptools to min version suppported by setuptools_scm

Signed-off-by: George Vauter &lt;gvauter@redhat.com&gt;

* fix: add include_all_parts to undo accidental deletion

Signed-off-by: George Vauter &lt;gvauter@redhat.com&gt;

---------

Signed-off-by: George Vauter &lt;gvauter@redhat.com&gt; ([`f81f567`](https://github.com/oscal-compass/compliance-trestle/commit/f81f5674ee2996532524eb014daadbbdbd33e6bb))

* fix: allow forks to correctly run the pipelines (#1633)

A small set of cleanups to the pipelines.

---------

Signed-off-by: Jennifer Power &lt;barnabei.jennifer@gmail.com&gt;
Signed-off-by: Chris Butler &lt;chris.butler@redhat.com&gt;
Co-authored-by: Jennifer Power &lt;barnabei.jennifer@gmail.com&gt; ([`af4e5a2`](https://github.com/oscal-compass/compliance-trestle/commit/af4e5a286279a0aebf70b1cb87fa97651711ada2))

### Unknown

* Merge pull request #1670 from oscal-compass/develop

chore: Trestle release ([`2420d97`](https://github.com/oscal-compass/compliance-trestle/commit/2420d9740fbaa78f8a8a4b92c54747984db70717))

* fix - make status and mitre column optional (#1649)

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt; ([`47e6936`](https://github.com/oscal-compass/compliance-trestle/commit/47e6936e47d1fa0840aef5c26f36140438f03c98))

## v3.3.0 (2024-07-15)

### Chore

* chore: Merge back version tags and changelog into develop. ([`0c6e3d9`](https://github.com/oscal-compass/compliance-trestle/commit/0c6e3d917009885ddbe700d582b89a89e62d5983))

### Documentation

* docs: re-phrasing code of conduct reference (#1620)

* docs: re-phrasing code of conduct reference

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;

* Update docs/mkdocs_code_of_conduct.md

Co-authored-by: Jennifer Power &lt;barnabei.jennifer@gmail.com&gt;

* Update docs/mkdocs_code_of_conduct.md

Co-authored-by: Jennifer Power &lt;barnabei.jennifer@gmail.com&gt;

---------

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;
Co-authored-by: Jennifer Power &lt;barnabei.jennifer@gmail.com&gt; ([`7dabaee`](https://github.com/oscal-compass/compliance-trestle/commit/7dabaee6cfaeb61b4048847dafdde8b8d9ffa33d))

* docs: removes CODE_OF_CONDUCT.md (#1609)

Removes the code of conduct file to allow
inheritance from the organization level

Signed-off-by: Jennifer Power &lt;barnabei.jennifer@gmail.com&gt; ([`7ba70c3`](https://github.com/oscal-compass/compliance-trestle/commit/7ba70c3556e48b7b77333a132c8f47b3ea32df05))

### Feature

* feat: adds `x-trestle-add-props` to the YAML header in SSP markdown (#1534)

* feat: adds `x-trestle-add-prop` processing to CatalogReader for SSP

Signed-off-by: Jennifer Power &lt;barnabei.jennifer@gmail.com&gt;

* feat: adds ADD_PROP header to ssp in ControlWriter

Signed-off-by: Jennifer Power &lt;barnabei.jennifer@gmail.com&gt;

* docs: updates ssp authoring tutorial docs in website

Signed-off-by: Jennifer Power &lt;barnabei.jennifer@gmail.com&gt;

* fix: updates docstring on add-props test function

Signed-off-by: Jennifer Power &lt;barnabei.jennifer@gmail.com&gt;

* docs: adds info on ssp props usage to ssp authoring tutorial

Signed-off-by: Jennifer Power &lt;barnabei.jennifer@gmail.com&gt;

---------

Signed-off-by: Jennifer Power &lt;barnabei.jennifer@gmail.com&gt; ([`cf3e552`](https://github.com/oscal-compass/compliance-trestle/commit/cf3e552061ecc11b78751a29b4a09f1f04c1d5b0))

### Fix

* fix: Ensure codeql still runs on main (#1618) ([`b796c0d`](https://github.com/oscal-compass/compliance-trestle/commit/b796c0ddf87f972d8fd86dcccd34b7998abd7fea))

* fix: abstract python version in pipelines (#1612)



Signed-off-by: Chris Butler &lt;chris.butler@redhat.com&gt; ([`60b6452`](https://github.com/oscal-compass/compliance-trestle/commit/60b64524b8ddec97cd1977177551e13f856e8f4d))

* fix: correct vulnerabilities (#1611)

* fix: correct vulns

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;

* fix: add requests version

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;

* fix: correct datamodel code gen dependency

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;

---------

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt; ([`a68439d`](https://github.com/oscal-compass/compliance-trestle/commit/a68439daf05f5aac279de8dca59132d8b4e9af6a))

* fix: improve trestle v3 README important info (#1592)

* fix: improve trestle v3 README important info

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;

* add OSCAL models upgrade development info

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;

* Make mdformat happy.

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;

* relocate OSCAL migration section to contributing markdown

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;

* revise development status

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;

* make mdformat happy

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;

---------

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt; ([`0d7bc20`](https://github.com/oscal-compass/compliance-trestle/commit/0d7bc202389c85ec9f204ab2c45dac25a385a577))

* fix: use pydantic.v1 plugin for mypy (#1595)

* fix: use pydantic.v1 plugin for mypy

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;

* add mypy testcase

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;

* format &amp; lint

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;

* sanity check

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;

* explicitly specify mypy config file

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;

* add mypy.cfg

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;

* revise mypy.cfg

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;

---------

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt; ([`fdd3d34`](https://github.com/oscal-compass/compliance-trestle/commit/fdd3d34d6da975c60b6b3457b1a933048eeca91b))

* fix: update the regex of template version to prevent invalid version format (#1594)

Signed-off-by: Ma1h01 &lt;yihaomai@gmail.com&gt; ([`031850f`](https://github.com/oscal-compass/compliance-trestle/commit/031850f91a83f6fdd569025982a923cd10123938))

### Refactor

* refactor: update trestle documentation webpage&#39;s Demo section to be in sync with the demo repo (#1614)

* refactor: remove obsolete ISM demo

Signed-off-by: Ma1h01 &lt;yihaomai@gmail.com&gt;

* fix: fix the arc42 demo link

Signed-off-by: Ma1h01 &lt;yihaomai@gmail.com&gt;

* refactor: extend and finish the Task examples section

Signed-off-by: Ma1h01 &lt;yihaomai@gmail.com&gt;

---------

Signed-off-by: Ma1h01 &lt;yihaomai@gmail.com&gt; ([`e5d510e`](https://github.com/oscal-compass/compliance-trestle/commit/e5d510e830ae69839129cb28d15b36f6fbaa4a67))

* refactor: update the error message when set parameters have invalid values (#1581)

Signed-off-by: Ma1h01 &lt;yihaomai@gmail.com&gt;
Co-authored-by: AleJo2995 &lt;alejandro.leiva.palomo@ibm.com&gt; ([`7ef4319`](https://github.com/oscal-compass/compliance-trestle/commit/7ef431970fcfe5563895c1864c304e2221819ded))

### Unknown

* Merge pull request #1616 from oscal-compass/develop

chore: Trestle release ([`11e1a06`](https://github.com/oscal-compass/compliance-trestle/commit/11e1a061f1dfb7a9f87d09ed4a53b0a3fa0badd1))

## v3.2.0 (2024-06-18)

### Chore

* chore: Merge back version tags and changelog into develop. ([`d72f1fd`](https://github.com/oscal-compass/compliance-trestle/commit/d72f1fdfe26cd03a92d07aabfa6cde37ab41bc70))

### Documentation

* docs: updates README.md communication details (#1588)

Communication information is now centralized to
the community repo

Signed-off-by: Jennifer Power &lt;barnabei.jennifer@gmail.com&gt; ([`a44312c`](https://github.com/oscal-compass/compliance-trestle/commit/a44312ce48e22bd71de9c6780e773b13b13eb575))

### Feature

* feat: add risk properties support to csv-to-oscal-cd task (#1577)

* feat: add risk properties support to csv-to-oscal-cd task

Signed-off-by: Ma1h01 &lt;yihaomai@gmail.com&gt;

* fix: update the risk properties tests to mock the risk columns instead of creating a new csv file

Signed-off-by: Ma1h01 &lt;yihaomai@gmail.com&gt;

---------

Signed-off-by: Ma1h01 &lt;yihaomai@gmail.com&gt;
Co-authored-by: AleJo2995 &lt;alejandro.leiva.palomo@ibm.com&gt; ([`dbe8e05`](https://github.com/oscal-compass/compliance-trestle/commit/dbe8e051cd4ad2ab073438a4e837356924d6e062))

### Fix

* fix: correct old pyhton versions (#1572)

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt; ([`d6ca166`](https://github.com/oscal-compass/compliance-trestle/commit/d6ca1666c89a1ea5bfa54d4d242d0814e62668bd))

* fix: handle NonNegativeIntegerDatatype and PositiveIntegerDatatype in gen_oscal (#1584)

* fix: handle *IntegerDatatype during gen_oscal

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;

* fix: test cases for NonNegative and Postive IntegerDatatypes

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;

---------

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt; ([`888c9eb`](https://github.com/oscal-compass/compliance-trestle/commit/888c9eb0f6ae106fefd3f9667d4fc9fa74f51008))

* fix: correct the argument for get_rule_key in csv_to_oscal_cd.py (#1578)

* fix: correct the argument for get_rule_key in csv_to_oscal_cd.py

Signed-off-by: Ma1h01 &lt;yihaomai@gmail.com&gt;

* test: correct comments and add another assert statement to test the existence of wrong key

Signed-off-by: Ma1h01 &lt;yihaomai@gmail.com&gt;

---------

Signed-off-by: Ma1h01 &lt;yihaomai@gmail.com&gt;
Co-authored-by: AleJo2995 &lt;alejandro.leiva.palomo@ibm.com&gt; ([`774e3cf`](https://github.com/oscal-compass/compliance-trestle/commit/774e3cff89647a5e2fbd494d5ec5f352a0dd0671))

### Unknown

* Merge pull request #1593 from oscal-compass/develop

chore: Trestle release ([`8e7c490`](https://github.com/oscal-compass/compliance-trestle/commit/8e7c4905efd4eb174d2d9afe7f20c575bd3d2d52))

## v3.1.0 (2024-06-12)

### Chore

* chore: Merge back version tags and changelog into develop. ([`3d54f07`](https://github.com/oscal-compass/compliance-trestle/commit/3d54f07cad319cf6986dcc4c0abbbeec38b9bad7))

### Feature

* feat: logo (#1575)

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt; ([`b33490a`](https://github.com/oscal-compass/compliance-trestle/commit/b33490a24c93521568697fc582ae48bf4af71181))

* feat: modify task csv_to_oscal_cd to allow any case for heading in csv file (#1573)

Signed-off-by: Ma1h01 &lt;yihaomai@gmail.com&gt;
Co-authored-by: AleJo2995 &lt;alejandro.leiva.palomo@ibm.com&gt; ([`677c7ea`](https://github.com/oscal-compass/compliance-trestle/commit/677c7ea81d78c0d5356b3f0bb5b7563565a2938f))

### Fix

* fix: correct semantic release behaviour (#1564)

* fix: Update python-sem-ver

Signed-off-by: Chris Butler &lt;chris.butler@redhat.com&gt;

* fix: Update python semantic version to latest

Signed-off-by: Chris Butler &lt;chris.butler@redhat.com&gt;

* fix: Add uploading details

Signed-off-by: Chris Butler &lt;chris.butler@redhat.com&gt;

* fix: Add uploading details

Signed-off-by: Chris Butler &lt;chris.butler@redhat.com&gt;

* fix: clean up comments

Signed-off-by: Chris Butler &lt;chris.butler@redhat.com&gt;

---------

Signed-off-by: Chris Butler &lt;chris.butler@redhat.com&gt;
Co-authored-by: AleJo2995 &lt;alejandro.leiva.palomo@ibm.com&gt; ([`064274d`](https://github.com/oscal-compass/compliance-trestle/commit/064274d09b999767f0c5c58fbe854214f5674c43))

### Unknown

* Merge pull request #1582 from oscal-compass/develop

chore: release ([`d068eb4`](https://github.com/oscal-compass/compliance-trestle/commit/d068eb406eab240e7bd8eb648a35eb3e51c2a6c9))

## v3.0.1 (2024-06-03)

### Breaking

* fix: updated README.md - breaking change (#1566)

BREAKING CHANGE: for new release

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt; ([`7397105`](https://github.com/oscal-compass/compliance-trestle/commit/739710572f7d62a390b3a71fe3d06f080dfc8ebe))

### Chore

* chore: Merge back version tags and changelog into develop. ([`6635584`](https://github.com/oscal-compass/compliance-trestle/commit/66355845add54147edbb613cf2e4acb45ba37162))

* chore: Merge back version tags and changelog into develop. ([`72717f2`](https://github.com/oscal-compass/compliance-trestle/commit/72717f2eff7a7beb726c5d7abd5052496624e7d7))

### Documentation

* docs: updates communication details in README.md (#1537)

* docs: updates communication details in README.md

This is a seperate meeting/communication channel
from the Compliance WG adding new meeting details and slack channel

Signed-off-by: Jennifer Power &lt;barnabei.jennifer@gmail.com&gt;

* docs: add meeting notes link

Signed-off-by: Jennifer Power &lt;barnabei.jennifer@gmail.com&gt;

* fix: correct conversion link

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;

* fix: correct lint error

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;

---------

Signed-off-by: Jennifer Power &lt;barnabei.jennifer@gmail.com&gt;
Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;
Co-authored-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt; ([`eb459a2`](https://github.com/oscal-compass/compliance-trestle/commit/eb459a292abb7251ee6d321a81d46d041f2a9b0a))

### Feature

* feat: oscal nist upgrade (#1550)

* feat: support for latest OSCAL Version upgrade

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;

* feat: support OSCAL 1.1.2 (#1533)

* fix: hack component schema, moving metadata location to same as other
models

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;

* fix: add large line-length specification to pyptroject.toml for
datamodel-codegen

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;

* doc: discourse on changes made.

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;

* fix - automate schema metadata relocation in comp-def

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;

* fix: undo fwd refs

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;

* fix: HowMany

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;

* fix: update gen_oscal.md with info on automated schema relocations

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;

* fix: isolate schema fixup code

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;

* fix: preprocess improved move metadata &amp; assign Type4

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;

* fix implementations move to common issues

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;

* OSCAL_VERSION 1.1.2

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;

* dynamic year for copyright

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;

* fix: reorder by name pre-processing; some post-processing (hacking)

397 failed, 738 passed, 3 skipped, 34 warnings, 68 errors

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;

* fix: code format/lint

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;

* hack: reduce failed/errors

386 failed, 785 passed, 3 skipped, 34 warnings, 32 errors

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;

* fix: hack for EmailAddressDatatype

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;

* fix: issue hack warning/info

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;

* fix: handle special case of &#34;id: TokenDatatype&#34; in catalog

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;

* fix: introduce schema patching and employ for email-address and
parameter-selection

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;

* fix: handle RiskStatus properly when applying renaming

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;

* code format &amp; lint

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;

* fix: validation error for Base64

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;

* fix AttributeError: module &#39;trestle.oscal.ssp&#39; has no attribute &#39;Status&#39;

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;

* fix AttributeError: &#39;StringDatatype&#39; object has no attribute &#39;strip&#39;

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;

* fix Origin vs. Origin1

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;

* Add Observation to assessment_results from common

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;

* fix value is not a valid enumeration member

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;

* fix: import__test.py::test_import_wrong_oscal_version

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;

* patch schemas to rename “status” to “objectiveStatus” to avoid conflict

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;

* patch POAM schema to make RelatedObservation same as the other models

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;

* fix base 64 issue

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;

* fix: determine common TaskValidValues, ThreatIdValidValues

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;

* fix: improve pre-process reordering; handle special cases &amp; valid values

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;

* fix: nist content ssp example has moved and changed

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;

* fix: OSCAL version in data/tasks/xlsx/output/profile.json

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;

* fix tests/trestle/tasks/oscal_catalog_to_csv_test.py::test_execute

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;

* fix: code generation of URIReferenceDatatype

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;

* fix test_xlsx_execute_with_missing_rule_name_id

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;

* fix tests/trestle/tasks/xlsx_to_oscal_profile_test.py

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;

* fix tests/trestle/tasks/csv_to_oscal_cd_test.py

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;

* fix tests/trestle/tasks/ocp4_cis_profile_to_oscal_cd_test.py

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;

* fix: test_generate_sample_model - OscalVersion

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;

* fix TypeError: unhashable type: &#39;WithId&#39;

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;

* fix: logger.warn deprecation

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;

* fix :test_profile_alter_props - &#39;str&#39; object has no attribute &#39;value&#39;

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;

* fix: AssertionError: assert StringDatatype(__root__=&#39;1.1.2&#39;) == &#39;1.1.2&#39;

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;

* fix lint error

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;

* fix: get rid of python 3.7 use (hopefully)

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;

* fix: sonar exclude generated code (hopefully)

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;

* fix direct hack of NIST schema for EmailAddress (handle in “normalizer”)

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;

* fix direct hack of NIST schema for Selection (HowMany)

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;

* fix: add common valid values integrity check

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;

* rectification of property name changes (objective_status, originations)

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;

* TelephoneType and AddressType valid values

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;

* ExternalScheme and DocumentScheme valid values

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;

* DefinedComponentType valid values

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;

* SystemComponentType valid values

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;

* code comments

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;

* simplify pre-process code

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;

* simplify

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;

* remove unused code

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;

* replace deprecated pkg_resources with importlib_resources

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;

* Add python 3.10 to matrix

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;

* python 3.9, 3.10, 3.11

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;

* flake8 fix?

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;

* rename trestle.core.commands.author.profile to prof - lint shadow issue

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;

* update docs for change from author profile -&gt; prof

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;

* add comments explaining refs creation in schema preprocessing

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;

* switch to pydantic latest version, but force v1 interface use for now

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;

* fix: remedy 17 test warning by removing semantic release install

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;

* make sonar happy

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;

* make sonar happy

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;

* make sonar happy

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;

* use trestle.oscal.common.HowMany.one

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;

* supported versions of python are 3.9, 3.10. 3.11

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;

* reduce some duplication, as per reviewer&#39;s comments.

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;

* fix: remove unused parameters, per reviewer comments.

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;

* revise imports per reviewer suggestion.

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;

* 2.7.0

Automatically generated by python-semantic-release

* restore python-semantic-release==7.33.2 to cfg (at old level, for now)

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;

* Remove &#34;We&#39;ve moved&#34; from README

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;

* fix: handle allOf construct (#1546)

* fix: handle allOf construct

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;

* How did .value get removed in 2 places??

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;

* fix: merge &amp; modify

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;

* test use of PositionValidValues as both string and enum

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;

* make flake8 happy

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;

* fix: unify create_refs + body integrity check

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;

* remove use of extraneous constants

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;

---------

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;

---------

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;
Co-authored-by: semantic-release &lt;semantic-release&gt;

* remove extraneous workflow lines of code (#1555)

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;

* Improve comments in new schema pre-processing module

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;

* upgrade cmarkgfm version

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;

* cmarkgfm==0.8.*

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;

* trestle version should not be updated by hand!

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;

* cmarkgfm==0.6.*

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;

* remove 1.1.2 from dir name &amp; use tmp folder for fixup schemas

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;

* cmarkgfm==0.8.* works locally...

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;

* cmarkgfm==2024.1.* works locally

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;

* pydantic &gt;= 2.0.0

* remove extraneous optional specifications

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;

---------

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;
Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;
Co-authored-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt; ([`82caf5f`](https://github.com/oscal-compass/compliance-trestle/commit/82caf5fe08796e10532410299d2032b2be7e7d61))

### Fix

* fix: reverting last serm ver changes

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt; ([`9df0703`](https://github.com/oscal-compass/compliance-trestle/commit/9df0703aa925af836a8e07dcb45ed6db31daae11))

* fix: revert sem release changelog and version

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt; ([`01427df`](https://github.com/oscal-compass/compliance-trestle/commit/01427df909cb8e3a25d46ba8e3c9049533d65a6b))

* fix: correct sonar quality checks (#1568)

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt; ([`7f93f86`](https://github.com/oscal-compass/compliance-trestle/commit/7f93f86ac384d3c68b801a24e166fd1774c31103))

* fix: remove obsolete text, fix broken links, fix spelling (#1565)

* fix: remove obsolete text, fix broken links, fix spelling

Signed-off-by: semantic-release (via Github actions) &lt;semantic-release@github-actions&gt;

* fix: revised important note

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;

* make mdformat happy.

Signed-off-by: Lou Degenaro &lt;lou.degenaro@gmail.com&gt;

---------

Signed-off-by: semantic-release (via Github actions) &lt;semantic-release@github-actions&gt;
Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;
Signed-off-by: Lou Degenaro &lt;lou.degenaro@gmail.com&gt;
Co-authored-by: semantic-release (via Github actions) &lt;semantic-release@github-actions&gt; ([`0955b4b`](https://github.com/oscal-compass/compliance-trestle/commit/0955b4b23537ea7d19d3902a7ff9e7c7e442a135))

* fix: BREAKING CHANGE (#1560)

* fix: BREAKING CHANGE

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;

* fix: BREAKING CHANGE

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;

* fix: correct wording

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;

---------

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt; ([`f714b12`](https://github.com/oscal-compass/compliance-trestle/commit/f714b12d179a2e83f9ef4c1904668a67ed936c3f))

* fix: zoom link (#1530)

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt; ([`95ff6b7`](https://github.com/oscal-compass/compliance-trestle/commit/95ff6b7f53ab325ec106c47d28a44f5e70f5f964))

### Unknown

* Merge pull request #1567 from oscal-compass/develop

chore: Trestle release ([`c8be4ab`](https://github.com/oscal-compass/compliance-trestle/commit/c8be4ab948db048c8e3802b890abedc7de8733bc))

## v2.6.1 (2024-02-22)

### Chore

* chore: Merge back version tags and changelog into develop. ([`11fbcda`](https://github.com/oscal-compass/compliance-trestle/commit/11fbcdaeb1173ba131c20df6ba5be66bfc997b23))

### Fix

* fix: correct vuln for cryptography (#1520)

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt; ([`353cc2b`](https://github.com/oscal-compass/compliance-trestle/commit/353cc2b75e611b9d851cca2022f4e0fbe2936d16))

### Unknown

* Merge pull request #1521 from oscal-compass/develop

chore: Trestle release ([`f097029`](https://github.com/oscal-compass/compliance-trestle/commit/f097029392963643932f471dbc7c1e6baec91896))

## v2.6.0 (2024-02-22)

### Chore

* chore: Merge back version tags and changelog into develop. ([`6b2412e`](https://github.com/oscal-compass/compliance-trestle/commit/6b2412e7e0e34fdc32a5e1af06c3bdc46a7687e8))

### Feature

* feat: multiple parms per rule (#1499)

* feat: multiple parameters per rule

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;

* fix: use correct columns names list

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;

* fix: add test for multi-parameters per rule

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;

* fix: a bit more on parameter sets in the help

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;

* fix: code smell

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;

* fix: test for modification to additional parameter set value

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;

* fix: test for delete of additional param set

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;

---------

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt; ([`218ffe4`](https://github.com/oscal-compass/compliance-trestle/commit/218ffe47a879e8bbca115bd956cfc9e99bbc5751))

### Fix

* fix: add multiple parameters per rule support on component definition (#1504)

* fix: add multiple parameters per rule in component definition

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;

* fix: correct code linting errors

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;

* fix: adding more testing

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;

* fix: add a value for the rule parameter in tests

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;

* fix: correct tests and add code for dup components validation

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;

* fix: correct quality gate error

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;

* fix: correct typo and fix test description

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;

* fix: correct typo

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;

---------

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt; ([`96e3f02`](https://github.com/oscal-compass/compliance-trestle/commit/96e3f02fc597ded59ed11f5bd2b07aa2c0ccb504))

* fix: community call (#1516)

* fix: update community call information

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;

* fix: removing unneded separators

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;

* fix: community meetings

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;

* fix: agenda and notes

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;

* fix: use every other Tue.; add login notes &amp; calendar link

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;

* fix: make mdformat happy.

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;

* fix: update calendar info

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;

* fix: add a passcode to zoom meeting

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;

* fix: correct wording for zoom login

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;

* fix: correct format check

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;

* fix: rephrase login options

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;

---------

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;
Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;
Co-authored-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt; ([`53d7fd4`](https://github.com/oscal-compass/compliance-trestle/commit/53d7fd484bdd42e22ff58e3244da732835c2cfea))

* fix: correct vulnerability (#1509)

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;
Co-authored-by: mrgadgil &lt;49280244+mrgadgil@users.noreply.github.com&gt; ([`4f70e0a`](https://github.com/oscal-compass/compliance-trestle/commit/4f70e0af0e4063ac3cd763ff0c7e319168c0d805))

* fix: add check for empty label to fix failure for statement with no label property (#1507)

* test: adds test for ssp assemble with fedramp profile

Signed-off-by: Jennifer Power &lt;barnabei.jennifer@gmail.com&gt;

* fix: adds fix for parts with no label during ssp-assemble

Signed-off-by: Jennifer Power &lt;barnabei.jennifer@gmail.com&gt;

* fix: don&#39;t put empty label into map

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;

* fix: make sonar happy -&gt; reduce complexity

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;

---------

Signed-off-by: Jennifer Power &lt;barnabei.jennifer@gmail.com&gt;
Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;
Co-authored-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt; ([`55ed462`](https://github.com/oscal-compass/compliance-trestle/commit/55ed462107d577efc9099b8ed59c5718eee9e47c))

### Unknown

* Merge pull request #1519 from oscal-compass/develop

chore: Trestle release ([`1987260`](https://github.com/oscal-compass/compliance-trestle/commit/198726001c6ea1911b11c1757f219eca032a46ad))

## v2.5.1 (2024-01-18)

### Chore

* chore: Merge back version tags and changelog into develop. ([`64c819a`](https://github.com/oscal-compass/compliance-trestle/commit/64c819a3b76acb3fb06396afc1f7fe2897ec1dab))

### Fix

* fix: correct security vulnerability (#1498)

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt; ([`e23792c`](https://github.com/oscal-compass/compliance-trestle/commit/e23792cb1cde490fa2951866c9f99f9d43e9c669))

### Unknown

* Merge pull request #1501 from oscal-compass/develop

chore: Trestle release ([`7966956`](https://github.com/oscal-compass/compliance-trestle/commit/79669569572b8777c3ef1b1b6663c99af4002bff))

## v2.5.0 (2024-01-05)

### Chore

* chore: Merge back version tags and changelog into develop. ([`5ac3067`](https://github.com/oscal-compass/compliance-trestle/commit/5ac3067ad2e81eb3b0d31f2d3f05a12b44ec1072))

### Feature

* feat: add parameter value origin field to parameters (#1470)

* feat: add parameter value origin field to parameters

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;

* fix: remove wrong added field from oscal model

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;

* fix: add param_value_origin to props and add validations

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;

* fix: correct ci

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;

* fix: correct param value origin cycle

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;

* fix: correct profile-param-value-origin flow

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;

* fix: adding final corrections and test for inherited param-value-origin

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;

* fix: correct formating

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;

* fix: add step to ignore param-value-origin if no replacement was done in profile-param-value-origin

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;

* fix: correct code format

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;

* fix: correct tests

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;

* fix: use replace me placeholder instead of literal text

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;

* fix: use replace me tag in default value for param-value-origin

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;

* fix: correct code format

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;

---------

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt; ([`b86aa2b`](https://github.com/oscal-compass/compliance-trestle/commit/b86aa2b5ef97a8fd988efb8ec995fb0624af6db0))

* feat: allow use of OpenSCAP result files in task xccdf_result_to_oscal_ar (#1411)

* feat: Allow use of OpenSCAP result files in task xccdf_result_to_oscal_ar

Before this commit if you wanted to use result files from OpenSCAP
in the task xccdf_result_to_oscal_ar you had to extract the
`TestResult` element and place it as the root of the XML
document, otherwise the resulting OSCAL document would be
blank. Thus making it impossible to directly use output from
OpenSCAP with the task.

With this commit the task will detect that the root element
is not `TestResult` and then it will find the `TestResult`
element in the XML document. This allows the use of files
created by OpenSCAP using the `--results` and `--results-arf`
switches.

Signed-off-by: Matthew Burket &lt;mburket@redhat.com&gt;

* Add tests for OpenSCAP results files for task xccdf_result_to_oscal_ar_test

Signed-off-by: Matthew Burket &lt;mburket@redhat.com&gt;

---------

Signed-off-by: Matthew Burket &lt;mburket@redhat.com&gt; ([`eeb715c`](https://github.com/oscal-compass/compliance-trestle/commit/eeb715c4cd86c3bd5183592c03beac1cc46859d9))

* feat: add inheritance view to ssp-generate and ssp-assemble (#1441)

* feat: adds ability to process exports from SSP and write Markdown by component

Adds ExportInterface and ExportWriter classes
Adds Markdown generation to ssp-generate
Add MarkdownWriter for leveraged statements

Signed-off-by: Jennifer Power &lt;barnabei.jennifer@gmail.com&gt;
Signed-off-by: Alex Flom &lt;alexander.flom@gmail.com&gt;

* feat: adds InheritanceMarkdownReader for reading leveraged statement markdown

Adds InheritanceMarkdownReader for processing into a leveraging SSP context
Adds persistance for components and satisified statements during updates
Changes leveraging component from a single dictionary to a list

Signed-off-by: Jennifer Power &lt;barnabei.jennifer@gmail.com&gt;

* feat: Adds reader class for inheritance markdown

Adds ExportReader class
Removes ExportInterface class
Adds a single ByComponentInterface class to interact with the model
in terms of inheritance

Signed-off-by: Jennifer Power &lt;barnabei.jennifer@gmail.com&gt;

Co-authored-by: Jennifer Power &lt;barnabei.jennifer@gmail.com&gt;

* docs: updates documentation with usage and API references updates for inheritance

Signed-off-by: Jennifer Power &lt;barnabei.jennifer@gmail.com&gt;

* chore: updates AgileAuthoring class for ssp-generate arg changes

Signed-off-by: Jennifer Power &lt;barnabei.jennifer@gmail.com&gt;

* docs: updates returns section in InheritanceMarkdownReader docstring

Signed-off-by: Jennifer Power &lt;barnabei.jennifer@gmail.com&gt;

* fix: updates line length on return statement in InheritanceMarkdownReader

Signed-off-by: Jennifer Power &lt;barnabei.jennifer@gmail.com&gt;

* refactor: updates markdown heading and comment strip function to remove regex

Signed-off-by: Jennifer Power &lt;barnabei.jennifer@gmail.com&gt;

* test: adds inheritance view testing for ssp-assemble

Signed-off-by: Jennifer Power &lt;barnabei.jennifer@gmail.com&gt;

* chore: adds more context to ExportReader class comments

Signed-off-by: Jennifer Power &lt;barnabei.jennifer@gmail.com&gt;

* feat: updates ssp-generate to filter control implementation for leveraged_ssp

Signed-off-by: Jennifer Power &lt;barnabei.jennifer@gmail.com&gt;

* refactor: updates ExportWriter to reduce code duplication

Signed-off-by: Jennifer Power &lt;barnabei.jennifer@gmail.com&gt;

* fix: updates ExportReader to add new statements if present in the inheritance view

Signed-off-by: Jennifer Power &lt;barnabei.jennifer@gmail.com&gt;

* fix: update logging to debug in ExportReader

Signed-off-by: Jennifer Power &lt;barnabei.jennifer@gmail.com&gt;

* refactor: simplify code in read_exports_from_markdown

Signed-off-by: Jennifer Power &lt;barnabei.jennifer@gmail.com&gt;

* tests: simplify tests for ExportReader test data generation

Signed-off-by: Jennifer Power &lt;barnabei.jennifer@gmail.com&gt;

* refactor: reduce code duplication in ExportReader methods

Signed-off-by: Jennifer Power &lt;barnabei.jennifer@gmail.com&gt;

* fix: allows inheritance info to be removed when component is unmapped

Signed-off-by: Jennifer Power &lt;barnabei.jennifer@gmail.com&gt;

* feat: adds leveraged authorization updates to system implementation

Adds SSPInheritanceAPI class for interacting with leveraged auth
information

Adds trestle global tags to markdown to store SSP location info

Signed-off-by: Jennifer Power &lt;barnabei.jennifer@gmail.com&gt;

Co-authored-by: Alex Flom &lt;alexander.flom@gmail.com&gt;

* docs: add docs updates for SSPInheritanceAPI class

Signed-off-by: Jennifer Power &lt;barnabei.jennifer@gmail.com&gt;

* chore: updates warning message for leveraged authorization with comps

Signed-off-by: Jennifer Power &lt;barnabei.jennifer@gmail.com&gt;

* fix: updates ssp-assemble to ensure existing leveraged comps persist

Signed-off-by: Jennifer Power &lt;barnabei.jennifer@gmail.com&gt;

* fix: adds fixes to address PR feedback

Signed-off-by: Jennifer Power &lt;barnabei.jennifer@gmail.com&gt;

* refactor: polishes SSPInheritanceAPI class to reduce complexity

Signed-off-by: Jennifer Power &lt;barnabei.jennifer@gmail.com&gt;

---------

Signed-off-by: Jennifer Power &lt;barnabei.jennifer@gmail.com&gt;
Signed-off-by: Alex Flom &lt;alexander.flom@gmail.com&gt;
Co-authored-by: Alex Flom &lt;aflom@redhat.com&gt;
Co-authored-by: Alex Flom &lt;alexander.flom@gmail.com&gt; ([`6cf498b`](https://github.com/oscal-compass/compliance-trestle/commit/6cf498b26aa2a2d583714470038291b0567fb80a))

### Fix

* fix: correct empty values going in assembled profile (#1491)

* fix: correct empty values going in assembled profile

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;

* fix: add test case to check profile values replaced

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;

---------

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt; ([`136b712`](https://github.com/oscal-compass/compliance-trestle/commit/136b712cfaf0392ae5673a6103700014d27b2866))

* fix: correct vulnerability (#1486)

* fix: correct critical vulnerability

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;

* fix: correcting vulnerability

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;

---------

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt; ([`4610d24`](https://github.com/oscal-compass/compliance-trestle/commit/4610d247516c7ddc37a1b1774b31fbfb9f5012fa))

* fix: move to new org (#1483)

* fix: move to new org

github.com/IBM -&gt; github.com/oscal-compass
ibm.github.io -&gt; oscal-compass.github.io

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;

* fix: run make mdformat

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;

* fix: correct missing org changes

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;

---------

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;
Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;
Co-authored-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt; ([`c456779`](https://github.com/oscal-compass/compliance-trestle/commit/c4567792cc62b7e9e85c8dca0ce2d26fe82fcbc6))

* fix: sonar (#1481)

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt; ([`4e7e8fd`](https://github.com/oscal-compass/compliance-trestle/commit/4e7e8fd6618852dcceb4b464a7cabc91154e171a))

* fix: correct critical vulnerability (#1479)

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt; ([`72b0f6f`](https://github.com/oscal-compass/compliance-trestle/commit/72b0f6f132fe7f6ed20fd29e47e13656082c0d29))

* fix: link main readme to agile authoring setup repo (#1477)

* fix: link main readme to agile authoring setup repo

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;

* fix: docs validate

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;

---------

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt; ([`88c1606`](https://github.com/oscal-compass/compliance-trestle/commit/88c16064897644db03aab11799a6dfc31ec8a1d2))

* fix(tests): pins oscal-content references in tests the latest 1.0 commit (#1474)

Signed-off-by: Jennifer Power &lt;barnabei.jennifer@gmail.com&gt; ([`0dc7551`](https://github.com/oscal-compass/compliance-trestle/commit/0dc755184fb8c061cacc90cc930ea7b0c43f2b7c))

### Unknown

* Merge pull request #1492 from oscal-compass/develop

chore: Trestle release ([`e6c42fa`](https://github.com/oscal-compass/compliance-trestle/commit/e6c42fad64855796fe21ca082cfc1c9fa879a2e9))

* fix - trestle direct dependency on requests pkg (#1488)

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt; ([`c112f9c`](https://github.com/oscal-compass/compliance-trestle/commit/c112f9cf1ec9ff5228b58a4383beb5f9684b9591))

## v2.4.0 (2023-10-26)

### Chore

* chore: Trestle release

chore: Trestle release ([`041a267`](https://github.com/oscal-compass/compliance-trestle/commit/041a267027e6023e477808934ba0727e411a5810))

* chore: Merge back version tags and changelog into develop. ([`a633327`](https://github.com/oscal-compass/compliance-trestle/commit/a63332709d49e54a4cd541e6afdb02b232cbce7d))

### Documentation

* docs: updating vtt documentation for trestle author docs (#1471)

* docs: updating vtt documentation for trestle author docs

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;

* fix: correct wording

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;

---------

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt; ([`63d436a`](https://github.com/oscal-compass/compliance-trestle/commit/63d436a7752e50ef0c52c93cbab36f4c1fc16748))

### Feature

* feat: adding validate template type to author docs command (#1465)

* feat: adding validate template type to author docs command

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;

* fix: rename test cases files to be more generic

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;

---------

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt; ([`5289f51`](https://github.com/oscal-compass/compliance-trestle/commit/5289f516e9710361e0dc391cefd979b5e2d46ed0))

### Fix

* fix: upgrade urllib version to fix vulnerability (#1472)

* fix: upgrade urllib version to fix vulnerability

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;

* fix: correct typo

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;

---------

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt; ([`e9d4175`](https://github.com/oscal-compass/compliance-trestle/commit/e9d4175fabd015ada6e8cdd26450c454ad83fbe8))

* fix: improve bad property error message by including csv row number (#1466)

* fix: improve bad property error message by including csv row number

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;

* fix: handle empty ProfileSource correctly

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;

* fix sonar code smells

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;

* fix sonar code smell

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;

---------

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt; ([`ab97beb`](https://github.com/oscal-compass/compliance-trestle/commit/ab97beb2367112e9e68fb258af6dc2c75d909279))

* fix: cryptic error message + feat: # indicates comment column (#1459)

* Fix: improve error message when invalid property value specified

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;

* feat: support #column heading name ignored

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;

---------

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt; ([`45eda01`](https://github.com/oscal-compass/compliance-trestle/commit/45eda015751d2f9121e14fe609b14acd890440fd))

* fix: update community call information (#1444)

* fix: update community call information

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;

* fix: extending timeout time test

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;

* fix: correct link

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;

* fix: update community call info

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;

* fix: remove unnecesary details on meeting host

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;

---------

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt; ([`5a03d06`](https://github.com/oscal-compass/compliance-trestle/commit/5a03d06783fff8db4bf402b1e21acb99fd485454))

## v2.3.1 (2023-09-20)

### Chore

* chore: Merge back version tags and changelog into develop. ([`420f341`](https://github.com/oscal-compass/compliance-trestle/commit/420f3410fccfcf1b3ddd606962290c9abed5ec2e))

### Fix

* fix: improper indentation structure validation not working (#1451)

* fix: improper indentation structure test

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;

* fix: addition to full profile

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;

* fix: correct profile generation issue

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;

* fix: correcting format

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;

* fix: adding new line each prose subpart gets added to final subpart

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;

* fix: correcting top comment on profile values comment

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;

---------

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt; ([`2e6936a`](https://github.com/oscal-compass/compliance-trestle/commit/2e6936a4705251fd8412fd67163a7cd9d801a4b8))

* fix: fixing typo in encoding name (#1448)

Co-authored-by: AleJo2995 &lt;alejandro.leiva.palomo@ibm.com&gt; ([`bdf60b2`](https://github.com/oscal-compass/compliance-trestle/commit/bdf60b26075f7250bcdbbe08745630b27042ad74))

* fix: parameter aggregation fix (#1443)

* fix: parameter aggregation fix

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;

* fix: arranging tests

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;

* fix: triggering build

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;

* fix: increase time out for cache response

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;

* fix: profile-values are shown in markdown even when there are values already

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;

* fix: adding alt identifier validation

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;

* fix: correct profile values validation

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;

* fix: remove parameter aggregation from assembly and remove label being shown in assembled profile

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;

* fix: correcting test failures and various formatting issues

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;

* fix: change order for parameters in markdown

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;

* fix: not setting empty values

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;

---------

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt; ([`dd9e3bc`](https://github.com/oscal-compass/compliance-trestle/commit/dd9e3bc2ebaeab23f3c4fc0647ec3942d38bed16))

* fix: prevent duplicates in set-parameters (#1450)

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt; ([`62e2f05`](https://github.com/oscal-compass/compliance-trestle/commit/62e2f059dd2ae08616895ebdfd6e37258483019d))

### Unknown

* Merge pull request #1452 from IBM/develop

chore: Trestle release ([`dd94dd8`](https://github.com/oscal-compass/compliance-trestle/commit/dd94dd8723bd23508504f789458510de6ae7c3d0))

## v2.3.0 (2023-09-06)

### Chore

* chore: Merge back version tags and changelog into develop. ([`3ea6add`](https://github.com/oscal-compass/compliance-trestle/commit/3ea6add2319bad28630afdcb9602c6b8e53fb125))

* chore: adds typing fixes in profile.py for ProfileInherit (#1433)

Signed-off-by: Jennifer Power &lt;barnabei.jennifer@gmail.com&gt;
Co-authored-by: AleJo2995 &lt;alejandro.leiva.palomo@ibm.com&gt; ([`0593651`](https://github.com/oscal-compass/compliance-trestle/commit/0593651a6da82b3a73163e79ce376134e93a84a4))

* chore: Merge back version tags and changelog into develop. ([`4f90258`](https://github.com/oscal-compass/compliance-trestle/commit/4f90258fc4490463de926fc77934d82b3ee6e7ac))

### Feature

* feat: extend multiple templates validation to trestle author folders (#1430)

* feat: extend multiple templates validation to trestle author folders command

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;

* docs: adding documentation to ne feature

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;

* fix: addressing validation through name of template instead of type field

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;

* fix: update guidance to correct wording

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;

* fix: add x trestle ignore field in header to correct mismatch

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;

* fix: correcting mdformat

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;

* fix: correct code linting problem

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;

* fix: return template type field to template header

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;

* docs: correcting documentation for x-trestle-template-type field

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;

---------

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt; ([`c7bef58`](https://github.com/oscal-compass/compliance-trestle/commit/c7bef589a6e671b96170e93feb88c6436a094da6))

* feat: adds agile authoring functionality to public API in repository.py (#1432)

Fixes #1426

Signed-off-by: Jennifer Power &lt;barnabei.jennifer@gmail.com&gt;
Co-authored-by: AleJo2995 &lt;alejandro.leiva.palomo@ibm.com&gt; ([`08b2559`](https://github.com/oscal-compass/compliance-trestle/commit/08b255902efb911c99422d49920c5ddaea98ef32))

* feat: support validation component_type for task csv-to-oscal-cd (#1431)

* feat: Support &#34;validation&#34; component_type for task csv-to-oscal-cd

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;

* fix sonar code smell

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;

* add notes to -i output regarding required/ignored columns

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;

* user properties for both validation and non-validation components

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;

---------

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;
Co-authored-by: AleJo2995 &lt;alejandro.leiva.palomo@ibm.com&gt; ([`80aaa72`](https://github.com/oscal-compass/compliance-trestle/commit/80aaa72fe96217d1c7dd93e4c1d5bd9c34cb012b))

### Fix

* fix: correcting typo

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt; ([`1810007`](https://github.com/oscal-compass/compliance-trestle/commit/181000731ada7af1348219581994bd58f2285329))

* fix: correcting python semantice release version

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt; ([`a8cb9b9`](https://github.com/oscal-compass/compliance-trestle/commit/a8cb9b9f1f11485ac70fa2f35a3e52b917b7a783))

* fix: moving watch config a level up (#1447)

* fix: moving watch config a level up

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;

* fix: disable check for changes build to make the change in mkdocs config

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;

* fix: revert changes

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;

* fix: change mkdocs version

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;

* fix: fix typo

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;

* fix: downgrade version to 1.5.0

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;

* fix: change mkdocstrings version to stable

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;

* fix: change mkdocs to pull latest version

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;

---------

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt; ([`ea5607f`](https://github.com/oscal-compass/compliance-trestle/commit/ea5607f9f404f38da1abf1c40f907196ea79c567))

* fix: xccdf parameter type (#1440)

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt; ([`431670c`](https://github.com/oscal-compass/compliance-trestle/commit/431670cd468693ca4581ec43d8de5d32413ec113))

* fix: headings levels validation is not working properly (#1436)

* fix: heading levels validation fixing

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;

* fix: correcting test cases and adding extra validation

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;

---------

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt; ([`22b65a9`](https://github.com/oscal-compass/compliance-trestle/commit/22b65a9b84af36d8c12c32c6e5c0dae88208ea49))

* fix: default set-parameter values as list (#1438)

* fix: default set-parameter values as list

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;

* fix string to list comment and blanks removal

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;

---------

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt; ([`419025d`](https://github.com/oscal-compass/compliance-trestle/commit/419025dfad47cf9f61b5e20a35a9683a84ed26e8))

* fix: expected nist profile missing (#1435)

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt; ([`c96f9ce`](https://github.com/oscal-compass/compliance-trestle/commit/c96f9ce82e453c83a07d9d4c1061833f38c7f104))

* fix: provide description and meaning to parameters in markdown (#1423)

* fix: provide description and meaning to parameters in markdown

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;

* fix: undo unneded removal to pass test cases

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;

* fix: ordering list of parameter values displayed in markdown

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;

---------

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt; ([`266f67b`](https://github.com/oscal-compass/compliance-trestle/commit/266f67bd220e15922caacb4de0e702f4d0927ceb))

### Unknown

* Merge pull request #1445 from IBM/develop

chore: Trestle release ([`73e125d`](https://github.com/oscal-compass/compliance-trestle/commit/73e125ded8cccada508fe7466ecd328847483b8f))

## v2.2.1 (2023-07-05)

### Chore

* chore: Merge back version tags and changelog into develop. ([`e9dad2b`](https://github.com/oscal-compass/compliance-trestle/commit/e9dad2b7888332a6cf63b82670946f9492f27023))

### Fix

* fix: parameter value default is never required (#1419)

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt; ([`01434f1`](https://github.com/oscal-compass/compliance-trestle/commit/01434f13b16054b035767985a9a02ed9fa91154f))

* fix: pydantic 2.0.0 break unit tests (#1418)

* fix: pydantic 2.0.0 break unit tests

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;

* fix minimum pydantic version

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;

---------

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;
Co-authored-by: AleJo2995 &lt;alejandro.leiva.palomo@ibm.com&gt; ([`2138831`](https://github.com/oscal-compass/compliance-trestle/commit/2138831f9bb36c5f91ab17cccc4412128c468a82))

* fix: adding parameter aggregation from other parameter values for given control (#1412)

* feat: adding parameter aggregation functionality

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;

* fix: fix code complexity

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;

* fix: reduce code complexity

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;

* fix: add parameters for test cases and reduce code complexity

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;

* fix: fixing tests merge

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;

* fix: correct code lint

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;

---------

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt; ([`7b8cad0`](https://github.com/oscal-compass/compliance-trestle/commit/7b8cad03e05024a406742720e5abed2e3febdf6f))

* fix: assessment objectives formatting in markdown is not correct (#1414)

* fix: assessment objectives formatting in markdown is not correct

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;

* fix: remove unneded variable

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;

---------

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt; ([`dbfc1d6`](https://github.com/oscal-compass/compliance-trestle/commit/dbfc1d6c59339a7f542f86cb74da4f05fe8a9a60))

### Unknown

* Merge pull request #1420 from IBM/develop

chore: Trestle release ([`2a0d40f`](https://github.com/oscal-compass/compliance-trestle/commit/2a0d40fada48b6263e6ce738ec94d930e94c4607))

## v2.2.0 (2023-06-26)

### Chore

* chore: Merge back version tags and changelog into develop. ([`1037c8e`](https://github.com/oscal-compass/compliance-trestle/commit/1037c8e35a31528a2610160a68f46f999e36d170))

### Documentation

* docs: update maintainers list (#1394) ([`c53faa4`](https://github.com/oscal-compass/compliance-trestle/commit/c53faa40ce23a5ad5476cbb6e2c3d32a8e6818dc))

### Feature

* feat: add profile-inherit command (#1392)

* test: adds testdata for profile init tests

Signed-off-by: Jennifer Power &lt;barnabei.jennifer@gmail.com&gt;

* feat(cli): adds profile-seed command

Adds profile-seed as author subcommand
Adds profile-seed unit test
Adds SSP testdata

Closes #1388

Signed-off-by: Jennifer Power &lt;barnabei.jennifer@gmail.com&gt;

* chore: updates flag wording in profile.py

Signed-off-by: Jennifer Power &lt;barnabei.jennifer@gmail.com&gt;

* test: adds test case for profile-seed

Adds additional test case to check for ids output
when all controls are filtered out

Signed-off-by: Jennifer Power &lt;barnabei.jennifer@gmail.com&gt;

* test: updates description leveraged ssp testdata

Signed-off-by: Jennifer Power &lt;barnabei.jennifer@gmail.com&gt;

* docs: updates author and tutorial docs with information on profile-seed command

Signed-off-by: Jennifer Power &lt;barnabei.jennifer@gmail.com&gt;

* chore: updates command to profile-inherit in docs and code

Signed-off-by: Jennifer Power &lt;barnabei.jennifer@gmail.com&gt;

* feat: adds excluded controls to the profile-inherit generated profile

Signed-off-by: Jennifer Power &lt;barnabei.jennifer@gmail.com&gt;

* docs: adds JSON example of profile-inherit import to website docs

Signed-off-by: Jennifer Power &lt;barnabei.jennifer@gmail.com&gt;

* chore: adds PR feedback on styling

Signed-off-by: Jennifer Power &lt;barnabei.jennifer@gmail.com&gt;

---------

Signed-off-by: Jennifer Power &lt;barnabei.jennifer@gmail.com&gt; ([`3bd53ff`](https://github.com/oscal-compass/compliance-trestle/commit/3bd53ff370cece77fc78082dbc04304af12c6647))

* feat: oscal-catalog-to-csv (#1396)

* feat: oscal-catalog-to-csv

Signed-off-by: degenaro &lt;lou.degenaro@gmail.com&gt;

* Populate testing spot checks.

Signed-off-by: degenaro &lt;lou.degenaro@gmail.com&gt;

* fix validate

Signed-off-by: degenaro &lt;lou.degenaro@gmail.com&gt;

* Use &#39;w&#39; for output file open.

Signed-off-by: degenaro &lt;lou.degenaro@gmail.com&gt;

* fix windows csv.

Signed-off-by: degenaro &lt;lou.degenaro@gmail.com&gt;

* Fix sonar complaints + improved test coverage

Signed-off-by: degenaro &lt;lou.degenaro@gmail.com&gt;

* Fix sonar complaint.

Signed-off-by: degenaro &lt;lou.degenaro@gmail.com&gt;

* Improve test coverage.

Signed-off-by: degenaro &lt;lou.degenaro@gmail.com&gt;

* 100% test coverage.

Signed-off-by: degenaro &lt;lou.degenaro@gmail.com&gt;

---------

Signed-off-by: degenaro &lt;lou.degenaro@gmail.com&gt; ([`5f59a7f`](https://github.com/oscal-compass/compliance-trestle/commit/5f59a7fc7cf8b88a9f77ba4554dd493acff67114))

* feat: adds control origination to ssp-filter (#1375)

* feat(cli): adds logic to filter ssp by control origination

Adds test to test one and multiple control origination value inputs
Adds test to test bad control origintation value input
Adds filtering logic to ssp.py

Closes #1361

Signed-off-by: Jennifer Power &lt;barnabei.jennifer@gmail.com&gt;

* docs: updates trestle author docs with ssp-filter changes for control origination

Signed-off-by: Jennifer Power &lt;barnabei.jennifer@gmail.com&gt;

* fix: updates control origination flag value in ssp.py

Signed-off-by: Jennifer Power &lt;barnabei.jennifer@gmail.com&gt;

* fix: adds break to remove duplicate implemented requirements

When filtering for control origination, the property could be
specified more than one time. This change adds a break and changes
to the test component defintion to ensure this case is covered.

Signed-off-by: Jennifer Power &lt;barnabei.jennifer@gmail.com&gt;

---------

Signed-off-by: Jennifer Power &lt;barnabei.jennifer@gmail.com&gt; ([`509afa7`](https://github.com/oscal-compass/compliance-trestle/commit/509afa7df124f8a6c3516ad06db256777baaef98))

### Fix

* fix: drop python 3.7 support as required 

Adding extra steps to run builds on optional for 3.7.16 on macos latest and 3.7 for windows and ubuntu ([`cf4160b`](https://github.com/oscal-compass/compliance-trestle/commit/cf4160bc25336cb9362150906a8aaeda308c4134))

* fix: Change the community call to use bluejeans events (#1400)

Co-authored-by: AleJo2995 &lt;alejandro.leiva.palomo@ibm.com&gt; ([`9380cc8`](https://github.com/oscal-compass/compliance-trestle/commit/9380cc813f8b044640fecb4ee302207d3c66d29a))

* fix: python 3.7.17 issue (#1408)

* fix: python 3.7.17 issue

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;

* fix: python 3.7.17 issue

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;

---------

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt; ([`6849c3b`](https://github.com/oscal-compass/compliance-trestle/commit/6849c3b01d0adfd1261b9929a7d5c1866dd38973))

* fix: log warning for duplicate part ids when writing markdown from json (#1395)

* fix: use empty string if part prose is None

Signed-off-by: Sharma-Amit &lt;Sharma.Amit@ibm.com&gt;

* test: add test for checking no prose in part

Signed-off-by: Sharma-Amit &lt;Sharma.Amit@ibm.com&gt;

* fix: write warning instead of exit with code 1 when duplicate parts

Signed-off-by: Sharma-Amit &lt;Sharma.Amit@ibm.com&gt;

---------

Signed-off-by: Sharma-Amit &lt;Sharma.Amit@ibm.com&gt; ([`760dd4b`](https://github.com/oscal-compass/compliance-trestle/commit/760dd4b4dd6ac405df3db0c2d39d9973ab61a0f4))

* fix: use empty string if prose in part is None while writing to markdown (#1390)

* fix: use empty string if part prose is None

Signed-off-by: Sharma-Amit &lt;Sharma.Amit@ibm.com&gt;

* test: add test for checking no prose in part

Signed-off-by: Sharma-Amit &lt;Sharma.Amit@ibm.com&gt;

---------

Signed-off-by: Sharma-Amit &lt;Sharma.Amit@ibm.com&gt;
Co-authored-by: AleJo2995 &lt;alejandro.leiva.palomo@ibm.com&gt; ([`5427fbb`](https://github.com/oscal-compass/compliance-trestle/commit/5427fbb445e9a54a2ede1caa7e15c15b8977dd10))

* fix: some tests failing on linux (#1387)

Signed-off-by: degenaro &lt;lou.degenaro@gmail.com&gt; ([`f0ffdec`](https://github.com/oscal-compass/compliance-trestle/commit/f0ffdecb963d7cd341b6b40be3a02efd3e76748d))

* fix: update readme with webex details (#1383) ([`4263f1a`](https://github.com/oscal-compass/compliance-trestle/commit/4263f1a72fa9a3ebea01b3b5c301cf89a962bf9c))

### Unknown

* Merge pull request #1399 from IBM/develop

chore: Trestle release ([`c3c28de`](https://github.com/oscal-compass/compliance-trestle/commit/c3c28de55120dc36988db1c3df95c3249ca5a26c))

## v2.1.1 (2023-05-12)

### Chore

* chore: Trestle release

chore: Trestle release ([`312203b`](https://github.com/oscal-compass/compliance-trestle/commit/312203b8c5eff6b50068a97b8f9be90ccb463438))

* chore: improve typing for mypy checks (#1350)

* initial typing fixes

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* phase 2 typing fixes

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* 20 files do not pass

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* fixed lists

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* tweak

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* made requested changes

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

---------

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt; ([`041fa46`](https://github.com/oscal-compass/compliance-trestle/commit/041fa46690673eb82e5da711888ab57e801048b5))

* chore: Merge back version tags and changelog into develop. ([`c4c972c`](https://github.com/oscal-compass/compliance-trestle/commit/c4c972cd8694257af10c3f2159f8a954e0b4c4b3))

### Documentation

* docs: update community call webex link (#1366)

* docs: update community call webex link

Signed-off-by: manjiree-gadgil &lt;manjiree.gadgil@ibm.com&gt;

* docs: update community call webex link

Signed-off-by: manjiree-gadgil &lt;manjiree.gadgil@ibm.com&gt;

* docs: address mdformat modification

Signed-off-by: manjiree-gadgil &lt;manjiree.gadgil@ibm.com&gt;

---------

Signed-off-by: manjiree-gadgil &lt;manjiree.gadgil@ibm.com&gt;
Co-authored-by: AleJo2995 &lt;alejandro.leiva.palomo@ibm.com&gt; ([`d5da18d`](https://github.com/oscal-compass/compliance-trestle/commit/d5da18d8f64fc0328d1b6592f663554c8aed3c22))

* docs: add community call information ([`b6d6451`](https://github.com/oscal-compass/compliance-trestle/commit/b6d6451408b79171021e00d883132eed1f5871b6))

### Fix

* fix: change lint title action (#1352)

* test bad pr title action change

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;

* fix: adding current branch to run pr title action

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;

* fix: changing settings for conventional pr title check

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;

* fix: chaning pr lint flow

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;

* fix: correct permissions on folders

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;

* fix: adding sudo to apt install

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;

* fix: adding correct branch

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;

* fix: correcting typo

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;

* fix: correcting branch

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;

* fix: add step to check

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;

* bad pr title test (#1356)

* bad pr title test

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;

* spacing

* fix: adding sudo to apt install

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;

* adding space

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;

* change readme

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;

* Update README.md

* Update README.md

---------

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;

* fix: fixing action condition

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;

* fix: correct conditional

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;

* fix: add config conventional install

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;

* fix: adding commitlint config

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;

* fix: chaning branch to checkout

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;

* add validation just for title

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;

* fix: grab the first commit msg

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;

* fix: adding config

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;

* fix: add pull request event

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;

* fix: correct action workflow

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;

* fix: remove message

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;

* fix: adding merge commit to check

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;

* fix: geting latest commit

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;

* fix: setup default branch

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;

* fix: fixing syntax error

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;

* fix: inverting commit order

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;

* fix: commitlint config

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;

* fix: fixing typo

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;

* fix: correcting typo

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;

* fix: fixing typo

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;

* fix: missing install

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;

* fix: adding corrections

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;

* fix: match pr title

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;

* fix: add validation step

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;

* fix: correct action

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;

* fix: change pr title check steps

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;

* fix: adding correct config

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;

* fix: fix mdformat errors in readme

* fix: target main and develop branches

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;

---------

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;
Co-authored-by: manjiree-gadgil &lt;manjiree.gadgil@ibm.com&gt; ([`5444206`](https://github.com/oscal-compass/compliance-trestle/commit/5444206f8b8c8e6904ec180472c569e246255975))

* fix: docs for task xlsx-result-to-oscal-ar replacing &#34;osco&#34; (#1369)

Signed-off-by: degenaro &lt;lou.degenaro@gmail.com&gt; ([`850ed0a`](https://github.com/oscal-compass/compliance-trestle/commit/850ed0a99e0298496b0df1e91c22bd80c290b6e1))

* fix: ssp response missing status and rules (#1358)

* quiet warning about system comp status

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* added docstring

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* added ssp md rules and status

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* updated ssp tutorial regarding the ssp demo

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* added options

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* fixed ssp parameter substitution

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

---------

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt; ([`43daf5f`](https://github.com/oscal-compass/compliance-trestle/commit/43daf5f9fca2495c1dbb8fa2ea39cb7184a9e191))

* fix: xccdf to oscal-ar (#1336)

* fix: xccdf to oscal-ar

Signed-off-by: degenaro &lt;lou.degenaro@gmail.com&gt;

* make docs

Signed-off-by: degenaro &lt;lou.degenaro@gmail.com&gt;

* Fix code smells.

Signed-off-by: degenaro &lt;lou.degenaro@gmail.com&gt;

* Fix code smells.

Signed-off-by: degenaro &lt;lou.degenaro@gmail.com&gt;

* Fix code smells.

Signed-off-by: degenaro &lt;lou.degenaro@gmail.com&gt;

* Agreed upon changes for transformation of xccdf to OSCAL AR

Signed-off-by: degenaro &lt;lou.degenaro@gmail.com&gt;

---------

Signed-off-by: degenaro &lt;lou.degenaro@gmail.com&gt; ([`7305883`](https://github.com/oscal-compass/compliance-trestle/commit/730588327ea54a5fc7a5d1f597a3ffeee92e0e48))

* fix: Handle tabs in statement prose and parts (#1359)

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt; ([`c34dbea`](https://github.com/oscal-compass/compliance-trestle/commit/c34dbeaa7dd75cd614393c57cba97fa9e5c8d699))

* fix: quiet warning about system component status as operational (#1354)

* quiet warning about system comp status

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* added docstring

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

---------

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt; ([`4313b85`](https://github.com/oscal-compass/compliance-trestle/commit/4313b850403e49a1db8e00f91e264e89e3175238))

* fix: Raise error if duplicate parts are found in the control statement (#1351)

* fix: Raise error if duplicate parts are found in statement

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;

* fix: Make lint happy

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;

* Remove unnecessary logging

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;

---------

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt; ([`74bd4f5`](https://github.com/oscal-compass/compliance-trestle/commit/74bd4f5e33c6d863fca3753955971ad460cac74a))

* fix: update author jinja command and add test (#1347)

* update author jinja command and add test

Signed-off-by: Sharma-Amit &lt;Sharma.Amit@ibm.com&gt;

* run yapf

Signed-off-by: Sharma-Amit &lt;Sharma.Amit@ibm.com&gt;

* resolve flake8 D205 and D400

Signed-off-by: Sharma-Amit &lt;Sharma.Amit@ibm.com&gt;

---------

Signed-off-by: Sharma-Amit &lt;Sharma.Amit@ibm.com&gt; ([`a0b1797`](https://github.com/oscal-compass/compliance-trestle/commit/a0b17972d82e106500f69dbfa78f86b8cf2da085))

### Unknown

* fix typo in task help text (#1365)

Signed-off-by: degenaro &lt;lou.degenaro@gmail.com&gt; ([`cbfa849`](https://github.com/oscal-compass/compliance-trestle/commit/cbfa849beda8b3bc42d6bc2ef8c07faa2cc559ca))

## v2.1.0 (2023-04-06)

### Chore

* chore: Refactor control reader Part 2 (#1330)

* chore: Refactor the processing of editable parts

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;

* Adjust typing for 3.8

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;

* Simplify code

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;

* Process code blocks in the markdown prose correctly

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;

* Address review comments

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;

* Adjust warning and docs

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;

---------

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt; ([`4a18b57`](https://github.com/oscal-compass/compliance-trestle/commit/4a18b57a0b4ab8888c4e266eac1b4a058d863b13))

* chore: Refactoring of control reader to a new type of markdown node (Part 1) (#1317)

* chore: Refactor control reader to a new control markdown node

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;

* chore: Update docs

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;

* Address sonar problems

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;

* Add timeout on the get call

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;

---------

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt; ([`2a43576`](https://github.com/oscal-compass/compliance-trestle/commit/2a43576d824a860451b95fe0ffb8c300d0137c78))

* chore: Merge back version tags and changelog into develop. ([`a1b1743`](https://github.com/oscal-compass/compliance-trestle/commit/a1b17432d413097958dac1be86ff0153694ddc9b))

### Documentation

* docs: fix refs to version numbers and update docs (#1326)

* updated docs

Signed-off-by: Frank Suits &lt;47203786+fsuits@users.noreply.github.com&gt;

* added warning for ssp compdefs

Signed-off-by: Frank Suits &lt;47203786+fsuits@users.noreply.github.com&gt;

* removed warning

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

---------

Signed-off-by: Frank Suits &lt;47203786+fsuits@users.noreply.github.com&gt;
Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt; ([`525f0f8`](https://github.com/oscal-compass/compliance-trestle/commit/525f0f80de39dfe230ab3d95486533ab72473980))

### Feature

* feat: validate SSP rule parameter values (#1337)

* sketched rules validator and test

Signed-off-by: Frank Suits &lt;47203786+fsuits@users.noreply.github.com&gt;

* feat: Rules parameter values validation in SSP

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;

* fix: correct parameter name on docstrings for rules_validator function

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;

* fix: correct value returned by val_diff_param_values function

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;

* fix: getting rid of nist updates

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;

* fix: initial logic handling for ssp

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;

* feat: adding rule param values validation for SSP

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;

* fix: addressing code changes

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;

* fix: correcting tests

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;

* fix: reducing conginitve complexity

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;

* fix: addressing new changes

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;

* fix: changing tests logic and addressing final changes

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;

* fix: cleaning test files

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;

* fix: remove unneded validation

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;

* fix: fixing typo in validation

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;

* fix: cleaning old ssp and generating new one for test

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;

* fix: full debug logs on test

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;

* fix: directory handling for setup ssp test

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;

* fix: applying changes for tests to pass on rule params validator

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;

* fix: cleaning up old and unused code

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;

* fix: adressing few minor changes to format and code

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;

* fix: optimizing logig for rule params validator

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;

---------

Signed-off-by: Frank Suits &lt;47203786+fsuits@users.noreply.github.com&gt;
Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;
Co-authored-by: Frank Suits &lt;47203786+fsuits@users.noreply.github.com&gt; ([`10dd58b`](https://github.com/oscal-compass/compliance-trestle/commit/10dd58b552f8f9a4618daea27e6d0ccd002dbd80))

* feat: adds implementation status to ssp-filter (#1338)

* docs: updates trestle author docs with ssp-filter changes

Adds ssp-filter by implementation status

Signed-off-by: Jennifer Power &lt;barnabei.jennifer@gmail.com&gt;

* feat(cli): adds logic to filter ssp by implementation status

- Adds test to test one and multiple implmentations status imputs
- Adds test to test bad implementation status input
- Adds filtering logic to ssp.py

Closes #1332

Signed-off-by: Jennifer Power &lt;barnabei.jennifer@gmail.com&gt;

* chore: updates ssp-filter test for updated compdef testdata

Signed-off-by: Jennifer Power &lt;barnabei.jennifer@gmail.com&gt;

* docs: updates wording on ssp-filter tutorial doc

Signed-off-by: Jennifer Power &lt;barnabei.jennifer@gmail.com&gt;

* chore: updates comment in ssp-filter test

Signed-off-by: Jennifer Power &lt;barnabei.jennifer@gmail.com&gt;

* refactor: updates ssp.py to use pre-defined constants and rewords errors

Signed-off-by: Jennifer Power &lt;barnabei.jennifer@gmail.com&gt;

---------

Signed-off-by: Jennifer Power &lt;barnabei.jennifer@gmail.com&gt;
Co-authored-by: Frank Suits &lt;47203786+fsuits@users.noreply.github.com&gt; ([`c33fc7d`](https://github.com/oscal-compass/compliance-trestle/commit/c33fc7d2ac9b430349962a08263db94c660a5f1c))

* feat: remove root references (#1316)

* updated gen_oscal and submodules for oscal 1.04

Signed-off-by: Frank Suits &lt;47203786+fsuits@users.noreply.github.com&gt;

* conversion completed all tests pass

Signed-off-by: Frank Suits &lt;47203786+fsuits@users.noreply.github.com&gt;

* fixed makefile

Signed-off-by: Frank Suits &lt;47203786+fsuits@users.noreply.github.com&gt;

* fixed .gitmodules

Signed-off-by: Frank Suits &lt;47203786+fsuits@users.noreply.github.com&gt;

* simplified makefile

Signed-off-by: Frank Suits &lt;47203786+fsuits@users.noreply.github.com&gt;

* more string consts

Signed-off-by: Frank Suits &lt;47203786+fsuits@users.noreply.github.com&gt;

* more details in oscal_normalize.py

Signed-off-by: Frank Suits &lt;47203786+fsuits@users.noreply.github.com&gt;

* added mapping class after manual edit

Signed-off-by: Frank Suits &lt;47203786+fsuits@users.noreply.github.com&gt;

* added mapping model

Signed-off-by: Frank Suits &lt;47203786+fsuits@users.noreply.github.com&gt;

* can now import mapping models

Signed-off-by: Frank Suits &lt;47203786+fsuits@users.noreply.github.com&gt;

* pulled from develop and updated docs

Signed-off-by: Frank Suits &lt;47203786+fsuits@users.noreply.github.com&gt;

* fixed typing

Signed-off-by: Frank Suits &lt;47203786+fsuits@users.noreply.github.com&gt;

* fixed mapping-collection

Signed-off-by: Frank Suits &lt;47203786+fsuits@users.noreply.github.com&gt;

* root removed

Signed-off-by: Frank Suits &lt;47203786+fsuits@users.noreply.github.com&gt;

* updated docs

Signed-off-by: Frank Suits &lt;47203786+fsuits@users.noreply.github.com&gt;

* bumped to oscal 1.0.4 and fixed checking of enums via text

Signed-off-by: Frank Suits &lt;47203786+fsuits@users.noreply.github.com&gt;

* updated docs for new oscal version support

Signed-off-by: Frank Suits &lt;47203786+fsuits@users.noreply.github.com&gt;

* merged dev and addressed pr feedback

Signed-off-by: Frank Suits &lt;47203786+fsuits@users.noreply.github.com&gt;

---------

Signed-off-by: Frank Suits &lt;47203786+fsuits@users.noreply.github.com&gt; ([`0dfdc79`](https://github.com/oscal-compass/compliance-trestle/commit/0dfdc797090a5ccbc64b6ba0e2b2dd16464a65ae))

### Fix

* fix: Comply with IBM Github action policy (#1344)

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt; ([`dd118f8`](https://github.com/oscal-compass/compliance-trestle/commit/dd118f84a26ce0e83cc4249837f91a118ae1f487))

* fix: duplicate param_id should be invalid only in profile (#1341)

* initial fix

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* docs

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* added extra test for comp def

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

---------

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt; ([`0edbd81`](https://github.com/oscal-compass/compliance-trestle/commit/0edbd81efdb164f56d90972aca8bbf7539a6ba57))

* fix: remove components from ssp during ssp-assemble and give warning (#1327)

* feat: remove compdefs from ssp when no longer valid

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;

* fix: correcting test case and adding warnings

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;

* fix: add test case proof for comp-defs removal

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;

* fix: change logic for using delete_list_from_list instead of delete_items_from_list

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;

* fix: improving warning messages

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;

* fix: changing tests for matching criteria

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;

* fix: switching to default nist submodules

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;

* fix: defining constant for generic uuid for testing

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;

* fix: enhance processing and corrrect test cases

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;

---------

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;
Co-authored-by: Frank Suits &lt;47203786+fsuits@users.noreply.github.com&gt; ([`03d4f05`](https://github.com/oscal-compass/compliance-trestle/commit/03d4f05a1d0bb0ef7c81e768238b67ae5cfbf5ca))

* fix: get_control_response was missing prose if statement has no parts (#1335)

* initial fix

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* added docs

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

---------

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt; ([`04c39d4`](https://github.com/oscal-compass/compliance-trestle/commit/04c39d4fb2911456c93495dce743cf971dec6f82))

* fix: better error handling when no comps specified during ssp-assemble - and added docs (#1328)

* added test and docs for assem with no comps

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* added docs

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* boosted test

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* fixed test

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* debugging test failure

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* debug test 2

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* final test fix

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* improved test

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

---------

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt; ([`2ecdb98`](https://github.com/oscal-compass/compliance-trestle/commit/2ecdb987f22f3da4592acd636637134161f05a0b))

* fix: ssp assemble includes controls not in the profile (#1325)

* fix for extra controls in ssp

Signed-off-by: Frank Suits &lt;47203786+fsuits@users.noreply.github.com&gt;

* added debug line

Signed-off-by: Frank Suits &lt;47203786+fsuits@users.noreply.github.com&gt;

---------

Signed-off-by: Frank Suits &lt;47203786+fsuits@users.noreply.github.com&gt; ([`138e95f`](https://github.com/oscal-compass/compliance-trestle/commit/138e95fd0598008b082fdf79a0306f68979c2c8e))

* fix: Version test (#1313)

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt; ([`3c1d7bb`](https://github.com/oscal-compass/compliance-trestle/commit/3c1d7bb439deab94851d2d0eb3b6a6766a0b5601))

### Unknown

* Merge pull request #1345 from IBM/develop

chore: Trestle hotfix release ([`88f0847`](https://github.com/oscal-compass/compliance-trestle/commit/88f08473c05f3b2d5645820afabf8c8fe07dad0b))

* Merge branch &#39;main&#39; into develop ([`48026eb`](https://github.com/oscal-compass/compliance-trestle/commit/48026eb2523ce9beeaddbfceec56e262c30b548e))

* Merge pull request #1343 from IBM/develop

chore: Trestle release ([`d18807c`](https://github.com/oscal-compass/compliance-trestle/commit/d18807c760c4e99f53c4a9feb2360f295413e103))

## v2.0.0 (2023-03-01)

### Breaking

* fix: BREAKING CHANGE (#1311)

* update docs

BREAKING CHANGE: Breaking release of Trestle

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* update docs again

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

---------

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt; ([`cb86284`](https://github.com/oscal-compass/compliance-trestle/commit/cb86284f1d6ee0299dc41d7d0fe66bb61139ce5a))

### Chore

* chore: Merge back version tags and changelog into develop. ([`b5d7ab4`](https://github.com/oscal-compass/compliance-trestle/commit/b5d7ab434de140df26bed3636f957e243c8770b0))

### Documentation

* docs: update maintainers.md for missed contributors (#1304)

* added ekat alej

Signed-off-by: Frank Suits &lt;47203786+fsuits@users.noreply.github.com&gt;

* fixed typo

Signed-off-by: Frank Suits &lt;47203786+fsuits@users.noreply.github.com&gt;

---------

Signed-off-by: Frank Suits &lt;47203786+fsuits@users.noreply.github.com&gt; ([`5443597`](https://github.com/oscal-compass/compliance-trestle/commit/5443597b0b4cd826b58320e787f47d59f84fe06b))

* docs: change trestle project references to workspace (#1276)

* docs: change trestle project references to workspace

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;

* docs: changing workspace for trestle workspace

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;

* docs:fix inconsistency in case senstive for trestle workspaces

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;

---------

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;
Co-authored-by: Frank Suits &lt;47203786+fsuits@users.noreply.github.com&gt; ([`2f1b4fd`](https://github.com/oscal-compass/compliance-trestle/commit/2f1b4fd79bb67c509ee7f7c4f0d3a14502d0c71f))

* docs: create tutorial for task csv-to-cd (2) (#1257)

* docs: create tutorial for task csv-to-cd

Signed-off-by: degenaro &lt;lou.degenaro@gmail.com&gt;

* docs: create tutorial for task csv-to-cd

Signed-off-by: degenaro &lt;lou.degenaro@gmail.com&gt;

* Temporary disable pre-commit autoupdate

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;

* Revise description: Resource_Instance_Type

Signed-off-by: degenaro &lt;lou.degenaro@gmail.com&gt;

Signed-off-by: degenaro &lt;lou.degenaro@gmail.com&gt;
Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;
Co-authored-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;
Co-authored-by: Frank Suits &lt;47203786+fsuits@users.noreply.github.com&gt; ([`d31df9f`](https://github.com/oscal-compass/compliance-trestle/commit/d31df9fb3ac4049f4710c2c9655ef8b1d17575e8))

### Feature

* feat: cd resolved profile controls check (#1309)

* feat: comp-def resolved profile controls validate (warn) option

Signed-off-by: degenaro &lt;lou.degenaro@gmail.com&gt;

* Use cwd as trestle workspace.

Signed-off-by: degenaro &lt;lou.degenaro@gmail.com&gt;

* validate-controls can be on, warn, off (default)

Signed-off-by: degenaro &lt;lou.degenaro@gmail.com&gt;

* Control_id_List cell should be stripped.

Signed-off-by: degenaro &lt;lou.degenaro@gmail.com&gt;

* Spelling.

Signed-off-by: degenaro &lt;lou.degenaro@gmail.com&gt;

* 100% test coverage.

Signed-off-by: degenaro &lt;lou.degenaro@gmail.com&gt;

* Use CatalogInterface to get list of control from catalog.

Signed-off-by: degenaro &lt;lou.degenaro@gmail.com&gt;

* Add row descriptions to task info.

Signed-off-by: degenaro &lt;lou.degenaro@gmail.com&gt;

---------

Signed-off-by: degenaro &lt;lou.degenaro@gmail.com&gt;
Co-authored-by: Frank Suits &lt;47203786+fsuits@users.noreply.github.com&gt; ([`638dd53`](https://github.com/oscal-compass/compliance-trestle/commit/638dd5384c6588ad9bb88726c8d716cfc6e4b03b))

* feat: Add ability to view version of the individual OSCAL object (#1298)

* feat: Add ability to view version of the object

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;

* feat: Add docs and more tests

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;

* feat: Address review feedback

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;

* feat: Fix docs

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;

* feat: Address review comments

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;

---------

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt; ([`cf2af61`](https://github.com/oscal-compass/compliance-trestle/commit/cf2af617fad82ccdfbebcd48948dd8a67512e7aa))

* feat: new format csv to oscal component definition (#1285)

Signed-off-by: degenaro &lt;lou.degenaro@gmail.com&gt;
Co-authored-by: Frank Suits &lt;47203786+fsuits@users.noreply.github.com&gt; ([`9572c4b`](https://github.com/oscal-compass/compliance-trestle/commit/9572c4b83c03eaec6518333670fa8d6c80cafbf2))

* feat: allow remote profiles to reference catalogs and profiles by relative path in href (#1288)

* import now handles local relative hrefs

Signed-off-by: Frank Suits &lt;47203786+fsuits@users.noreply.github.com&gt;

* updated docs

Signed-off-by: Frank Suits &lt;47203786+fsuits@users.noreply.github.com&gt;

* addressed pr changes

Signed-off-by: Frank Suits &lt;47203786+fsuits@users.noreply.github.com&gt;

---------

Signed-off-by: Frank Suits &lt;47203786+fsuits@users.noreply.github.com&gt; ([`0a7e2cf`](https://github.com/oscal-compass/compliance-trestle/commit/0a7e2cf47680c19ef406aeb49afc35412478fc57))

* feat: CIS spread sheet to OSCAL catalog (#1270)

* Initial delivery.

Signed-off-by: degenaro &lt;lou.degenaro@gmail.com&gt;

* Add tests.

Signed-off-by: degenaro &lt;lou.degenaro@gmail.com&gt;

* Remove duplicate lines?

Signed-off-by: degenaro &lt;lou.degenaro@gmail.com&gt;

* Sonar.

Signed-off-by: degenaro &lt;lou.degenaro@gmail.com&gt;

* Combined Profiles sheet, only.

Signed-off-by: degenaro &lt;lou.degenaro@gmail.com&gt;

* Refine functionality + tests for 100% coverage.

Signed-off-by: degenaro &lt;lou.degenaro@gmail.com&gt;

* Remove use of deprecated methods.

Signed-off-by: degenaro &lt;lou.degenaro@gmail.com&gt;

* Support RHEL spread sheet.

Signed-off-by: degenaro &lt;lou.degenaro@gmail.com&gt;

* Include namespace for props.

Signed-off-by: degenaro &lt;lou.degenaro@gmail.com&gt;

* Fix comment.

Signed-off-by: degenaro &lt;lou.degenaro@gmail.com&gt;

* mkdocs

Signed-off-by: degenaro &lt;lou.degenaro@gmail.com&gt;

* description -&gt; statement

Signed-off-by: degenaro &lt;lou.degenaro@gmail.com&gt;

* Fix part-id.

Signed-off-by: degenaro &lt;lou.degenaro@gmail.com&gt;

* Fix (rhel) multiple controls -&gt; multiple profile props

Signed-off-by: degenaro &lt;lou.degenaro@gmail.com&gt;

* More precise test case names.

Signed-off-by: degenaro &lt;lou.degenaro@gmail.com&gt;

* Fix duplicate part ids.

Signed-off-by: degenaro &lt;lou.degenaro@gmail.com&gt;

* Use BackMatter for links.

Signed-off-by: degenaro &lt;lou.degenaro@gmail.com&gt;

* factor out duplicate LOCs.

Signed-off-by: degenaro &lt;lou.degenaro@gmail.com&gt;

* Replace &#34;if len(my_array)&#34; construct with &#34;if my_array&#34;.

Signed-off-by: degenaro &lt;lou.degenaro@gmail.com&gt;

* Remove title from Resources in BackMatter for Links.

Signed-off-by: degenaro &lt;lou.degenaro@gmail.com&gt;

* Remove first in property list detection: unnecessary.

Signed-off-by: degenaro &lt;lou.degenaro@gmail.com&gt;

---------

Signed-off-by: degenaro &lt;lou.degenaro@gmail.com&gt; ([`ba9dec0`](https://github.com/oscal-compass/compliance-trestle/commit/ba9dec0f4799b68160bd0e2aee66423763df21a6))

* feat: csv to oscal cd reconcile3 (#1272)

* feat: csv to oscal cd reconcile3

Signed-off-by: degenaro &lt;lou.degenaro@gmail.com&gt;

* Major test cases changes.

Signed-off-by: degenaro &lt;lou.degenaro@gmail.com&gt;

* Reduce code duplication in tests.

Signed-off-by: degenaro &lt;lou.degenaro@gmail.com&gt;

* Remove extraneous test data file.

Signed-off-by: degenaro &lt;lou.degenaro@gmail.com&gt;

---------

Signed-off-by: degenaro &lt;lou.degenaro@gmail.com&gt; ([`a19e7be`](https://github.com/oscal-compass/compliance-trestle/commit/a19e7be1ce8b8fb267bfd797ddcad742fdf4fcfd))

* feat: SSP cli changes to load comp defs (#1264)

* added profile href

Signed-off-by: Frank Suits &lt;47203786+fsuits@users.noreply.github.com&gt;

* hooked profile title into all commands

Signed-off-by: Frank Suits &lt;47203786+fsuits@users.noreply.github.com&gt;

* use compdef info

Signed-off-by: Frank Suits &lt;47203786+fsuits@users.noreply.github.com&gt;

* fixed rewrite behavior of ssp assemble

Signed-off-by: Frank Suits &lt;47203786+fsuits@users.noreply.github.com&gt;

* fixed dropped control imps during ssp assemble

Signed-off-by: Frank Suits &lt;47203786+fsuits@users.noreply.github.com&gt;

* this system uuid now used

Signed-off-by: Frank Suits &lt;47203786+fsuits@users.noreply.github.com&gt;

* improved set param handling

Signed-off-by: Frank Suits &lt;47203786+fsuits@users.noreply.github.com&gt;

* values are now always list

Signed-off-by: Frank Suits &lt;47203786+fsuits@users.noreply.github.com&gt;

* added props to comp_info

Signed-off-by: Frank Suits &lt;47203786+fsuits@users.noreply.github.com&gt;

* fixed duplicate line

Signed-off-by: Frank Suits &lt;47203786+fsuits@users.noreply.github.com&gt;

* pull direct from compdefs into ssp

Signed-off-by: Frank Suits &lt;47203786+fsuits@users.noreply.github.com&gt;

* insert content into ssp

Signed-off-by: Frank Suits &lt;47203786+fsuits@users.noreply.github.com&gt;

* add bycomp at control level and require rules

Signed-off-by: Frank Suits &lt;47203786+fsuits@users.noreply.github.com&gt;

* added rules check

Signed-off-by: Frank Suits &lt;47203786+fsuits@users.noreply.github.com&gt;

* added imp status

Signed-off-by: Frank Suits &lt;47203786+fsuits@users.noreply.github.com&gt;

* tests pass with some things turned off

Signed-off-by: Frank Suits &lt;47203786+fsuits@users.noreply.github.com&gt;

* changed operational to planned

Signed-off-by: Frank Suits &lt;47203786+fsuits@users.noreply.github.com&gt;

* fixed empty list

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* improved merging into ssp

Signed-off-by: Frank Suits &lt;47203786+fsuits@users.noreply.github.com&gt;

* assemble is now repeatable

Signed-off-by: Frank Suits &lt;47203786+fsuits@users.noreply.github.com&gt;

* ssp assemble now does not write if no change

Signed-off-by: Frank Suits &lt;47203786+fsuits@users.noreply.github.com&gt;

* added more help comments to the md yaml header

Signed-off-by: Frank Suits &lt;47203786+fsuits@users.noreply.github.com&gt;

* boost coverage and cleanup

Signed-off-by: Frank Suits &lt;47203786+fsuits@users.noreply.github.com&gt;

* refactored smell

Signed-off-by: Frank Suits &lt;47203786+fsuits@users.noreply.github.com&gt;

* add set_param

Signed-off-by: Frank Suits &lt;47203786+fsuits@users.noreply.github.com&gt;

* updated docs and map setparams to rules

Signed-off-by: Frank Suits &lt;47203786+fsuits@users.noreply.github.com&gt;

* fixed dropped setparams

Signed-off-by: Frank Suits &lt;47203786+fsuits@users.noreply.github.com&gt;

* addressed pr change requests

Signed-off-by: Frank Suits &lt;47203786+fsuits@users.noreply.github.com&gt;

* fixed empty set params and rules at top level of imp req

Signed-off-by: Frank Suits &lt;47203786+fsuits@users.noreply.github.com&gt;

* flake8 ignore B017,B028

Signed-off-by: Frank Suits &lt;47203786+fsuits@users.noreply.github.com&gt;

* fixed docs and added error msg to ssp-filter

Signed-off-by: Frank Suits &lt;47203786+fsuits@users.noreply.github.com&gt;

* fixed comment for rule param values

Signed-off-by: Frank Suits &lt;47203786+fsuits@users.noreply.github.com&gt;

* better handling of rule param value

Signed-off-by: Frank Suits &lt;47203786+fsuits@users.noreply.github.com&gt;

Signed-off-by: Frank Suits &lt;47203786+fsuits@users.noreply.github.com&gt;
Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt; ([`2835eed`](https://github.com/oscal-compass/compliance-trestle/commit/2835eed4bf700ca0f90120063a707fb811f610fb))

* feat: ssp based on components and refactor (#1261)

* initial ssp based on comps

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* cleaned up for push

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* ssp mostly working

Signed-off-by: Frank Suits &lt;47203786+fsuits@users.noreply.github.com&gt;

* chore: Initial split

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;

* merged with refactor branch and added ssp test data

Signed-off-by: Frank Suits &lt;47203786+fsuits@users.noreply.github.com&gt;

* now generate ssp output

Signed-off-by: Frank Suits &lt;47203786+fsuits@users.noreply.github.com&gt;

* Split profile as markdown to parts, rename yaml_header

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;

* fixed yaml header issue

Signed-off-by: Frank Suits &lt;47203786+fsuits@users.noreply.github.com&gt;

* Small change to component

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;

* more content in ssp header

Signed-off-by: Frank Suits &lt;47203786+fsuits@users.noreply.github.com&gt;

* A small fix in the header merge

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;

* more header content

Signed-off-by: Frank Suits &lt;47203786+fsuits@users.noreply.github.com&gt;

* cleaned up ssp header

Signed-off-by: Frank Suits &lt;47203786+fsuits@users.noreply.github.com&gt;

* improved comp gen

Signed-off-by: Frank Suits &lt;47203786+fsuits@users.noreply.github.com&gt;

* ssp gen and assemble mostly working

Signed-off-by: Frank Suits &lt;47203786+fsuits@users.noreply.github.com&gt;

* initial ssp-values working

Signed-off-by: Frank Suits &lt;47203786+fsuits@users.noreply.github.com&gt;

* fixed test data for jinja and ssp outputs all controls

Signed-off-by: Frank Suits &lt;47203786+fsuits@users.noreply.github.com&gt;

* Make jinja tests happy

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;

* better handling ssp vals

Signed-off-by: Frank Suits &lt;47203786+fsuits@users.noreply.github.com&gt;

* better handling of ssp rules and params

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* Change doc strings

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;

* fixed comp gen test

Signed-off-by: Frank Suits &lt;47203786+fsuits@users.noreply.github.com&gt;

* prompts are now comments

Signed-off-by: Frank Suits &lt;47203786+fsuits@users.noreply.github.com&gt;

* bracked around ssp params in prose

Signed-off-by: Frank Suits &lt;47203786+fsuits@users.noreply.github.com&gt;

* all tests pass

Signed-off-by: Frank Suits &lt;47203786+fsuits@users.noreply.github.com&gt;

* updated docs

Signed-off-by: Frank Suits &lt;47203786+fsuits@users.noreply.github.com&gt;

* boosted coverage and fixed smells

Signed-off-by: Frank Suits &lt;47203786+fsuits@users.noreply.github.com&gt;

* fixed empty lists in header

Signed-off-by: Frank Suits &lt;47203786+fsuits@users.noreply.github.com&gt;

* fixed comment closure

Signed-off-by: Frank Suits &lt;47203786+fsuits@users.noreply.github.com&gt;

* fixed empty lists

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* improved description text

Signed-off-by: Frank Suits &lt;47203786+fsuits@users.noreply.github.com&gt;

* fixed typo

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* fixed empty lists

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* initial fixes to pr

Signed-off-by: Frank Suits &lt;47203786+fsuits@users.noreply.github.com&gt;

* fixed list issues

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* fixed stings

Signed-off-by: Frank Suits &lt;47203786+fsuits@users.noreply.github.com&gt;

* responded to multiple pr changes

Signed-off-by: Frank Suits &lt;47203786+fsuits@users.noreply.github.com&gt;

* added test coverage

Signed-off-by: Frank Suits &lt;47203786+fsuits@users.noreply.github.com&gt;

* fixed non-write of response prompt

Signed-off-by: Frank Suits &lt;47203786+fsuits@users.noreply.github.com&gt;

* fixed repeat ssp gen issue

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* more fixes per pr feedback

Signed-off-by: Frank Suits &lt;47203786+fsuits@users.noreply.github.com&gt;

* added tests for ssp_io and prune function

Signed-off-by: Frank Suits &lt;47203786+fsuits@users.noreply.github.com&gt;

* sort pruned controls

Signed-off-by: Frank Suits &lt;47203786+fsuits@users.noreply.github.com&gt;

* refactor cat interface

Signed-off-by: Frank Suits &lt;47203786+fsuits@users.noreply.github.com&gt;

* added typing

Signed-off-by: Frank Suits &lt;47203786+fsuits@users.noreply.github.com&gt;

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;
Signed-off-by: Frank Suits &lt;47203786+fsuits@users.noreply.github.com&gt;
Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;
Co-authored-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt; ([`f0de73a`](https://github.com/oscal-compass/compliance-trestle/commit/f0de73ad2152be75f456ff5a1b273d6c1d21988b))

* feat: create separate markdown directories per source (#1242)

* named dirs under comps works

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* fixed ssp

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* fixed duplicate keys bug

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* expanded test coverage

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* fixed bind

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* fixed prune

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* fixed rules

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* edited docs

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* addressed review comments

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* fixed try except block

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt; ([`3ffbdb0`](https://github.com/oscal-compass/compliance-trestle/commit/3ffbdb04da1c72aba7b1304c0060d948d5501608))

* feat: Add force-overwrite for generate (#1241)

* feat: Add force overwrite for generate

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;

* Update docs, increase coverage

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;

* Reduce duplicates

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;

* Address review feedback

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt; ([`d7612a9`](https://github.com/oscal-compass/compliance-trestle/commit/d7612a9a769d72e7a0338506aed4013b299519a7))

### Fix

* fix: codeql update from v1 to v2 (#1310)

* codeql to version 2

Signed-off-by: Frank Suits &lt;47203786+fsuits@users.noreply.github.com&gt;

* updated docs

Signed-off-by: Frank Suits &lt;47203786+fsuits@users.noreply.github.com&gt;

---------

Signed-off-by: Frank Suits &lt;47203786+fsuits@users.noreply.github.com&gt; ([`6731560`](https://github.com/oscal-compass/compliance-trestle/commit/6731560201a596a986906086bf1d337d5495a816))

* fix: Give warnings when component references control not loaded by profile for comp-gen and ssp-gen (#1305)

* added tests

Signed-off-by: Frank Suits &lt;47203786+fsuits@users.noreply.github.com&gt;

* added comment

Signed-off-by: Frank Suits &lt;47203786+fsuits@users.noreply.github.com&gt;

* changed errors to warnings and checked warning text in tests

Signed-off-by: Frank Suits &lt;47203786+fsuits@users.noreply.github.com&gt;

* removed unneeded logging commands

Signed-off-by: Frank Suits &lt;47203786+fsuits@users.noreply.github.com&gt;

* addressed pr feedback

Signed-off-by: Frank Suits &lt;47203786+fsuits@users.noreply.github.com&gt;

---------

Signed-off-by: Frank Suits &lt;47203786+fsuits@users.noreply.github.com&gt; ([`429b3c1`](https://github.com/oscal-compass/compliance-trestle/commit/429b3c19023f4232b0853818c6039629dce4dc26))

* fix: Temporary fix for the multiline control statement in catalog-assemble (#1308)

* fix: Temporary fix for the multiline statement bug

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;

* Fix objective part as well

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;

* Make matching case insensitive

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;

* Delete trailing and leading new lines from the prose

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;

* Delete spaces

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;

---------

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt; ([`7a7aa8c`](https://github.com/oscal-compass/compliance-trestle/commit/7a7aa8cf53c8361d79cc837615bbf7fae3b134c9))

* fix: boost test coverage for component generate and assemble (#1306)

* boosted coverage comp_gen assem

Signed-off-by: Frank Suits &lt;47203786+fsuits@users.noreply.github.com&gt;

* simplified test code

Signed-off-by: Frank Suits &lt;47203786+fsuits@users.noreply.github.com&gt;

---------

Signed-off-by: Frank Suits &lt;47203786+fsuits@users.noreply.github.com&gt; ([`52b863b`](https://github.com/oscal-compass/compliance-trestle/commit/52b863b2ea684073afdb2ca85af7114ad43ac51c))

* fix: ssp-generate error with components (#1303)

* initial fix of ssp gen issue

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* removed test

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* enhanced test data for coverage

Signed-off-by: Frank Suits &lt;47203786+fsuits@users.noreply.github.com&gt;

---------

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;
Signed-off-by: Frank Suits &lt;47203786+fsuits@users.noreply.github.com&gt; ([`7a49a0a`](https://github.com/oscal-compass/compliance-trestle/commit/7a49a0a5e4a273755a2f6279a1cb51000cf02d40))

* fix: adding multiple value set to rule param values during component … (#1301)

* fix: adding multiple value set to rule param values during component assemble

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;

* fixed test for multiple values.  cleaned up debug/info msgs from comp assemble

Signed-off-by: Frank Suits &lt;47203786+fsuits@users.noreply.github.com&gt;

* cleaned up warning and info messages

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* component -&gt; component-def

Signed-off-by: Frank Suits &lt;47203786+fsuits@users.noreply.github.com&gt;

---------

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;
Signed-off-by: Frank Suits &lt;47203786+fsuits@users.noreply.github.com&gt;
Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;
Co-authored-by: Frank Suits &lt;47203786+fsuits@users.noreply.github.com&gt;
Co-authored-by: Frank Suits &lt;frankst@au1.ibm.com&gt; ([`c357e15`](https://github.com/oscal-compass/compliance-trestle/commit/c357e15691bb9eee553c8531edd1f4ce024f60a3))

* fix: change python badge for addressing current python supported versions (#1300)

* fix: change python badge for addresing current python supported versions

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;

* Fix docs page

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;

---------

Signed-off-by: Alejandro Jose Leiva Palomo &lt;alejandro.leiva.palomo@ibm.com&gt;
Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;
Co-authored-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt; ([`7a8d895`](https://github.com/oscal-compass/compliance-trestle/commit/7a8d895d5ca16e9c7ebbcf3c862c14721d4a6421))

* fix: allow edit of rule param values during component assemble (#1299)

* comp gen assemble loads rule param vals

Signed-off-by: Frank Suits &lt;47203786+fsuits@users.noreply.github.com&gt;

* updated docs

Signed-off-by: Frank Suits &lt;47203786+fsuits@users.noreply.github.com&gt;

---------

Signed-off-by: Frank Suits &lt;47203786+fsuits@users.noreply.github.com&gt; ([`041a2c3`](https://github.com/oscal-compass/compliance-trestle/commit/041a2c3d567b91404a7bc63ebdb9689b8a447463))

* fix: adding new components via markdown caused error (#1294)

* generalized last_modified setting

Signed-off-by: Frank Suits &lt;47203786+fsuits@users.noreply.github.com&gt;

* boosted component coverage

Signed-off-by: Frank Suits &lt;47203786+fsuits@users.noreply.github.com&gt;

---------

Signed-off-by: Frank Suits &lt;47203786+fsuits@users.noreply.github.com&gt; ([`39fd590`](https://github.com/oscal-compass/compliance-trestle/commit/39fd590c85b7e2cf9b0e7770596def8c41e8ae98))

* fix: problem in cat assemble with subgroups (#1291)

* fixed groups in catalog assemble

Signed-off-by: Frank Suits &lt;47203786+fsuits@users.noreply.github.com&gt;

* added docs

Signed-off-by: Frank Suits &lt;47203786+fsuits@users.noreply.github.com&gt;

---------

Signed-off-by: Frank Suits &lt;47203786+fsuits@users.noreply.github.com&gt; ([`88337a4`](https://github.com/oscal-compass/compliance-trestle/commit/88337a4b16a24c8391a60e99347aa34cdb65307f))

* fix: assignment representation for ssp was not doing the right things (#1273)

* fixed ASSIGNMENT_FORM parameter rep

Signed-off-by: Frank Suits &lt;47203786+fsuits@users.noreply.github.com&gt;

* updated docs

Signed-off-by: Frank Suits &lt;47203786+fsuits@users.noreply.github.com&gt;

* assignment now means needs assignment

Signed-off-by: Frank Suits &lt;47203786+fsuits@users.noreply.github.com&gt;

* simplified param_str code

Signed-off-by: Frank Suits &lt;47203786+fsuits@users.noreply.github.com&gt;

* made assignment form more generic with prefixes

Signed-off-by: Frank Suits &lt;47203786+fsuits@users.noreply.github.com&gt;

* made -bf consistent.  started adding -sl

Signed-off-by: Frank Suits &lt;47203786+fsuits@users.noreply.github.com&gt;

* fixed label rep mode

Signed-off-by: Frank Suits &lt;47203786+fsuits@users.noreply.github.com&gt;

* updated docs

Signed-off-by: Frank Suits &lt;47203786+fsuits@users.noreply.github.com&gt;

* fixed issue with -sl, boosted coverage, added to jinja docs

Signed-off-by: Frank Suits &lt;47203786+fsuits@users.noreply.github.com&gt;

* pr feedback

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

---------

Signed-off-by: Frank Suits &lt;47203786+fsuits@users.noreply.github.com&gt;
Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt; ([`cac2aa3`](https://github.com/oscal-compass/compliance-trestle/commit/cac2aa351530f76834d53d10e08252ffb0786327))

* fix: Remove attrs version pinning (#1280)

Removing pinning of attrs version, as there seems to be no breaking dependency.
I tested this using poetry command

Signed-off-by: Pritam &lt;pritamdutt@gmail.com&gt;
Co-authored-by: Ekaterina Nikonova &lt;91102120+enikonovad@users.noreply.github.com&gt; ([`8260e03`](https://github.com/oscal-compass/compliance-trestle/commit/8260e03cddcf682ebdf931f2b262f58156c8f56c))

* fix: Fix typo in the curl (#1278)

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt; ([`d7576d5`](https://github.com/oscal-compass/compliance-trestle/commit/d7576d5cc4e8536b1f94ca668b3b7b87e01f3148))

* fix: rules at component level2 (#1259)

* docs: create tutorial for task csv-to-cd

Signed-off-by: degenaro &lt;lou.degenaro@gmail.com&gt;

* docs: create tutorial for task csv-to-cd

Signed-off-by: degenaro &lt;lou.degenaro@gmail.com&gt;

* Temporary disable pre-commit autoupdate

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;

* docs: rules at component level

Signed-off-by: degenaro &lt;lou.degenaro@gmail.com&gt;

* fix: rules at component level

Signed-off-by: degenaro &lt;lou.degenaro@gmail.com&gt;

* Revise description: Resource_Instance_Type

Signed-off-by: degenaro &lt;lou.degenaro@gmail.com&gt;

Signed-off-by: degenaro &lt;lou.degenaro@gmail.com&gt;
Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;
Co-authored-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;
Co-authored-by: Frank Suits &lt;47203786+fsuits@users.noreply.github.com&gt; ([`3633d1f`](https://github.com/oscal-compass/compliance-trestle/commit/3633d1f0f4bcd7ee481f7db382aab2b23e91687f))

* fix: trestle task csv-to-oscal-cd cannot handle whitespace (#1252)

* fix: trestle task csv-to-oscal-cd cannot handle whitespace

Signed-off-by: degenaro &lt;lou.degenaro@gmail.com&gt;

* Test cases.

Signed-off-by: degenaro &lt;lou.degenaro@gmail.com&gt;

Signed-off-by: degenaro &lt;lou.degenaro@gmail.com&gt; ([`ac4b5e0`](https://github.com/oscal-compass/compliance-trestle/commit/ac4b5e08a8233d7f807cd6824197dca45f12b17b))

* fix: Fix docs template validate flags (#1245)

* fix: Fix docs template validate flags

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;

* Address feedback

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt; ([`6eac0c2`](https://github.com/oscal-compass/compliance-trestle/commit/6eac0c2c620d933761e9660021a5005490bf5ea5))

* fix: Adjust documentation (#1248)

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt; ([`5b31925`](https://github.com/oscal-compass/compliance-trestle/commit/5b31925ac82042db98467552bfef415796ca57d3))

* fix: Update flake8 in precommit (#1246)

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt; ([`a63b094`](https://github.com/oscal-compass/compliance-trestle/commit/a63b094ef05924ba8a8a600ff7ec5192bfe285d8))

### Unknown

* Merge pull request #1312 from IBM/develop

chore: Trestle release ([`c41f873`](https://github.com/oscal-compass/compliance-trestle/commit/c41f873d0996b5100acf1952a0007201ef10a056))

## v1.2.0 (2022-11-07)

### Chore

* chore: Optimize images for imgbot (#1234)

* [ImgBot] Optimize images

/docs/tutorials/ssp_profile_catalog_authoring/trestle_ssp_author_options.png -- 90.68kb -&gt; 76.08kb (16.1%)

Signed-off-by: ImgBotApp &lt;ImgBotHelp@gmail.com&gt;

* docs: edited docs

Signed-off-by: ImgBotApp &lt;ImgBotHelp@gmail.com&gt;
Co-authored-by: ImgBotApp &lt;ImgBotHelp@gmail.com&gt;
Co-authored-by: Frank Suits &lt;47203786+fsuits@users.noreply.github.com&gt; ([`17383ab`](https://github.com/oscal-compass/compliance-trestle/commit/17383abfbeb55adc4e34afdc2cec01a5899ee44e))

* chore: expand test coverage and make markdown more consistent (#1210)

* fixed tests and clarified prompts for prose

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* refined parameters in yaml headers and added tests

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt; ([`6c551c6`](https://github.com/oscal-compass/compliance-trestle/commit/6c551c6fc4e220ed475f259af022ae366e6ed1fb))

* chore: Optimize images (#1152)

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;

Co-authored-by: ImgBotApp &lt;ImgBotHelp@gmail.com&gt; ([`5ce472d`](https://github.com/oscal-compass/compliance-trestle/commit/5ce472d077dff4857bd8412c63827b1285e51f06))

* chore: Update documentation for the governed-documents (#1150)

* chore: Update governed-document documentation

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;

* chore: Add picture

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;

* Address pr comments

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt; ([`2b37cd9`](https://github.com/oscal-compass/compliance-trestle/commit/2b37cd9f47b7f36ff790624be9a1da504efeadc0))

* chore: Merge back version tags and changelog into develop. ([`58bc2a5`](https://github.com/oscal-compass/compliance-trestle/commit/58bc2a5cb0bcc11e15c05e40aaf3b3cabc8b01d7))

### Documentation

* docs: update ssp and profile authoring guide to describe addition of parts (#1185)

* updated help prose when control written

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* updated ssp authoring docs

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* major additions to content

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* addressed feedback and grouped into details sections

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt; ([`35c3c78`](https://github.com/oscal-compass/compliance-trestle/commit/35c3c78105721712340a3ab1a9fbe3fdba44ac8e))

### Feature

* feat: Allow trestle init to specify the purpose of initialisation (#1228)

* feat: Add init modes

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;

* Fix tests

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;

* Address review feedback

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt; ([`8d02b68`](https://github.com/oscal-compass/compliance-trestle/commit/8d02b68d5cae32273e179494bafb235c2a004a22))

* feat: provide full path to controls in catalog including sub-controls (#1227)

* added sub-control path to control

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* added comment

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* added tests

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* boosted test

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt; ([`ec96ee9`](https://github.com/oscal-compass/compliance-trestle/commit/ec96ee9067629b4d9932b39b2915b1b45bc6bae0))

* feat: get statement parts to allow easy capture of statement prose (#1221)

* added get statement parts

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* added check

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt; ([`708b6b5`](https://github.com/oscal-compass/compliance-trestle/commit/708b6b52e152ac4b21563f415cc0da3c8ca2ff8a))

* feat: remove default namespace and define generic trestle ns (#1215)

* no-ns now working

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* boosted tests

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* removed ns references

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt; ([`105152b`](https://github.com/oscal-compass/compliance-trestle/commit/105152b15bab526429394ba398c3f512266086df))

* feat: made model equivalence check more rigorous (#1217)

* reworked models_are_equiv

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* removed sizeof checks

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* added tests and clarified fields_set when Nones possible

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt; ([`ab89b45`](https://github.com/oscal-compass/compliance-trestle/commit/ab89b45286dfbbfd1b3f4b9dc003246b4050b9e1))

* feat: allow profile-resolve to specify brackets around value (#1207)

* added bracket format option

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* tweaked docstring

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* simplified test

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt; ([`16d9dbc`](https://github.com/oscal-compass/compliance-trestle/commit/16d9dbcdc7fadaf7ddbbdd9c19b68e99777c4551))

* feat: show inherited props in yaml header for profile-generate markdown (#1198)

* added profile flow tests

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* tweak some code

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* more list comprehension

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* formalized merging of section_dicts from header and command line

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* inherited props now working

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* fixed smells

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* fix: component generate will use sources in components if profile not specified (#1201)

* fixed component generate with no profile given

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* updated docstring

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* addressed pr change requests

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* typing tweaks

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt; ([`d4b4680`](https://github.com/oscal-compass/compliance-trestle/commit/d4b4680e49ca8912ef34f0d472dc9997303227b8))

* feat: csv to oscal component definition (#1197)

* feat: csv to oscal component definition

* Address comments from Ekaterina.

* PR fixes

- one control impl per source
- property Rule_Id mistakenly omitted

* Issue #1195

- rules should be at source level
- for each source level, all rules should be in single property set

* Issue #1195

- in impl req for each control, there should be a set of properties one
for each rule with Rule Id same except for remarks removed

* Issue #1141

- &#34;unknown&#34; columns become another property for that rule &amp; use user
defined namespace
- two namespaces in config, one is &#34;standard&#34; and other is &#34;user&#34;

* Issue #1141

Fix missing property

* Issue #1141

- specify in config column name to class mapping (Rule Id and Rule
Description, and user specified columns)

* Issue #1141

- class is missing from prop in ipml reqs
- Rule_description prop is coming twice

* Issue #1141

- Add initial test cases &gt; 90%

* Issue #1141

- test coverage 100% for csv_helper.py

* Issue #1141

- test coverage 100% for csv_to_oscal_cd.py

* Issue #1141

- check for and employ catalog (just one allowed, presently)

* Issue #1141

- catalog title into component-definition

* Issue #1141

- remove config flag: catalog-file
- add config flag: title

* Issue #1141

- add to config: version (of component definition)

* Issue #1141

- do not put class on private columns

* fix: csv to cd command

Co-authored-by: Vikas &lt;avikas@in.ibm.com&gt;
Co-authored-by: Vikas Agarwal &lt;75295756+vikas-agarwal76@users.noreply.github.com&gt; ([`c6e8bad`](https://github.com/oscal-compass/compliance-trestle/commit/c6e8bad9f8c3feaab12778c90dde45830ab6ab01))

* feat: profile-resolve command to generate resolved profile catalog (#1194)

* added tests and removed script

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* added docs

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* simplified test

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* expanded coverage

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* added tests and responded to pr requests

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* removed unneeded dir check

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt; ([`9faf572`](https://github.com/oscal-compass/compliance-trestle/commit/9faf5726a1bc1bf8c9263a4d84a472653e76ebf9))

* feat: added new parameter rep ASSIGNMENT_FORM to leave params in brackets with text (#1193)

* initial refactor to controlinterface

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* changed parameter format to ASSIGNMENT_FORM, refactored ControlInterface, made some private functions public

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt; ([`d41b2b6`](https://github.com/oscal-compass/compliance-trestle/commit/d41b2b665b6e455288724347165f51b3078ac487))

* feat: allow culling headers from an existing md file (#1180)

* working now

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* added additional string test

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* fixed typo

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* reverted markdownapi changes and moved to md_writer

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* reverted files for real

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* removed residual node code

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* typo

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* fix typo boost coverage

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* better culling of header content and added starting line to markdown node

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* fixed test

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* handled pr feedback

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt; ([`a0a0369`](https://github.com/oscal-compass/compliance-trestle/commit/a0a0369c53a7c06225e7e927aac8d8397f7b7c55))

* feat: handle display name and namespace (#1165)

* initial fix of dup headers

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* final fixes

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* changed default position to ending

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* prop ns now working

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* handled pr feedback and new approach for namespaces

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* fixed bug with namespace on profile assemble

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* added file encoding

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt; ([`a898216`](https://github.com/oscal-compass/compliance-trestle/commit/a898216c812411646e263482393fd9669f43a5b2))

* feat: handle display name as property and initial handling of namespace option (#1162)

* handle display-name

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* fixed tests

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt; ([`e6641fe`](https://github.com/oscal-compass/compliance-trestle/commit/e6641fea53e486d41df899f5adc73ee6d79c8e8c))

* feat: profile add props to control or part, and add prose to statement part (#1158)

* improved component handling, cleaned up cache and import tests

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* component generate works with new format

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* added control_read test with bad component header

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* enhanced coverage with updated test file

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* profile props working

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* labels work in profile

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* aggregated parts and adds in alters

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* added props comment to yaml and refactored

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* fixed smell

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* add profile title to generated markdown

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* removed package version limits for jinja and cryptography

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* addressed pr requests

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt; ([`541eddb`](https://github.com/oscal-compass/compliance-trestle/commit/541eddbfcbdf7b5fff6c4e6f765fda1a2f05bacf))

* feat: Add various docs md improvements (#1159)

* feat: Add various docs md improvements

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;

* Make lint happy

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;

* Make lint fully happy

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;

* Increase test coverage, address review comments

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt; ([`c93b4a1`](https://github.com/oscal-compass/compliance-trestle/commit/c93b4a1554697d184544634fc182bdc01cfe5790))

* feat: add component-generate and component-assemble (#1145)

* initial sketch of author_component

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* initial implementation of author component

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* cleaned output

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* fixed update_uuids.py

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* fixed prose and clarified status consts

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* improve typing for load top level model

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* improved typing and formalized component imp status support

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* cleaned up status defines and removed connection to fedramp in ssp author

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* clarified status

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* comp-gen works with imp status and remarks

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* now make multi-comp markdown

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* added sketch of comp assemble

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* fixed docstrings

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* added comp assem test coverage

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* major refactor of control io

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* made some privates public

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* implemented context and tests pass

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* fixed copy reference issue

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* tests pass and lint ok

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* cleaned up doc strings

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* fixed some smells

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* added generic classes for ssp and comp_def

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* updated docs

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* handle status and remarks better

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* improved remarks handling

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* improved test

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* comp assemble working better

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* addressed pr changes

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* enhanced component test

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* temp fix to markdown version

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* fixed small bug and enhanced test

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* fixed changes in comp generation and removed markdown version from setup.cfg

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt; ([`a4caab2`](https://github.com/oscal-compass/compliance-trestle/commit/a4caab28c26b6391d4b258457c3009e960465a0f))

### Fix

* fix: Use python 3.8 for the release (#1236)

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt; ([`7a9fbe8`](https://github.com/oscal-compass/compliance-trestle/commit/7a9fbe8a1dba77357fd5b87136a56d9ad06bd3a0))

* fix: Update the docs for governed documents (#1219)

* fix: Update the docs for governed documents

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;

* Fix index

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;

* Fix grammar

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt; ([`b38a809`](https://github.com/oscal-compass/compliance-trestle/commit/b38a809c95d04c269498c036df5bc1c198ab679e))

* fix: Fix a bug in governed section validation (#1231)

* fix: Small bug in validation

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;

* Fix typos

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt; ([`c7f3c0d`](https://github.com/oscal-compass/compliance-trestle/commit/c7f3c0d566c988c63979a3bfb40d351824898e3b))

* fix: add top level to parts output by get_statement_parts (#1230)

* added high level statement part to query

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* fixed test

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt; ([`597999e`](https://github.com/oscal-compass/compliance-trestle/commit/597999ef1898d5746e10b2fe706da7e4e57e936d))

* fix: change implementation prompt for part (#1229)

* added for part to imp response

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* added explicit function to find imp label

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt; ([`f929aba`](https://github.com/oscal-compass/compliance-trestle/commit/f929abab713612810434363f8fc8530553b4b51a))

* fix: empty dirs were created during comp-gen (#1225)

* fixed issue

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* added docs

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt; ([`805c9f3`](https://github.com/oscal-compass/compliance-trestle/commit/805c9f3eb4b7cbd2ec717ae0cb0bec5cb0a2d37b))

* fix: issue #1222 (#1223)

Co-authored-by: Vikas Agarwal &lt;75295756+vikas-agarwal76@users.noreply.github.com&gt; ([`96c7290`](https://github.com/oscal-compass/compliance-trestle/commit/96c72902b6b4411e21df658cef5119f7be486829))

* fix: better handling of params in component generate (#1220)

* no-ns now working

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* boosted tests

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* removed ns references

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* refactor and split catalog write

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* fixed arg flags

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* comp_gen fails

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* comp def works

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* changed to param values

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* fix to get title

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* fixed smell

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* fixed lambda loop

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* fixed doc string

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* addressed pr feedback

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt; ([`2675e2f`](https://github.com/oscal-compass/compliance-trestle/commit/2675e2f1ff5823787819b4854b4e35e034a1c8bf))

* fix: csv to oscal cd task (#1208)

* Issue #1141

- assure required columns present

Signed-off-by: degenaro &lt;lou.degenaro@gmail.com&gt;

* Issue #1141

- parameters

* Issue #1141

Refactor code for quality improvement.

* Issue #1141

- include missing columns
- fix several code smells
- fix bug in get_value

* Issue #1141

- Fix code smells.

* Issue #1141.

- Fix code smell.

* Issue #1141

- Code test coverage 100%

* Issue #1141

- remove excess properties
- component description should be blank

Signed-off-by: degenaro &lt;lou.degenaro@gmail.com&gt; ([`049ee83`](https://github.com/oscal-compass/compliance-trestle/commit/049ee83f70e955fa92817222405adbc08f8deb5e))

* fix: simple fix for statement labels not showing properly (#1213)

* removed bad break

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* added test

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt; ([`8d8ae1e`](https://github.com/oscal-compass/compliance-trestle/commit/8d8ae1e5d388e2491e6558f1325ff4d22cc5a58d))

* fix: add profile title to comp-generate md and remove profile option (#1202)

* removed profile option and added prof title to md

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* fixed docstrings

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* reworked comp generate

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* fixed status and rewrite issue

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* capture prose in description

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* added prompt prose and test

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt; ([`711597b`](https://github.com/oscal-compass/compliance-trestle/commit/711597b08490bcc8887d5970e376dc4c0e176df8))

* fix: component definition issues (#1200)

* Issue #1141

- honor user_column.class in config file

* fixed doc string

Co-authored-by: Frank Suits &lt;47203786+fsuits@users.noreply.github.com&gt; ([`067fb91`](https://github.com/oscal-compass/compliance-trestle/commit/067fb9171b8396515cfb2dc6b06623a65cf81183))

* fix: prof resolve should use moustache form as default (#1196)

* default to moustache

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* fixed profile test

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt; ([`530e28b`](https://github.com/oscal-compass/compliance-trestle/commit/530e28bf2143427b9b9dc1aa3cbfb4fb5c3ef2aa))

* fix: profile assemble &#39;after&#39; and &#39;by-id&#39; issue, and added resolve_profile_catalog script (#1190)

* initial fix

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* fixed tests

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* fixed linting

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* handle subparts in prof-gen -assemble

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* fixed sub-part issue

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* fixed oscal version and resolved cat name

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* final tweaks to prof resolution and added tests

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;
Co-authored-by: Ekaterina Nikonova &lt;91102120+enikonovad@users.noreply.github.com&gt; ([`4c772dc`](https://github.com/oscal-compass/compliance-trestle/commit/4c772dcf141b9ffd6c92c62fb7efa586f82bd272))

* fix: Pull display name from the resolved catalog (#1192)

* fix: Pull display name from the catalog

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;

* Small change

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt; ([`8cedd9f`](https://github.com/oscal-compass/compliance-trestle/commit/8cedd9f6ee4b45b8db762a81c2e59dfc83ce3504))

* fix: ssp-assemble was not capturing prose properly for control level imp req responses (#1191)

* fixed comp def issue

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* added doc

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt; ([`2a973cb`](https://github.com/oscal-compass/compliance-trestle/commit/2a973cb83ebaf925071c3bb59c0205b6e0387da3))

* fix: name of subparts added into statement should not be &#34;item&#34; (#1184)

* changed item name assignment

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* fixed jinja subparts test

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt; ([`fcc79cb`](https://github.com/oscal-compass/compliance-trestle/commit/fcc79cb7db14385db1e2e174f27d18726ae4392e))

* fix: Add subparts to the markdown docs (#1182)

* fix: Add adds subparts to the markdown docs

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;

* Make lint happy

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;

* Make lint happy

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;

* fix: Address review comments

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt; ([`44e286b`](https://github.com/oscal-compass/compliance-trestle/commit/44e286ba1ba7369607b4299a13600c117fafd5ca))

* fix: parts labeled Control should be Part (#1176)

* fixed part vs. control bug

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* added docs

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* sub parts mostly working except statement prose

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* fixed control statement prose test

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* fixed control props during cat assemble

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* removed log msgs

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* fixed typo

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* fixed typo

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt; ([`6287991`](https://github.com/oscal-compass/compliance-trestle/commit/62879916da55804bd7171ba51c6794ec021e36d5))

* fix: Fix various issues in markdown docs (#1174)

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt; ([`4615be2`](https://github.com/oscal-compass/compliance-trestle/commit/4615be22ba4522455c441b8474aac45042606024))

* fix: prevent output of default namespace in markdown (#1173)

* fixed output of ns

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* updated docs

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt; ([`7ffc37e`](https://github.com/oscal-compass/compliance-trestle/commit/7ffc37e0f0ef67c9a30bb309a7cf7eee11a77c24))

* fix: combine parts props into a single add rather than two separate ones (#1172)

* initial fix not working

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* fixed order issue with by_ids

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* fixed test after merge conflict

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt; ([`a1ded2c`](https://github.com/oscal-compass/compliance-trestle/commit/a1ded2c08bb94c9b5b61ef828ac6fc73a3fb00c4))

* fix: only show missing value warnings when resolving a profile for ssp (#1171)

* add show_value_warnings to control output of value warning messages

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* updated docs

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt; ([`4afb7fc`](https://github.com/oscal-compass/compliance-trestle/commit/4afb7fc5b2cbb750bd4dbdd99e61825c04b61c07))

* fix: duplicate headers and statement parts added in wrong place (#1163)

* initial fix of dup headers

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* final fixes

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt; ([`ee505f5`](https://github.com/oscal-compass/compliance-trestle/commit/ee505f5b14a0281e9bda1365de7a4f2b15a5096b))

* fix: utf8 issue (#1160)

* fixed utf8 issue

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* added docs

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* updated pre-commit

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt; ([`f1e2a9f`](https://github.com/oscal-compass/compliance-trestle/commit/f1e2a9fa0f44db46fd6674be29cbf1b7dd5bf14e))

* fix: Fix global headers validation when no drawio files are present  (#1155)

* fix: Fix headers validation

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;

* Fix Sonar

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;

* Fix review comments

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;

* Fix typing

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt; ([`0d59427`](https://github.com/oscal-compass/compliance-trestle/commit/0d59427b89d3303b1392c08a7aa07a4ccdcab8a1))

* fix: component generate with new format, clean up of cache tests (#1153)

* improved component handling, cleaned up cache and import tests

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* component generate works with new format

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* added control_read test with bad component header

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* enhanced coverage with updated test file

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt; ([`a5ab848`](https://github.com/oscal-compass/compliance-trestle/commit/a5ab848e836198b09fe819307a2931de072df400))

* fix: Handle adding/deleting section from the markdown control (#1154)

* fix: Handle adding section to the control without alters

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;

* Add tests

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;

* fix: Adress the reviews comment

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt; ([`40cd08b`](https://github.com/oscal-compass/compliance-trestle/commit/40cd08ba48522d20b26343690fb43f57580c610b))

* fix: Bump mkdocstring version (#1151)

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt; ([`aad593b`](https://github.com/oscal-compass/compliance-trestle/commit/aad593b7fdf0a7019c736d5e464a7136f76f5085))

* fix: Correct typo in README (#1142)

Signed-off-by: folksgl &lt;Gfolks14@gmail.com&gt; ([`160707a`](https://github.com/oscal-compass/compliance-trestle/commit/160707a2e2fc23879085263806e851584d2dd405))

* fix: Dont add empty template folder (#1140)

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;

Co-authored-by: Frank Suits &lt;47203786+fsuits@users.noreply.github.com&gt; ([`cf7a63b`](https://github.com/oscal-compass/compliance-trestle/commit/cf7a63bea9b442d39af8f4dccda5f7d484314cf6))

* fix: allow catalog groups with no id and fix validation of links and reference matching (#1137)

* fixed link counting issue

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* refined warning

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* make id changes in groups

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* enhanced group id warning

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* added load_validate functions

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* added more complete test

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* import order

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* adjust warning messages

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt; ([`9e1b206`](https://github.com/oscal-compass/compliance-trestle/commit/9e1b20686b85d166cee98b444e8deb7f40c06b3e))

* fix: catalog-assemble was writing a new file when there were no changes to the file (#1139)

* fixed overwrite issue caused by empty params list in assembled catalog

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* cleaned up

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt; ([`e6949e2`](https://github.com/oscal-compass/compliance-trestle/commit/e6949e276dd683f5f54072b7db29c9bf15335d34))

* fix: remove extraneous parens in unit tests. (#1138)

* Remove extraneous parens in unit tests.

* Fix comment.

* Fix .pre-commit-config.yaml. ([`90cb2ee`](https://github.com/oscal-compass/compliance-trestle/commit/90cb2ee8f3d6b04c69971a542440ad66fec5188c))

* fix: Fix trestle version in the docs (#1134)

* fix: Fix trestle version in the docs

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;

* Downgrade version of mkdocstrings

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;

* fix: Update docs

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt; ([`d7d3cfc`](https://github.com/oscal-compass/compliance-trestle/commit/d7d3cfce8f2de248fc957a5146907cac118071a6))

* fix: Improve logging when validating headings in gov docs (#1133)

* fix: Improve logging when validating headings in gov docs

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;

* Downgrade mkdocstrings for now

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt; ([`a641299`](https://github.com/oscal-compass/compliance-trestle/commit/a6412996d991c49261448b6eae80471d37ab2664))

### Unknown

* Merge pull request #1237 from IBM/develop

chore: Trestle release ([`85264e9`](https://github.com/oscal-compass/compliance-trestle/commit/85264e97c8cb8019b4478b121af7e5db258c5520))

* Merge branch &#39;main&#39; into develop ([`5994c29`](https://github.com/oscal-compass/compliance-trestle/commit/5994c29581a59e34b16932c3a9c0cdb63a8b93c9))

* Merge pull request #1235 from IBM/develop

chore: Trestle Release ([`ac6de64`](https://github.com/oscal-compass/compliance-trestle/commit/ac6de6416739a2ed0b77c314d5f4528a74885806))

## v1.1.0 (2022-05-24)

### Chore

* chore: Merge back version tags and changelog into develop. ([`babfc7e`](https://github.com/oscal-compass/compliance-trestle/commit/babfc7eef148d5d6ff9c31f72c44f10093aa7c23))

### Feature

* feat: filter ssp by component

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt; ([`d675e49`](https://github.com/oscal-compass/compliance-trestle/commit/d675e4936151d0467362ada4442154cb841d87e2))

* feat: validate refs and resources in catalogs and models

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt; ([`1c17bf7`](https://github.com/oscal-compass/compliance-trestle/commit/1c17bf75df4ceab99c6f3ae68ee620e57738d592))

### Fix

* fix: resolve pre-commit issue (#1126)

* fix: resolve precommit issue

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* fix: updated doc string

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt; ([`679cadc`](https://github.com/oscal-compass/compliance-trestle/commit/679cadc8bb839131d7a458b4b5cd082ed4535e24))

* fix: Do not validate extra files in author folders

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt; ([`25a1721`](https://github.com/oscal-compass/compliance-trestle/commit/25a172160c651411c1521507557450d49592561d))

* fix: better handling of child controls

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt; ([`c224f92`](https://github.com/oscal-compass/compliance-trestle/commit/c224f929ce2f9e682149e73055b7b195bbdaf92c))

* fix: remove unused classes from the generated oscal files

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt; ([`9a3ee20`](https://github.com/oscal-compass/compliance-trestle/commit/9a3ee20be9520bad084ac2df556eacbd23c7907f))

* fix: Allow subfolders in template folder

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt; ([`7223e1b`](https://github.com/oscal-compass/compliance-trestle/commit/7223e1b7d9dd8ef659867853a00cdbc7ca66a050))

* fix: updated documentation

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt; ([`8eca1f0`](https://github.com/oscal-compass/compliance-trestle/commit/8eca1f0abc4a62a6e1db34b32b4f615aff097c0d))

* fix: Add control id to the generated docs

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt; ([`b666956`](https://github.com/oscal-compass/compliance-trestle/commit/b666956adf221420b77a980eedec2ffc044d0e6e))

### Unknown

* Merge pull request #1127 from IBM/develop

chore: Trestle Release ([`7ee1088`](https://github.com/oscal-compass/compliance-trestle/commit/7ee10884fc72ed318c3e62dd72b27518b16e4bf5))

## v1.0.2 (2022-05-05)

### Chore

* chore: Merge back version tags and changelog into develop. ([`219bada`](https://github.com/oscal-compass/compliance-trestle/commit/219bada663cf6620c232718c50a6379c41473261))

### Fix

* fix: check for circular imports during profile resolution (#1107)

* now check circular imports

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* updated docs

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt; ([`81469db`](https://github.com/oscal-compass/compliance-trestle/commit/81469dbcca3ffcb140ac09023b7de17671c4386b))

* fix: prevent moustaches in resolved profile catalog (#1106)

* better handling of choice prose

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* added new test

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt; ([`f9edc81`](https://github.com/oscal-compass/compliance-trestle/commit/f9edc8185db30330cfe33d3cf02ef55e90135692))

* fix: Add ability to remove group title (#1114)

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt; ([`4303d76`](https://github.com/oscal-compass/compliance-trestle/commit/4303d760935b0f34a13cccf9caaac4e90a05de83))

* fix: prevent blowfish warning due to new release of cryptography (#1112)

* force backlevel cryptography due to blowfish issue

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* added doc string

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt; ([`f13fe31`](https://github.com/oscal-compass/compliance-trestle/commit/f13fe31ae4c790ef7b495c3f5418d3c26de96841))

### Unknown

* Merge pull request #1115 from IBM/develop

chore: Trestle bugfix release ([`746d239`](https://github.com/oscal-compass/compliance-trestle/commit/746d239ce64df487fae5bdbd5c727cfd132935cc))

## v1.0.1 (2022-04-27)

### Chore

* chore: Merge back version tags and changelog into develop. ([`77f0e50`](https://github.com/oscal-compass/compliance-trestle/commit/77f0e50bfe4e369a215401f9a4b9e56d193fd829))

### Fix

* fix: bump readme refs to 1.0.x (#1103)

* initial change to 1.0.x

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* final changes for 1.0.x

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt; ([`488cd40`](https://github.com/oscal-compass/compliance-trestle/commit/488cd4003a97d0142cc65e91fa660dd2b83bd75b))

### Unknown

* Merge pull request #1104 from IBM/develop

chore: Trestle Stable Release OSCAL 1.0.2 ([`f992596`](https://github.com/oscal-compass/compliance-trestle/commit/f99259668f9faf8ed7af0b0a41beb8dc4b9d4cd4))

## v1.0.0 (2022-04-27)

### Breaking

* feat: updated to OSCAL 1.0.2 support (#1097)

BREAKING CHANGE: pushed to OSCAL 1.0.2

* updated to oscal 1.0.2 and tests pass

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* updated readme and move oscal version

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* updated json oscal version to 1.0.2

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* clarified wording re 1.0.0 and 1.0.2

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt; ([`a2aa3dd`](https://github.com/oscal-compass/compliance-trestle/commit/a2aa3dd53e67096004ba4e202fef8c7586462888))

### Chore

* chore: Merge back version tags and changelog into develop. ([`4b6500e`](https://github.com/oscal-compass/compliance-trestle/commit/4b6500e58189db65254b9c13864fbb01cc4278a7))

### Documentation

* docs: update readme and index md files (#1099)

* updated readme and index

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* tweaked docs

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt; ([`f0bd541`](https://github.com/oscal-compass/compliance-trestle/commit/f0bd5412be6bb7b9f88dc2ee3f6b1608c12a9268))

### Fix

* fix: various task transformer improvements (#1100)

* fix: various task transformer improvements

for xlsx
- remove support for column &#34;Version&#34;
- add support for columns &#34;goal_version&#34;, &#34;rule_name_id&#34;, &#34;rule_version&#34;
- add support for profile-type generation &#34;by-goal&#34;, &#34;by-rule&#34;,
&#34;by-control&#34;, &#34;by-check&#34;
- skip rows where control_id or goal_id is missing with complaint
- skip rows where control_id and goal_id are missing, after 100
consecutive terminate processing
- improve sotring of controls

for ocp4
- give warning (not failure) when unable to extract title from
compliance-as-code rule.yml

* &#34;oscal-version&#34;: &#34;1.0.2&#34;

* Fix code smell.

* Do not emit parameters in the case of &#34;by-control&#34;.

Co-authored-by: Frank Suits &lt;47203786+fsuits@users.noreply.github.com&gt; ([`c869f37`](https://github.com/oscal-compass/compliance-trestle/commit/c869f37f9c942dc151ac729a6fa3506c375c9da7))

### Unknown

* Merge pull request #1102 from IBM/develop

chore: Trestle Stable Release OSCAL 1.0.2 ([`ca23972`](https://github.com/oscal-compass/compliance-trestle/commit/ca239723e0cb51f64d44a86c7b0d4fc98828d13e))

## v0.37.0 (2022-04-12)

### Chore

* chore: Merge back version tags and changelog into develop. ([`0850d21`](https://github.com/oscal-compass/compliance-trestle/commit/0850d21a38ac26e2c250c3fded5f5aca7a5e736d))

### Documentation

* docs: small fixes to cli.md (#1091)

* minor doc fixes

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* spreadsheet typo

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt; ([`6206869`](https://github.com/oscal-compass/compliance-trestle/commit/6206869f12a16150fccb652896c1743add1a8c59))

### Feature

* feat: bump feature with added docs (#1092)

* updated doc

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* final update

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt; ([`d1cdad3`](https://github.com/oscal-compass/compliance-trestle/commit/d1cdad3360a122cfa9bcd7ea8c3252369966f49e))

### Fix

* fix: Cherry pick all fixes from the prerelease hotfix branch (#1090)

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt; ([`06e1470`](https://github.com/oscal-compass/compliance-trestle/commit/06e147088ec0808bd04f7a5f4a10dc1f13bb7275))

* fix: Improved filtering column matching. (#1082)

* Improved filtering column matching.

* Fix lint.

Co-authored-by: Frank Suits &lt;47203786+fsuits@users.noreply.github.com&gt; ([`712822e`](https://github.com/oscal-compass/compliance-trestle/commit/712822e387c592f667a763ede6f145590a9b088e))

### Unknown

* Merge pull request #1093 from IBM/develop

chore: Trestle Stable Release OSCAL 1.0.0 ([`0c09ed9`](https://github.com/oscal-compass/compliance-trestle/commit/0c09ed9cbae909a2e833335f06684b60540f01b5))

## v0.36.0 (2022-04-04)

### Chore

* chore: Merge back version tags and changelog into develop. ([`acf1143`](https://github.com/oscal-compass/compliance-trestle/commit/acf11432fe455474425cf7245bfe55b85294cad7))

### Documentation

* docs: update ssp and profile authoring document (#1075)

* fixed issue with cat-assem overwrite when same

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* fixed pro assem when no change

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* fixed ssp assem

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* fixed doc names

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* initial update

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* final doc changes ssp

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt; ([`4211529`](https://github.com/oscal-compass/compliance-trestle/commit/42115298bb835885eb6662d8dabfcd68e05b1f59))

### Feature

* feat: Add ability to generate multiple markdown files using Jinja (#1077)

* Add ability to generate multiple markdown files with sections

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;

* feat: Add docs

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;

* Add more tests

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;

* Use sorted id flow

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;

Co-authored-by: Frank Suits &lt;47203786+fsuits@users.noreply.github.com&gt; ([`f41fc9f`](https://github.com/oscal-compass/compliance-trestle/commit/f41fc9fe3df95985f50ef29e09be07962fc8a7e9))

### Fix

* fix: profile tools now handle choice and label properly (#1078)

* fixed loops

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* added text for second column

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* fixed typo

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* choice update working now

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* updated docs

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* removed unneeded check

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt; ([`4d9363a`](https://github.com/oscal-compass/compliance-trestle/commit/4d9363ab827cc3d26a032336b35a50feec9a59ad))

* fix: jinja control loops sort controls better (#1076)

* fixed loops

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* added text for second column

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* fixed typo

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt; ([`d89128b`](https://github.com/oscal-compass/compliance-trestle/commit/d89128b83deddcd64dfab00d0a7ddcabe8415349))

* fix: catalog name confusion and overwrite of same assembled files (#1074)

* fixed issue with cat-assem overwrite when same

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* fixed pro assem when no change

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* fixed ssp assem

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* fixed doc names

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* addressed review requests

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt; ([`1ba9a35`](https://github.com/oscal-compass/compliance-trestle/commit/1ba9a35dee356e3b8df0fedbad30d9a420fa4e79))

* fix: trestle transformation tasks naming convention. (#1071)

* Rename cis-to ... ocp4-cis-profile-to-catalog,cd

* component-definition

* oscal-profile-to-osco-profile

* docs

* fix bug + 100% code coverage for ocp4-catalog

* tanium-report-to-oscal-ar

* docs

* Legacy.

* Update test name.

* OSCO result + Tanium result fixes.

* Fix missed re-names.

* Simplify tests.

* Remove logger.error

* Fix Code Smells.

* Fix code smells.

* paths constants

Signed-off-by: degenaro &lt;lou.degenaro@gmail.com&gt; ([`d179d78`](https://github.com/oscal-compass/compliance-trestle/commit/d179d78671f2926c1651ad1eaa8f906f8c2aaefb))

* fix: delay choice subst (#1072)

* first attempt

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* param choice subst works

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* better handling of setparams and ssp table

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* boosted coverage

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* boosted coverage

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* ssp_io coverage

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* more realistic names

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* cleaned up choices and moustaches

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* choice sub happens at last stage

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* update docs

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* add new profile

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* fixed smell

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt; ([`16cf5e4`](https://github.com/oscal-compass/compliance-trestle/commit/16cf5e4374ce5f304cd491d1dc1e30de07e6a293))

* fix: param choice substitution works properly (#1070)

* first attempt

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* param choice subst works

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* better handling of setparams and ssp table

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* boosted coverage

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* boosted coverage

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* ssp_io coverage

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* more realistic names

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* cleaned up choices and moustaches

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt; ([`181f586`](https://github.com/oscal-compass/compliance-trestle/commit/181f58697ef18b114dd339e0ac903ee52bfa6c97))

* fix: use set-parms of CD ctl-impl for alternatives; discard catalog hack (#1068)

* fix: use set-parms of CD ctl-impl for alternatives; discard catalog hack

* Oops, misc. debug junk to be removed.

* Improve function descriptions.

* Various fixes.

Co-authored-by: Frank Suits &lt;47203786+fsuits@users.noreply.github.com&gt; ([`d9e75e7`](https://github.com/oscal-compass/compliance-trestle/commit/d9e75e78b53851232adc635eca4f224e4c05d81a))

* fix: Fix Jinja dependency version (#1069)

* fix: Fix Jinja version

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;

* Add init file

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;

* added comment to config.ini

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* added keep_cwds

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* added root info output

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* updated setup.cfg

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* fixed brackets

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* again

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* setup requires

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* latest setuptools_scm

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* limit setuptools

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* limit both

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* try again

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* try explicit ini

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* added .md

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* again

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* added jinja

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* added more

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* now use latest setuptools and setuptools_scm

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

Co-authored-by: Frank Suits &lt;frankst@au1.ibm.com&gt; ([`34c703a`](https://github.com/oscal-compass/compliance-trestle/commit/34c703abca210c9e2c2d4675822119214f1bf3e5))

* fix: added methods in catalog interface to sort controls by sort-id (#1067)

* provide sort by sort-id when using catalog_interface

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* fixed doc string

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt; ([`dd04292`](https://github.com/oscal-compass/compliance-trestle/commit/dd04292d41090fb951b5a6284356e41c6a07d62a))

* fix: lock oscal to release-1.0.0 (#1065)

* point nist-source to release 1.0

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* lock oscal to 1.0.1 patch

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* updated docs

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* now at v1.0.0

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* updated nist-content to tags/v1.0.0

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* moved nist-source again

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt; ([`1e6b554`](https://github.com/oscal-compass/compliance-trestle/commit/1e6b5547ed53b82e45f0c9478cc91970c8980d29))

### Unknown

* Merge pull request #1080 from IBM/develop

chore: Trestle Beta Release ([`8859463`](https://github.com/oscal-compass/compliance-trestle/commit/885946305b750bc96117915f420f74f24873ab6b))

## v0.35.0 (2022-03-22)

### Chore

* chore: remove catalog_helper and use functionality in catalog_interface (#1061)

* moved validator_helper to model_utils

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* changed doc string

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* docs validate

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* initial removal of catalog_helper

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* removed cat_helper

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* docs validate

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* removed tg

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* fixed bad loop references

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt; ([`4a60a20`](https://github.com/oscal-compass/compliance-trestle/commit/4a60a2037698e0c796b598557a5bdd94d0293e4e))

* chore: move val helper (#1060)

* moved validator_helper to model_utils

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* changed doc string

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* docs validate

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* removed unneeded TG

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt; ([`8864d5d`](https://github.com/oscal-compass/compliance-trestle/commit/8864d5d41da388363e4d8b58f2ecf80cb8415bb3))

* chore: Remove error duplicates and standarize exceptions part 2 (#1058)

* Remove the rest of logger errors

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;

* Remove useless debug line

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;

* Remove more duplicated logs

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;

* Change debug logs to trace

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;

* Small change

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt; ([`484de2c`](https://github.com/oscal-compass/compliance-trestle/commit/484de2cb2f0957bcf062eb143dd8791a08e8a55e))

* chore: Remove error duplicates and standarize exceptions (part 1) (#1052)

* chore: Example of logging and exception handling

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;

* Convert more files to the common structure

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;

* More changes

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt; ([`4f92845`](https://github.com/oscal-compass/compliance-trestle/commit/4f928451e7a3a44d9e240627ce1cdf9056304503))

* chore: Optimize images (#1054)

/docs/tutorials/ssp_profile_catalog_authoring/trestle_ssp_author_options.png -- 55.51kb -&gt; 44.47kb (19.9%)

Signed-off-by: ImgBotApp &lt;ImgBotHelp@gmail.com&gt;

Co-authored-by: ImgBotApp &lt;ImgBotHelp@gmail.com&gt;
Co-authored-by: Frank Suits &lt;47203786+fsuits@users.noreply.github.com&gt; ([`85bfd94`](https://github.com/oscal-compass/compliance-trestle/commit/85bfd941213dc8ecaa389ff2150a5e2be62b30d9))

* chore: increase coverage and remove checks for dict that arent needed after OSCAL 1.0.0 (#1039)

* initial cleanup of dicts

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* fixed typo

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* attempt fix for 3.7

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* responded to pr change requests

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt; ([`e84855e`](https://github.com/oscal-compass/compliance-trestle/commit/e84855e160e730991f7d85ae57baf5c42fca4e56))

* chore: Refactor utils and split common functionality into logical parts (#1000)

* chore: Refactor utils

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;

* chore: Update docs

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;

* chore: Change imports

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;

* chore: Fix test import

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;

* chore: Rename utils

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;

* chore: Update docs

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;

* chore: Address feedback

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;

Co-authored-by: Frank Suits &lt;47203786+fsuits@users.noreply.github.com&gt; ([`4fb833d`](https://github.com/oscal-compass/compliance-trestle/commit/4fb833df34129498894e36c00210aa7fd001719a))

* chore: Merge back version tags and changelog into develop. ([`38492fa`](https://github.com/oscal-compass/compliance-trestle/commit/38492fae9b7ea921857457d34348a8d448b8d6df))

### Documentation

* docs: ssp tutorial update (#1034)

* updated ssp authoring tutorial

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* added comment

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* addressed review requests to clarify docs

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* final doc tweaks

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* force flake8 not to run parallel

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* jobs set to 1 in setup.cfg

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* jobs=1 in makefile

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* edited yaml

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* tweaked yaml

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* disabled flake8-bandit, updated ssp docs

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt; ([`12ab44f`](https://github.com/oscal-compass/compliance-trestle/commit/12ab44f39a15f8de0388cf7ffab3cce44bc396cf))

* docs: Fix typo personell-&gt;personnel. (#1014)

Signed-off-by: Alexander Stein &lt;alexander.stein@nist.gov&gt; ([`f3041be`](https://github.com/oscal-compass/compliance-trestle/commit/f3041beea9ea6093bc7b462521c9cff325cf9f4b))

### Feature

* feat: xlsx filter (#1050)

* Check for xlsx-to-profile required config vars.

* Support for filter-column.

* Feat/xlsx filter.

* Fix code review items. ([`9f63412`](https://github.com/oscal-compass/compliance-trestle/commit/9f6341257f755e49173050b4d0f2e32c75874610))

* feat: xlsx-to-oscal-profile (#1046)

* feat: xlsx-to-oscal-profile

- create common xlsx module
- create xlsx-to-oscal-profile task
- artifacts for 100% code coverage

* fix lint error - mkdocs

* Relocate xlsx_helper.

* Refactor common code.

* Refactor.

* Refactor.

* Code smell.

* Code smells.

* Use &#34;public&#34; URL in test data.

* Fix: year is 2022 in code copyright.

* fix: list_utils is_ordered_sublist

* Ugh. lint.

* Update cli.md with new changed task name.

* Add xlsx-to-oscal-profile to cli.md.

* Tweak.

* Ugh. mdformat.

* Reduce duplicate code. ([`9695933`](https://github.com/oscal-compass/compliance-trestle/commit/96959339818baaa06b0a9c00dedae81c9c99dcec))

* feat: Resolve UUID Imports During Profile Resolution, Not Only Explicit Imports (#1023)

* feat: Resolve import uuid anchor during profile resolution.

Signed-off-by: Alexander Stein &lt;alexander.stein@nist.gov&gt;

* feat: Add profile resolv docs

And of course reach to the two commit minimum for the PR. :-)

Signed-off-by: Alexander Stein &lt;alexander.stein@nist.gov&gt;

* feat: Check for missing resources pre-assignment

Tests wisely indicate that a profile.back_matter, can have a falsey None
value for resources and there should a conditional assignment test before
to ensure that.

Signed-off-by: Alexander Stein &lt;alexander.stein@nist.gov&gt;

* feat: Add with @fsuit&#39;s feedback.

Signed-off-by: Alexander Stein &lt;alexander.stein@nist.gov&gt; ([`ae803e7`](https://github.com/oscal-compass/compliance-trestle/commit/ae803e74cda58694a294ccfe1e979f2993626ec8))

* feat: aggregate properties as results level (#997)

* feat: aggregate properties as results level

* fix code smell.

* Generalize common property removal from observations.

* Use @classmethod annotation.

* Undo @classmethod annotation.

* mkdocs

* Tanium - result per local definition with aggregate properties.

* Use if x: rather than if len(x) &gt; 0: for most circumstances.

* Handle empty local-definitions.

* List comprehension.

* Employ set intersection.

Co-authored-by: Frank Suits &lt;47203786+fsuits@users.noreply.github.com&gt; ([`174aabe`](https://github.com/oscal-compass/compliance-trestle/commit/174aabe401b9fbe35a10efcc9df159a3537d3c0d))

* feat: Validate OSCAL directories (#990)

* feat: Validate OSCAL directories

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;

* feat: Add yaml extension

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;

* feat: Clean up tests

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;

* feat: Make keep files hidden on windows

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;

* feat: Make keep files hidden on windows

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;

* feat: Address feedback

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;

* feat: Address review feedback

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;

* feat: Typo

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt; ([`941e4fc`](https://github.com/oscal-compass/compliance-trestle/commit/941e4fc6fe9e3c4700f4f7c43be849fb176fb57d))

### Fix

* fix: use control sort-id for sorting (#1062)

* implemented sort-id

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* improved docs

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* no cover as needed

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* clarified sub name

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* fixed iterations

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* consistent handling of sort-id

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt; ([`fb65bfb`](https://github.com/oscal-compass/compliance-trestle/commit/fb65bfbaadca2240f535d7db057baed108ec0bf2))

* fix: task tanium-to-oscal poor aggregation performance (#1053)

* fix: task tanium-to-oscal poor aggregation performance

* Ugh. docs.

* Fix review items for cache.py

* Fix for comments on list_utils.py

* Fix review items for tanium.py

* Improve aggregation performance.

* Remove obsolete code.

* Docs.

* Types.

* Add test for list_utils and fix bug!

* Improve function name and test.

* Add unit tests for transformer helper.

* Skip accounting when not needed.

Co-authored-by: Frank Suits &lt;47203786+fsuits@users.noreply.github.com&gt; ([`9ea118c`](https://github.com/oscal-compass/compliance-trestle/commit/9ea118c472b83491a30bbeabe35afbc35fd4e96d))

* fix: avoid write of new file if no changes after -assemble (#1057)

* update timestamps

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* added tests

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* profile assemble write only on change

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* no overwrite ssp assemble

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* cleaned up ssp overwrite

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* removed transform tests

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* all write on assemble will check for change

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* modified docs

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* fixed typing

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* changed to last_modified

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt; ([`893eec6`](https://github.com/oscal-compass/compliance-trestle/commit/893eec6afcf6eaaa9f831528995de267a0cabe6b))

* fix: update timestamps for all assemble tools (#1056)

* update timestamps

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* added tests

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* handle last_modified missing

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt; ([`cccd7a2`](https://github.com/oscal-compass/compliance-trestle/commit/cccd7a2e9399bf001ab101a405f370d92c1d000c))

* fix: flake8 bandit reenable, remove transformcmd, empty config.ini (#1055)

* enabled flake8-orbit and emptied config.ini

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* removed xform cmd

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* disable password check in cache.py

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* try again

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* noqa on correct lines

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* reran mkdocs

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt; ([`a7543c2`](https://github.com/oscal-compass/compliance-trestle/commit/a7543c24c80b6904a27a678aff3bce357fc44629))

* fix: more complete parameter info in yaml headers (#1049)

* added param_to_dict and reverse

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* fixed tests with full parameter

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* added docstring

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* fixed smell

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* fixed docstring

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* params without values also output by default

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* reworked profile assemble setparams

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* updated docs

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* tweaked help string

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* redid using profile-values

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* removed dead code and updated docs

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* fixed typo

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* fixed ohv

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt; ([`7a3b098`](https://github.com/oscal-compass/compliance-trestle/commit/7a3b098d2ef9f88f564908927240524021d5c768))

* fix: block withdrawn controls from being written as markdown (#1045)

* updated ssp authoring tutorial

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* added comment

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* addressed review requests to clarify docs

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* final doc tweaks

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* force flake8 not to run parallel

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* jobs set to 1 in setup.cfg

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* jobs=1 in makefile

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* edited yaml

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* tweaked yaml

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* disabled flake8-bandit, updated ssp docs

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* initial move of add as part of create command

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* updated docstrings

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* fixed add test docstring

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* clarified json yaml in add

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* dont write out withdrawn controls

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* more doc strings

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* lowercase check for withdrawn

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* added function to remove withdrawn controls from catalog

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt; ([`053ab0e`](https://github.com/oscal-compass/compliance-trestle/commit/053ab0eac098104ed062acb80b4b65f419d37323))

* fix: remove add command and incorporate it into the create command (#1036)

* updated ssp authoring tutorial

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* added comment

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* addressed review requests to clarify docs

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* final doc tweaks

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* force flake8 not to run parallel

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* jobs set to 1 in setup.cfg

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* jobs=1 in makefile

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* edited yaml

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* tweaked yaml

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* disabled flake8-bandit, updated ssp docs

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* initial move of add as part of create command

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* updated docstrings

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* fixed add test docstring

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* clarified json yaml in add

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* more fixes of docs after moving add to create

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* fixed mdformat

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* typos

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* typo

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt; ([`ddde5f5`](https://github.com/oscal-compass/compliance-trestle/commit/ddde5f537158f5621f3d5d0a06791400076d4a4f))

* fix: Improve column heading matching. (#1035)

* fix: Improve column heading matching.

* Spelling fixes.

* Standardize task name and remove extraneous typing.

* Fix code-format.

* Fix docs.

* Reduce code smells.

* Fix code smells.

* Fix code smells.

* Fix code smells.

* Fix code smells.

* Fix code smells.

* Fix code smells.

* Fix code smells. ([`a51fa1e`](https://github.com/oscal-compass/compliance-trestle/commit/a51fa1e9a953dd84e88c344b4d8368d90e9cea41))

* fix: improve sections (#1033)

* normalized commands and added required-sections

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* added docs

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* improve handling of sections_dict

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* sections better and fixed args issue

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* ready to prompt for params

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* required sections working

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* added allowed sections

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* address PR change requests

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* trestle_root should be path

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt; ([`8e6c632`](https://github.com/oscal-compass/compliance-trestle/commit/8e6c632237747e6e75cf24886418438a25ae46f1))

* fix: consistent author commands and support for required-sections (#1030)

* normalized commands and added required-sections

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* added docs

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* improve handling of sections_dict

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt; ([`08953d1`](https://github.com/oscal-compass/compliance-trestle/commit/08953d19a2144f98051b33917eca534521de115c))

* fix: profile params (#1015)

* updated docs and abstracted string formatting of params

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* added param_id

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* fixed param_id

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* added comments

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* more control over parameter formatting

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* minor bug

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* boosted coverage and enabled cat assemble into orig catalog

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* boosted coverage

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* converted preserve_header_values to overwrite_header_values

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* addresed review questions

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt; ([`30c0ec1`](https://github.com/oscal-compass/compliance-trestle/commit/30c0ec1097140c9e88bc43f46a2ccc7a1273f81e))

* fix: 2 bugs xlsx-to-oscal-component-definition (#1017) ([`81d4bf2`](https://github.com/oscal-compass/compliance-trestle/commit/81d4bf2682dacaba3ee09061a790e8a2c15564a4))

* fix: updated documentation for trestle (#1006)

* fix: updated documentation for trestle

* fix: updated documentation

Co-authored-by: Vikas &lt;avikas@in.ibm.com&gt;
Co-authored-by: Frank Suits &lt;47203786+fsuits@users.noreply.github.com&gt; ([`8d3187d`](https://github.com/oscal-compass/compliance-trestle/commit/8d3187dd27cbf2fec0eab787bf6b19ddceebf519))

* fix: missing params in generated catalog and better hidden file handling on windows (#999)

* initial cleanup

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* fixed missing params in catalogs

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* setting param values rather than label

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt; ([`c4550f5`](https://github.com/oscal-compass/compliance-trestle/commit/c4550f541c53327bac3ad38f1feaf262d0b9be27))

* fix: Second stage code cleanup and dead code removal (#993)

* reverted utils change

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* final cleanup

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* addressed pr review changes

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt; ([`79b2f61`](https://github.com/oscal-compass/compliance-trestle/commit/79b2f61baac7adbf69e1474a5e218d664bec65ff))

* fix: cleanup phase I including split of profile_resolver (#991)

* initial cleanup including prof resolver split

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* removed parse_file

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* function to query verbosity

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* cleaned up repository

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* as_list and prof resolver

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* updated mkdocs

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* address pr feedback and more cleanup

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* regen of docs

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* made log calls private

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt; ([`39134aa`](https://github.com/oscal-compass/compliance-trestle/commit/39134aad2ee55e60a89f59c691dc145008b77206))

* fix: allow trace logging with verbose level 2 (#989)

* initial version of trace logging

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* added example

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt; ([`7b4b349`](https://github.com/oscal-compass/compliance-trestle/commit/7b4b34955020ff5f2608c0f9af84520f45cb86f7))

* fix: README documentation improvements (#987)

* Remove redundant dot

Signed-off-by: Guy Zylberberg &lt;guyzyl@gmail.com&gt;

* Add pip install command line

Signed-off-by: Guy Zylberberg &lt;guyzyl@gmail.com&gt;

* Grammer improvements

Signed-off-by: Guy Zylberberg &lt;guyzyl@gmail.com&gt;

* Add reference to Python installation guide

Signed-off-by: Guy Zylberberg &lt;guyzyl@gmail.com&gt; ([`0ad4996`](https://github.com/oscal-compass/compliance-trestle/commit/0ad499611c3fd6a0c0e8dc258bb1dd8190e4bfba))

* fix: change verbose assignments from boolean to integer (#988)

* added link to trestle ssp demo

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* added docs

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* did pre-commit properly

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt; ([`6aed714`](https://github.com/oscal-compass/compliance-trestle/commit/6aed7142334af6ee97345248224d05de875eae12))

### Unknown

* Merge pull request #1064 from IBM/develop

chore: Trestle release ([`79d828e`](https://github.com/oscal-compass/compliance-trestle/commit/79d828e96f6a721bdc55eadd02247277a579a750))

* Optimize images (#1038)

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;

Co-authored-by: ImgBotApp &lt;ImgBotHelp@gmail.com&gt;
Co-authored-by: Ekaterina Nikonova &lt;91102120+enikonovad@users.noreply.github.com&gt; ([`9ccce98`](https://github.com/oscal-compass/compliance-trestle/commit/9ccce98ff03b535f7ea3dc6790e05cd5b310c9bc))

## v0.34.0 (2022-01-07)

### Chore

* chore: Merge back version tags and changelog into develop. ([`496973a`](https://github.com/oscal-compass/compliance-trestle/commit/496973afeb1c3bfa697bf1fa4705764008ffd8d8))

### Documentation

* docs: update ssp workflow and minor changes to other docs (#985)

* updated ssp docs

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* additional edits and validation of docs

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* typo

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt; ([`45be184`](https://github.com/oscal-compass/compliance-trestle/commit/45be1842d1fdc634d8ae9b5b404da4e59ea13d18))

### Feature

* feat: Add custom parameter wrapping to jinja (#976)

* feat: Add custom parameter wrapping to jinja

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;

* feat: Fix docs

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;

* feat: Address feedback

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt; ([`4289ca0`](https://github.com/oscal-compass/compliance-trestle/commit/4289ca0bd1cac83146a4f9080e0eb7f766d78db3))

* feat: add jinja datestamp output (#970)

* feat: add jinja datestamp output

Signed-off-by: Doug Chivers &lt;doug.chivers@uk.ibm.com&gt;

* update doc formatting

Signed-off-by: Doug Chivers &lt;doug.chivers@uk.ibm.com&gt;

* fix deprecation warning for number captions regex

Signed-off-by: Doug Chivers &lt;doug.chivers@uk.ibm.com&gt;

* mdformat for docs addition

Signed-off-by: Doug Chivers &lt;doug.chivers@uk.ibm.com&gt;

* add tests for md datestamp

Signed-off-by: Doug Chivers &lt;doug.chivers@uk.ibm.com&gt;

* add test case for invalid jinja tag

Signed-off-by: Doug Chivers &lt;doug.chivers@uk.ibm.com&gt;

* use const for datestamp format string

Signed-off-by: Doug Chivers &lt;doug.chivers@uk.ibm.com&gt;

* update docs for new datestamp format

Signed-off-by: Doug Chivers &lt;doug.chivers@uk.ibm.com&gt;

Co-authored-by: Doug Chivers &lt;doug.chivers@uk.ibm.com&gt;
Co-authored-by: Ekaterina Nikonova &lt;91102120+enikonovad@users.noreply.github.com&gt; ([`2b92da1`](https://github.com/oscal-compass/compliance-trestle/commit/2b92da100f0646dabf3a56a6544dd72bc66c4958))

* feat: add optional numbering of figures and tables when generating md… (#964)

* feat: add optional numbering of figures and tables when generating md ssp using jinja

Signed-off-by: Doug Chivers &lt;doug.chivers@uk.ibm.com&gt;

* fix lint errors

Signed-off-by: Doug Chivers &lt;doug.chivers@uk.ibm.com&gt;

* add tests for number caption &amp; bug fix

Signed-off-by: Doug Chivers &lt;doug.chivers@uk.ibm.com&gt;

Co-authored-by: Doug Chivers &lt;doug.chivers@uk.ibm.com&gt;
Co-authored-by: Ekaterina Nikonova &lt;91102120+enikonovad@users.noreply.github.com&gt; ([`89bafe7`](https://github.com/oscal-compass/compliance-trestle/commit/89bafe7f1fcfe3fe1db4900be483f8416fb824b7))

### Fix

* fix: OCP4 CIS Component Definition rules should have unique descriptions (#975)

* fix: OCP4 CIS Component Definition rules should have unique descriptions

* Use consistent json format for selected &amp; enabled rules.

* Revise tutorial: use 3 selected rules to reduce comp-def.json size.

* Use https.

* Add types to parameters and return value of method _get_title.

* Add detailed operational description to method _get_title.

Co-authored-by: Ekaterina Nikonova &lt;91102120+enikonovad@users.noreply.github.com&gt;
Co-authored-by: Frank Suits &lt;47203786+fsuits@users.noreply.github.com&gt; ([`299db5a`](https://github.com/oscal-compass/compliance-trestle/commit/299db5acffe3f247cba86382a873cc1029b45ded))

* fix: better handling of groups containing groups in ssp gen and assemble (#977)

* added test and json files

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* final fixes of recursive group handling

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* boosted coverage

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* boosted coverage and changed recurse to mean recurse within controls only

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt; ([`5fa1820`](https://github.com/oscal-compass/compliance-trestle/commit/5fa18203d89ff353f8500f892b85b957385ebb11))

* fix: several issues in profile assemble and catalog generate (#974)

* fixed several bugs in profile and catalog

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* doc string

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* improved doc strings and cleaned up namings

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt; ([`0435c84`](https://github.com/oscal-compass/compliance-trestle/commit/0435c8405e4ff1b6608ec93fb3baafb61356d1d8))

* fix: fix json blocks in md so mdformat doesnt raise cannot format warning (#973)

Signed-off-by: Doug Chivers &lt;doug.chivers@uk.ibm.com&gt;

Co-authored-by: Doug Chivers &lt;doug.chivers@uk.ibm.com&gt; ([`73b0612`](https://github.com/oscal-compass/compliance-trestle/commit/73b061275e101c19e34a45fa5ab959b1f29f6293))

* fix: add toml as yapf pre-commit dependency (#972)

* fix: add toml as yapf pre-commit dependency

Signed-off-by: Doug Chivers &lt;doug.chivers@uk.ibm.com&gt;

* fix: Add yapf extra dependency

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;

Co-authored-by: Doug Chivers &lt;doug.chivers@uk.ibm.com&gt;
Co-authored-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt; ([`d026282`](https://github.com/oscal-compass/compliance-trestle/commit/d0262826f30e0c7f89f8a3551b93142669fa2c66))

* fix: fix blind link in readme (#969)

Signed-off-by: Doug Chivers &lt;doug.chivers@uk.ibm.com&gt;

Co-authored-by: Doug Chivers &lt;doug.chivers@uk.ibm.com&gt;
Co-authored-by: Ekaterina Nikonova &lt;91102120+enikonovad@users.noreply.github.com&gt; ([`3f054bd`](https://github.com/oscal-compass/compliance-trestle/commit/3f054bd8d82032371955627023ceb257e2f3d4f6))

* fix: Handle error when dealing with profiles with no modify object. (#963)

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`7ad3c82`](https://github.com/oscal-compass/compliance-trestle/commit/7ad3c82058991507808580e800f0bc9df16d2071))

### Unknown

* Merge pull request #986 from IBM/develop

chore: Trestle release ([`03ca23e`](https://github.com/oscal-compass/compliance-trestle/commit/03ca23eccf7d5086c47eeaf81a1fd8ef154d1861))

## v0.33.0 (2021-12-21)

### Chore

* chore: custom pruning for a smaller catalog but preserving controls ac-1 through -5 (#953)

* feat: custom pruning for a smaller catalog but preserving controls ac-1 through ac-5.
Signed-off-by: Jeff Tan &lt;jefferson.tan@gmail.com&gt;

* added full controls and hooked into all existing tests

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

Co-authored-by: Frank Suits &lt;frankst@au1.ibm.com&gt;
Co-authored-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`4099d48`](https://github.com/oscal-compass/compliance-trestle/commit/4099d48e5e289367eed588bd70ff9d6f8d90ee35))

* chore: Merge back version tags and changelog into develop. ([`4db0a04`](https://github.com/oscal-compass/compliance-trestle/commit/4db0a047e290437ff09c7c54072494af15eef191))

### Feature

* feat: Support for SSP writing with jinja templating. (#787)

* chore: Committing to change priorities.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix: Demonstration of jinja extensions allowing processing of oscal fields.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix:Added example on jinja if tags

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* feat: Add Jinja markdown filters

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* feat: Adding jinja transform command

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* chore: Lazy stashing.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* feat: updated signatures

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* feat: Adding kwarg to allow jinja templates to adjust header level

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* chore: Add ssp io (#938)

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;

* chore: Fix control response

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;

* fix: Corrected mdtags to use kwargs properly

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* chore: Adjust control response

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;

* chore: Remove extra test data

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;

* chore: Fix test name

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;

* chore: Small adjustment

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;

* fix: Working ssp templating

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* chore: adding missing test files.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* chore: Print response for this system

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;

* fix: Minor edits

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix: CICD Cleanups (#943)

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* chore: Adjust tables and headers (#944)

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;

* fix: Correcting tables in ssp_io

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix: fix attribute error in catalog_interface (#946)

Signed-off-by: Doug Chivers &lt;doug.chivers@uk.ibm.com&gt;

Co-authored-by: Doug Chivers &lt;doug.chivers@uk.ibm.com&gt;

* chore: Fix tests and tables

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;

* chore: Add more tests

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;

* chore: Small fix

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;

* chore: documentation for the jinja command. (#948)

* fix: Added jinja cmd documentation

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix: Revising docs based on PR feedback.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* chore: More tests

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;

* fix: add trailing newlines to md front_matter content (#956)

fixes format issue in pandoc docx conversion of front matter, where the header of the following section is included in the previous paragraph if there is no trailing newline in the markdown file of the previous paragraph.

Signed-off-by: Doug Chivers &lt;doug.chivers@uk.ibm.com&gt;

Co-authored-by: Doug Chivers &lt;doug.chivers@uk.ibm.com&gt;

* fix: Removed extra unnessary unit tests and unneeded code. (#959)

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* chore: Add Jinja (#958)

* chore: Add jinja tests

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;

* chore: Address review feedback

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;

* chore: Address feedback

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;

* chore: Small fix

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;

* chore: Fix tests

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;

* chore: Small enchancement

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;

* fix: update control title format for ssp output (#960)

Signed-off-by: Doug Chivers &lt;doug.chivers@uk.ibm.com&gt;

Co-authored-by: Doug Chivers &lt;doug.chivers@uk.ibm.com&gt;

* chore: Adjust title in ssp

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;

Co-authored-by: Frank Suits &lt;47203786+fsuits@users.noreply.github.com&gt;
Co-authored-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;
Co-authored-by: Ekaterina Nikonova &lt;91102120+enikonovad@users.noreply.github.com&gt;
Co-authored-by: D9 &lt;dougchivers@gmail.com&gt;
Co-authored-by: Doug Chivers &lt;doug.chivers@uk.ibm.com&gt; ([`e47fc77`](https://github.com/oscal-compass/compliance-trestle/commit/e47fc778ab66a8997b689753ce5ead1849543e52))

### Fix

* fix: merge dicts and remove transform command from CLI until mature.(#954)

* initial changes to ssp docs

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* reworked merge and fixed tests

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* fixes for cidd-script

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

Co-authored-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`82e484b`](https://github.com/oscal-compass/compliance-trestle/commit/82e484b59a4415c2ece1fda55b2b7e9f1a46ab68))

### Unknown

* Merge pull request #961 from IBM/develop

chore: Trestle release ([`1874b18`](https://github.com/oscal-compass/compliance-trestle/commit/1874b1800d74f4997296b3343abdbe6d98a8ba6e))

## v0.32.1 (2021-12-17)

### Chore

* chore: Merge back version tags and changelog into develop. ([`0f808d1`](https://github.com/oscal-compass/compliance-trestle/commit/0f808d14e59d789dd0f634fab03a2a5a7f265d85))

### Fix

* fix: cidd issues (#949)

* fixed file encoding issue and changed signature of get_group_id

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* added doc string

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt; ([`038ca2e`](https://github.com/oscal-compass/compliance-trestle/commit/038ca2ec96a6d85aa891d0cf36e9f9c03e0733d7))

* fix: OSCO rules with prefix ocp- and dashes (#932)

* fix: OSCO rules with prefix ocp- and dashes

* Produce customized yaml based on &#34;profile_check_version&#34;.

* Simplify.

* Fix code smell.

* Add info note.

* Expect metadata property profile_osco_version to customize emitted yaml.

* Remove unnecessary typing.

* Use non-empty href in profiles.

* Simplify by using as_list function.

* Simplify, use tuples.

* Simplify, use tuples. (sneak in)

* Emit description for OSCO version &gt;= 0.1.40.

* Several changes:

- Remove flag profile_check_version. Always emit parameters if given.
- Don&#39;t add ocp4- prefix if its already there.
- Revise -i text accordingly.
- Revise unit tests accordingly.

* Flag name &#34;osco_version&#34;.

Co-authored-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`64f7a97`](https://github.com/oscal-compass/compliance-trestle/commit/64f7a973f5bb7c7946b789770034da186dbcd77e))

### Unknown

* Merge pull request #957 from IBM/develop

chore: Trestle Release ([`5bccc2c`](https://github.com/oscal-compass/compliance-trestle/commit/5bccc2cf8df53db5de00eabb57b518cf9f81025f))

## v0.32.0 (2021-12-14)

### Chore

* chore: Remove simulate from Plan (#916)

* chore: Remove simulate

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;

* chore: Rollback changes

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt; ([`221471d`](https://github.com/oscal-compass/compliance-trestle/commit/221471d9773e26ddcb176ec24ef849325739c523))

* chore: Standarize return codes (#888)

* chore: Standarize return codes

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;

* chore: Move exception catch

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;

* fix: Decrease test cov for now

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;

* chore: Adjust tests

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;

* chore: Remove exception coverage

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;

* chore: Increase coverage

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;

* chore: Increase coverage

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt; ([`6b376e3`](https://github.com/oscal-compass/compliance-trestle/commit/6b376e3e21875720ff91aaf4fef7d655d93a3514))

* chore: Merge back version tags and changelog into develop. ([`ccb0859`](https://github.com/oscal-compass/compliance-trestle/commit/ccb0859996ffbe6a9a2a589e8a98ef3de78f0faa))

### Documentation

* docs: clear edit_uri to remove edit pencil (#937)

* docs: clear edit_uri to remove edit pencil

Closes: https://github.com/IBM/compliance-trestle/issues/529

Signed-off-by: Ryan Moats &lt;rmoats@us.ibm.com&gt;

* fix: Removing incorrect flag in mkdocs.yml

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

Co-authored-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`e32c7ce`](https://github.com/oscal-compass/compliance-trestle/commit/e32c7ce46df3ff905e115ab315c36005f8e0e246))

* docs: add versioning tutorial (#917)

* docs: add versioning tutorial

Signed-off-by: Ryan Moats &lt;rmoats@us.ibm.com&gt;

* Fix mkdocs yml mistake

Signed-off-by: Ryan Moats &lt;rmoats@us.ibm.com&gt;

* Remove default front matter

Signed-off-by: Ryan Moats &lt;rmoats@us.ibm.com&gt;

Co-authored-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`b682806`](https://github.com/oscal-compass/compliance-trestle/commit/b682806f25783a8cc4df18647ac96973d365012d))

### Feature

* feat: added documentation for fedramp plugin (#936)

* feat: added documentation for fedramp plugin

* fix: updated plugin docs

Co-authored-by: Vikas &lt;avikas@in.ibm.com&gt;
Co-authored-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`3deff2c`](https://github.com/oscal-compass/compliance-trestle/commit/3deff2c857c55348242e06a74f2647224517506c))

* feat: params in header for profile generate and assemble (#935)

* writing profile params to header

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* clarified header_dont_merge behavior

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* profile assemble handles set_params in header

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* fixed issue merging headers and added tests

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* fixed issue with controls that just have statement

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* fixed doc string

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* fixed typing

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* fixed typing and doc string

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* fix: Improved handling of line feeds in profile-assemble.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* numerous fixes

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* added tests

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* fixed bugs

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

Co-authored-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`a1b293f`](https://github.com/oscal-compass/compliance-trestle/commit/a1b293f8cac65d32b1cf21a22f49e02967f4e184))

* feat: tutorial cis-to-catalog (#931)

* feat: tutorial cis-to-catalog

* fix: removed unneeded escaped double quotes.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix: removed unneeded escaped double quotes.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix: Added missing reference file.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

Co-authored-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`e2842a8`](https://github.com/oscal-compass/compliance-trestle/commit/e2842a8d66a261c98e973a7edf1bdddb2a342d06))

* feat: task cis-to-catalog (#911)

* feat: task cis-to-catalog

* Make code-format and code-lint happy.

* Fix code smell: Exception

* Fix code smell: ValuesView

* Simplify class Node.

* Oops, use pydantic BaseModel.

Co-authored-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`0a492d0`](https://github.com/oscal-compass/compliance-trestle/commit/0a492d01977467fb6839fbc83322149f5474bbe4))

* feat: roles in metadata (#926)

* added function to get control param dict

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* removed special catalog group and use empty string instead

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* added doc files

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* fixed format

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt; ([`ddc1e66`](https://github.com/oscal-compass/compliance-trestle/commit/ddc1e662ef345eaecf5b5584964d5739f1c3ab43))

* feat: allow components in markdown and ssp assemble (#902)

* adding support for header metadata

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* added template

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* have bycomp working for ssp

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* boosted coverage

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* fixed docstring

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* added doc files

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* made test less rigid

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* simplified test

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* fixed test

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* have components working properly with ssp assemble

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* handled pr feedback

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* added tests and test files

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

Co-authored-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`b03a236`](https://github.com/oscal-compass/compliance-trestle/commit/b03a236ad2928b384677e5777b1880d3386a4fe0))

* feat: Add ability to modify headers in the tree (#909)

* feat: Add ability to modify headers in the tree

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;

* feat: Extra check

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;

* feat: Ensure tree identity

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;

* feat: Use better naming

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt; ([`b455c18`](https://github.com/oscal-compass/compliance-trestle/commit/b455c18c3492b7e4a4fced8b701780d109bed55e))

* feat: Altering ssp-generate to add all sections by default (#905)

* feat: Altering ssp-generate to add all sections by default

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix: adding extra test coverage.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`55a399b`](https://github.com/oscal-compass/compliance-trestle/commit/55a399bf129aa39e42e83e93e8b1b69aec20d9bb))

### Fix

* fix: Fire off sonar only on local PRs. (#934)

* fix: Fire off sonar only on local PRs.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix: Fire off sonar only on local PRs.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix: Update developer docs to explain sonar work around.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`26f4f0a`](https://github.com/oscal-compass/compliance-trestle/commit/26f4f0ab08af2d37c05130e3189bfa74f79b5a57))

* fix: Ensuring that mkdocs yaml both remains stable an is up to date. (#927)

* fix: Correcting documentation website index.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix: Correcting documentation website index such that it does not change again.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix: adding check script to linter

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`ee48763`](https://github.com/oscal-compass/compliance-trestle/commit/ee487634cbf80b3aeac12a7f103c19730b18e2da))

### Unknown

* Merge pull request #942 from IBM/develop

chore: Trestle release ([`57a5523`](https://github.com/oscal-compass/compliance-trestle/commit/57a55234b3d95a2b1a555333d250d77369ea96f2))

## v0.31.0 (2021-12-01)

### Chore

* chore: Increase test coverage for validation (#901)

* feat: Add ignore files flag to the validation

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;

* feat: Ignore directories

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;

* feat: Update docs

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;

* feat: Update tests

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;

* feat: Add deprecate warning

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;

* chore: Add missing tests for validation

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;

Co-authored-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`0799c37`](https://github.com/oscal-compass/compliance-trestle/commit/0799c37b7d1a5c36535d0fa71c58e1bb2f73c863))

* chore: Merge back version tags and changelog into develop. ([`1cd9894`](https://github.com/oscal-compass/compliance-trestle/commit/1cd989494b5707d15a5b593987d8071a27ddd95d))

### Feature

* feat: added trestle-fedramp project discovery and command (#899)

* feat: added trestle-fedramp project discovery and command

* fix: updated cli.py to add commands from plugins generically. Also added a CommandBase class to not check for trestle-root.

* fix: Adding nocover statements.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix: Adding nocover statements.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

Co-authored-by: Vikas &lt;avikas@in.ibm.com&gt;
Co-authored-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`f0cc836`](https://github.com/oscal-compass/compliance-trestle/commit/f0cc8367a9001749a81c1a069f02ea00e49a7cec))

* feat: Ignore files from the validation (#898)

* feat: Add ignore files flag to the validation

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;

* feat: Ignore directories

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;

* feat: Update docs

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;

* feat: Update tests

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;

* feat: Add deprecate warning

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;

Co-authored-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`c2af814`](https://github.com/oscal-compass/compliance-trestle/commit/c2af8148cd7698bc75803bec0c4d6b181e11cd64))

* feat: Enforce OSCAL version and notify user (#895)

* feat: Enforce OSCAL version

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;

* feat: Print only version error if present

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;

* feat: Add safer version error check

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;

* fix: gen oscal version (#900)

* fixed validator for gen_oscal

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* added docstring

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* fixed comment typo

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

Co-authored-by: Frank Suits &lt;47203786+fsuits@users.noreply.github.com&gt; ([`246875c`](https://github.com/oscal-compass/compliance-trestle/commit/246875ce0c7d42f931072739ae340b39bbb0399e))

* feat: sample generic oscal transform to filter ssp by profile (#820)

* initial version of trestle transform

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* enhanced

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* removed dead code

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* increased coverage

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* added new arg for header

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* refined command options - tests pass

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* improved docstrings

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* boosted coverage

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* ssp assemble regenerate is working

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* clean up and boost coverage

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* fixed try block and added comments

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

Co-authored-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`afe243f`](https://github.com/oscal-compass/compliance-trestle/commit/afe243f6ece6fb9b361870e69b32d8d84a2e9335))

### Fix

* fix: Remove empty folders (#904)

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt; ([`552fb36`](https://github.com/oscal-compass/compliance-trestle/commit/552fb36a53198d9d1fcc06a0a3eb3cfe59b753b2))

* fix: tmp req init (#894)

* fixed indent

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* docstring

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt; ([`e2d3ed0`](https://github.com/oscal-compass/compliance-trestle/commit/e2d3ed0f98a281ac5ef77edf5f4e90a0a09f53d8))

* fix: bad control causes uncaught exception in ssp-generate (#893)

* fixed issue with bad control id

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* added docstring

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* added test profile

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* improved multiline f string format

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt; ([`c50515a`](https://github.com/oscal-compass/compliance-trestle/commit/c50515a55452b776ed9397b62e658fb5d5b1d5b0))

* fix: Ignore subfolders in folders validation (#889)

* fix: Fix template version for empty headers

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;

* fix: Ignore subfolders in folders

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;

* fix: Remove added line

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;

Co-authored-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`727265a`](https://github.com/oscal-compass/compliance-trestle/commit/727265aebbcbdeffce5575c5907ba1fd000bdea3))

### Refactor

* refactor: osco-to-oscal performance improvements. (#886)

* Remove extraneous typing.

* Remove osco_helper.py, consolidate into osco.py.

* Oscal Result Factory.

* Add checking flag.

* Use monkeypatch.

* Observation properties, without checking.

* Remove more extraneous typing.

* Correct return type of OscalResultsFactory.components.

* Fix code smell.

* Fix rule_use_generator return type.

* Expunge pass statement (code smells).

* 100% test coverage.

* Fix presumed existence of &#34;-&#34;.

* Add cis-to-component-definition tutorial to mkdocs.yml ([`b3ae044`](https://github.com/oscal-compass/compliance-trestle/commit/b3ae044923935623ff162129e5ba5206e20ad23a))

### Unknown

* Merge pull request #907 from IBM/develop

chore: Trestle release - enabling plugin architecture ([`0865000`](https://github.com/oscal-compass/compliance-trestle/commit/08650008ffb5252c61d55eb2727825edb7d67889))

## v0.30.0 (2021-11-22)

### Chore

* chore: Trestle release

chore: Trestle release ([`94e161b`](https://github.com/oscal-compass/compliance-trestle/commit/94e161b3ccde191b97361a3e5d37222ad04ff27b))

* chore: Merge back version tags and changelog into develop. ([`ab49b65`](https://github.com/oscal-compass/compliance-trestle/commit/ab49b65ddfe6e9b4d28abe0c796c62bacbaf717a))

### Feature

* feat: OSCO transformer support for OpenScap 1.3.5 (#876)

* feat: OSCO transformer support for OPenScap 1.3.5

* Use host_name as scc_inventory_item_id.

* Fix code smell.

* Use dict for passing args; use else clause when necessary.

* Oops, signature typing issue.

Co-authored-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`dcfb34a`](https://github.com/oscal-compass/compliance-trestle/commit/dcfb34ae67ce0bf057d224a6eb4065e25d616a42))

## v0.29.0 (2021-11-19)

### Chore

* chore: Allowing multiple PR templates. (#873)

* chore: UTesting multiple PR templates.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* chore: UTesting multiple PR templates.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`d34dc72`](https://github.com/oscal-compass/compliance-trestle/commit/d34dc7291aa5901f0751b69adf7437a5b85f468a))

* chore: Merge back version tags and changelog into develop. ([`aeae771`](https://github.com/oscal-compass/compliance-trestle/commit/aeae771e0e90c7c69ef914ca02d4857ed6f50222))

### Feature

* feat: tutorial for task cis-to-component-definition (#870)

* feat: tutorial for task cis-to-component-definition

* reduce size of sample output.

* mdformat

* Remedies for reviewer comments.

Co-authored-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`4e4d6b4`](https://github.com/oscal-compass/compliance-trestle/commit/4e4d6b4ba600792ce5a6dfd3606fb730099cbdef))

* feat: Add support for ignored fields to header (#794)

* feat: Add support for ignored fields to header

Specific list:
- &#39;extra-fields&#39;
- &#39;additional-approvers&#39;

Signed-off-by: Ryan Moats &lt;rmoats@us.ibm.com&gt;

* Update added tests

Conform to new directory structure

Signed-off-by: Ryan Moats &lt;rmoats@us.ibm.com&gt;

Co-authored-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`37e9b60`](https://github.com/oscal-compass/compliance-trestle/commit/37e9b60cecf6516c934fafa8fa969672ade8ef7f))

### Fix

* fix: cat assemble label needs to load labels as properties when reading controls (#878)

* load label as property when reading controls

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* fixed invocations involving header_dont_merge

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* force prompt of additional content

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* added test and more docs

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

Co-authored-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`0b97476`](https://github.com/oscal-compass/compliance-trestle/commit/0b97476db8bfbac4925b2af2ec1b8edda9178e33))

* fix: cleanup PR template. ([`f7c433b`](https://github.com/oscal-compass/compliance-trestle/commit/f7c433b8a4d86a39150e596e4e395b03a2dab984))

* fix: Current support for multiple PR templates is insufficient in Github. (#879)

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`bf12f2e`](https://github.com/oscal-compass/compliance-trestle/commit/bf12f2e464adaf371ec2f7f63050395a05ec1cfb))

* fix: Updating documentation to exploit code highlighting. (#877)

* fix: Updating documentation to exploit code highlighting.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix: Minor changes

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`10bd679`](https://github.com/oscal-compass/compliance-trestle/commit/10bd6792d8a9b9b42d26653fffd40baaad4d3251))

* fix: mangled merging of lists and lack of recursion in profile resolver (#869)

* generalized recursive profile resolver

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* tweaked docs

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* added list item types

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* small cleanup

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* more simplification

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* fix: Ensure trackback logging occurs only on debug level. (#872)

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* final tweaks

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* removed unreachable code

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

Co-authored-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`e3ccbbc`](https://github.com/oscal-compass/compliance-trestle/commit/e3ccbbc4c6675264dcc245ed6c5e2454d04078c8))

* fix: Incorrect behaviour of lint PR. (#868)

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`e5209c3`](https://github.com/oscal-compass/compliance-trestle/commit/e5209c33f8d53bd022e410d52ef97d3316746023))

### Refactor

* refactor: use monkeypatch to replace more mock library patch blocks (#874)

* refactor(tests): migrated tests from unittest.mock to monkeypatch for assemble.py and command.py
Signed-off-by: Jeff Tan &lt;jefferson.tan@gmail.com&gt;

* refactor(tests): lint and format.
Signed-off-by: Jeff Tan &lt;jefferson.tan@gmail.com&gt;

* refactor(tests): migrated from unittest.mock to monkeypatch for docs_test.py
Signed-off-by: Jeff Tan &lt;jefferson.tan@gmail.com&gt;

* refactor(tests): migrated from unittest.mock to monkeypatch for folders_test.py
Signed-off-by: Jeff Tan &lt;jefferson.tan@gmail.com&gt;

* refactor(tests): migrated from unittest.mock to monkeypatch for task_test.py
Signed-off-by: Jeff Tan &lt;jefferson.tan@gmail.com&gt;

* refactor(tests): migrated from unittest.mock to monkeypatch for replicate_test.py
Signed-off-by: Jeff Tan &lt;jefferson.tan@gmail.com&gt; ([`256f5d4`](https://github.com/oscal-compass/compliance-trestle/commit/256f5d4fcd5a2f9193ee374a098565c64a71d2bf))

### Unknown

* Merge pull request #880 from IBM/develop

chore: Trestle release ([`c6b1bf8`](https://github.com/oscal-compass/compliance-trestle/commit/c6b1bf833b4d692b73546ee2d7c03a913c76cea6))

## v0.28.1 (2021-11-17)

### Chore

* chore: Merge back version tags and changelog into develop. ([`2704553`](https://github.com/oscal-compass/compliance-trestle/commit/2704553dda7b8f8daa9dbb6003084080871adbc3))

### Fix

* fix: remove results {} from osco-to-oscal console display (#866)

Co-authored-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`d62051e`](https://github.com/oscal-compass/compliance-trestle/commit/d62051e0fb45c99edd97b0314117b7208dd11d91))

* fix: add spec.desctiption to produced yaml (#865) ([`b988684`](https://github.com/oscal-compass/compliance-trestle/commit/b988684ffb02011c4f890b8f889abb0c7184e03c))

### Unknown

* Merge pull request #867 from IBM/develop

fix: trestle release ([`b952390`](https://github.com/oscal-compass/compliance-trestle/commit/b952390f90a97eb60c60cd69b71f67431f5744c0))

## v0.28.0 (2021-11-16)

### Chore

* chore: Merge back version tags and changelog into develop. ([`60920c6`](https://github.com/oscal-compass/compliance-trestle/commit/60920c6da1bb2d10f56575ff9a4012887a176ab3))

### Fix

* fix: Fix instance version (#862)

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt; ([`56f7cdf`](https://github.com/oscal-compass/compliance-trestle/commit/56f7cdfe537adfcfcb8398df7d06b71cbf35781d))

### Unknown

* Merge pull request #863 from IBM/develop

fix: Trestle bug fix release. ([`9bcb217`](https://github.com/oscal-compass/compliance-trestle/commit/9bcb21787a71e67db1bf94f812aa0e3ba8260cfe))

## v0.27.2 (2021-11-16)

### Chore

* chore: Merge back version tags and changelog into develop. ([`c5480f5`](https://github.com/oscal-compass/compliance-trestle/commit/c5480f5d51c65c9066dabb347102dbc0a9b9a05d))

* chore: Merge back version tags and changelog into develop. ([`3ab740b`](https://github.com/oscal-compass/compliance-trestle/commit/3ab740ba766941e9ea93368b20458a7f26f21f24))

* chore: Merge back version tags and changelog into develop. ([`d546739`](https://github.com/oscal-compass/compliance-trestle/commit/d5467397cbfe0ccc66e6f5bfd783747e7751603e))

### Feature

* feat: Add yaml header to various trestle author docs in a safe manner. (#853)

* fix: Preserve yaml header ordering in markdown ssp workflows.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* feat: Add safe yaml behaviour

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`0b6f8a1`](https://github.com/oscal-compass/compliance-trestle/commit/0b6f8a18d1de460c14fa36d107729e367682045e))

### Fix

* fix: force trestle relesae. ([`49243e3`](https://github.com/oscal-compass/compliance-trestle/commit/49243e369120958536a644a4a063cf19f1870b7a))

* fix: Correcting mkdocs (#860)

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`89a6d0d`](https://github.com/oscal-compass/compliance-trestle/commit/89a6d0dc42d87b7082ec4c1a2def684cc4ae543b))

* fix: Relabel yaml-safe to header-dont-merge. (#858)

* fix: Relabel yaml-safe to header-merge.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix: recommended changes to be backwards compatible.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`58e6b1d`](https://github.com/oscal-compass/compliance-trestle/commit/58e6b1d8bec4a5b210d47d24acaf2ea770a31000))

* fix: 2 bugs in task cis-to-component-definition (#856)

Co-authored-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`61da0b8`](https://github.com/oscal-compass/compliance-trestle/commit/61da0b89aaab4c15b0e4a2c885efbdf387b30d10))

* fix: Fix headers recurse flag (#849)

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt; ([`d285cc6`](https://github.com/oscal-compass/compliance-trestle/commit/d285cc61ff52531d821c03ab4bcfdf4966b9c44e))

### Unknown

* Trestle Release (#861)

* fix: Fix headers recurse flag (#849)

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;

* feat: Add yaml header to various trestle author docs in a safe manner. (#853)

* fix: Preserve yaml header ordering in markdown ssp workflows.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* feat: Add safe yaml behaviour

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix: 2 bugs in task cis-to-component-definition (#856)

Co-authored-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix: Relabel yaml-safe to header-dont-merge. (#858)

* fix: Relabel yaml-safe to header-merge.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix: recommended changes to be backwards compatible.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix: Correcting mkdocs (#860)

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

Co-authored-by: compliance-trestle-1 &lt;84952801+compliance-trestle-1@users.noreply.github.com&gt;
Co-authored-by: Ekaterina Nikonova &lt;91102120+enikonovad@users.noreply.github.com&gt;
Co-authored-by: degenaro &lt;lou.degenaro@gmail.com&gt; ([`c0d2901`](https://github.com/oscal-compass/compliance-trestle/commit/c0d29012b74d239d45e7e25ca841ebee3a2a09ec))

* Trestle release (#859)

* fix: Fix headers recurse flag (#849)

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;

* feat: Add yaml header to various trestle author docs in a safe manner. (#853)

* fix: Preserve yaml header ordering in markdown ssp workflows.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* feat: Add safe yaml behaviour

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix: 2 bugs in task cis-to-component-definition (#856)

Co-authored-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix: Relabel yaml-safe to header-dont-merge. (#858)

* fix: Relabel yaml-safe to header-merge.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix: recommended changes to be backwards compatible.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

Co-authored-by: compliance-trestle-1 &lt;84952801+compliance-trestle-1@users.noreply.github.com&gt;
Co-authored-by: Ekaterina Nikonova &lt;91102120+enikonovad@users.noreply.github.com&gt;
Co-authored-by: degenaro &lt;lou.degenaro@gmail.com&gt; ([`127e7ba`](https://github.com/oscal-compass/compliance-trestle/commit/127e7baf4688c505a6e51259af093823594c86b9))

## v0.27.1 (2021-11-15)

### Chore

* chore: Merge back version tags and changelog into develop. ([`8168c8c`](https://github.com/oscal-compass/compliance-trestle/commit/8168c8cf39c0cff989d34c5e983e3fbd7be9e469))

### Fix

* fix: profile resolver issues with alter that has no adds (#847)

* fixed issue with alter no adds

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* updated docstring

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt; ([`6865eb7`](https://github.com/oscal-compass/compliance-trestle/commit/6865eb7967ae954b14f5a10921d88ca567fae921))

### Unknown

* Bug fix release

Bug fix release ([`89fde8c`](https://github.com/oscal-compass/compliance-trestle/commit/89fde8ceee2b4eef9aec97a56f8b5e45f90711a7))

## v0.27.0 (2021-11-14)

### Chore

* chore: Correct CI triggering issues. ([`6d529dc`](https://github.com/oscal-compass/compliance-trestle/commit/6d529dc2d85845dedc78b5af809bc18f2f23cb51))

* chore: Adding docstrings automatically to all oscal models. (#827)

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`0ff4dce`](https://github.com/oscal-compass/compliance-trestle/commit/0ff4dce660c0753c562b8d52eddcaa8ffd6bed98))

* chore: Remove baseexceptions (#826)

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt; ([`69492ff`](https://github.com/oscal-compass/compliance-trestle/commit/69492ff292f1aa39fe6730552fa69821dbf70b41))

* chore: reduce lists in given input file and save into given output file (#807)

* feat: recursively reduce lists in given input json file and save into given output file in json
Signed-off-by: Jeff Tan &lt;jefferson.tan@gmail.com&gt;

* feat: just one non-zero return code value of 1 for any exception
Signed-off-by: Jeff Tan &lt;jefferson.tan@gmail.com&gt;

* feat: last minute change in error, neglected to lint.
Signed-off-by: Jeff Tan &lt;jefferson.tan@gmail.com&gt;

* feat: lint again
Signed-off-by: Jeff Tan &lt;jefferson.tan@gmail.com&gt; ([`998cdee`](https://github.com/oscal-compass/compliance-trestle/commit/998cdee4bd3c816ee7a1d816948bc615f209d026))

* chore: Merge back version tags and changelog into develop. ([`8dc9934`](https://github.com/oscal-compass/compliance-trestle/commit/8dc99341f8512c8de1039b329067e6ee8448af17))

### Feature

* feat: Add ability to use different versions of templates (#837)

* feat: Add Template_Version to templates and instances

Partially Closes: https://github.com/IBM/compliance-trestle/issues/761

Signed-off-by: Ryan Moats &lt;rmoats@us.ibm.com&gt;

* Restructure to remove duplicate code

Signed-off-by: Ryan Moats &lt;rmoats@us.ibm.com&gt;

* Address Lint failures

Signed-off-by: Ryan Moats &lt;rmoats@us.ibm.com&gt;

* feat: Add template versioning

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;

* feat: Fix python version

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;

* feat: Refactor code

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;

* feat: Update docs

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;

* feat: Switch logic to allow custom versions

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;

* feat: Allow validation of all versions

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;

* feat: Attempt to fix Windows issue

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;

* feat: Attempt to fix Windows issue

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;

* feat: Attempt to fix Windows hidden file

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;

* fix: improved handling of hidden files in tests for windows (#846)

* feat: facilitate improved performance within Tanium transformer. (#835)

* Facilitate parallel processing to boost transform performance.

* Add comments.

* Multi-CPU testing fix.

* monkey uuid.getnode()

* lint.

* Fix test uuid generation.

* Another testing fix for UUID generation.

* Monkey business.

* Bypass multiprocessing for single batch.

* add: temporary hack to test execute cpus, for windows.

* Fix code smells.

* Hack cpus test for now, since windows fails intermittently.

* Unhack cpus test.

* Lint.

* Tidy up.

* Update for 100% code coverage.

* &#34;huge&#34; test case, config, and backup of &#34;hack&#34; solution.

* fix: Tune property construction to reduce overhead

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* Remove extraneous.

* Fix transform time and batch size calculations.

* Support checking and/or multiprocessing.

* Typing fixes.

* Delete re-named file.

* Updates to address comments:

- for loop
- type int
- large cpu values in test
- signature of __init__

* Fix comment re: OscalFactory.

* Code smells fixes.

* More code smells fixes.

* Continue code smells fixing.

* Test coverage 100%

* fix: Minor signature changes

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

Co-authored-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fixed handling of hidden files on windows

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* improved docstring

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

Co-authored-by: degenaro &lt;lou.degenaro@gmail.com&gt;
Co-authored-by: Chris Butler &lt;chris@thebutlers.me&gt;

Co-authored-by: Ryan Moats &lt;rmoats@us.ibm.com&gt;
Co-authored-by: Chris Butler &lt;chris@thebutlers.me&gt;
Co-authored-by: Frank Suits &lt;47203786+fsuits@users.noreply.github.com&gt;
Co-authored-by: degenaro &lt;lou.degenaro@gmail.com&gt; ([`c6d3618`](https://github.com/oscal-compass/compliance-trestle/commit/c6d3618f13e6dc945413867a8d102cd3a7c3c211))

* feat: facilitate improved performance within Tanium transformer. (#835)

* Facilitate parallel processing to boost transform performance.

* Add comments.

* Multi-CPU testing fix.

* monkey uuid.getnode()

* lint.

* Fix test uuid generation.

* Another testing fix for UUID generation.

* Monkey business.

* Bypass multiprocessing for single batch.

* add: temporary hack to test execute cpus, for windows.

* Fix code smells.

* Hack cpus test for now, since windows fails intermittently.

* Unhack cpus test.

* Lint.

* Tidy up.

* Update for 100% code coverage.

* &#34;huge&#34; test case, config, and backup of &#34;hack&#34; solution.

* fix: Tune property construction to reduce overhead

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* Remove extraneous.

* Fix transform time and batch size calculations.

* Support checking and/or multiprocessing.

* Typing fixes.

* Delete re-named file.

* Updates to address comments:

- for loop
- type int
- large cpu values in test
- signature of __init__

* Fix comment re: OscalFactory.

* Code smells fixes.

* More code smells fixes.

* Continue code smells fixing.

* Test coverage 100%

* fix: Minor signature changes

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

Co-authored-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`4d2ded4`](https://github.com/oscal-compass/compliance-trestle/commit/4d2ded49d314f6e632f531b08a58bc66d53d8997))

* feat: Significant json (de)serialisation performance improvements. (#841)

* feat: Significant json performance improvements

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* feat: Improved json IO performance

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix: Adding benchmarking scripts

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix: Add orjson for loading as well

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix: Remove now unused internal function

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix: Optimising opportunistic copy

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix: Correct issues with conventional PR

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`d6f3cb1`](https://github.com/oscal-compass/compliance-trestle/commit/d6f3cb1ab8113c997d463d832aa8c8b721faffd2))

* feat: add yaml header output for profile and catalog generate (#833)

* added yaml header support

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* boosted coverage

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* convert strings to const and boost coverage

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt; ([`50093f0`](https://github.com/oscal-compass/compliance-trestle/commit/50093f075615fe25bb6e25b16ff5d98fb0a308f9))

* feat: Add ability to write modified drawio files (#813)

* feat: Write modified drawio

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;

* feat: Use constants

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;

* feat: Keep old attributes and encoding

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;

* feat: Add docs

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt; ([`ea814bf`](https://github.com/oscal-compass/compliance-trestle/commit/ea814bfdcfb8e75e2812e182ec09b009e693312a))

* feat: build-component-definition (#788)

* feat: build-component-definition

* format + lint fix-up.

* sonar fixes.

* rename task as cis-to-component-definition, misc changes + 100% test cov

* sunc

* remove assert

* fix code smell.

* use https.

* Remove t_&lt;type&gt; statements.

* use monkeypatch.

* Remove locally defined get_trestle_version().

* Remove properties.

* Simplify ingestion of filtering rules json.

* Use Path.open()

* Revise fetch parameters map.

* function parameter types.

* coverage 100%

Co-authored-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`9f7b1fe`](https://github.com/oscal-compass/compliance-trestle/commit/9f7b1fec0efc017698ceef4c6bf77c132626ec93))

* feat: ssp filter allows filter of ssp based on profile (#805)

* initial version of ssp filter

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* refactor and boost coverage

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* cleaned up smells

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* removed model enum and converted strings to const

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* reworked the fs top_level_model access and cleaned up further

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* final cleanup of const

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* optional on filecontent

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt; ([`494ba1b`](https://github.com/oscal-compass/compliance-trestle/commit/494ba1b9a749c44657365f45fc88a8c4aa94ed73))

* feat: Add centralised markdown API (#797)

* feat: Add markdown api

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;

* feat: Fix test

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;

* feat: Small changes

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;

* feat: Handle html tags

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;

* Add documentation

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;

Co-authored-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`8582516`](https://github.com/oscal-compass/compliance-trestle/commit/8582516f59a8258b513312185b8efdd4cb7a001e))

### Fix

* fix: Preliminary fix for parameters where &#39;set parameter&#39; is called an a value does not exist. (#823)

* chore: Adding tests to verify behaviour parameter resolution

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix: Allow for cases where a&#34;set parameter&#34; is used without setting values

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix: Adding more complexity to tests to ensure coverage of the tests.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix: Initial implementation of imporoved props adding. Testing TBC.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix: Staging for Frank

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix: remove dependency on bad logging behaviour.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix: profile merge support (#828)

* added support for merge methods in profile resolver

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* added doc string

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* fix: Small typo fixes

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix: Correct small errors

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* chore: Segregate functions to reduce cognitive complexity.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix: Reduce cognitive complexity.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* extended support for profile_resolver

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* fix: Completing UT&#39;s and reducing code redudancy

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix: Added missing test files.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* better coverage

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* increased coverage

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* addressed pr feedback

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* fix: Small formatting changes.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* profile param order sub works

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* trying to make constraints work

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* minor change to convert a warning to a debug msg

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* now using attrs for part components

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* changed default behavior in tests

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

Co-authored-by: Frank Suits &lt;47203786+fsuits@users.noreply.github.com&gt;
Co-authored-by: Frank Suits &lt;frankst@au1.ibm.com&gt; ([`d20f2b9`](https://github.com/oscal-compass/compliance-trestle/commit/d20f2b9e6ca10c4fa829bb723d68ea3d06902cd0))

* fix: merge yaml header content when writing control (#825)

* now write catalog as markdown will check for yaml header contents

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* added comments

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* added coverage and docs

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* fixed small bug in merge dicts

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* one more coverage line

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* another coverage line

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* small bug

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* error in tutorial text

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* final fix

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* clarified doc strings

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* test utils return bool instead of int

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt; ([`8d0b3b0`](https://github.com/oscal-compass/compliance-trestle/commit/8d0b3b0f3a6c5e3a47a42b46b77081a700947d6b))

* fix: all Alter/Add of prop by_id (#821)

* allow add by_id

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* added by_id prop to test file

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* removed unneeded catalog interface

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt; ([`a9047a8`](https://github.com/oscal-compass/compliance-trestle/commit/a9047a83e0b0c64c34448f776a7e13fff77e6b2a))

* fix: ssp generate with alter props issue (#819)

* fix for ssp generate

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* increase coverage

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt; ([`a1e4219`](https://github.com/oscal-compass/compliance-trestle/commit/a1e421944ce11432b2b2832b8f669b65428f1b38))

* fix: Allow markdown substitutions (#812)

* fix: Allow markdown substitutions

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;

* fix: Refactor code

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;

* fix: Fix typos

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt; ([`8d52d3e`](https://github.com/oscal-compass/compliance-trestle/commit/8d52d3eb4aaa0a73685983114ffa38c494b9fec4))

* fix: Handle hard line breaks (#804)

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt; ([`b1e39c1`](https://github.com/oscal-compass/compliance-trestle/commit/b1e39c1173b235a87981a2856081cd54aeac86e3))

### Unknown

* Merge pull request #845 from IBM/develop

Trestle release ([`7e8292d`](https://github.com/oscal-compass/compliance-trestle/commit/7e8292db889b8f1e3babf1e6327641b7e179b967))

## v0.26.0 (2021-10-20)

### Chore

* chore: Accomodate forked repos by separating sonarqube quality gate (#791)

* chore: Accomodate forked repos by separting sonarqube quality gate

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* chore: Add triggers for remote branches

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* chore(cicd): Correcting CI yaml format.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix: Alter CI pipeline to use PR target, potentially avoiding issues for sonarqube

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`ae95c25`](https://github.com/oscal-compass/compliance-trestle/commit/ae95c25dd1e3fec3c86ea34cd9981ddca65bf6d4))

* chore: Ensure sonar quality gate is measured (#775)

* chore: Ensure sonar quality gate is measured

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* chore: Cleaning up badges

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* chore: Cleaning up PR template

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix: Clean up links

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix: Correct image links

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`ca25f93`](https://github.com/oscal-compass/compliance-trestle/commit/ca25f935749ef3dae804e98c82cee5cc4a587136))

* chore: Updated python directory.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`cbc451e`](https://github.com/oscal-compass/compliance-trestle/commit/cbc451e2c81eab0b9e509ff050b53e95d18bb85c))

* chore: Correct trestle sonar config.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`6bd8002`](https://github.com/oscal-compass/compliance-trestle/commit/6bd80026d10b9587ea086e8f41c76783959cac37))

* chore: Correct trestle sonar config.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`2c75f03`](https://github.com/oscal-compass/compliance-trestle/commit/2c75f03914d89e60b017e17eb0779eda85253a89))

* chore: Correct trestle sonar config.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`9884eb6`](https://github.com/oscal-compass/compliance-trestle/commit/9884eb6c4c458432422d23e750e36e3220160a0a))

* chore: replace codecov with sonarcloud (#765)

* chore: replace codecov

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* chore: Force clean coveralls install.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* chore: Force clean coveralls install.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix: Correcting tokens

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix: Testing sonarcloud

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix:Update for SONAR to use coverage.xml

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix: Removing pcoveralls

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix:Adding sonar properties file.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix: Update sonar workflow.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix: Adding develop &#39;push&#39; to ensure develop build is okay

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`1c41a04`](https://github.com/oscal-compass/compliance-trestle/commit/1c41a04bb7943f016e1148af6516da0d27fe9b9b))

* chore: Adding extra developer documentation (#763)

* chore:Adding extra developer documentation

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* chore: Adding extra developer documentation.

* chore: Correcting typos

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`3242fc8`](https://github.com/oscal-compass/compliance-trestle/commit/3242fc85b9b66083b8d44fece2ce0c7349b741ce))

* chore: Merge back version tags and changelog into develop. ([`84c1b4d`](https://github.com/oscal-compass/compliance-trestle/commit/84c1b4d81fbecb639aa846773c1fa1fd4352bdf8))

### Feature

* feat: Add exclusion flags to trestle author header validate to allow practical use without a task name. (#793)

* fix: Adding more UTs

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* feat: Adding exclude flag to trestle author headers.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix: Update test function names.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix: Correct sonar gate which was not triggering

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix: Correct sonar gate which was not triggering

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix: Resolve python 3.7 compatibility issues

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix: Cater to files w/o extensions

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`d77408f`](https://github.com/oscal-compass/compliance-trestle/commit/d77408f39e914bff3dfc20ecf91e3a982a49bf4e))

* feat: allow author edits and update of profile (#771)

* added control objective handling

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* objective seems ok

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* author profile works for prose

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* added profile test

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* added tests

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* added test coverage for control_io

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* profile author now working

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* removed dead code

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* fixed docstring

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* addressed pr changes and boosted coverage

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* check moustaches

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* refined moustache work and improved excep handling

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* added docs for author profile and ssp tutorial

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* extra files

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* tutorial edits and conversion to monkeypatch

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

Co-authored-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`650b6c9`](https://github.com/oscal-compass/compliance-trestle/commit/650b6c95eadfc68c5f0646761f57ac4b2542bb6c))

* feat: Improve profile resolver to cover &#34;adds&#34; scenarios in fedramp &amp; NIST 800-53 (#766)

* feat: Support additional adding positions in adds

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;

* feat: Change doc line

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;

* feat: Move validation to profile resolver

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;

* feat: Backout profile to original state

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt; ([`75911f3`](https://github.com/oscal-compass/compliance-trestle/commit/75911f3f88c6b4d9a4adaea03a77db7f9a83faf9))

* feat: author catalog to support reading and writing controls and catalogs (#734)

* new catalog module

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* recurse the catalog

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* improved format

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* more consistent format

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* refactored catalog interface and control writing

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* hooking in new methods

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* hooking in read controls

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* renamed some items

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* cleaned up control output

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* added tests for control_io and now read/write controls

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* changes for statement and item

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* now test assembled catalog is equivalent

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* boost coverage

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* boosted coverage

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* additional cleanup based on PR review

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* fixed typo and clarified some code

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* multiple changes based on revision requests

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* adjust md format and test

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* remove test md files

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* small tweaks to md format

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

Co-authored-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`0a2bcea`](https://github.com/oscal-compass/compliance-trestle/commit/0a2bcea49841c774a667aeb9368e776402db23cf))

### Fix

* fix: ssp issues (#795)

* fixed small issues with ssp generate and assemble

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* updated comments

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* dont prompt for content if already there

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* prevent leading and trailing new lines in prose

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* boosted coverage

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

Co-authored-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`3532e4e`](https://github.com/oscal-compass/compliance-trestle/commit/3532e4ef7c7db33e6875a27123a4b6a4fa2655cc))

* fix: Further refinements to CI pipeline (#796)

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`b46c63b`](https://github.com/oscal-compass/compliance-trestle/commit/b46c63be8a192993126b49c289e99ea5c10dc3a1))

* fix: Correct broken guards of sonarqube actions. ([`9e10c1e`](https://github.com/oscal-compass/compliance-trestle/commit/9e10c1e3fedc96c5f6e0b02651b77ce20d1421c5))

* fix: Add missing __init__.py, which can cause issues with pytest. (#792)

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`bc6fbf3`](https://github.com/oscal-compass/compliance-trestle/commit/bc6fbf34843f3101edd4236f5dab904fa6a3606f))

* fix: Document submodule requirement for testing. (#782)

* fix: Ensure git submodules are checked out when setting up a developers environment.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix: Updated develop docs w.r.t. submodules.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix: Updated develop docs w.r.t. submodules.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`3e711a3`](https://github.com/oscal-compass/compliance-trestle/commit/3e711a3416e8155a0e082b65e89060ac3e9d3227))

* fix: Resolve bugs in xlsx to component definition (#772)

* fix: 2 bugs

- print_info attempts to get non-existent data
- missing comma for correct alphabet specification

* Employ more pythonic way of iterating through lower case alphabet.

Co-authored-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`ebff124`](https://github.com/oscal-compass/compliance-trestle/commit/ebff1247b5bc9abf615f10ae943b0fdff3644507))

* fix: Remove two bugs generated from unraised exceptions. (#777)

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`5f698a6`](https://github.com/oscal-compass/compliance-trestle/commit/5f698a6c28c84a9eb9595ddd1248ce29f149895a))

* fix: Remove use of http aligning with zero trust principles. (#770)

* fix: Remove use of http aligning with zero trust principles.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix:correct typo

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* chore: Exclude OSCAL automatically generated code from duplication metrics.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`5b0240c`](https://github.com/oscal-compass/compliance-trestle/commit/5b0240cfa83f89d5182e04efa91feb4eb06ad8fd))

* fix(security): Remove user name from logs (#767)

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`4d075b8`](https://github.com/oscal-compass/compliance-trestle/commit/4d075b89776552a1f58751674e2056ac7afac3cc))

* fix(cli): Correctly capture return codes (#760)

* fix(conftest): Correctly capture return codes (#745).

Signed-off-by: Jeff Tan &lt;jefferson.tan@gmail.com&gt;

* fix(cli): Correctly capture return codes.

Signed-off-by: Jeff Tan &lt;jefferson.tan@gmail.com&gt; ([`170d911`](https://github.com/oscal-compass/compliance-trestle/commit/170d9117dc318e39fa43249e424dcf244614ff1a))

* fix: Added more checks for pylint. (#758)

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`2443ced`](https://github.com/oscal-compass/compliance-trestle/commit/2443cedf0ad7f7357aa4a1606fe7ddc8f6f3830b))

* fix: Adding automated tests of binary distribution validate release. (#756)

* fix: Adding automated tests of binary distribution to ensure final release passes all tests.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* Add python tests.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* chore: Correct yaml indentation

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix: adding extra checks for pre-commit

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix: Add check for yaml files syntax

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix: Correct issues with docstrings.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix: Corrected mdformat issues

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* chore: Changing PR check names to be cleaner

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`c0b6748`](https://github.com/oscal-compass/compliance-trestle/commit/c0b67485cd6e5619bbe4654d651931ce378315ca))

* fix: Ignore hidden files throughout the project (#755)

* fix: Ignore hidden files throughout the project

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;

* fix: Add additional test

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;

* fix: Adopt tests for Windows

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;

* fix: Remove test cleaning

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt; ([`aec1df4`](https://github.com/oscal-compass/compliance-trestle/commit/aec1df4e80168998a368d951861e62b502ca7fae))

### Refactor

* refactor: Refactor replicate command to use CLI choices (#753)

* refactor: Refactor replicate command to use CLI choices

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;

* refactor: Comply with code formatting

Signed-off-by: Ekaterina Nikonova &lt;enikonovad@gmail.com&gt;

Co-authored-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`1c0a5fe`](https://github.com/oscal-compass/compliance-trestle/commit/1c0a5fef09f28e2fd663dcb3cb33e50396f0a27d))

### Unknown

* Merge pull request #800 from IBM/develop

Trestle release ([`bc908f4`](https://github.com/oscal-compass/compliance-trestle/commit/bc908f41c688cfb530724439c68865a58397e00b))

* Create codeql-analysis.yml ([`2e73916`](https://github.com/oscal-compass/compliance-trestle/commit/2e73916730a0bac9f6a49b77d520785be28680b6))

## v0.25.1 (2021-09-30)

### Chore

* chore: Trestle release ([`e420bc5`](https://github.com/oscal-compass/compliance-trestle/commit/e420bc5fab4c0dcbf28ffdd1b57cf4e69069a3c0))

* chore: Merge back version tags and changelog into develop. ([`5f7c07d`](https://github.com/oscal-compass/compliance-trestle/commit/5f7c07d7379fc6c63e332397889aa2c376bcdad2))

### Fix

* fix: Emergency fix for trestle packaging. (#751)

* fix: Emergency fix for trestle packaging.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix: move install_requeest back into the correct setup.cfg section.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`8fedeaa`](https://github.com/oscal-compass/compliance-trestle/commit/8fedeaa641e7817fb4092224a315e1a38166078e))

## v0.25.0 (2021-09-29)

### Chore

* chore: trestle release

chore: trestle release ([`f76a2d1`](https://github.com/oscal-compass/compliance-trestle/commit/f76a2d1944e02a74cc782fa1c6812df66ce45422))

* chore: Merge back version tags and changelog into develop. ([`e6dd0d7`](https://github.com/oscal-compass/compliance-trestle/commit/e6dd0d7b94ba7581800bb10304d973ffe5e7d0bf))

### Feature

* feat: osco results remove scc_goal_description (#736)

- remove scc_goal_description class (but keep benchmark_id property)
- use result id rather than benchmark.id for scc_predefined_profile
class
- fix corresponding expected test outputs
- reduce size of rhel7 expected test output

Co-authored-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`f687a3d`](https://github.com/oscal-compass/compliance-trestle/commit/f687a3dcc44590a60f777d38eafe4013d54909e6))

### Fix

* fix: Ensure a minimimal code base is delivered via pypi (#741)

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`03557bd`](https://github.com/oscal-compass/compliance-trestle/commit/03557bdd44980899342665bac2d1905489981a75))

* fix: Adding extra documentation for element path. (#735)

* fix: Add extra documenntation for element path

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* chore: Correcting typos.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`bc32371`](https://github.com/oscal-compass/compliance-trestle/commit/bc32371e3f81adab5cd4621055421f2acb05c566))

* fix: Test files to confirm and close issues (#732)

* fix: Adding extra test files.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix: Updated code docs.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix: Correct packages

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`e87eb84`](https://github.com/oscal-compass/compliance-trestle/commit/e87eb84aabffd842275a673e63e42c75bd418203))

### Refactor

* refactor: use monkeypatch to replace mock library patch blocks (#739)

* chore(tests): replace mock patching with monkeypatch(ing) instead.

Signed-off-by: Jeff Tan &lt;jefferson.tan@gmail.com&gt;

* chore(tests): linted and formatted.

Signed-off-by: Jeff Tan &lt;jefferson.tan@gmail.com&gt;

* chore(tests): One monkeypatch switch for cache_test.py.

Signed-off-by: Jeff Tan &lt;jefferson.tan@gmail.com&gt;

* chore(cache_test): with patch (unittest) blocks replaced with monkeypatch in cache_test.py.

Signed-off-by: Jeff Tan &lt;jefferson.tan@gmail.com&gt;

* chore(conftest): monkeypatch switched for unittest patch block in conftest.py.

Signed-off-by: Jeff Tan &lt;jefferson.tan@gmail.com&gt;

* chore(split_test): monkeypatch instead of unittest patch block in split_test.py.

Signed-off-by: Jeff Tan &lt;jefferson.tan@gmail.com&gt;

* chore(validate_test): monkeypatch instead of unittest &#39;with patch&#39; blocks in validate_test.py.

Signed-off-by: Jeff Tan &lt;jefferson.tan@gmail.com&gt;

* chore(init_test): monkeypatch instead of unittest &#39;with patch&#39; blocks in init_test.py.

Signed-off-by: Jeff Tan &lt;jefferson.tan@gmail.com&gt;

* chore(href_test): monkeypatch instead of unittest &#39;with patch&#39; blocks in href_test.py.

Signed-off-by: Jeff Tan &lt;jefferson.tan@gmail.com&gt;

* chore(version_test): monkeypatch instead of unittest &#39;with patch&#39; block in version_test.py.

Signed-off-by: Jeff Tan &lt;jefferson.tan@gmail.com&gt;

* chore(import__test): monkeypatch instead of unittest &#39;with patch&#39; blocks in import__test.py.

Signed-off-by: Jeff Tan &lt;jefferson.tan@gmail.com&gt;

* chore(main_test): monkeypatch instead of unittest &#39;with patch&#39; block in main_test.py.

Signed-off-by: Jeff Tan &lt;jefferson.tan@gmail.com&gt;

* chore(cli_test): monkeypatch instead of unittest &#39;with patch&#39; block in cli_test.py.

Signed-off-by: Jeff Tan &lt;jefferson.tan@gmail.com&gt;

* chore(test_utils): monkeypatch instead of unittest &#39;with patch&#39; block in test_utils.py.

Signed-off-by: Jeff Tan &lt;jefferson.tan@gmail.com&gt;

* Revert &#34;chore(test_utils): monkeypatch instead of unittest &#39;with patch&#39; block in test_utils.py.&#34;

This reverts commit a99ad81a143f43b0c656d8975fa9c670d75b9b46.

Explanation:
 The changes being reverted really just makes the code look nicer for one &#39;with patch&#39; block.
If this is indeed replaced with monkeypatch, with the latter as an art for the create_trestle_project_with_model()
function, then all calls to create_trestle_project_with_model() will need refactoring to include a MonkeyPatch
argument. This does not seem worth it, so reverting.

Signed-off-by: Jeff Tan &lt;jefferson.tan@gmail.com&gt;

* refactor(tests): monkeypatch instead of unittest &#39;with patch&#39; block in test_utils.py and, being affected, split_test.py.

Signed-off-by: Jeff Tan &lt;jefferson.tan@gmail.com&gt;

Co-authored-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`88a4f3c`](https://github.com/oscal-compass/compliance-trestle/commit/88a4f3ccc08778deb3596c06203bd139048af25f))

## v0.24.0 (2021-09-21)

### Chore

* chore: add link to compliance-trestle demos in main README.md. (#722) ([`cbf9524`](https://github.com/oscal-compass/compliance-trestle/commit/cbf95247dcba5731221db22393a67beff3c92770))

* chore: Merge back version tags and changelog into develop. ([`e8a7b82`](https://github.com/oscal-compass/compliance-trestle/commit/e8a7b82befcfe4a95e6e8d42a4829c03d050e3ee))

### Feature

* feat: Allow import to use the caching functionality to access external URLs (https/sftp etc) (#718)

* import now via cache

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* some cleanup

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* import now uses cache and can work with relative paths.

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* updated docs

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* remove sftp:// from fetcher uri test causing failure cicd

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* localizing test failure in cicd

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* added try clause for urlparse

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* fix: Refactored test to use parametrize

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* removed ftp case

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* blocked off bad uri tests

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* added tests back in

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* disallow : in local files for unix

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* tweaked slashes for unix

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* tutorial import via url and add windows encoding

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* fixed encoding issue on write in cache

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* fixes made based on PR feedback

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

Co-authored-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`3527259`](https://github.com/oscal-compass/compliance-trestle/commit/352725952687fde4627c97037e68f2238c638a04))

### Fix

* fix: Update OCP compliance operator transform to use classes expected by IBM SCC. ([`2068f57`](https://github.com/oscal-compass/compliance-trestle/commit/2068f570ff6d47bb0348e630cd4dc01e2d90e4b5))

* fix:  Correct split merge pathing inconsistencies. (#725)

* fix: Corrections to fix merge

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix: Update tests for drawio functionality.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix: Initial set of tests.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix: Initial set of tests.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix: Temp patch for testing

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix: update changes to fix merge to clean up functionality.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix: Correct validator behaviour

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix: Correcting doctags

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix: Correcting doctags

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix: Updated comments / errors.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix: Updated comments / errors.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`1ea7f63`](https://github.com/oscal-compass/compliance-trestle/commit/1ea7f63549ad1f74a47572fb00f04f42bce2e5ab))

* fix: Correct merge (including repository functionality) and improve merge cwd handling. (#724)

* fix: Corrections to fix merge

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix: Update tests for drawio functionality.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`a780e2c`](https://github.com/oscal-compass/compliance-trestle/commit/a780e2ca16f8e5ca99a74e8167b6ccb66c3e91e1))

### Unknown

* Merge pull request #729 from IBM/develop

chore(release): Bug fixes and enabling caching for import ([`1f1598e`](https://github.com/oscal-compass/compliance-trestle/commit/1f1598eae114e4b6223cc09e162ad770dfd7bf69))

## v0.23.0 (2021-09-03)

### Chore

* chore: regen oscal with new datamodel-codegen and make develop (#714)

* re run gen-oscal after make develop

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* added comment

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt; ([`60973b8`](https://github.com/oscal-compass/compliance-trestle/commit/60973b8134cbd724763c5b3b14dc7e2c28f1f9c2))

* chore: Clean up issue templates. (#707)

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`9f6db2d`](https://github.com/oscal-compass/compliance-trestle/commit/9f6db2daf3cbe942bbf5133ff03e450bd5c42f75))

* chore: Merge back version tags and changelog into develop. ([`7a994f3`](https://github.com/oscal-compass/compliance-trestle/commit/7a994f31d8113403bf5b3ab750a1b1659d6318ae))

### Feature

* feat: Update of Oscal profile to osco from initial PoC with stakeholder review.

* feat/oscal-profile-to-osco-yaml-rev2

* Comments.

Co-authored-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`c47092a`](https://github.com/oscal-compass/compliance-trestle/commit/c47092aecf0d4b73eef2147738832748ecb04b1a))

* feat: resolved profile catalog functionality and enhanced ssp generation (#694)

* initial changes prior to pull.

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* now creating basic resolved profile catalog

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* now prune controls

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* clean up a bit

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* fix: Documentation fixes as well as fixes to json serializisation for full utf-8 support.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* now good except for unicode

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* ssp now matches, added warning for odd files during validate

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* tweak validate

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* tidy ssp

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* initial pipeline for generating resolved catalog

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* cascaded profiles do correct selection

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* modify mostly working

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* all seems ok

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* all tests pass

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* ssp generation looks good

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* Typo

* added more recursion

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* fixed sections being dropped

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* clarify part text for ssp assemble

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* ssp now doesnt overwrite

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* increase coverage

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* fixed docs

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* fix: Corrected issues from inconsistent versions of mdformat including in the CI pipeline.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* added complex profile with depth

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* added test profile c

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* updated docs

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* tweaked doc text

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* clean up ssp a bit

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* chore: Fixing code formatting after merge conflict.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* addressed review requests.

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* typing generators as iterators

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

Co-authored-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`193e3b9`](https://github.com/oscal-compass/compliance-trestle/commit/193e3b9e8179d3be0b5eaa4692e9106c5e4ad628))

* feat: Add new OSCAL profile-to-osco-yaml transformer functionality. (#677)

* OSCAL profile to osco yaml transformer

* Fix unit test description.

* Fix import of text_files_equal.

* Address reviewer suggestions and other improvements

- change default output filename to osco-profile.yaml
- fix interface types
- fix incorrect comments
- return json string, not dict
- set new or default values on class creation
- reduce size of test data

* fix: Updated href to the nist 800-53 catalog.

Co-authored-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`c7e2156`](https://github.com/oscal-compass/compliance-trestle/commit/c7e2156b9cc2546d15a70e7699091465c8a54e91))

* feat: Adding rich model generation to trestle add and trestle create. (#693)

* feat: Adding optional argument to allow richer model generation to trestle add and trestle create

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* chore: Refactoring more tests to take advantage of monkeypatch.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* chore: Improved tests.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix: Extra unit tests.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* chore: Improved  documentation.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix: Correct md issues.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`9d32953`](https://github.com/oscal-compass/compliance-trestle/commit/9d329530893da01de1b71dce8711fa3edb1fc2cb))

* feat: Adding capability to allowing generator to generate optional fields. (#690)

* feat: Adding capability to allow gOscal Generator to generate optional fields

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix: Clean up arguments.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix: Clean up arguments.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`4a0f631`](https://github.com/oscal-compass/compliance-trestle/commit/4a0f6318b426e24a2764e0a75edcaa84861cadd8))

### Fix

* fix: Refactor underlying methods to isolate calls to Path.cwd() (#716)

* fix: Refactor underlying methods to isolate calls to cwd

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix: Cleaned up unit tests and command docstrings.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix: Cleaned up unit tests and command docstrings.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix: Further code clean up.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`473c1d8`](https://github.com/oscal-compass/compliance-trestle/commit/473c1d8ca85e688bd75362a3f0f22e8cc81c327d))

* fix: Cleanup assemble command to reduce LoC covering the same functionality. (#709)

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`c40cfca`](https://github.com/oscal-compass/compliance-trestle/commit/c40cfca85af92c6e5d6c725ea069db4d534676f9))

### Unknown

* Merge pull request #717 from IBM/develop

feat: Trestle release ([`e0aacad`](https://github.com/oscal-compass/compliance-trestle/commit/e0aacadc3706f86ad86fd27c7df26a2e2b2425ec))

## v0.22.1 (2021-08-19)

### Chore

* chore: Merge back version tags and changelog into develop. ([`639a9c1`](https://github.com/oscal-compass/compliance-trestle/commit/639a9c1fdbc7257457065d753beed8ac82fe0486))

### Fix

* fix: Strip back dependencies due to dependency error (#684)

* fix: Updating developer docs on CI workflow

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix: Additional documentation details

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix: removed dependencies that are causing conflicts.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix: removed dependencies that are causing conflicts.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`a8b4768`](https://github.com/oscal-compass/compliance-trestle/commit/a8b476859cbc3ba77f9bf389ed2bb977bd80c592))

* fix: Updating developer docs to include details on the CI workflow. (#683)

* fix: Updating developer docs on CI workflow

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix: Additional documentation details

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`e8d63e1`](https://github.com/oscal-compass/compliance-trestle/commit/e8d63e1ddcfb9bf1b179de195bb86b7af7758fe3))

### Unknown

* Merge pull request #686 from IBM/develop

fix: Trestle release ([`8d76b52`](https://github.com/oscal-compass/compliance-trestle/commit/8d76b5259782f7a8782df3491c391cc77472220b))

## v0.22.0 (2021-08-13)

### Chore

* chore: Merge pull request #679 from IBM/develop

feat: Trestle release ([`6582a5c`](https://github.com/oscal-compass/compliance-trestle/commit/6582a5cb20ff092763beb5059fbb8c34dd712b79))

* chore: Adding google analytics to website (#680)

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`4375ab9`](https://github.com/oscal-compass/compliance-trestle/commit/4375ab92fca03a699cdd788c0bfe01b9a60a45c0))

* chore: Merge back version tags and changelog into develop. ([`1ba9815`](https://github.com/oscal-compass/compliance-trestle/commit/1ba9815b75b82ee04acffbea4c1532fdd0f1feb4))

### Feature

* feat: Schema validate command including miscellaneous fixes. (#665)

* chore: Initial skeleton

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix: Clean up of text_files_equal (#664)

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix: Working on unit tests.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix: Complete basic Unit tests

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix: Cleaning up code.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix: Removing target model from scope

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix: adding testing.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix: Added remaining unit tests.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix:Adding the missing files.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix:Added extra documentation.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix: Addressed issues in review

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix: Adding more unit tests.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`3ab088a`](https://github.com/oscal-compass/compliance-trestle/commit/3ab088a9a9b4927a660510fe6fe8438a9b48fdfa))

* feat: new command href and now ssp gen uses caching to pull catalog from remote (#669)

* first reworking of cache. tests pass

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* have expiration working.

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* added test

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* improved uri handling and tests

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* added new command href

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* ssp gen works via cache

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* increased coverage

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* fixed docstring

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* fix unix test failures

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* more href tests and fixes based on pr feedback

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* boost coverage

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* fix docstrings

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* windows drive path issue

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* added docs for href and now dont cache local hrefs

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* updated cli.md

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* updated href text 3

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* fixed changes to pre-commit for mdformat

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* fix: Correct missing/bad  mdformatted documents and add mdformat to pre-commit.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

Co-authored-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`660ef47`](https://github.com/oscal-compass/compliance-trestle/commit/660ef47b48d17ce19ab31690ef8264afb085e326))

### Fix

* fix: Improved error handling of yaml headers in markdown files.  (#676)

* chore: Initial skeleton

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix: Clean up of text_files_equal (#664)

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix: Working on unit tests.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix: Complete basic Unit tests

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix: Cleaning up code.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix: Removing target model from scope

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix: adding testing.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix: Added remaining unit tests.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix:Adding the missing files.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix:Added extra documentation.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix: Addressed issues in review

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix: Improved error handling of yaml header.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix: Adding more unit tests.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix: Covering bad yaml headers with testing.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix: Covering bad yaml headers with testing.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix: Bad md header.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`1983925`](https://github.com/oscal-compass/compliance-trestle/commit/198392543a864ab213d869ddeaa123817d69b3c2))

* fix: Documentation fixes as well as fixes to json serializisation for full utf-8 support. (#674)

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`d051638`](https://github.com/oscal-compass/compliance-trestle/commit/d0516381a8be4d4c97c14395965ade00f8181083))

* fix: relocate ParameterHelper class. (#667)

Co-authored-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`0dbf472`](https://github.com/oscal-compass/compliance-trestle/commit/0dbf472c5d3513fb85d66e4f76bb3bc037fc726f))

* fix: file compare issue in task xlsx-to-component-definition unit test (#666)

* Fix file compare issue in task xlsx-to-component-definition unit test

trestle version increases with each release, which affects the produced
output but not in any material way with respect to the unit tests at
hand.

fix is to employ local function to get_trestle version which nominally
returns the actual trestle version, but to mock said function in the
unit test.

* fix: file compare issue in task xlsx-to-component-definition unit test

* Use trestle version 0.21.0 in compare data, same as parameter-helper
fix. ([`052d184`](https://github.com/oscal-compass/compliance-trestle/commit/052d184a1cb5b83e034e7f2bc7c8a240299f7b6e))

## v0.21.0 (2021-07-30)

### Chore

* chore: Further improvements to testing performance (#662)

* chore: Improving testing performance in CICD

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix: Further scleaning of CICD to optimise performance

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix: Further scleaning of CICD to optimise performance

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`e281fa9`](https://github.com/oscal-compass/compliance-trestle/commit/e281fa936fbd232e36825e4609585c4e669f6ca7))

* chore: Improving testing performance for the CICD pipeline(#661)

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`83abe2d`](https://github.com/oscal-compass/compliance-trestle/commit/83abe2dd8a74c818cfac5e45b4e2900cb609c423))

* chore: Merge back version tags and changelog into develop. ([`4e1bb9f`](https://github.com/oscal-compass/compliance-trestle/commit/4e1bb9fee0ccc67f2be27693eb28b3707e1fe888))

### Documentation

* docs: Cross link documentation between compliance-trestle and compliance-trestle-demos repositories. (#637)

* feat: Added demonstration content.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix: Cleaned up demo content.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix: Removed dupicate demos.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`f28aca1`](https://github.com/oscal-compass/compliance-trestle/commit/f28aca1073888a7575a277c819449302e8e52b23))

### Feature

* feat: Trestle Release #659 from IBM/develop

feat: Trestle release ([`6329c82`](https://github.com/oscal-compass/compliance-trestle/commit/6329c82ddd59e2699bd6e7dc8cd571e948fa21f6))

* feat: describe command to describe contents of model files with optional element path (#650)

* added describe.py file

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* initial describe parsing

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* describe mostly working

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* added comments

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* added test file

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* added typing for docstrings

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* more docstring fixes

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* boost coverage

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* wrong test docstring

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* more tests and enhancements

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* initial documentation for describe

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* updated docs for split and describe

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* added new md doc files

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* check for commas and added to docs for describe

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

Co-authored-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`905ff8a`](https://github.com/oscal-compass/compliance-trestle/commit/905ff8ac3cb0c7f11a8d8601bbcbcb2f9b40cae0))

* feat: spread sheet to component definition (#635)

* spread sheet to OSCAL component definition task

* spread sheet to OSCAL component definition task

* Merge with develop, minor fixes.

* Add missing column specs to -i output.

* Relocate references to IBM and SCC from code to config.

* Remove hard-coded NIST values, relocate to config file.

* Use from trestle.utils.fs import text_files_equal

* Fix flake8.

* Remove the copy of the nist 800-53 catalog.

* Remove the copy of the nist 800-53 catalog.

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;

* flake8, but no complaint on my laptop?

* Fix bare except.

* Fix bare except.

Signed-off-by: Lou DeGenaro &lt;lou.degenaro@gmail.com&gt;

* linter fixes.

* linter fixes.

* Reduce size of main execute function.

Size of for loop reduced to 28 lines, including comments.
Minor bug fix in output catalog.

* Fix test spreadsheets.

- remove hidden and unused columns
- delete ods file

* To identify column use heading (row 1) rather than letter.

* Cosmetic fix to doc (for tanium-to-oscal).

* Remove unused column and between blank columns from &#34;good&#34; spread sheet.

Also, remove corresponding heading check from code.

* Document trestle task xlsx-to-oscal-component-definition. ([`6fe4e22`](https://github.com/oscal-compass/compliance-trestle/commit/6fe4e22ce9235e95ccd73c836bc8cbedfa99799c))

### Fix

* fix: ssp dropping section prose when in profile, now supporting profile &amp; catalog section prose. (#657)

* fixed section issue in ssps

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* added docs

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* boost coverage

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

Co-authored-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`4eadf47`](https://github.com/oscal-compass/compliance-trestle/commit/4eadf475dc0ccd0f38bd365b9b71be90e6f98cce))

* fix: ssp section generation failed due to changes due to 1.0.0 (#649)

* fixed ssp section generation - changes due to 1.0.0

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* tweaked doc string

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

Co-authored-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`26dac34`](https://github.com/oscal-compass/compliance-trestle/commit/26dac345c65a59ef49f49af11dbacb1f2094ceb4))

* fix: split bugs and make -f optional (#639)

* split working except for parent issue

Signed-off-by: fsuits &lt;frankst@au1.ibm.com&gt;

* split working - needs cleanup

Signed-off-by: fsuits &lt;frankst@au1.ibm.com&gt;

* cleaned up and fixed compdef props issue

Signed-off-by: fsuits &lt;frankst@au1.ibm.com&gt;

* fixed rel path split issue

Signed-off-by: fsuits &lt;frankst@au1.ibm.com&gt;

* renamed respository refs

Signed-off-by: fsuits &lt;frankst@au1.ibm.com&gt;

* start split with no -f

Signed-off-by: fsuits &lt;frankst@au1.ibm.com&gt;

* split with no file works

Signed-off-by: fsuits &lt;frankst@au1.ibm.com&gt;

* updated docs

Signed-off-by: fsuits &lt;frankst@au1.ibm.com&gt;

* boost coverage

Signed-off-by: fsuits &lt;frankst@au1.ibm.com&gt;

* fix lint issue

Signed-off-by: fsuits &lt;frankst@au1.ibm.com&gt;

* made requested changes from pr feedback.

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* fixed split issues with new repository

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* converted TLO to TopLevelOscalModel

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* fixed extra variable assignment

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

* added try/except for test chdir

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt; ([`c514301`](https://github.com/oscal-compass/compliance-trestle/commit/c51430175117e1c1071442d3c564fae4afcef461))

* fix: Cleanup and enhancement of linting. (#636)

* fix: Improved linting

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix: Improved linting

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`631eba9`](https://github.com/oscal-compass/compliance-trestle/commit/631eba9ac1795bfcd109ed0e840898c2e6101528))

## v0.20.0 (2021-07-16)

### Chore

* chore: Merge back version tags and changelog into develop. ([`7656043`](https://github.com/oscal-compass/compliance-trestle/commit/7656043d4311f909b2fc3fa82ffe1d930a36c787))

### Feature

* feat: Adding a global option to trestle author headers. (#628)

* feat: Adding a global option to trestle author headers.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix: Added some unit tests for trestle author.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix: Added tests for missing coverage.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix: Updated docs.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`16f0265`](https://github.com/oscal-compass/compliance-trestle/commit/16f0265b1296066a203a5f844d89fd642a00fdb6))

* feat: Repository APIs to allow developer a consistent interface to a trestle repo. (#583)

* Added Repo APIs and set trestle root in main command

* implementing read for managedOSCAL

* fix init validation in commad_docs

* fix: Restructured command inherhitence to ensure trestle-root is found.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* Completed ManagedOSCAL class implementation

* removed __main__ from trestle_repo

* Updated tests for trestle_root

* Moved trestle_repo.ps to trestle/core/repository.py ans some other cleanup

* Update fs.py

Small typo error.

Co-authored-by: Vikas &lt;avikas@in.ibm.com&gt;
Co-authored-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`7bfabc5`](https://github.com/oscal-compass/compliance-trestle/commit/7bfabc5a9e078cbfb6b190d3ccb7f06942d9ea37))

### Fix

* fix: Added test cases for Repository code (#625)

* Added test cases for Repository code

* updated comment

* added more test cases

* updated tests

* updated test

* updated repository split code and tests

Co-authored-by: Vikas &lt;avikas@in.ibm.com&gt; ([`c3f8a33`](https://github.com/oscal-compass/compliance-trestle/commit/c3f8a339bb66ea4723c9b1fa7b7ef30edf275cb5))

* fix: split catalog star, enable split of model with wildcard (#626)

* split nearly working

Signed-off-by: fsuits &lt;frankst@au1.ibm.com&gt;

* split star seems ok

Signed-off-by: fsuits &lt;frankst@au1.ibm.com&gt;

* boosted coverage - split star seems fine

Signed-off-by: fsuits &lt;frankst@au1.ibm.com&gt;

* cleaned up, about to pull develop

Signed-off-by: fsuits &lt;frankst@au1.ibm.com&gt;

* added doc

Signed-off-by: fsuits &lt;frankst@au1.ibm.com&gt;

* fixed error in docstring

Signed-off-by: fsuits &lt;frankst@au1.ibm.com&gt; ([`d17389e`](https://github.com/oscal-compass/compliance-trestle/commit/d17389e824ce8f33f2a091cd541622fb40513a37))

* fix: tutorial tweaks (#623)

* added editing of files in test of ssp assemble

Signed-off-by: fsuits &lt;frankst@au1.ibm.com&gt;

* improved handling of prose for implementations in ssp assemble

Signed-off-by: fsuits &lt;frankst@au1.ibm.com&gt;

* boost coverage

Signed-off-by: fsuits &lt;frankst@au1.ibm.com&gt;

* tweaks to the tutorial

Signed-off-by: fsuits &lt;frankst@au1.ibm.com&gt;

* explicit download of catalog file from nist github.

Signed-off-by: fsuits &lt;frankst@au1.ibm.com&gt;

* fixed backslash

Signed-off-by: fsuits &lt;frankst@au1.ibm.com&gt; ([`3ab018d`](https://github.com/oscal-compass/compliance-trestle/commit/3ab018d6dd63ae4ee98d90daca9b5580687ac8ae))

* fix: Add gfm support for mdformat (#620)

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`f67a74c`](https://github.com/oscal-compass/compliance-trestle/commit/f67a74c63aedd1cabdb6fcfd8f5be99b25886949))

* fix: ssp assemble prose, all extraction of general prose for responses (#618)

* added editing of files in test of ssp assemble

Signed-off-by: fsuits &lt;frankst@au1.ibm.com&gt;

* improved handling of prose for implementations in ssp assemble

Signed-off-by: fsuits &lt;frankst@au1.ibm.com&gt;

* boost coverage

Signed-off-by: fsuits &lt;frankst@au1.ibm.com&gt; ([`06e8627`](https://github.com/oscal-compass/compliance-trestle/commit/06e862705bbf3880678324ba29e4be54e54322e6))

* fix: boost coverage fix split_too_fine (#615)

* improved test coverage, fixed split_too_fine, removed dict queries that arent needed

Signed-off-by: fsuits &lt;frankst@au1.ibm.com&gt;

* removed exception check in validate

Signed-off-by: fsuits &lt;frankst@au1.ibm.com&gt;

* reworked split_too_fine to deal with pydantic collection classes

Signed-off-by: fsuits &lt;frankst@au1.ibm.com&gt;

* improved typing and simplified multiple ifs to try except

Signed-off-by: fsuits &lt;frankst@au1.ibm.com&gt; ([`891227b`](https://github.com/oscal-compass/compliance-trestle/commit/891227b9899b38f7ce609f8b4b715740cb9a84f7))

### Unknown

* Merge pull request #629 from IBM/develop

feat: Release of trestle repository functionality ([`4135275`](https://github.com/oscal-compass/compliance-trestle/commit/4135275e0874d1a5107e5494075c7ef4bae2d9f7))

## v0.19.0 (2021-07-06)

### Chore

* chore: [ImgBot] Optimize images (#609)

*Total -- 343.57kb -&gt; 285.47kb (16.91%)

/3rd-party-schema-documents/IBM_assessment_result_interchange_SCC/Unification-SCC-class-for-OSCO-and-Tanium-to-OSCAL.png -- 171.79kb -&gt; 142.74kb (16.91%)
/docs/reference/Unification-SCC-class-for-OSCO-and-Tanium-to-OSCAL.png -- 171.79kb -&gt; 142.74kb (16.91%)

Signed-off-by: ImgBotApp &lt;ImgBotHelp@gmail.com&gt;

Co-authored-by: ImgBotApp &lt;ImgBotHelp@gmail.com&gt; ([`d6f5148`](https://github.com/oscal-compass/compliance-trestle/commit/d6f514882934b895d4f1c3b22cf1d5e63288d95f))

* chore: Merge back version tags and changelog into develop. ([`18d4d38`](https://github.com/oscal-compass/compliance-trestle/commit/18d4d385dd1a4ba743a59811d199ab7dd1109820))

### Feature

* feat: Merge pull request #611 from IBM/develop

feat: Support for OSCAL 1.0.0 ([`0e9a4c5`](https://github.com/oscal-compass/compliance-trestle/commit/0e9a4c51f75470c202efa53b625e3181bd31254c))

* feat: remove validate mode option and yaml_header optional in ssp-gen (#607)

* fixed ssp assemble

Signed-off-by: FrankSuits &lt;frankst@au1.ibm.com&gt;

* updated doc

Signed-off-by: FrankSuits &lt;frankst@au1.ibm.com&gt;

* fixed error checking blank line

Signed-off-by: FrankSuits &lt;frankst@au1.ibm.com&gt;

* yaml header now optional in ssp-generate

Signed-off-by: FrankSuits &lt;frankst@au1.ibm.com&gt;

* removed validate -mode

Signed-off-by: FrankSuits &lt;frankst@au1.ibm.com&gt;

* fully removed validate mode and updated docs

Signed-off-by: FrankSuits &lt;frankst@au1.ibm.com&gt;

* fixed problem with missing header and now check all optional class members for None

Signed-off-by: FrankSuits &lt;frankst@au1.ibm.com&gt;

* clean up statement labels to satisfy regex in ssp-assemble

Signed-off-by: frank &lt;freestar8n@yahoo.com&gt;

* provide text for params when value not given.  Add statement id to the Add description text

Signed-off-by: frank &lt;freestar8n@yahoo.com&gt;

Co-authored-by: Chris Butler &lt;chris@thebutlers.me&gt;
Co-authored-by: frank &lt;freestar8n@yahoo.com&gt; ([`3a5e104`](https://github.com/oscal-compass/compliance-trestle/commit/3a5e104d100feaad5334e8ee3231bdd6e93bbf82))

* feat: restore oscal write to use windows newlines on windows (#608)

* restored oscal_write to use windows newlines on windows and removed dep. on filecmp

Signed-off-by: FrankSuits &lt;frankst@au1.ibm.com&gt;

* modified comment

Signed-off-by: FrankSuits &lt;frankst@au1.ibm.com&gt;

Co-authored-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`b7d8345`](https://github.com/oscal-compass/compliance-trestle/commit/b7d83458a233204b52e4271ee908392870992d5c))

* feat: Remove target model from trestle with OSCAL 1.0.0 release (#595)

* feat: Remove target v1

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* chore: Pre-merge commit.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix: Clean up UT&#39;s / formatting

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix: Remove docs references to target definition.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* chore: Remove typos and other issues identified in PR review.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix: Remove bad comments

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`ececd37`](https://github.com/oscal-compass/compliance-trestle/commit/ececd3792281b08bf26831acee1254bd24338815))

* feat: Ingestion of XML and other improvements for the OSCO transformer. (#586)

* 0.18.1

Automatically generated by python-semantic-release

* feat: oscal normalize major changes to support new OSCAL 1.0.0 (#577)

* removed nist modules

Signed-off-by: FrankSuits &lt;frankst@au1.ibm.com&gt;

* reloaded nist

Signed-off-by: FrankSuits &lt;frankst@au1.ibm.com&gt;

* added oscal_normalize

Signed-off-by: FrankSuits &lt;frankst@au1.ibm.com&gt;

* first new oscal with common

Signed-off-by: FrankSuits &lt;frankst@au1.ibm.com&gt;

* tests now load

Signed-off-by: FrankSuits &lt;frankst@au1.ibm.com&gt;

* tmpdir -&gt; tmp_path, fixed Model in files

Signed-off-by: FrankSuits &lt;frankst@au1.ibm.com&gt;

* added lous fixes to transformers

Signed-off-by: FrankSuits &lt;frankst@au1.ibm.com&gt;

* more fixes for new oscal - 25 fail 379 pass

Signed-off-by: FrankSuits &lt;frankst@au1.ibm.com&gt;

* fix: Consolidate UUID sample and sample fix for POAM forward refs.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fixed ordering issue in oscal files

Signed-off-by: FrankSuits &lt;frankst@au1.ibm.com&gt;

* fix to poam forward

Signed-off-by: FrankSuits &lt;frankst@au1.ibm.com&gt;

* fix: Correct typing of assertion with OSCAL model changes.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fixed split compdef and updated split data up to including step2

Signed-off-by: FrankSuits &lt;frankst@au1.ibm.com&gt;

* updated data in step3 of splitmerge

Signed-off-by: FrankSuits &lt;frankst@au1.ibm.com&gt;

* added more files from split merge workflow

Signed-off-by: FrankSuits &lt;frankst@au1.ibm.com&gt;

* more fixes to data files.  11 fails

Signed-off-by: FrankSuits &lt;frankst@au1.ibm.com&gt;

* improved add tests, started updating profile for ssp.  10 failures.

Signed-off-by: FrankSuits &lt;frankst@au1.ibm.com&gt;

* fix: Correct generator behaviour

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* ssp tests now pass - fixed simple profile for 1.0.0

Signed-off-by: FrankSuits &lt;frankst@au1.ibm.com&gt;

* fixed add and replicate failures

Signed-off-by: FrankSuits &lt;frankst@au1.ibm.com&gt;

* fixed validate failure - replaced tests using target to use catalog instead

Signed-off-by: FrankSuits &lt;frankst@au1.ibm.com&gt;

* fixed 2 import failures

Signed-off-by: FrankSuits &lt;frankst@au1.ibm.com&gt;

* removed test for load_dict, removed test for split too fine - all tests pass

Signed-off-by: FrankSuits &lt;frankst@au1.ibm.com&gt;

* boost validate test coverage

Signed-off-by: FrankSuits &lt;frankst@au1.ibm.com&gt;

* hooked oscal_normalize into gen_oscal and refined split of common files.

Signed-off-by: FrankSuits &lt;frankst@au1.ibm.com&gt;

* now include oscal dir for yapf formatting.  This commit is only a format change.

Signed-off-by: FrankSuits &lt;frankst@au1.ibm.com&gt;

Co-authored-by: Chris Butler &lt;chris@thebutlers.me&gt;

* ingest xml and other improvements for OSCO transformer

- enable ingestion of xml
- add target_type
- remove name &amp; node
- improve test cases

* Fix typo.

Co-authored-by: semantic-release &lt;semantic-release&gt;
Co-authored-by: Frank Suits &lt;47203786+fsuits@users.noreply.github.com&gt;
Co-authored-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`f555f1e`](https://github.com/oscal-compass/compliance-trestle/commit/f555f1e1607edde8b6fc67d03b7804d28a0a345f))

* feat: oscal normalize major changes to support new OSCAL 1.0.0 (#577)

* removed nist modules

Signed-off-by: FrankSuits &lt;frankst@au1.ibm.com&gt;

* reloaded nist

Signed-off-by: FrankSuits &lt;frankst@au1.ibm.com&gt;

* added oscal_normalize

Signed-off-by: FrankSuits &lt;frankst@au1.ibm.com&gt;

* first new oscal with common

Signed-off-by: FrankSuits &lt;frankst@au1.ibm.com&gt;

* tests now load

Signed-off-by: FrankSuits &lt;frankst@au1.ibm.com&gt;

* tmpdir -&gt; tmp_path, fixed Model in files

Signed-off-by: FrankSuits &lt;frankst@au1.ibm.com&gt;

* added lous fixes to transformers

Signed-off-by: FrankSuits &lt;frankst@au1.ibm.com&gt;

* more fixes for new oscal - 25 fail 379 pass

Signed-off-by: FrankSuits &lt;frankst@au1.ibm.com&gt;

* fix: Consolidate UUID sample and sample fix for POAM forward refs.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fixed ordering issue in oscal files

Signed-off-by: FrankSuits &lt;frankst@au1.ibm.com&gt;

* fix to poam forward

Signed-off-by: FrankSuits &lt;frankst@au1.ibm.com&gt;

* fix: Correct typing of assertion with OSCAL model changes.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fixed split compdef and updated split data up to including step2

Signed-off-by: FrankSuits &lt;frankst@au1.ibm.com&gt;

* updated data in step3 of splitmerge

Signed-off-by: FrankSuits &lt;frankst@au1.ibm.com&gt;

* added more files from split merge workflow

Signed-off-by: FrankSuits &lt;frankst@au1.ibm.com&gt;

* more fixes to data files.  11 fails

Signed-off-by: FrankSuits &lt;frankst@au1.ibm.com&gt;

* improved add tests, started updating profile for ssp.  10 failures.

Signed-off-by: FrankSuits &lt;frankst@au1.ibm.com&gt;

* fix: Correct generator behaviour

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* ssp tests now pass - fixed simple profile for 1.0.0

Signed-off-by: FrankSuits &lt;frankst@au1.ibm.com&gt;

* fixed add and replicate failures

Signed-off-by: FrankSuits &lt;frankst@au1.ibm.com&gt;

* fixed validate failure - replaced tests using target to use catalog instead

Signed-off-by: FrankSuits &lt;frankst@au1.ibm.com&gt;

* fixed 2 import failures

Signed-off-by: FrankSuits &lt;frankst@au1.ibm.com&gt;

* removed test for load_dict, removed test for split too fine - all tests pass

Signed-off-by: FrankSuits &lt;frankst@au1.ibm.com&gt;

* boost validate test coverage

Signed-off-by: FrankSuits &lt;frankst@au1.ibm.com&gt;

* hooked oscal_normalize into gen_oscal and refined split of common files.

Signed-off-by: FrankSuits &lt;frankst@au1.ibm.com&gt;

* now include oscal dir for yapf formatting.  This commit is only a format change.

Signed-off-by: FrankSuits &lt;frankst@au1.ibm.com&gt;

Co-authored-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`fd7e137`](https://github.com/oscal-compass/compliance-trestle/commit/fd7e137d0cc19527754e1e6a25c2361f9338a513))

### Fix

* fix: remove incorrect scc_check_version in tanium transformer (#591)

* fix: remove incorrect scc_check_version

* Fix doc per Chris Butler&#39;s review.

* Policy Validation Points, spelling.

Co-authored-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`4c59eda`](https://github.com/oscal-compass/compliance-trestle/commit/4c59edacfcacef2921711642776126a9b4e6a386))

* fix: duplicate oscal classes and reordered.  oscal_write line ending (#592)

* fixed duplicate oscal classes and reordered.  oscal_write specifies unix line ending.  increased test coverage.

Signed-off-by: FrankSuits &lt;frankst@au1.ibm.com&gt;

* added documentation

Signed-off-by: FrankSuits &lt;frankst@au1.ibm.com&gt;

Co-authored-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`ddaeece`](https://github.com/oscal-compass/compliance-trestle/commit/ddaeecebbf884f7b96509e3c75d798f65472278a))

* fix: Ensure line endings do not change (#593)

* fix: Ensure line endings do not change

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix: Scope git config to only the CICD user.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix: Correct config scope.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`82fcab3`](https://github.com/oscal-compass/compliance-trestle/commit/82fcab3ea5e4b06b6ff31a6e2749b30729cfd48d))

## v0.18.1 (2021-06-17)

### Chore

* chore: Merge back version tags and changelog into develop. ([`2b987f9`](https://github.com/oscal-compass/compliance-trestle/commit/2b987f99f3f8bd3c4b36aec071887e7f4766882c))

### Fix

* fix: Small scale fixes to the author validation system. (#572) (#573)

* fix: Minor fixes of author capability

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix:Adding more unit tests

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix:Added test fixtures.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix: Remove redundant statement.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`04e16cc`](https://github.com/oscal-compass/compliance-trestle/commit/04e16ccd508607eadb2c0ab4db69fb324cf0e24c))

* fix: Small scale fixes to the author validation system. (#572)

* fix: Minor fixes of author capability

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix:Adding more unit tests

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix:Added test fixtures.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix: Remove redundant statement.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`8cd2232`](https://github.com/oscal-compass/compliance-trestle/commit/8cd22323c0b0bcb556c15fa3bb91d4a7c36bb683))

## v0.18.0 (2021-06-17)

### Chore

* chore: Merge back version tags and changelog into develop. ([`f98a852`](https://github.com/oscal-compass/compliance-trestle/commit/f98a852b6782f0c0760b1aab8a30eeef16039085))

### Feature

* feat: Allow explicit inclusion / exclusion of readme files in author workflows (#570)

* feat: Optional flags for readme validation

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix: Added missing test files.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`0ca1d20`](https://github.com/oscal-compass/compliance-trestle/commit/0ca1d202fa4865acf20fb9156a9c13437350b16e))

### Fix

* fix: Replace yaml library to ensure that errors are thrown / recognised on duplicate keys. (#569)

* chore: Moderniing to ruamel.yaml

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix: Bad testing data

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix: Replace yaml library with modernized and safe yaml library

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* chore: Fixing missing code format / linting.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix: Corrected behaviour in UT&#39;s by forcing file flush in oscal_write

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix: Correct docs setup.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix: For content flushing / IO issues.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix: More YAML IO sync issues

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`9464420`](https://github.com/oscal-compass/compliance-trestle/commit/9464420cb3bba1dc684051ff35e2d13e9a115203))

### Unknown

* Trestle release  - update prior to OSCAL 1.0.0 support.

Pre OSCAL 1.0.0 release ([`797a291`](https://github.com/oscal-compass/compliance-trestle/commit/797a2918dbbe4771ae950364c560c4561216b011))

## v0.17.0 (2021-06-09)

### Chore

* chore: Correct expression path.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`9378863`](https://github.com/oscal-compass/compliance-trestle/commit/9378863861270f67fe16d6a6e4891d2856a55878))

* chore: readding comments.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`4a45cff`](https://github.com/oscal-compass/compliance-trestle/commit/4a45cff3485039681643ba7eb52f3a41a5ff739f))

* chore: CICD refinements

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`c09119c`](https://github.com/oscal-compass/compliance-trestle/commit/c09119ce80c38b4d4d966e80a420ef7e0731131c))

* chore: Merge back version tags and changelog into develop. ([`2f88d60`](https://github.com/oscal-compass/compliance-trestle/commit/2f88d60d0f599778d5005c636c7a404c385c0071))

### Feature

* feat: ssp generation of markdown files for groups of controls (#556)

* added ssp_generator and test

Signed-off-by: FrankSuits &lt;frankst@au1.ibm.com&gt;

* added section output and separate file for md_writer

Signed-off-by: FrankSuits &lt;frankst@au1.ibm.com&gt;

* ssp now a command and improved tests

Signed-off-by: FrankSuits &lt;frankst@au1.ibm.com&gt;

* added docs for ssp

Signed-off-by: FrankSuits &lt;frankst@au1.ibm.com&gt;

* clean up and boost coverage

Signed-off-by: FrankSuits &lt;frankst@au1.ibm.com&gt;

* added comments

Signed-off-by: FrankSuits &lt;frankst@au1.ibm.com&gt;

* initial ssp creation

Signed-off-by: FrankSuits &lt;frankst@au1.ibm.com&gt;

* now output ssp json

Signed-off-by: FrankSuits &lt;frankst@au1.ibm.com&gt;

* made requested changes for ssp generation

Signed-off-by: FrankSuits &lt;frankst@au1.ibm.com&gt;

* changed add to get in func name

Signed-off-by: FrankSuits &lt;frankst@au1.ibm.com&gt;

* split ssp into ssp-generate and ssp-assemble

Signed-off-by: FrankSuits &lt;frankst@au1.ibm.com&gt; ([`1dcf139`](https://github.com/oscal-compass/compliance-trestle/commit/1dcf1395469b20b32e67c02cc52ede15d5b35f4b))

* feat: Update `trestle md` to `trestle author` and introduce functionality for validating drawio metadata. (#551)

* feat: renamed md to author to prepare for drawio content

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix: Ensure mkdocs must update successfully

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* hello

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* chore: reorganisation of code to clean up

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* chore: Cleanup of the codebase as exists to meet formatting / linting.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* chore: More cleanup

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix: Significant cleanups of markdown (now author) codebase.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* chore: Code formatting was missing.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix: Add missing test files

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* feat: Finish basic implementation of header validation

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* Cleanup documentation

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* feat: Added documentation for author and enforce utf-8 everywhere

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* chore: Complete unit testing for author headers

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix: Added missing unit tests for DrawIOMetadataValidator

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix: Adding more unit tests.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix: Corrected drawio behaviour where it was not raising an exception

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix: Additional fixes

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* Added missing dependencies

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* adding utility functions

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix: Removed google analytics which no longer is supported.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix: Cleaned up reporting

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* chore: Small documentation updates.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`2567e6c`](https://github.com/oscal-compass/compliance-trestle/commit/2567e6c55039ce4b2db0d76fb4ae3c7495a26301))

### Fix

* fix: Lint PR firing off dev (#562)

* fix Lint PR firing off dev

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix: Added small set of updates

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`81f44c6`](https://github.com/oscal-compass/compliance-trestle/commit/81f44c628d687ab4f0d96b9c16d018459e9fc062))

* fix: [ImgBot] Optimize images (#560)

*Total -- 1,247.86kb -&gt; 604.94kb (51.52%)

/docs/assets/drawio_editing_data.png -- 558.20kb -&gt; 257.90kb (53.8%)
/docs/assets/drawio_data_menu.png -- 663.19kb -&gt; 321.66kb (51.5%)
/docs/tutorials/continuous-compliance/ContinuousCompliance.jpg -- 26.46kb -&gt; 25.38kb (4.11%)

Signed-off-by: ImgBotApp &lt;ImgBotHelp@gmail.com&gt;

Co-authored-by: ImgBotApp &lt;ImgBotHelp@gmail.com&gt; ([`62b870d`](https://github.com/oscal-compass/compliance-trestle/commit/62b870d3d98bf2a67be2c7fc68b0cf9e8d4b7f07))

* fix: Allow for check suite to trigger a PR

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`5c95318`](https://github.com/oscal-compass/compliance-trestle/commit/5c95318f8c43b6901d0992512e029d2aa584a73c))

* fix: Allow for check suite to trigger a PR

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`9bce041`](https://github.com/oscal-compass/compliance-trestle/commit/9bce041a02326d9e148ada7271eda5dbda46e504))

* fix: Allow for test completion to trigger automerge correctly

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`dc6864f`](https://github.com/oscal-compass/compliance-trestle/commit/dc6864f8a3bc03ec1f694d25dbeda19969507ab9))

* fix: correct github expression path.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`9ab4936`](https://github.com/oscal-compass/compliance-trestle/commit/9ab4936dc0aef7d4b2bd445dd4d8f1e3a13c6f9b))

* fix: Ensrue automerge fires off correctly

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`d0f51b8`](https://github.com/oscal-compass/compliance-trestle/commit/d0f51b841073d06269272f2e5f5a7f04bb07bc3a))

* fix: CICD refinements

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`a2d836b`](https://github.com/oscal-compass/compliance-trestle/commit/a2d836bc8e29d6cbe16346ed4172e258546e1196))

* fix: Dump context in automerge workflow.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`144a54f`](https://github.com/oscal-compass/compliance-trestle/commit/144a54f8ef51252b4a4fec6117e85b388cd69b17))

* fix: Cleanup CIDC workflow to prevent admin rights pushing over checks.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`56127e7`](https://github.com/oscal-compass/compliance-trestle/commit/56127e733dc0539d36e3faf32be1c3be701da1d8))

* fix: Cleanup CIDC workflow to prevent admin rights pushing over checks.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`a305ebb`](https://github.com/oscal-compass/compliance-trestle/commit/a305ebb24c8595a0014afe1d6da5886400f1211b))

* fix: Cleanup CIDC workflow to prevent admin rights pushing over checks.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`31e8cde`](https://github.com/oscal-compass/compliance-trestle/commit/31e8cde6b68009372a7dcf9562dc6e420ecec6d2))

### Unknown

* Merge pull request #561 from IBM/develop ([`da34485`](https://github.com/oscal-compass/compliance-trestle/commit/da344851f6b373e19f900899c64f147eb08d7ff9))

* Merge pull request #552 from IBM/fix/cicd_cleanup ([`48d537b`](https://github.com/oscal-compass/compliance-trestle/commit/48d537bedc40f5127dba008f72fc63e5b4897457))

* Merge branch &#39;develop&#39; into fix/cicd_cleanup ([`7b099c6`](https://github.com/oscal-compass/compliance-trestle/commit/7b099c65a8843fb33aaf9a89d7c0f6081c54fda2))

## v0.16.0 (2021-05-28)

### Chore

* chore: Merge back version tags and changelog into develop. ([`a463460`](https://github.com/oscal-compass/compliance-trestle/commit/a46346082a8c98d85354fcb0e51b0c63d9d60b0f))

### Feature

* feat: OSCO transformer conform to Results interface class. (#532) ([`fc251b9`](https://github.com/oscal-compass/compliance-trestle/commit/fc251b9e9c231de67fd214b16bdd7c2a6cb4d3c1))

### Fix

* fix: move unreachable debug statement

Signed-off-by: Doug Chivers &lt;doug.chivers@uk.ibm.com&gt; ([`f5b9c1a`](https://github.com/oscal-compass/compliance-trestle/commit/f5b9c1a029e6257c789ebc573105b582dca23e1b))

* fix: move unreachable debug statement ([`0ce9c24`](https://github.com/oscal-compass/compliance-trestle/commit/0ce9c24a8fcc5e464f4194970e82740e6c0cd4f1))

* fix: Complete coverage of drawio class

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`225403c`](https://github.com/oscal-compass/compliance-trestle/commit/225403c4f85ca77cb322bb9620992ab0c6673e9b))

* fix: Adding basic UT suite for drawio.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`44cc8c3`](https://github.com/oscal-compass/compliance-trestle/commit/44cc8c3fcb57bb23743fbe12d5bc180bf13edab5))

* fix: Corrected errors

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`8187d6d`](https://github.com/oscal-compass/compliance-trestle/commit/8187d6d5932669dddd676e68c24fe0d058703d52))

* fix: correcting errors

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`5bfedac`](https://github.com/oscal-compass/compliance-trestle/commit/5bfedac6575d3e57ea530b0e69e55ebbcbb26c37))

* fix: improve devops to stop squash merging to main (#542) ([`a8313fb`](https://github.com/oscal-compass/compliance-trestle/commit/a8313fbf75b8c8eb5d2791b2dadafc1be03cc492))

### Unknown

* Merge pull request #550 from IBM/develop ([`736d2d4`](https://github.com/oscal-compass/compliance-trestle/commit/736d2d4130210a571eacf36a24403b4a26c570e5))

* Merge pull request #549 from IBM/fix/split_roles ([`11add07`](https://github.com/oscal-compass/compliance-trestle/commit/11add074c00c9d96dbe8a493976e61e55961624c))

* fixed incorrect comment line

Signed-off-by: FrankSuits &lt;frankst@au1.ibm.com&gt; ([`0ccd64e`](https://github.com/oscal-compass/compliance-trestle/commit/0ccd64ef75d79a7e088fc16e39397bba3c452a19))

* fix to bug splitting roles and compdefs.  Better handling of lists and dicts in splits

Signed-off-by: FrankSuits &lt;frankst@au1.ibm.com&gt; ([`d17a8f9`](https://github.com/oscal-compass/compliance-trestle/commit/d17a8f94447494dfb523a75c04a0d06f89d234fe))

* Merge pull request #539 from IBM/feat/drawio-metadata ([`20b848b`](https://github.com/oscal-compass/compliance-trestle/commit/20b848b903e529dec99177163220a4aa7e23624f))

* Merge develop into feat/drawio-metadata ([`f47d7a6`](https://github.com/oscal-compass/compliance-trestle/commit/f47d7a65a62c54f0a54ced213d73db596d5d5bbb))

* Merge pull request #546 from IBM/fix/split-debug-txt ([`e98af5e`](https://github.com/oscal-compass/compliance-trestle/commit/e98af5e18a452079db7fbca65731122df3029e69))

* move unreachable debug statement ([`b104a3d`](https://github.com/oscal-compass/compliance-trestle/commit/b104a3d4a30952615bbfe906e3a42dc03aa9c07f))

* Merge branch &#39;develop&#39; into feat/drawio-metadata ([`265cb91`](https://github.com/oscal-compass/compliance-trestle/commit/265cb91a89ee681f0701659c91d19bbf95120e3c))

* Merge branch &#39;develop&#39; into feat/drawio-metadata ([`7278618`](https://github.com/oscal-compass/compliance-trestle/commit/72786181d8b00a536b1e98d0ba34ce6f5f919c47))

## v0.15.1 (2021-05-20)

### Chore

* chore: Release to main to update documentation (#537) ([`ecd5a58`](https://github.com/oscal-compass/compliance-trestle/commit/ecd5a589f82e1c8cc2d8fb576ab413643c88f5f7))

* chore: clean bad data files and improve all_validator feedback (#536) ([`2cb9d7c`](https://github.com/oscal-compass/compliance-trestle/commit/2cb9d7ceb093b1071cbd2184d6191aa07a49f3bd))

* chore: update tools and models for 914 (#534) ([`163043f`](https://github.com/oscal-compass/compliance-trestle/commit/163043fa6837ded959a63f3de13c0cac12022b80))

* chore: Added drawio UTs

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`56aabeb`](https://github.com/oscal-compass/compliance-trestle/commit/56aabeb427962c450c0252653d42f0a9de7555e8))

* chore: Updated some docs to trigger a PR (#523)

* chore: Updated some docs to trigger a PR

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix: there is a mistake in the workflow syntax

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`6c4ad8c`](https://github.com/oscal-compass/compliance-trestle/commit/6c4ad8cefd7e3b6b69f4838611eec0ccdcb20f01))

* chore: Clean up PR automation (#521)

* chore: DevOps automation for PRs

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* Experiment with pr helper

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* Experiment with pr helper

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* chore: cleanup CICD pipelines to help remove duplication

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* chore: cleanup CICD pipelines to help remove duplication

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* chore: cleanup CICD pipelines to help remove duplication

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* chore: cleanup CICD pipelines to help remove duplication

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix: Specify explicitly action versions

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix: revised filtering to decrease the number of runs

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`35ce91a`](https://github.com/oscal-compass/compliance-trestle/commit/35ce91a65543255ce053633ade0543bfcdf02223))

* chore: CICD improvements (#518)

* chore: DevOps automation for PRs

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* chore: DevOps automation for PRs

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* Added cache to github actions to accelerate workflow.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* Added cache to github actions to accelerate workflow.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* chore: change versions

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* chore: change versions

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* Clean up build process

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix: Conventional PR

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix: Conventional PR

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix: Conventional PR

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix: Change automerge tooling

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix: Change automerge tooling

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* Experiment with pr helper

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* Experiment with pr helper

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* Experiment with pr helper

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* Experiment with pr helper

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* Experiment with pr helper

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* Experiment with pr helper

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`64c95cd`](https://github.com/oscal-compass/compliance-trestle/commit/64c95cd21816919d702aac72863e89f5d020c007))

* chore: Merge back version tags and changelog into develop. ([`4d0acd4`](https://github.com/oscal-compass/compliance-trestle/commit/4d0acd466cd82d370c0e018f4f1d05e7bc303c45))

### Documentation

* docs: Reorg and cleanup content (#531) ([`380e924`](https://github.com/oscal-compass/compliance-trestle/commit/380e92476ff63126df470f31a4e8e0190e608fad))

* docs: Updated third party schema as per latest tanium to oscal conversion and added it to documentation (#527) ([`9feb690`](https://github.com/oscal-compass/compliance-trestle/commit/9feb6908c80c3873cf310079144fbbbe20002c54))

* docs: More google style doc strings (#526) ([`28914f0`](https://github.com/oscal-compass/compliance-trestle/commit/28914f088a78b57fdfb090eda662ea5c8b362884))

* docs: Addtional documentation. (#525) ([`516f01e`](https://github.com/oscal-compass/compliance-trestle/commit/516f01eb0eff580bcfc95ea7b0909cd0ebdb8221))

* docs: Small set of document updates (#524)

* docs: Small set of document updates

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix: Update again

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix: more cleaning and error logging

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`7b339d7`](https://github.com/oscal-compass/compliance-trestle/commit/7b339d7e81d0a2e626bc29c7718d0e1081996fbb))

### Feature

* feat: functionaly complete

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`b7c903b`](https://github.com/oscal-compass/compliance-trestle/commit/b7c903b703c78026ac14e31177cd4e3a7541d469))

* feat: oscal version validator (#528) ([`2b132d5`](https://github.com/oscal-compass/compliance-trestle/commit/2b132d5f09832452def258284bb40090d32bab01))

* feat: create title  - place names in title of created objects - issue #473 (#519)

* upgrade pydantic to 1.8.2 for security issue

Signed-off-by: FrankSuits &lt;frankst@au1.ibm.com&gt;

* Simple change to insert model name in created objects.

Signed-off-by: FrankSuits &lt;frankst@au1.ibm.com&gt;

Co-authored-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`b676ed3`](https://github.com/oscal-compass/compliance-trestle/commit/b676ed379b4328f3b69fe1806a7dad46ccc5319a))

### Fix

* fix: Trigger release (#540) ([`aeffa5b`](https://github.com/oscal-compass/compliance-trestle/commit/aeffa5b5aa1609b23fdbfed7d167068e366f72e9))

* fix: Remove problematic concurrency restrictions in devops pipeline (#538) ([`5181c70`](https://github.com/oscal-compass/compliance-trestle/commit/5181c70b44e283a21b4fedb05ecc36590d04c319))

* fix: stop split at strings, better handling of component-def splits (#506) ([`43c9edd`](https://github.com/oscal-compass/compliance-trestle/commit/43c9edd790579a7000a444a703b2d30a485480d1))

* fix: Correct bad syntax in devops tooling. ([`dcec2ea`](https://github.com/oscal-compass/compliance-trestle/commit/dcec2eaeacff7e7ad981e801255c844a37446390))

* fix: Ensure PR automation system cannot override checks. (#522)

* chore: DevOps automation for PRs

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* Experiment with pr helper

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* Experiment with pr helper

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* chore: cleanup CICD pipelines to help remove duplication

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* chore: cleanup CICD pipelines to help remove duplication

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* chore: cleanup CICD pipelines to help remove duplication

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* chore: cleanup CICD pipelines to help remove duplication

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix: Specify explicitly action versions

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix: revised filtering to decrease the number of runs

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix: TSetting up automerge that respects permissions

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix: TSetting up automerge that respects permissions

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix: Remove aconcurrency restriction from matrix build jobs.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix: Remove aconcurrency restriction from matrix build jobs.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix: Remove aconcurrency restriction from matrix build jobs.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`5817316`](https://github.com/oscal-compass/compliance-trestle/commit/5817316ff06cecba6b3662b96cb77655aa70277b))

* fix: Correct semantic / conventional commit behaviour (#520)

* chore: DevOps automation for PRs

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* Experiment with pr helper

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* Experiment with pr helper

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`a6f7d01`](https://github.com/oscal-compass/compliance-trestle/commit/a6f7d013998e0a198347d987558f7974e372b5ea))

### Unknown

* Merge branch &#39;main&#39; into develop ([`8aa6b82`](https://github.com/oscal-compass/compliance-trestle/commit/8aa6b828bfaaf9f9bceb50da13de271a7d3b954b))

## v0.15.0 (2021-05-13)

### Chore

* chore: Merge back version tags and changelog into develop. ([`d6cf057`](https://github.com/oscal-compass/compliance-trestle/commit/d6cf0576e4408d349f0a156e4e0d70ff76f60378))

### Feature

* feat: Added error checking and enforce 1 to 1 keys in header validation (#512)

* added error checking and enforce 1 to 1 keys in yaml validation

Signed-off-by: FrankSuits &lt;frankst@au1.ibm.com&gt;

* added test

Signed-off-by: FrankSuits &lt;frankst@au1.ibm.com&gt;

* key test

Signed-off-by: FrankSuits &lt;frankst@au1.ibm.com&gt;

* added header-only validation

Signed-off-by: FrankSuits &lt;frankst@au1.ibm.com&gt;

* header validation for gov folders

Signed-off-by: FrankSuits &lt;frankst@au1.ibm.com&gt;

* added dir recursion for gov header validate

Signed-off-by: FrankSuits &lt;frankst@au1.ibm.com&gt; ([`da95862`](https://github.com/oscal-compass/compliance-trestle/commit/da958620ffca76cbfae1762159a7ca51007c8b88))

* feat: Role ID cross reference validator and refactors to validators to allow all

* added role id refs validation and refactored validators

Signed-off-by: FrankSuits &lt;frankst@au1.ibm.com&gt;

* renamed and added validator files

Signed-off-by: FrankSuits &lt;frankst@au1.ibm.com&gt;

* added check for item name and made roleid name more consistent

Signed-off-by: FrankSuits &lt;frankst@au1.ibm.com&gt;

* removed -item validator option, added all validator, import now validates all

Signed-off-by: FrankSuits &lt;frankst@au1.ibm.com&gt; ([`c894704`](https://github.com/oscal-compass/compliance-trestle/commit/c894704875ae54e8376fb50d62cd064f1d293b66))

* feat: Roleid validation via ncname and parametrized tests (#499)

Signed-off-by: FrankSuits &lt;frankst@au1.ibm.com&gt;

Co-authored-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`84dc9a2`](https://github.com/oscal-compass/compliance-trestle/commit/84dc9a293e35f1c4010a38c7ecc8f99e5fa7dfb2))

### Fix

* fix: Upgrade pydantic to 1.8.2 for security issue (#513)

* upgrade pydantic to 1.8.2 for security issue

Signed-off-by: FrankSuits &lt;frankst@au1.ibm.com&gt;

* Constrain markupsafe to the correct version

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* Constrain markupsafe to the correct version

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* Constrain markupsafe to the correct version

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

Co-authored-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`6e01f36`](https://github.com/oscal-compass/compliance-trestle/commit/6e01f36cc6fdfd8b14d453f470968ad7ea4164fa))

* fix: Remove problematic code-QL plugin which is causing problems. (#507)

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`47529a7`](https://github.com/oscal-compass/compliance-trestle/commit/47529a7714f0c99bb711033ca1863651de99dbf5))

### Unknown

* Merge pull request #517 from IBM/develop

Release: Security update and gov header only scanning. ([`da99cfe`](https://github.com/oscal-compass/compliance-trestle/commit/da99cfe0b3a769eba3ec6fdb0ad2e3d63aa9d72d))

* feat:Tanium converged format updated to IBM SCC format (#515)

* Tanium converged format

Signed-off-by: Lou DeGenaro &lt;degenaro@li-dd41d84c-35a5-11b2-a85c-eb5d345ed15a.ibm.com&gt;

* Revise doc.

Signed-off-by: Lou DeGenaro &lt;degenaro@li-dd41d84c-35a5-11b2-a85c-eb5d345ed15a.ibm.com&gt;

* fix: Upgrade pydantic to 1.8.2 for security issue (#513)

* upgrade pydantic to 1.8.2 for security issue

Signed-off-by: FrankSuits &lt;frankst@au1.ibm.com&gt;

* Constrain markupsafe to the correct version

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* Constrain markupsafe to the correct version

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* Constrain markupsafe to the correct version

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

Co-authored-by: Chris Butler &lt;chris@thebutlers.me&gt;
Signed-off-by: Lou DeGenaro &lt;degenaro@li-dd41d84c-35a5-11b2-a85c-eb5d345ed15a.ibm.com&gt;

Co-authored-by: degenaro &lt;degenaro@localhost&gt;
Co-authored-by: Frank Suits &lt;47203786+fsuits@users.noreply.github.com&gt;
Co-authored-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`b2b0db6`](https://github.com/oscal-compass/compliance-trestle/commit/b2b0db6584f985b0c0d634f08c43e835b41e6a6b))

## v0.14.4 (2021-04-22)

### Chore

* chore: Merge back version tags and changelog into develop. ([`6c5e7b1`](https://github.com/oscal-compass/compliance-trestle/commit/6c5e7b1ef8dbf1b8e17c1fdf2ebf64c605779fcb))

### Fix

* fix: Add timestamp to tanium-to-oscal transformer (#503)

* Feat/tanium scc (#493)

* Tanium transformer revisions

- add add components
- change namespace
- use agreed upon class identifiers and remove others
- use statement-id
- add end time
- list controls in verbose mode
- manage &#34;pocket&#34; for missing computer-name

* Update tanium-to-oscal tutorial

Co-authored-by: Frank Suits &lt;47203786+fsuits@users.noreply.github.com&gt;

* Feat/tanium scc 2 (#497)

* Tanium transformer revisions

- add add components
- change namespace
- use agreed upon class identifiers and remove others
- use statement-id
- add end time
- list controls in verbose mode
- manage &#34;pocket&#34; for missing computer-name

* Update tanium-to-oscal tutorial

Co-authored-by: degenaro &lt;lou.degenaro@gmail.com&gt;

* Feat/tanium observation timestamp (#502)

* Add timestamp property to each observation.

* Add timestamp property to each observation.

* Update tutorial to include timestamp property.

Co-authored-by: Chris Butler &lt;chris@thebutlers.me&gt;
Co-authored-by: degenaro &lt;lou.degenaro@gmail.com&gt; ([`e8dc204`](https://github.com/oscal-compass/compliance-trestle/commit/e8dc204935b5d1f4584bcaaef77bba2c41d80a9f))

### Unknown

* Feat/tanium observation timestamp (#502)

* Add timestamp property to each observation.

* Add timestamp property to each observation.

* Update tutorial to include timestamp property. ([`688bc35`](https://github.com/oscal-compass/compliance-trestle/commit/688bc350f0afba47a3122a18fe66304d2732eaff))

## v0.14.3 (2021-04-20)

### Chore

* chore: Merge back version tags and changelog into develop. ([`17cd61c`](https://github.com/oscal-compass/compliance-trestle/commit/17cd61c3a8d024af06b7620fffb61e51c40c37a9))

### Fix

* fix: tanium updates for scc, 2 (#498)

* Feat/tanium scc (#493)

* Tanium transformer revisions

- add add components
- change namespace
- use agreed upon class identifiers and remove others
- use statement-id
- add end time
- list controls in verbose mode
- manage &#34;pocket&#34; for missing computer-name

* Update tanium-to-oscal tutorial

Co-authored-by: Frank Suits &lt;47203786+fsuits@users.noreply.github.com&gt;

* Feat/tanium scc 2 (#497)

* Tanium transformer revisions

- add add components
- change namespace
- use agreed upon class identifiers and remove others
- use statement-id
- add end time
- list controls in verbose mode
- manage &#34;pocket&#34; for missing computer-name

* Update tanium-to-oscal tutorial

Co-authored-by: degenaro &lt;lou.degenaro@gmail.com&gt;

Co-authored-by: Chris Butler &lt;chris@thebutlers.me&gt;
Co-authored-by: degenaro &lt;lou.degenaro@gmail.com&gt; ([`9b9b61e`](https://github.com/oscal-compass/compliance-trestle/commit/9b9b61e6236da2f15cd6fc125925c6e4e708465f))

### Unknown

* Feat/tanium scc 2 (#497)

* Tanium transformer revisions

- add add components
- change namespace
- use agreed upon class identifiers and remove others
- use statement-id
- add end time
- list controls in verbose mode
- manage &#34;pocket&#34; for missing computer-name

* Update tanium-to-oscal tutorial

Co-authored-by: degenaro &lt;lou.degenaro@gmail.com&gt; ([`bd12c27`](https://github.com/oscal-compass/compliance-trestle/commit/bd12c274afd30aab55ca41afcad3ed37da5f52e3))

## v0.14.2 (2021-04-20)

### Chore

* chore: Merge back version tags and changelog into develop. ([`2ce5be2`](https://github.com/oscal-compass/compliance-trestle/commit/2ce5be2a1a0469bf4ec0e77acabf84e29ff6c6fa))

* chore: Merge back version tags and changelog into develop. ([`76092cd`](https://github.com/oscal-compass/compliance-trestle/commit/76092cd547ff82cb2d33f882319dd509d5778242))

* chore: Merge back version tags and changelog into develop. ([`1956a42`](https://github.com/oscal-compass/compliance-trestle/commit/1956a426896aca92aa2e7688c9f41b9f1ae4086b))

### Fix

* fix: tanium enhancements for scc

* Tanium transformer revisions

- add add components
- change namespace
- use agreed upon class identifiers and remove others
- use statement-id
- add end time
- list controls in verbose mode
- manage &#34;pocket&#34; for missing computer-name

* Update tanium-to-oscal tutorial

Co-authored-by: Frank Suits &lt;47203786+fsuits@users.noreply.github.com&gt;

Co-authored-by: Chris Butler &lt;chris@thebutlers.me&gt;
Co-authored-by: degenaro &lt;lou.degenaro@gmail.com&gt; ([`8bae421`](https://github.com/oscal-compass/compliance-trestle/commit/8bae421df04a7683bccc52ea40420bb85d4bcebe))

### Unknown

* Revert &#34;Feat/tanium scc (#493) (#494)&#34; (#495)

This reverts commit 98109ce27e4a9ff4917ba7bcb99790ed02a58963. ([`7ccaf35`](https://github.com/oscal-compass/compliance-trestle/commit/7ccaf3568da532066b02c31e7050ca265d6dde58))

* Feat/tanium scc (#493) (#494)

* Tanium transformer revisions

- add add components
- change namespace
- use agreed upon class identifiers and remove others
- use statement-id
- add end time
- list controls in verbose mode
- manage &#34;pocket&#34; for missing computer-name

* Update tanium-to-oscal tutorial

Co-authored-by: Frank Suits &lt;47203786+fsuits@users.noreply.github.com&gt;

Co-authored-by: Chris Butler &lt;chris@thebutlers.me&gt;
Co-authored-by: degenaro &lt;lou.degenaro@gmail.com&gt; ([`98109ce`](https://github.com/oscal-compass/compliance-trestle/commit/98109ce27e4a9ff4917ba7bcb99790ed02a58963))

* Feat/tanium scc (#493)

* Tanium transformer revisions

- add add components
- change namespace
- use agreed upon class identifiers and remove others
- use statement-id
- add end time
- list controls in verbose mode
- manage &#34;pocket&#34; for missing computer-name

* Update tanium-to-oscal tutorial

Co-authored-by: Frank Suits &lt;47203786+fsuits@users.noreply.github.com&gt; ([`264966c`](https://github.com/oscal-compass/compliance-trestle/commit/264966c2b8b20da315179fbf9cee5dd13aefb3ed))

## v0.14.1 (2021-04-16)

### Chore

* chore: Merge back version tags and changelog into develop. ([`840c73a`](https://github.com/oscal-compass/compliance-trestle/commit/840c73a6edec203b7dd35bac804b098469e68f41))

### Fix

* fix: Chore/fs cleanup (#489)

* cleanup of fs.py to allow relative and absolute paths

Signed-off-by: FrankSuits &lt;frankst@au1.ibm.com&gt;

* global change of absolute() to resolve()

Signed-off-by: FrankSuits &lt;frankst@au1.ibm.com&gt;

* added debug lines and exception handling

Signed-off-by: FrankSuits &lt;frankst@au1.ibm.com&gt;

* better resolve handling, updated docs, silenced stack trace, added debug lines

Signed-off-by: FrankSuits &lt;frankst@au1.ibm.com&gt;

* fixed docs typos

Signed-off-by: FrankSuits &lt;frankst@au1.ibm.com&gt; ([`bf8be03`](https://github.com/oscal-compass/compliance-trestle/commit/bf8be03fc62e56928e8f92cfe746b004e0c54b71))

### Unknown

* Merge pull request #492 from IBM/develop

Release to main: essential fixes to file IO ([`6be5246`](https://github.com/oscal-compass/compliance-trestle/commit/6be5246b530a6613f7af8cf5ad1ba689d8806f0b))

## v0.14.0 (2021-04-15)

### Chore

* chore: Update pre-commit markdown formatting (#476)

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`89946e6`](https://github.com/oscal-compass/compliance-trestle/commit/89946e6458958343193f0d66f6af94d5b38ef69e))

* chore: Merge back version tags and changelog into develop. ([`c31cfa0`](https://github.com/oscal-compass/compliance-trestle/commit/c31cfa07b868cdff44ec125b6bcdde6bf5dd5f96))

### Feature

* feat: Release of enhanced markdown functionality ([`f327fd6`](https://github.com/oscal-compass/compliance-trestle/commit/f327fd67131c90afbe6c3644ab41b0dc56412b78))

* feat: Assessment result schema updates(#481)

* changed print to logger

* Added experiments profiling setup

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* added flah to benchmark with or without json serialization

* readme file for assessment. result object

* changed prinet to logger

Signed-off-by: Vikas &lt;avikas@in.ibm.com&gt;

* feat: Update NIST models to latest including refactors &amp; UT&#39;s

* feat:Update Oscal version

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* transformer changes with respect to OSCAL 1.0.0 rc2

* update documentation (transform results)

* multiple changes for latest nist - some tests still fail

Signed-off-by: FrankSuits &lt;frankst@au1.ibm.com&gt;

* removed ssp validate test

Signed-off-by: FrankSuits &lt;frankst@au1.ibm.com&gt;

* fixed code format

Signed-off-by: FrankSuits &lt;frankst@au1.ibm.com&gt;

* fix:Reworking generators

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* cleaned up gen-oscal.py and regenerated the oscal models.

Signed-off-by: FrankSuits &lt;frankst@au1.ibm.com&gt;

Co-authored-by: Chris Butler &lt;chris@thebutlers.me&gt;
Co-authored-by: degenaro &lt;lou.degenaro@gmail.com&gt;
Signed-off-by: Vikas &lt;avikas@in.ibm.com&gt;

* 0.11.0

Automatically generated by python-semantic-release

Signed-off-by: Vikas &lt;avikas@in.ibm.com&gt;

* feat:Improved serialisation support for OscalBaseModel (#454)

* feat:Improved serialization support.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix:Serializing by appropriate key and minimizing file size.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;
Signed-off-by: Vikas &lt;avikas@in.ibm.com&gt;

* Feat:transformer factory (#455)

* initial prototype of transformer factory

Signed-off-by: FrankSuits &lt;frankst@au1.ibm.com&gt;

* added singleton transformer factory

Signed-off-by: FrankSuits &lt;frankst@au1.ibm.com&gt;

* added base transformer class

Signed-off-by: FrankSuits &lt;frankst@au1.ibm.com&gt;

* more fixes and added tests

Signed-off-by: FrankSuits &lt;frankst@au1.ibm.com&gt;

* added test for transform factory

Signed-off-by: FrankSuits &lt;frankst@au1.ibm.com&gt;

* restructured, added more docs and tests.

Signed-off-by: FrankSuits &lt;frankst@au1.ibm.com&gt;

* removed bad file names.

Signed-off-by: FrankSuits &lt;frankst@au1.ibm.com&gt;

* fix:Typing information

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

Co-authored-by: Chris Butler &lt;chris@thebutlers.me&gt;
Signed-off-by: Vikas &lt;avikas@in.ibm.com&gt;

* 0.12.0

Automatically generated by python-semantic-release

Signed-off-by: Vikas &lt;avikas@in.ibm.com&gt;

* Added experiments profiling setup

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;
Signed-off-by: Vikas &lt;avikas@in.ibm.com&gt;

* added flah to benchmark with or without json serialization

Signed-off-by: Vikas &lt;avikas@in.ibm.com&gt;

* readme file for assessment. result object

Signed-off-by: Vikas &lt;avikas@in.ibm.com&gt;

* feat: Update of OSCAL schema to 1.0.0-rc2 (#465)

* feat:Update core OSCAL schema

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix:Corrected OSCAL version in the docs

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;
Signed-off-by: Vikas &lt;avikas@in.ibm.com&gt;

* fix: Cleanup of fs.py to allow relative and absolute paths (#464)

* cleanup of fs.py to allow relative and absolute paths

Signed-off-by: FrankSuits &lt;frankst@au1.ibm.com&gt;

* global change of absolute() to resolve()

Signed-off-by: FrankSuits &lt;frankst@au1.ibm.com&gt;

Co-authored-by: Chris Butler &lt;chris@thebutlers.me&gt;
Signed-off-by: Vikas &lt;avikas@in.ibm.com&gt;

* feat: Tanium to oscal tranform refactored to exploit the ResultsTransformer interface (#466)

* ResultsTransformer interface

* remove trestle.utils.tanium

* remove trestle.utils.tanium.py

* added registration of tanium transformer

Signed-off-by: FrankSuits &lt;frankst@au1.ibm.com&gt;

* added name for registration

Signed-off-by: FrankSuits &lt;frankst@au1.ibm.com&gt;

Co-authored-by: Chris Butler &lt;chris@thebutlers.me&gt;
Co-authored-by: FrankSuits &lt;frankst@au1.ibm.com&gt;
Signed-off-by: Vikas &lt;avikas@in.ibm.com&gt;

* 0.13.0

Automatically generated by python-semantic-release

Signed-off-by: Vikas &lt;avikas@in.ibm.com&gt;

* fix:Corrected transforms behaviour and added example script. (#468)

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;
Signed-off-by: Vikas &lt;avikas@in.ibm.com&gt;

* 0.13.1

Automatically generated by python-semantic-release

Signed-off-by: Vikas &lt;avikas@in.ibm.com&gt;

* chore: Update pre-commit markdown formatting (#476)

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;
Signed-off-by: Vikas &lt;avikas@in.ibm.com&gt;

* fix:Moved directories to fix testing errors.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix:Moved directories to fix testing errors.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* chnaged benchmark to use transform API

* removed script reslted to thrid party - exchange protocol, observations and their tests

* fix:Perf tuning of OscalBaseModel serialization.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix:Mkdocs automation

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix:Mkdocs automation

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

Co-authored-by: Vikas &lt;avikas@in.ibm.com&gt;
Co-authored-by: Chris Butler &lt;chris@thebutlers.me&gt;
Co-authored-by: Frank Suits &lt;47203786+fsuits@users.noreply.github.com&gt;
Co-authored-by: degenaro &lt;lou.degenaro@gmail.com&gt;
Co-authored-by: semantic-release &lt;semantic-release&gt;
Co-authored-by: FrankSuits &lt;frankst@au1.ibm.com&gt; ([`0f5c4ee`](https://github.com/oscal-compass/compliance-trestle/commit/0f5c4eedb0eaa1afcc2f11cfca026e840cbfac37))

* feat: trestle markdown updates (#477)

* chore: Commit for merge workflow

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix: Adding more unit tests.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix: Adding more unit tests and documentation.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`ddc2420`](https://github.com/oscal-compass/compliance-trestle/commit/ddc2420ff71dae6fcb6597654d69dbd16fba8cb6))

## v0.13.1 (2021-04-13)

### Chore

* chore: Merge back version tags and changelog into develop. ([`10d6634`](https://github.com/oscal-compass/compliance-trestle/commit/10d663499c617fdea797e5d92810bcc0b55e5ec5))

* chore: Merge back version tags and changelog into develop. ([`7dd62f4`](https://github.com/oscal-compass/compliance-trestle/commit/7dd62f4ca10fc7f4f2e21411741e3ffb1d827508))

### Fix

* fix: Force release.

fix: Force release ([`0e90265`](https://github.com/oscal-compass/compliance-trestle/commit/0e90265c7192979a613c30abd3561a68b612d8ac))

### Unknown

* Minor release: Fix behaviour of trestle transforms

Minor release: Fix behaviour of trestle transforms ([`02d23b5`](https://github.com/oscal-compass/compliance-trestle/commit/02d23b5ed0a7e68c8b3a74cc8b50e1fe76ba8315))

* fix:Corrected transforms behaviour and added example script. (#468)

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`7f05800`](https://github.com/oscal-compass/compliance-trestle/commit/7f0580042842663f39c8c221a890c6e77ac700da))

## v0.13.0 (2021-04-13)

### Chore

* chore: Merge back version tags and changelog into develop. ([`78fc812`](https://github.com/oscal-compass/compliance-trestle/commit/78fc812965797e676629c8afde132011a4abd94b))

### Feature

* feat: Tanium to oscal tranform refactored to exploit the ResultsTransformer interface (#466)

* ResultsTransformer interface

* remove trestle.utils.tanium

* remove trestle.utils.tanium.py

* added registration of tanium transformer

Signed-off-by: FrankSuits &lt;frankst@au1.ibm.com&gt;

* added name for registration

Signed-off-by: FrankSuits &lt;frankst@au1.ibm.com&gt;

Co-authored-by: Chris Butler &lt;chris@thebutlers.me&gt;
Co-authored-by: FrankSuits &lt;frankst@au1.ibm.com&gt; ([`6fced57`](https://github.com/oscal-compass/compliance-trestle/commit/6fced57a5c011aafb26220e94b038ebae884b20d))

* feat: Update of OSCAL schema to 1.0.0-rc2 (#465)

* feat:Update core OSCAL schema

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix:Corrected OSCAL version in the docs

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`4e2f64d`](https://github.com/oscal-compass/compliance-trestle/commit/4e2f64dd5a4f80f4081c0168b0e669b97dab79c8))

### Fix

* fix: Cleanup of fs.py to allow relative and absolute paths (#464)

* cleanup of fs.py to allow relative and absolute paths

Signed-off-by: FrankSuits &lt;frankst@au1.ibm.com&gt;

* global change of absolute() to resolve()

Signed-off-by: FrankSuits &lt;frankst@au1.ibm.com&gt;

Co-authored-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`1407911`](https://github.com/oscal-compass/compliance-trestle/commit/140791190569e5673a216fe8dfdffc35d6c2424e))

### Unknown

* Release to update to OSCAL 1.0.0-rc2

Release to update to OSCAL 1.0.0-rc2 ([`5f6c05d`](https://github.com/oscal-compass/compliance-trestle/commit/5f6c05d7cd3f79d4303689872e22d0f5b66a4c28))

## v0.12.0 (2021-04-09)

### Chore

* chore: Merge back version tags and changelog into develop. ([`e3d7f69`](https://github.com/oscal-compass/compliance-trestle/commit/e3d7f698caa3a99a7e484ed4d0ff6c87c2ef5497))

### Feature

* feat: Release of transformation factory interface for beta testing.

Release of transformation factory interface for beta testing. ([`a036522`](https://github.com/oscal-compass/compliance-trestle/commit/a0365226175adfd38c5e37d863c4c50038a1658c))

### Unknown

* Feat:transformer factory (#455)

* initial prototype of transformer factory

Signed-off-by: FrankSuits &lt;frankst@au1.ibm.com&gt;

* added singleton transformer factory

Signed-off-by: FrankSuits &lt;frankst@au1.ibm.com&gt;

* added base transformer class

Signed-off-by: FrankSuits &lt;frankst@au1.ibm.com&gt;

* more fixes and added tests

Signed-off-by: FrankSuits &lt;frankst@au1.ibm.com&gt;

* added test for transform factory

Signed-off-by: FrankSuits &lt;frankst@au1.ibm.com&gt;

* restructured, added more docs and tests.

Signed-off-by: FrankSuits &lt;frankst@au1.ibm.com&gt;

* removed bad file names.

Signed-off-by: FrankSuits &lt;frankst@au1.ibm.com&gt;

* fix:Typing information

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

Co-authored-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`a5c86fd`](https://github.com/oscal-compass/compliance-trestle/commit/a5c86fd374a9cfc96859c22f8056dddefb3607e5))

* feat:Improved serialisation support for OscalBaseModel (#454)

* feat:Improved serialization support.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix:Serializing by appropriate key and minimizing file size.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`b87f158`](https://github.com/oscal-compass/compliance-trestle/commit/b87f158d9b1f54a3fc68857d7732ceb8a2f830df))

## v0.11.0 (2021-04-08)

### Chore

* chore: Merge back version tags and changelog into develop. ([`ee17ea5`](https://github.com/oscal-compass/compliance-trestle/commit/ee17ea5524fd56e92698d6f7e0106d48c55c66c8))

### Feature

* feat: Update NIST models to latest including refactors &amp; UT&#39;s

* feat:Update Oscal version

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* transformer changes with respect to OSCAL 1.0.0 rc2

* update documentation (transform results)

* multiple changes for latest nist - some tests still fail

Signed-off-by: FrankSuits &lt;frankst@au1.ibm.com&gt;

* removed ssp validate test

Signed-off-by: FrankSuits &lt;frankst@au1.ibm.com&gt;

* fixed code format

Signed-off-by: FrankSuits &lt;frankst@au1.ibm.com&gt;

* fix:Reworking generators

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* cleaned up gen-oscal.py and regenerated the oscal models.

Signed-off-by: FrankSuits &lt;frankst@au1.ibm.com&gt;

Co-authored-by: Chris Butler &lt;chris@thebutlers.me&gt;
Co-authored-by: degenaro &lt;lou.degenaro@gmail.com&gt; ([`5a7a8a3`](https://github.com/oscal-compass/compliance-trestle/commit/5a7a8a338ad3ef427f2ae9f26e2de4ac920fa525))

* feat: Initial trestle markdown functionality. (#407)

* Initial markdown template for use with cidd

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* Update for merge

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* feat: MVP markdown validator working

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* feat: MVP markdown validator working

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* Initial full pass of content validation for markdown.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix:Added missing test files for md workflows.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix:Correct dependency issues.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* chore: Refactored md codebase.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix: Fixed up unit tests.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix: Adding markdown_validator tests.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* chore: Small updates.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix:Removing governed projects to reduce scope of PR

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* chore: Adding UT&#39;s for trestle md subcommands.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* chore: Added unit test for allowed_task_name

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* chore: more UT&#39;s

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* chore: Adding more unit tests.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix: Removing python 3.8+ feature from unit tests.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* docs: Adding more documentation.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* chore: Updating docs

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* chore: Adding windows dependencies

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix:Added unit tests.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* added windows tests for hidden files

Signed-off-by: FrankSuits &lt;frankst@au1.ibm.com&gt;

* fix:documentation

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix:documentation

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix:documentation

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix:documentation

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix:documentation

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix:documentation

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix:documentation

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix:Completed documentation

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix:Correcting unit tests with bad logic

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix: More unit tests.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

Co-authored-by: FrankSuits &lt;frankst@au1.ibm.com&gt; ([`4d58e26`](https://github.com/oscal-compass/compliance-trestle/commit/4d58e265392388c81549967384546ddad8f46e4e))

* feat: Basics of HTTPS Fetcher for remote caching (#421)

* feat (remote) HTTPS Fetcher with basic tests.

Signed-off-by: Jeff Tan &lt;jeffetan@au1.ibm.com&gt;

* feat (remote) More tests for HTTPS Fetcher.

Signed-off-by: Jeff Tan &lt;jeffetan@au1.ibm.com&gt;

* feat (remote) More tests for HTTPS Fetcher and some improvements.

Signed-off-by: Jeff Tan &lt;jeffetan@au1.ibm.com&gt;

* feat (remote) Setting explicit verify arg in requests.get for HTTPS Fetcher, with tests. This is a precaution in case current behavior with verify=None by default becomes verify=False by default, which can be bad (no SSL verification of source certificate).

Signed-off-by: Jeff Tan &lt;jeffetan@au1.ibm.com&gt;

* feat (remote) Minor error message fix.

* feat (remote) Minor error message fix.

Signed-off-by: Jeff Tan &lt;jeffetan@au1.ibm.com&gt;

* feat (remote) Removed outfile use -- was left over from debugging.

Signed-off-by: Jeff Tan &lt;jeffetan@au1.ibm.com&gt;

Co-authored-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`cbb43ae`](https://github.com/oscal-compass/compliance-trestle/commit/cbb43ae4876a2015b0f10292c50268160b0a6dfd))

### Fix

* fix: Issue 344 checked rc for commands in tests and removed dependency on dictdiffer (#440)

Signed-off-by: FrankSuits &lt;frankst@au1.ibm.com&gt; ([`acc337b`](https://github.com/oscal-compass/compliance-trestle/commit/acc337b368602d5191244f973029b6ab02f212b2))

* fix: Strangely behaving log lines (#425)

* fix errant log lines --signoff

* format fix

signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

Co-authored-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`2cca882`](https://github.com/oscal-compass/compliance-trestle/commit/2cca88201e0fcd68419b72d04403a5baf1c1b33d))

### Unknown

* Trestle release: Markdown functionality and OSCAL updates prepping for rc2

Release to main ([`0d923e1`](https://github.com/oscal-compass/compliance-trestle/commit/0d923e15df8c1fc1936a2efea1d70e9af4750ad0))

* chore:Add google analytics to the trestle website. (#437)

* chore:Add google analytics to websie.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* chore:Add google analytics to website.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`eedf171`](https://github.com/oscal-compass/compliance-trestle/commit/eedf17180e0ffef777ed1b1b5b6451ac5661462c))

* chore:Updating mkdocs to avoid errors (#438)

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`966360f`](https://github.com/oscal-compass/compliance-trestle/commit/966360ffc822882019b551a2dceb9219b6beb5a6))

* added uuid regen for import and replicate (#428)

* added uuid regen for import and replicate

Signed-off-by: FrankSuits &lt;frankst@au1.ibm.com&gt;

* some cleanup and added docs

Signed-off-by: FrankSuits &lt;frankst@au1.ibm.com&gt; ([`805485f`](https://github.com/oscal-compass/compliance-trestle/commit/805485ffafe0ebc6dd08573d347924eccb6debb9))

* tutorial: what&#39;s your compliance posture? (#427)

* tutorial: what&#39;s your compliance posture?

* changed trestle links and fixed typos

Signed-off-by: Frank Suits &lt;frankst@au1.ibm.com&gt;

Co-authored-by: FrankSuits &lt;frankst@au1.ibm.com&gt; ([`49c5870`](https://github.com/oscal-compass/compliance-trestle/commit/49c5870dd9a9c3a8cb79c739e3e6d39dfc9b7df7))

## v0.10.0 (2021-03-25)

### Chore

* chore: Adjust codecov to allow for some wiggle room. (#414) ([`888696b`](https://github.com/oscal-compass/compliance-trestle/commit/888696bd060b5b10caf35692ff400cbcf2a7de59))

* chore: Typos and remove automation that is causing issues.

* fix: Updating documentation website content

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix: Small corrections

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix:Formatting issues introduced by manual merging in GH

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`ec94c22`](https://github.com/oscal-compass/compliance-trestle/commit/ec94c220ed061073e608023d593b6ff7978f0a58))

* chore: Auto-update pre-commit hooks (#390)

Co-authored-by: github-actions[bot] &lt;41898282+github-actions[bot]@users.noreply.github.com&gt;
Co-authored-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`fa040d0`](https://github.com/oscal-compass/compliance-trestle/commit/fa040d0840fa1102ca262e6550301d0485d655ec))

* chore: Merge back version tags and changelog into develop. ([`be2e49a`](https://github.com/oscal-compass/compliance-trestle/commit/be2e49a5f3733af8d9403f961f88878eba3d86fc))

### Documentation

* docs: Added more tutorials to the documentation for split and merge.

* added debug lines

* partial changes - added version command

* added changes to handle names vs. files

* load_distributed can now load object by name

* added test coverage.  suppressed trash msg.  better handling of top level model

* removed commented code line

* shortened comment

* fixes to some failure modes of split/merge

* new tutorial for split merge of oscal catalog

* fixed links and added missing file to mkdocs.yaml

* update mkdocs ([`0bf275a`](https://github.com/oscal-compass/compliance-trestle/commit/0bf275af173ac563147d73daaf5d500edd5c8729))

* docs: Instructions for gen_oscal and fix_any added to website.md (#389)

* updated with description of how to build models with gen_oscal and fix_any

* Added text for order_classes

Co-authored-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`5053e52`](https://github.com/oscal-compass/compliance-trestle/commit/5053e52e02e6f3761627b358b7e5abe107f17e21))

### Feature

* feat: Adding exchange protocol as a supported 3rd party schema and object model. (#416)

* chore: Adjust codecov to allow for some wiggle room.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* feat:Added exchange protocol support

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`05b8781`](https://github.com/oscal-compass/compliance-trestle/commit/05b8781283a32131ee0fd4a7097edef4bfdb6cb2))

* feat: added collection utilities. (#413)

* feat: added collection utilities.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix: Updated documentation to pass build.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix: leveraged new capability in load_distributed.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`83c1f17`](https://github.com/oscal-compass/compliance-trestle/commit/83c1f17e8902d969b07d9e3cf9fa1c80c22755c8))

### Fix

* fix: Correcting more issues with load_distributed impacting trestle split and merge

* added debug lines

* partial changes - added version command

* added changes to handle names vs. files

* load_distributed can now load object by name

* added test coverage.  suppressed trash msg.  better handling of top level model

* removed commented code line

* shortened comment

* fixes to some failure modes of split/merge ([`6ccb4db`](https://github.com/oscal-compass/compliance-trestle/commit/6ccb4db1614b521b9a132cbae17ac0922dea729b))

* fix: Cleanup and add unit tests to the exchange_protocol module (#417)

* chore: Adjust codecov to allow for some wiggle room.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* feat:Added exchange protocol support

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* chore: Cleanup for merge.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix:Added UT&#39;s and corrected schema to work with gen_oscal.py

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`a194580`](https://github.com/oscal-compass/compliance-trestle/commit/a19458008c5df39dbaf7bbcbfbc4431d16db4831))

* fix: merge updates - added version subcommand and modified load_distrib to load files by name (#415)

* added debug lines

* partial changes - added version command

* added changes to handle names vs. files

* load_distributed can now load object by name

* added test coverage.  suppressed trash msg.  better handling of top level model

* removed commented code line

* shortened comment

Co-authored-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`0a22c83`](https://github.com/oscal-compass/compliance-trestle/commit/0a22c833671a72f1d204eed50cb881e610ef0595))

* fix: Correct OSCAL output to desired design point for osco-to-oscal.

* Several small-ish fix-ups to produced OSCAL.

* Fix comparison data for utils tests.

Co-authored-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`5530eb4`](https://github.com/oscal-compass/compliance-trestle/commit/5530eb4d334251b336a376a6b165b0874f43f391))

* fix: Model behaviour correction and update to latest pydantic version.

* initial generation of uuids

* updated version of uuid regen

* new script to sort classes to allow diff after fix_any

* Initial fix to fix_any prior to cleanup

* Min pydantic version now 1.8.1 after recent fix for __root__

* New script to order classes for comparison after applying fix_any

* Simplified fix_any and fixed handling of *Item classes

* cleanup for code-lint

* fixes from new fix_any

* Allow creation of duplicate class names by tagging with index: 1,2,3 etc. ([`fcbaa23`](https://github.com/oscal-compass/compliance-trestle/commit/fcbaa2356dc2c7c53e3df1e5c7cd43b5c55c368b))

### Unknown

* Merge pull request #424 from IBM/develop

Release to master ([`1a1fd19`](https://github.com/oscal-compass/compliance-trestle/commit/1a1fd199aeedfac6316f5a994454a4a457941dc6))

* [ImgBot] Optimize images (#411) ([`1bc5860`](https://github.com/oscal-compass/compliance-trestle/commit/1bc58607cb80227bdfc49e77373ce8369562c2b6))

* Doc/tutorial task tanium to oscal (#406)

* Tutorial: use of trestle task tanium-to-oscal

* transformer-construction

* title change.

* put &#34;lite&#34; in title

* remove &lt;style&gt; tags.

* Add OSCAL snippets; enlarge diagram.

* Add data processing details for Observation and Finding cases.

* Other possible code stack configurations.

* Tutorials.

* Remove eclipse specific file; ignore eclipse things.

* Fix tutorials link. ([`1c7b700`](https://github.com/oscal-compass/compliance-trestle/commit/1c7b70012000c56ccb223484faada67bb174e5be))

* fix:Remove dead workflow

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`a730db6`](https://github.com/oscal-compass/compliance-trestle/commit/a730db649079b2dd7a083b33dc84b88939b931d7))

* fix to problem where split has trouble with files specified with path (#396)

* fix to problem where split has trouble with files specified with directory path

* boost test coverage

Co-authored-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`e0c1651`](https://github.com/oscal-compass/compliance-trestle/commit/e0c1651340e5700a827d8205bf497476b86b7cf3))

* Feature/tanium plus (#391)

* task tainium-to-oscal results

* Minor fixes, cleanup, and support for merge or separate output.

* Include top level result: in json output.

* Simulate should not produce output file.

* Fix finding aggregate; code clean-up; 100% test coverage.

* Fix finding aggregate; code clean-up; 100% test coverage.

* task tainium-to-oscal results

* Minor fixes, cleanup, and support for merge or separate output.

* Include top level result: in json output.

* Simulate should not produce output file.

* Fix finding aggregate; code clean-up; 100% test coverage.

* Fix finding aggregate; code clean-up; 100% test coverage.

* Updates to handle fixes to oscal layer.

LocalDefinitions1
InventoryItem

* Update website doc.

* Use ObjectiveStatus, and several small result fixes.

* Use &lt;details&gt; + &lt;summary&gt; to manage large samples in doc. ([`6ecfd13`](https://github.com/oscal-compass/compliance-trestle/commit/6ecfd133b2d0a47e21e7538fe94e3315bddbe55b))

* Cull duplicate oscal models, update to DMCG 0.9.1, add oscal version … (#392)

* Cull duplicate oscal models, update to DMCG 0.9.1, add oscal version to -v

* fix: Strip development to minimum commitments.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* docs: Call out restriction in changes

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

Co-authored-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`32ae0e8`](https://github.com/oscal-compass/compliance-trestle/commit/32ae0e83b4d49a55316bb715575f83c64fc8e6aa))

* Merge branch &#39;develop&#39; into fix/fix_any_drops_item ([`e400738`](https://github.com/oscal-compass/compliance-trestle/commit/e4007381af3812e07acfd00e66a25ed9beca5f59))

* Merge pull request #383 from IBM/feature/samples-oscal-1.0.0-rc1

Updated interchange schema, catching up with OSCAL 1.0.0-rc1, with samples, README, and a script to generate the schema ([`e4b0124`](https://github.com/oscal-compass/compliance-trestle/commit/e4b01244b7be60d1ff467daa201ed4e0fb199760))

* Merge branch &#39;feature/samples-oscal-1.0.0-rc1&#39; of github.com:IBM/compliance-trestle into feature/samples-oscal-1.0.0-rc1 ([`f070907`](https://github.com/oscal-compass/compliance-trestle/commit/f0709075c157fab7ecf6acefb186084af9fc62ab))

* Merge branch &#39;develop&#39; into feature/samples-oscal-1.0.0-rc1 ([`ae4544f`](https://github.com/oscal-compass/compliance-trestle/commit/ae4544ff0e08f8dc5a435f67c6f65fddba900e1c))

* feat (samples-oscal-1.0.0-rc1): Improved behavior of script in Windows environments where /dev/stdout won&#39;t work for output.

Signed-off-by: Jeff Tan &lt;jeffetan@au1.ibm.com&gt; ([`6a02920`](https://github.com/oscal-compass/compliance-trestle/commit/6a029208fadcc419b0d4a1f764689b58029a570d))

* feat (samples-oscal-1.0.0-rc1): Formatted README.

Signed-off-by: Jeff Tan &lt;jeffetan@au1.ibm.com&gt; ([`d3da956`](https://github.com/oscal-compass/compliance-trestle/commit/d3da95655b0a1c3fde66f72f00c9e3d13ed904c7))

* feat (samples-oscal-1.0.0-rc1): Clarified README.

Signed-off-by: Jeff Tan &lt;jeffetan@au1.ibm.com&gt; ([`ec18022`](https://github.com/oscal-compass/compliance-trestle/commit/ec1802208c5d60d58c94099a0ac43d9711d2bb36))

* feat (samples-oscal-1.0.0-rc1): Sanitized README some more.

Signed-off-by: Jeff Tan &lt;jeffetan@au1.ibm.com&gt; ([`a419961`](https://github.com/oscal-compass/compliance-trestle/commit/a4199616869fc894174f66524a5a112d3252b2b3))

* feat (samples-oscal-1.0.0-rc1): Updated custom schema and samples to catch up with OSCAL 1.0.0-rc1. Script to generate schema also added.

Signed-off-by: Jeff Tan &lt;jeffetan@au1.ibm.com&gt; ([`de22ac7`](https://github.com/oscal-compass/compliance-trestle/commit/de22ac7c1b32596bd267c8b1f967839d51de1173))

* Allow creation of duplicate class names by tagging with index: 1,2,3 etc. ([`d07a398`](https://github.com/oscal-compass/compliance-trestle/commit/d07a398e806bd9e30c09bde4be8f5848705680a9))

* fixes from new fix_any ([`80aa9c4`](https://github.com/oscal-compass/compliance-trestle/commit/80aa9c4775159c357889c5c191fb364e4a545c85))

* cleanup for code-lint ([`fd93eb5`](https://github.com/oscal-compass/compliance-trestle/commit/fd93eb528a3f9afdf4bc7611435763b781032d3d))

* Simplified fix_any and fixed handling of *Item classes ([`b424150`](https://github.com/oscal-compass/compliance-trestle/commit/b424150aa676a58e2255507f2c08088d36e85cb1))

* New script to order classes for comparison after applying fix_any ([`8904913`](https://github.com/oscal-compass/compliance-trestle/commit/8904913cc0f8955b2b97b5472482af44434bc123))

* Min pydantic version now 1.8.1 after recent fix for __root__ ([`6a686d2`](https://github.com/oscal-compass/compliance-trestle/commit/6a686d29dbae0f81e3e6f4c3f04340042cde1123))

* Initial fix to fix_any prior to cleanup ([`9675a3a`](https://github.com/oscal-compass/compliance-trestle/commit/9675a3ac7f9cdfc9e17d955f4ef37d5c8d796461))

* new script to sort classes to allow diff after fix_any ([`bec3e3a`](https://github.com/oscal-compass/compliance-trestle/commit/bec3e3a9c96203af6824016cab9b79ef4f2db52b))

* updated version of uuid regen ([`27382ce`](https://github.com/oscal-compass/compliance-trestle/commit/27382ce7f098adc64f731cd19d8920a4e3d491fb))

* Merge branch &#39;develop&#39; of https://github.com/IBM/compliance-trestle into feat/uuid_regen ([`f90ba17`](https://github.com/oscal-compass/compliance-trestle/commit/f90ba17e0c6d261a3a743cbf571da072aedcde73))

## v0.9.0 (2021-03-02)

### Chore

* chore: Auto-update pre-commit hooks (#379)

Co-authored-by: github-actions[bot] &lt;41898282+github-actions[bot]@users.noreply.github.com&gt;
Co-authored-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`58e766c`](https://github.com/oscal-compass/compliance-trestle/commit/58e766c8fcfea47a12da4e3672cfe394d3efc5db))

* chore: Merge back version tags and changelog into develop. ([`5475dbe`](https://github.com/oscal-compass/compliance-trestle/commit/5475dbe2502cd649661d7cd14370c161610f7b18))

### Feature

* feat: Tanium export to oscal conversion task.

* task tanium-to-oscal

* task tanium-to-oscal website documentation

* Add config param timestamp.

* 3rd party tools.

* Fix code format issues.

* Missing types.

* Missing return type.

Co-authored-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`5f7bcbf`](https://github.com/oscal-compass/compliance-trestle/commit/5f7bcbf885b5fcb77da054917b6e66fa83ce66e9))

### Fix

* fix: Enforce oscal version in models and tests (#377)

Now enforce oscal version defined in one place.  Many changes to tests and data.

Co-authored-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`7fc08e1`](https://github.com/oscal-compass/compliance-trestle/commit/7fc08e10b78b658359dc119080d64d44b09a572d))

### Unknown

* Merge pull request #382 from IBM/develop

Bug fix release: clean up issue due to pydantic changes in 1.8.0 ([`48e60ed`](https://github.com/oscal-compass/compliance-trestle/commit/48e60ed1f2f1e0eae71799eec2e49873fd3da0eb))

* Fix: Dependency issues including pydantic (#380)

* Fix: Dependency issues

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix:Constrain pydantic version

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`e70a023`](https://github.com/oscal-compass/compliance-trestle/commit/e70a0233e35bec329e2c283998bbc27a20877bc9))

* initial generation of uuids ([`9c8fd13`](https://github.com/oscal-compass/compliance-trestle/commit/9c8fd139665a4042ff3fb115b2e2625ec03534ba))

* Merge pull request #356 from IBM/feature/remote

remote cache with SFTP and local fetchers ([`52a49db`](https://github.com/oscal-compass/compliance-trestle/commit/52a49db6df28e6d188b3ec5729d265def2b84128))

* Merge branch &#39;develop&#39; into feature/remote ([`eca4236`](https://github.com/oscal-compass/compliance-trestle/commit/eca4236c5aec2d0cb70ce0c382bb769e74ed1309))

## v0.8.1 (2021-02-24)

### Chore

* chore: Merge back version tags and changelog into develop. ([`6eb2939`](https://github.com/oscal-compass/compliance-trestle/commit/6eb293999bbbf2052c7a480ffd5a77d7a7304a0f))

### Fix

* fix: Import issues with hyphen named files (#371)

Includes fixes to:
1) Parsing of unknown OSCAL content types (for top level schemas)
2) Method for testing that the website working. ([`07493ad`](https://github.com/oscal-compass/compliance-trestle/commit/07493ad76f720503d756c54d67a1199abe181693))

### Unknown

* Merge pull request #374 from IBM/develop

Bugfix merge to master ([`ade0c5f`](https://github.com/oscal-compass/compliance-trestle/commit/ade0c5f695c976ecc7169dc4241133fb5c9326b4))

* Merge branch &#39;feature/remote&#39; of github.com:IBM/compliance-trestle into feature/remote
Signed-off-by: Jeff Tan &lt;jeffetan@au1.ibm.com&gt; ([`b3da0f1`](https://github.com/oscal-compass/compliance-trestle/commit/b3da0f1ab03664419ae3cd8fd250e5170eed00ef))

* Merge branch &#39;develop&#39; into feature/remote ([`99967cc`](https://github.com/oscal-compass/compliance-trestle/commit/99967cc13e3dec608fb9af0426075f3b09ebb929))

* Fix: Corrected componnent model caused by new datamodel-gen, using original nist source (#373)

Co-authored-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`b18a815`](https://github.com/oscal-compass/compliance-trestle/commit/b18a8150846d0019753cbe536e8532eec0c0cccc))

* feat:Improved documentation abstraction to use the doc string at multiple levels. (#370)

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`a5510aa`](https://github.com/oscal-compass/compliance-trestle/commit/a5510aa786d4de26dfd2991f902ee420faae6e86))

* Merge branch &#39;develop&#39; into feature/remote ([`20c793e`](https://github.com/oscal-compass/compliance-trestle/commit/20c793e8cf93c5624d249eaac17c53c3153ddc73))

## v0.8.0 (2021-02-22)

### Chore

* chore: Auto-update pre-commit hooks (#362)

Co-authored-by: github-actions[bot] &lt;41898282+github-actions[bot]@users.noreply.github.com&gt; ([`b6c1da5`](https://github.com/oscal-compass/compliance-trestle/commit/b6c1da5af3bdca8971de0796422caaf3f3c7b4f0))

* chore: Unit test runs to ensure website boots and is usable. (#338)

* unit test: website boots and is usable.

Signed-off-by: Lou Degenaro &lt;degenaro@us.ibm.com&gt;

* whoopsi - forgot to format &amp; lint.

Signed-off-by: Lou Degenaro &lt;degenaro@us.ibm.com&gt;

Co-authored-by: degenaro &lt;degenaro@us.ibm.com&gt;
Co-authored-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`7b1b48d`](https://github.com/oscal-compass/compliance-trestle/commit/7b1b48d8438c0f2f800741945811fb832ad76df0))

* chore: Merge back version tags and changelog into develop. ([`4686dd4`](https://github.com/oscal-compass/compliance-trestle/commit/4686dd46d14e9d9c57431c238a8bed2e4a816acc))

### Documentation

* docs: website documentation for trestle task osco-to-oscal (#336)

Signed-off-by: Lou Degenaro &lt;degenaro@us.ibm.com&gt;

Co-authored-by: degenaro &lt;degenaro@us.ibm.com&gt;
Co-authored-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`95c5c09`](https://github.com/oscal-compass/compliance-trestle/commit/95c5c09b9f6f56aa4697609459f1369e06b7f3c2))

### Feature

* feat: Added bulk operations for assemble (#367)

Allows assemble to be executed across all files of a given type.
Co-authored-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`771d54e`](https://github.com/oscal-compass/compliance-trestle/commit/771d54e29ee839d38330929001c908b6ad669f8f))

* feat: Utility to transform OSCO yaml data into OSCAL observations json data. (#348)

Signed-off-by: Lou Degenaro &lt;degenaro@us.ibm.com&gt;

Co-authored-by: degenaro &lt;degenaro@us.ibm.com&gt;
Co-authored-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`488a75a`](https://github.com/oscal-compass/compliance-trestle/commit/488a75a7fa5f259b2655b624ba7e3643c4ab7b28))

* feat: validate duplicates now loads distributed models (#346)

Co-authored-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`1d54353`](https://github.com/oscal-compass/compliance-trestle/commit/1d54353e595a502a3f1d0f4410f9da38f501daaa))

### Fix

* fix: Allow assemble to succeed when no model is found. (#368)

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`fe7a288`](https://github.com/oscal-compass/compliance-trestle/commit/fe7a2882f447a628a30a08d1c089fac752d16579))

* fix: To website automation test on windows (#366) ([`8e3ecbf`](https://github.com/oscal-compass/compliance-trestle/commit/8e3ecbf5f9acb8db4e200f7769cefcb20941a410))

### Unknown

* Merge pull request #364 from IBM/develop

Release to main: Refactored behaviour for validate and assemble. ([`194c005`](https://github.com/oscal-compass/compliance-trestle/commit/194c0058d2d2e806ea19cefddde8a05ea9c5bfe2))

* feat (remote): SSH_KEY must now contain the private key (RSA), not its file name, e.g., SSH_KEY=$(cat ~/.ssh/id_rsa). It is expected to have newlines. Unit test updated accordingly.
Signed-off-by: Jeff Tan &lt;jeffetan@au1.ibm.com&gt; ([`74223a1`](https://github.com/oscal-compass/compliance-trestle/commit/74223a18a7e4d81a55167d0237d0fb1f14d9385d))

* feat (remote): Linted.
Signed-off-by: Jeff Tan &lt;jeffetan@au1.ibm.com&gt; ([`23dc762`](https://github.com/oscal-compass/compliance-trestle/commit/23dc76213d376ee9295d9e0d0bed94c64887a283))

* feat (remote): Removed HTTPS and Github Fetcher code for now, to be dealt with sometime after this version merges in.
Signed-off-by: Jeff Tan &lt;jeffetan@au1.ibm.com&gt; ([`b9c4778`](https://github.com/oscal-compass/compliance-trestle/commit/b9c47781b7b8c8fcd49d64cbb3a6a2a678be9119))

* feat (remote): Updated test_https_fetcher() so a try block isn&#39;t included.
Signed-off-by: Jeff Tan &lt;jeffetan@au1.ibm.com&gt; ([`54019af`](https://github.com/oscal-compass/compliance-trestle/commit/54019af446c3942897c142913176a6775248dbe1))

* feat (remote): Local fetcher will now refuse to cache an object that is inside a trestle project. Unit tests adjusted accordingly.
Signed-off-by: Jeff Tan &lt;jeffetan@au1.ibm.com&gt; ([`663af76`](https://github.com/oscal-compass/compliance-trestle/commit/663af764627d36bc3c33f14186d25aafa980ea54))

* Merge branch &#39;feature/remote&#39; of github.com:IBM/compliance-trestle into feature/remote
Chris merged develop into this more recently.
Signed-off-by: Jeff Tan &lt;jeffetan@au1.ibm.com&gt; ([`90437e4`](https://github.com/oscal-compass/compliance-trestle/commit/90437e4b18ed59c8374cc331bd41a08f8f24d07a))

* Merge branch &#39;develop&#39; into feature/remote ([`2db970f`](https://github.com/oscal-compass/compliance-trestle/commit/2db970fc4afdfdffb8fcbeb1f38ad68b7044dc30))

* Wrap validate in try block to catch exceptions.  Increase test coverage. (#363) ([`14686a8`](https://github.com/oscal-compass/compliance-trestle/commit/14686a873b71aff2ba6a4494efed49d8f95ec29d))

* Feature/validate distributed now validates models by type and all (#360)

* validate duplicates now loads distributed models

* Extensive changes to support loading models by name

* validate by type now works.  Increased test coverage.

* validate now works on -all.  all tests pass

Co-authored-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`b347222`](https://github.com/oscal-compass/compliance-trestle/commit/b347222314282d520bdcb60f1de325429fd5d5e7))

* Feat: Trestle init now adds keep files. (#357)

* trestle init now adds .keep files to preserve directory structure for git

Signed-off-by: Juliet Rubinstein &lt;juliet.rubinstein@ibm.com&gt;

* trestle init now adds .keep files to preserve directory structure for git

Signed-off-by: Juliet Rubinstein &lt;juliet.rubinstein@ibm.com&gt;

* trestle init now adds .keep files to preserve directory structure for git

Signed-off-by: Juliet Rubinstein &lt;juliet.rubinstein@ibm.com&gt;

Co-authored-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`f6ca64a`](https://github.com/oscal-compass/compliance-trestle/commit/f6ca64adf99eca5a89d678266b377d07eb3d3ce3))

* Merge pull request #354 from IBM/feature/import-validate

feat (import): Validation is now part of trestle import, with a rollback if duplicates are found. ([`4080dc2`](https://github.com/oscal-compass/compliance-trestle/commit/4080dc23e13eba0398face98d55f705a60b7216e))

* feat (import): Updated test for import with validation calls, coverage up to 100%.
Signed-off-by: Jeff Tan &lt;jeffetan@au1.ibm.com&gt; ([`c168922`](https://github.com/oscal-compass/compliance-trestle/commit/c1689223330d28c9487cde5337ea1a3a18e9883e))

* Merge branch &#39;develop&#39; into feature/import-validate
Signed-off-by: Jeff Tan &lt;jeffetan@au1.ibm.com&gt; ([`c41df46`](https://github.com/oscal-compass/compliance-trestle/commit/c41df46508ccc5d7d8ee8d19630c6279e1beba35))

* feat (import): Updated tests for import with validation calls.
Signed-off-by: Jeff Tan &lt;jeffetan@au1.ibm.com&gt; ([`2a3b71f`](https://github.com/oscal-compass/compliance-trestle/commit/2a3b71f290077bef6e1247c8d29ec5d5eb78a7eb))

* feat (import): Linted.
Signed-off-by: Jeff Tan &lt;jeffetan@au1.ibm.com&gt; ([`2ea9df6`](https://github.com/oscal-compass/compliance-trestle/commit/2ea9df6a70daca840fa9bbfae262acb277175b59))

* feat (import): Validating imported model using trestle validate, rolling back if unhappy with results.
Signed-off-by: Jeff Tan &lt;jeffetan@au1.ibm.com&gt; ([`d9c810a`](https://github.com/oscal-compass/compliance-trestle/commit/d9c810ad09e7c33baf3f424b5ea9fb38e2483d21))

* feat (remote): Fixed confused use of SSH_KEY, so now it refers to a private key, if supplied. Host keys are now loaded from usual/default paths.
Signed-off-by: Jeff Tan &lt;jeffetan@au1.ibm.com&gt; ([`7cd95ca`](https://github.com/oscal-compass/compliance-trestle/commit/7cd95ca59b2a193d1651f777cfa2eb3d0dadd71c))

* feat (remote): Setting relative paths for the local fetcher aside, for now.
Signed-off-by: Jeff Tan &lt;jeffetan@au1.ibm.com&gt; ([`d5c6285`](https://github.com/oscal-compass/compliance-trestle/commit/d5c628509e871cf7b962b6ca36c497233fa1ec32))

* feat (remote): Can&#39;t handle relative paths properly on Windows just yet.
Signed-off-by: Jeff Tan &lt;jeffetan@au1.ibm.com&gt; ([`d1632a7`](https://github.com/oscal-compass/compliance-trestle/commit/d1632a7636a8ab24d0303dfb2f5aa84077875c9e))

* feat (remote): code-format prefers one line.
Signed-off-by: Jeff Tan &lt;jeffetan@au1.ibm.com&gt; ([`cb806bb`](https://github.com/oscal-compass/compliance-trestle/commit/cb806bb0fbacb174adc1399d89c6771c744c70ab))

* feat (remote): Allowing for sftp uri with a password but no username, which is pulled in from environment instead.
Signed-off-by: Jeff Tan &lt;jeffetan@au1.ibm.com&gt; ([`b7f3630`](https://github.com/oscal-compass/compliance-trestle/commit/b7f3630800a6164f9d5e151cd6ff4a992544d493))

* feat (remote): Fixed unwanted attribute assignments (may remove them completely). Added local fetcher test for relative paths.
Signed-off-by: Jeff Tan &lt;jeffetan@au1.ibm.com&gt; ([`0dbf1a5`](https://github.com/oscal-compass/compliance-trestle/commit/0dbf1a55ceb278ea497b9978276137fe1060f78e))

* feat (remote): Fixed naming for _cached_dir variable to disambiguate across fetchers.
Signed-off-by: Jeff Tan &lt;jeffetan@au1.ibm.com&gt; ([`2292f7b`](https://github.com/oscal-compass/compliance-trestle/commit/2292f7b8cd79295dd6f8976af6982c7c47c6f2ad))

* feat (remote): Improved docstrings, with attributes and arguments listed where applicable.
Signed-off-by: Jeff Tan &lt;jeffetan@au1.ibm.com&gt; ([`c779099`](https://github.com/oscal-compass/compliance-trestle/commit/c7790990cb9fe661456808d1c4789d4a4522b0d6))

* feat (remote): Improved docstrings, cleaned up code a bit.
Signed-off-by: Jeff Tan &lt;jeffetan@au1.ibm.com&gt; ([`a96a0c6`](https://github.com/oscal-compass/compliance-trestle/commit/a96a0c6af225b152ec28c54b6c451b70de8d0988))

* feat (remote): Accepting any Windows filesystem drive letter in uri.
Signed-off-by: Jeff Tan &lt;jeffetan@au1.ibm.com&gt; ([`12b4d11`](https://github.com/oscal-compass/compliance-trestle/commit/12b4d11021c3ff43e7d66c7637e976331b32320e))

* feat (remote): Added or improved docstrings, and removed unnecessary fail_hard attribute.
Signed-off-by: Jeff Tan &lt;jeffetan@au1.ibm.com&gt; ([`68d384f`](https://github.com/oscal-compass/compliance-trestle/commit/68d384f881ab0133220f67f5dcad0bd5283f7e61))

* feat (remote): Moving settings work out of this branch.
Signed-off-by: Jeff Tan &lt;jeffetan@au1.ibm.com&gt; ([`178cc4b`](https://github.com/oscal-compass/compliance-trestle/commit/178cc4b7e8dabea1941561f68c1208158385faac))

* feat (settings): Moving settings-related work out of this branch and into its own branch.
Signed-off-by: Jeff Tan &lt;jeffetan@au1.ibm.com&gt; ([`b3de78c`](https://github.com/oscal-compass/compliance-trestle/commit/b3de78c896316bb04ff06ab64281a8a4cc05e196))

* feat (settings): Using random non-functional token string.
Signed-off-by: Jeff Tan &lt;jeffetan@au1.ibm.com&gt; ([`e72ea65`](https://github.com/oscal-compass/compliance-trestle/commit/e72ea6576b431a0351984514eae159714dd81154))

* feat (remote): Again, username and password for HTTPSFetcher tests instead of expecting a particular env var.
Signed-off-by: Jeff Tan &lt;jeffetan@au1.ibm.com&gt; ([`c7390c1`](https://github.com/oscal-compass/compliance-trestle/commit/c7390c1b5138b6707627346c18b32ba3c3ed3a66))

* feat (remote): Setting username and password for HTTPSFetcher tests instead of expecting a particular env var.
Signed-off-by: Jeff Tan &lt;jeffetan@au1.ibm.com&gt; ([`38d4a87`](https://github.com/oscal-compass/compliance-trestle/commit/38d4a8746a63eaeba3014282edbf542695fb3611))

* feat (remote): linted HTTPSFetcher tests.
Signed-off-by: Jeff Tan &lt;jeffetan@au1.ibm.com&gt; ([`664da29`](https://github.com/oscal-compass/compliance-trestle/commit/664da29e91f38a7e9ae9a41888f4f4c1399d4758))

* feat (remote): improved get test for HTTPSFetcher.
Signed-off-by: Jeff Tan &lt;jeffetan@au1.ibm.com&gt; ([`e4aec2c`](https://github.com/oscal-compass/compliance-trestle/commit/e4aec2cd848e5db39b7509ac70727cfac9c1fb34))

* feat (remote): get failure test for HTTPSFetcher.
Signed-off-by: Jeff Tan &lt;jeffetan@au1.ibm.com&gt; ([`620fe44`](https://github.com/oscal-compass/compliance-trestle/commit/620fe442685a8dee0bac53bccb5d578130e90ea9))

* feat (remote): HTTPSFetcher now fills _inst_cache_path, and now has a basic unit test. Minor fix to test_fetcher_factory.
Signed-off-by: Jeff Tan &lt;jeffetan@au1.ibm.com&gt; ([`d3d96e6`](https://github.com/oscal-compass/compliance-trestle/commit/d3d96e6c6d43bde4de1b7d1d4b5b69d9445b317d))

* Added tests for unsupported scheme in url and a local file in a Windows filesystem.
Signed-off-by: Jeff Tan &lt;jeffetan@au1.ibm.com&gt; ([`c8f8de7`](https://github.com/oscal-compass/compliance-trestle/commit/c8f8de79ceeb729511ca830fc60b7911de3128b4))

* feat (import): Updated nist submodules.
Signed-off-by: Jeff Tan &lt;jeffetan@au1.ibm.com&gt; ([`05db1a0`](https://github.com/oscal-compass/compliance-trestle/commit/05db1a08bbc6143a2f66145978d5da13270cfa37))

* feat (import): Linted/formatted/modified to allow make test to succeed.
Signed-off-by: Jeff Tan &lt;jeffetan@au1.ibm.com&gt; ([`f51023f`](https://github.com/oscal-compass/compliance-trestle/commit/f51023f078b993331c59ad561533e8211d8115ac))

* Merge branch &#39;develop&#39; into feature/remote
Just to align this branch with recent updates in develop.
Signed-off-by: Jeff Tan &lt;jeffetan@au1.ibm.com&gt; ([`f5e5723`](https://github.com/oscal-compass/compliance-trestle/commit/f5e57238fe48c7c63e57ce9116c02b98012f5cf1))

* New command replicate and functionality to deduce content type based on discovered file extension (#331)

* Initial mock up of replicate and test

* More complete implementation - passes test

* more fixes due to changing --name to --output

* Added path_to_content_type and tests

Allows determining content type from extension of file in directory.

* Usable version of replicate with more comprehensive tests.

* Improved docstring and pluralize function

* increase coverage for replicate

* added tests to bring coverage to 100%

Co-authored-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`2694101`](https://github.com/oscal-compass/compliance-trestle/commit/2694101f4414446d5b1fae8b4218083379d7d2ea))

## v0.7.2 (2021-02-02)

### Fix

* fix: DevOps fixes onto main (#334)

* Implemented trestle assemble with some UT

* Modified docs

* Code format

* Code lint

* Extending UT

* Full UT

* assemble bug fix

* fix &#39;make docs-serve&#39; on linux (Red Hat 7.9)

Signed-off-by: Lou Degenaro &lt;degenaro@us.ibm.com&gt;

* Updated to deal with inherently plural model names.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix: Fix merge main to back to develop automatically.(#332)

* Corrected errors in the build process.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* Corrected errors in the build process.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

Co-authored-by: Nebula Alam &lt;anebula@au1.ibm.com&gt;
Co-authored-by: degenaro &lt;degenaro@us.ibm.com&gt; ([`74df375`](https://github.com/oscal-compass/compliance-trestle/commit/74df375c15ad0bc2f0fb8c54e1ed83faf11d66e4))

### Unknown

* Merge branch &#39;main&#39; into develop ([`59b9945`](https://github.com/oscal-compass/compliance-trestle/commit/59b994536fa7ffe78498bfa4b17bf0d4943c970a))

## v0.7.1 (2021-02-02)

### Fix

* fix: Assembly behaviour correction and devops fixes.

* Implemented trestle assemble with some UT

* Modified docs

* Code format

* Code lint

* Extending UT

* Full UT

* assemble bug fix

* fix &#39;make docs-serve&#39; on linux (Red Hat 7.9)

Signed-off-by: Lou Degenaro &lt;degenaro@us.ibm.com&gt;

* Updated to deal with inherently plural model names.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

Co-authored-by: Nebula Alam &lt;anebula@au1.ibm.com&gt;
Co-authored-by: degenaro &lt;degenaro@us.ibm.com&gt; ([`ac3828d`](https://github.com/oscal-compass/compliance-trestle/commit/ac3828de66874807b70ee372be51976a724322d1))

* fix: Fix merge main to back to develop automatically.(#332)

* Corrected errors in the build process.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* Corrected errors in the build process.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`b64dd9f`](https://github.com/oscal-compass/compliance-trestle/commit/b64dd9f5d1183109fe18bd3a75f5953af269d985))

### Unknown

* Merge branch &#39;main&#39; into develop ([`31e0ac5`](https://github.com/oscal-compass/compliance-trestle/commit/31e0ac5c1ae956140b38d2a7f1b1961a93dd707c))

## v0.7.0 (2021-01-28)

### Fix

* fix: Corrected assemble to push files into the correct location. ([`f3bc0e5`](https://github.com/oscal-compass/compliance-trestle/commit/f3bc0e5df22430d396ca0d82bc70624db34a6986))

### Unknown

* Release of trestle of assembly and osco-to-oscal.

feat: Release of assembly, osco-to-oscal and other tasks ([`a56c546`](https://github.com/oscal-compass/compliance-trestle/commit/a56c54683ca8ac938f1fc2af787db34f852a9a44))

* Merge branch &#39;develop&#39; into feat/assemble ([`44d884e`](https://github.com/oscal-compass/compliance-trestle/commit/44d884e0fd9ddd4e207f54dde3ae684c80d4eb96))

* fix:Correct casing in mkdocs serve to work on case sensitive file sytems.

fix &#39;make docs-serve&#39; on linux (Red Hat 7.9) ([`a2949e1`](https://github.com/oscal-compass/compliance-trestle/commit/a2949e15b79bfc8ee13dd9822aa49e708548c62d))

* fix &#39;make docs-serve&#39; on linux (Red Hat 7.9)

Signed-off-by: Lou Degenaro &lt;degenaro@us.ibm.com&gt; ([`28e5fc0`](https://github.com/oscal-compass/compliance-trestle/commit/28e5fc048bafdec4d42d6e2d838df41f83179189))

* Updated to deal with inherently plural model names.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`3404043`](https://github.com/oscal-compass/compliance-trestle/commit/34040437cd9b26361934ad24e89926264bb137c6))

* Merge develop ([`d0b2d26`](https://github.com/oscal-compass/compliance-trestle/commit/d0b2d26c0fd81d13e904b95e162e1279747ad517))

* Merge branch &#39;main&#39; into develop ([`0a4e9c7`](https://github.com/oscal-compass/compliance-trestle/commit/0a4e9c7577576597fa70e1e21abe5d579f155387))

## v0.6.2 (2021-01-17)

### Chore

* chore: Updated bad documentation. (#317)

* Corrected bad link for website homepage.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* Typo corrections in documentation website

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`b5a58f7`](https://github.com/oscal-compass/compliance-trestle/commit/b5a58f71ba1bd7f6a89bb5626999ab8ee6a0049a))

* chore: Auto-update pre-commit hooks (#312)

Co-authored-by: github-actions[bot] &lt;41898282+github-actions[bot]@users.noreply.github.com&gt; ([`0c6c748`](https://github.com/oscal-compass/compliance-trestle/commit/0c6c7487aa26e6666511ec159e35e41e7052db95))

### Documentation

* docs: Fix typos and grammar in cli and misspelling in split_merge docs (#306) ([`272c2cc`](https://github.com/oscal-compass/compliance-trestle/commit/272c2ccf6fbfca5fe6cdac7f0623b85fa8d5ddd7))

### Feature

* feat: trestle assemble implemented and documented.

* Implemented trestle assemble with some UT

* Modified docs

* Code format

* Code lint

* Extending UT

* Full UT

Co-authored-by: Nebula Alam &lt;anebula@au1.ibm.com&gt; ([`e752bc2`](https://github.com/oscal-compass/compliance-trestle/commit/e752bc2a6923c05c6251622499137d0c40633467))

* feat: Enhancement to handle arboretum fetcher-built OSCO evidence as input (#311)

Signed-off-by: Lou Degenaro &lt;degenaro@us.ibm.com&gt;

Co-authored-by: degenaro &lt;degenaro@us.ibm.com&gt;
Co-authored-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`e9c4196`](https://github.com/oscal-compass/compliance-trestle/commit/e9c41969597c6bf587b5732e0851da3e7b24429e))

* feat: task osco-to-oscal to allow transformation from OpenSHift Compliance Operator to OSCAL (#296)

* task osco-to-oscal

Signed-off-by: Lou Degenaro &lt;degenaro@us.ibm.com&gt;

* Fixes to address review by Chris Butler.

- move AssessmentResultsPartial class into osco.py
- fix wacky typing
- fix function/class variable annotations
- fix OSCAL object initialization
- fix awkward while true construct
- use tmp_path
- remove extraneous import

Signed-off-by: Lou Degenaro &lt;degenaro@us.ibm.com&gt;

* Fixes to address PR comments from CB.

Signed-off-by: Lou Degenaro &lt;degenaro@us.ibm.com&gt;

* Remedy the metadata cluster-X info concern.

Signed-off-by: Lou Degenaro &lt;degenaro@us.ibm.com&gt;

* output file reduced to observations list only &amp; improved test cases.

Signed-off-by: Lou Degenaro &lt;degenaro@us.ibm.com&gt;

* oops, missed a return type.

Signed-off-by: Lou Degenaro &lt;degenaro@us.ibm.com&gt;

Co-authored-by: degenaro &lt;degenaro@us.ibm.com&gt;
Co-authored-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`ad995a2`](https://github.com/oscal-compass/compliance-trestle/commit/ad995a22029aa67972bc9e6fdd3ebd0e987f50ba))

* feat: Merge allows use of both yaml and json files.

Co-authored-by: Nebula Alam &lt;anebula@au1.ibm.com&gt;
Co-authored-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`4d87e6a`](https://github.com/oscal-compass/compliance-trestle/commit/4d87e6aac5a49d1624da06d4f7bab4accb13b033))

### Fix

* fix: Corrected branch for mkdocs deploy. (#304) (#305)

Note: Alternative techniques may be required, however, with devops integration it must be tested live.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`be3f13a`](https://github.com/oscal-compass/compliance-trestle/commit/be3f13a89d44c3f773ad7e372e4116eb609c8f5d))

* fix: Corrected bad link to website homepage. (#314)

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`81124fb`](https://github.com/oscal-compass/compliance-trestle/commit/81124fba5f25772cbcabf3fd0923ac6284794ff1))

### Unknown

* assemble bug fix ([`fcbbfd2`](https://github.com/oscal-compass/compliance-trestle/commit/fcbbfd2127c9bab2ac07fafd4b8ff4a9fe85e804))

* Full UT ([`f90c351`](https://github.com/oscal-compass/compliance-trestle/commit/f90c3512f466c9ea3cd5cca6290c1b6f288046c0))

* Merge branch &#39;develop&#39; into feat/assemble ([`963e9b9`](https://github.com/oscal-compass/compliance-trestle/commit/963e9b967d87404cedca959f5f05eeae260fc567))

* Extending UT ([`3662b83`](https://github.com/oscal-compass/compliance-trestle/commit/3662b83a660eed4c1f14eb864afd20b04633be19))

* Code lint ([`d0c8e84`](https://github.com/oscal-compass/compliance-trestle/commit/d0c8e847dd4a13cc7993e86fe567d43a021db6a6))

* Code format ([`9a9235f`](https://github.com/oscal-compass/compliance-trestle/commit/9a9235ff62735bd300ad41b9c24945517d276cd0))

* Modified docs ([`ff49c03`](https://github.com/oscal-compass/compliance-trestle/commit/ff49c03a762abd1ea2fc54d69e2a93e576e07318))

* Merge branch &#39;develop&#39; into feat/assemble ([`71b0497`](https://github.com/oscal-compass/compliance-trestle/commit/71b04976a7b35403a61e750ff4ea5c30995d9934))

* Implemented trestle assemble with some UT ([`cc02d70`](https://github.com/oscal-compass/compliance-trestle/commit/cc02d70febe86e6b1579f40c323a92637b3b1a8d))

* feat (remote): testing local fetcher get_oscal() and get_raw(), and code format/lint fixes.
Signed-off-by: Jeff Tan &lt;jeffetan@au1.ibm.com&gt; ([`05a1e04`](https://github.com/oscal-compass/compliance-trestle/commit/05a1e04c8afabda3e266d1fa97e02060b94b5db8))

* feat (remote): updated get_oscal() and get_raw() to adjust to proper treatment of _inst_cache_path as full paths to the cache object
Signed-off-by: Jeff Tan &lt;jeffetan@au1.ibm.com&gt; ([`df886e0`](https://github.com/oscal-compass/compliance-trestle/commit/df886e04a3c2dfbf8f530bfe075ecab155db1148))

* feat (remote): local and  sftp fetchers now treat _inst_cache_path as full paths to the cache object, rather than the containing directory.
Signed-off-by: Jeff Tan &lt;jeffetan@au1.ibm.com&gt; ([`c43292e`](https://github.com/oscal-compass/compliance-trestle/commit/c43292ee879cfe4f29fe45cd2d7f9cd23fa7559d))

* feat (remote): merge resolution: sftp tests.
Signed-off-by: Jeff Tan &lt;jeffetan@au1.ibm.com&gt; ([`e2a387d`](https://github.com/oscal-compass/compliance-trestle/commit/e2a387df314a729058562e96bc5dca181ce3adb7))

* feat (remote): Fixed some unit tests, and linted.
Signed-off-by: Jeff Tan &lt;jeffetan@au1.ibm.com&gt; ([`83de1bc`](https://github.com/oscal-compass/compliance-trestle/commit/83de1bcd57e279e540452802f84eb28da5d1da0d))

* feat (remote): More sftp fetcher unit tests.
Signed-off-by: Jeff Tan &lt;jeffetan@au1.ibm.com&gt; ([`0b3ede0`](https://github.com/oscal-compass/compliance-trestle/commit/0b3ede0bd0e7e0d8cc233433aa9d70dc7e691155))

* feat (remote): Removed unnecessary mkdir success check for subdirectory inside _trestle_cache_path, which would have been created successfully previously via __init__.
Signed-off-by: Jeff Tan &lt;jeffetan@au1.ibm.com&gt; ([`8f5f66b`](https://github.com/oscal-compass/compliance-trestle/commit/8f5f66b4e35c58f2d69a8de5c524b110278816be))

* feat (remote): linting and improving test code.
Signed-off-by: Jeff Tan &lt;jeffetan@au1.ibm.com&gt; ([`bef5013`](https://github.com/oscal-compass/compliance-trestle/commit/bef50133da6c306934ef8c1b8cfb5158ae2e1448))

* feat (remote): merging get_oscal and tests in.
Signed-off-by: Jeff Tan &lt;jeffetan@au1.ibm.com&gt; ([`de5bf83`](https://github.com/oscal-compass/compliance-trestle/commit/de5bf83c02f415ad06777993399121119d22ed83))

* feat (remote): cleaned up: get_oscal() doesn&#39;t need JSONDecodeError.
Signed-off-by: Jeff Tan &lt;jeffetan@au1.ibm.com&gt; ([`b84a5d1`](https://github.com/oscal-compass/compliance-trestle/commit/b84a5d17275ed8654c043a4a303a3017712cd063))

* feat (remote): get_oscal() implemented and tested, with limited linting. However, yapf did include other parts beyond get_oscal() code for both cache.py and cache_test.py
Signed-off-by: Jeff Tan &lt;jeffetan@au1.ibm.com&gt; ([`d71607c`](https://github.com/oscal-compass/compliance-trestle/commit/d71607c447d181a74600b84cea1ac1fff1d125eb))

* feat (remote): cleaned up commented region.
Signed-off-by: Jeff Tan &lt;jeffetan@au1.ibm.com&gt; ([`a73bed1`](https://github.com/oscal-compass/compliance-trestle/commit/a73bed1806db0d85487ce10b5df946077a243396))

* feat (remote): Removed unused import.
Signed-off-by: Jeff Tan &lt;jeffetan@au1.ibm.com&gt; ([`6f3a2c7`](https://github.com/oscal-compass/compliance-trestle/commit/6f3a2c72a9e0cf868a9fd4175252c957d8d2054f))

* feat (remote): Implemented base class get_raw() method with on unit tests using local fetcher.
Signed-off-by: Jeff Tan &lt;jeffetan@au1.ibm.com&gt; ([`7abf6a7`](https://github.com/oscal-compass/compliance-trestle/commit/7abf6a7c2a947d8b4043002655bdfdef5e6b87db))

* feature (remote): Fixed settings.py being inside main_test.py... ([`3dfe3b9`](https://github.com/oscal-compass/compliance-trestle/commit/3dfe3b91c049c9c69daede44b4a7fec1c398a458))

* Merge branch &#39;main&#39; into develop ([`0411969`](https://github.com/oscal-compass/compliance-trestle/commit/04119696cf646b15b3aed0933eaae95923f3af0e))

## v0.6.1 (2021-01-15)

### Chore

* chore: Updated UTs more 100% coverage (#302)

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`e77fda3`](https://github.com/oscal-compass/compliance-trestle/commit/e77fda329924230f70a18b34b63011d882ed6297))

* chore: Make fix_any deterministic in output generation (#300)

also added full coverage for snake and camel tests ([`c66292e`](https://github.com/oscal-compass/compliance-trestle/commit/c66292ece62dde1aa3df5857b890d543ee99add1))

* chore: Auto-update pre-commit hooks (#299)

Co-authored-by: github-actions[bot] &lt;41898282+github-actions[bot]@users.noreply.github.com&gt; ([`cf83024`](https://github.com/oscal-compass/compliance-trestle/commit/cf83024629b3588891273c5bdcee57d47b2e9a7c))

### Fix

* fix: Corrected branch for mkdocs deploy. (#304)

Note: Alternative techniques may be required, however, with devops integration it must be tested live.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`2dd5d93`](https://github.com/oscal-compass/compliance-trestle/commit/2dd5d93df759f9bde345ca1f8d59014d8eb15787))

* fix: Extra unit tests and cleanup to close more significant gaps (#298)

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`2abcaad`](https://github.com/oscal-compass/compliance-trestle/commit/2abcaadc1bc14419111e1778bbb1fab61d633d5e))

### Unknown

* Documentation website up and running. (#297)

Minor release: Documentation website up and running. ([`1f8b364`](https://github.com/oscal-compass/compliance-trestle/commit/1f8b364f534131678e74c05538d7db79efe5aabe))

* Merge branch &#39;main&#39; into develop ([`b984828`](https://github.com/oscal-compass/compliance-trestle/commit/b98482828d085c0ba796522b27a75c9162f86871))

## v0.6.0 (2021-01-07)

### Chore

* chore: Ensure develop is correctly updated after a release.  (#294)

* chore: Ensure develop is updated after release is completed.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* Corrected typos in PR template.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`72539c9`](https://github.com/oscal-compass/compliance-trestle/commit/72539c956be59422056bdb82143772587a9f5f05))

* chore: Add mdformat-gfm to setup.cfg (#292)

Signed-off-by: Taneli Hukkinen &lt;hukkinj1@users.noreply.github.com&gt; ([`4750882`](https://github.com/oscal-compass/compliance-trestle/commit/4750882396ea44dbfdebe8860cc527a7768a7ac6))

* chore: Auto-update pre-commit hooks (#277)

Co-authored-by: github-actions[bot] &lt;41898282+github-actions[bot]@users.noreply.github.com&gt; ([`2a2d394`](https://github.com/oscal-compass/compliance-trestle/commit/2a2d39432cd6c32c0373465eee0f84893a7f0718))

* chore: Autoformat GFM tables with mdformat-gfm (#268)

Signed-off-by: Taneli Hukkinen &lt;hukkinj1@users.noreply.github.com&gt; ([`fe4d907`](https://github.com/oscal-compass/compliance-trestle/commit/fe4d9077318fd46aab8088ad1405b6d22bb573b6))

### Documentation

* docs: Initial setup of documentation website. (#234)

* Documentation website builds. Needs significantly more content.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* Fixes missing deploy script

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* More updates to the documentation website.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* Updated contributing documentation

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* Pre-merge commit

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* Precommit update test.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* Updated documentation for basemodel

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* Added missing docs files

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* Fixing mdformatting issues with include

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* Added more api docs pages

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* chore: Fix gitignore to cover html coverage website.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* chore: Fix gitignore to cover html coverage website.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* Updates

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* Corrected poorly formatted links.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* Improvements in documentation build process.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* Basic documentation website setup complete.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* docs/cli.md

Co-authored-by: Nebula Alam &lt;anebula@au1.ibm.com&gt; ([`a51081b`](https://github.com/oscal-compass/compliance-trestle/commit/a51081bd93cb43b02135b72f00e16cf805eacba9))

### Feature

* feat: Force update of version

Version failed due to migration to &#39;main&#39; branch. ([`fc0357b`](https://github.com/oscal-compass/compliance-trestle/commit/fc0357b297bb59d64ad28af23fe2404c31364010))

* feat: Update to OSCAL 1.0.0rc1 and simplified models. (#286)

* Start using latest version of datamodel-generator

* Provide Camel and Snake conversion without datamodel-generator

* Flatten refs in schema and use latest datamodel-generator

This is not passing tests yet but may be due to other issues.
Also there may still be classes missing that should be defined.

* Better handling of corner cases.  Need forward refs.

* Now can import and fixed_any works.  Need cleanup.

* fixed fix_any to handle componentdefinition

* update dateauthorized in generators.py

* Partial resolution of issues with new version of OSCAL.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* Initial fixes to fix_any.py

* Fixes issues with the generators for constrained ints. (#279)

* Updated get_origin and other calls to ensure constrained lists are handled.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* Various updates including support for conint.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* Various updates including support for conint.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* more fixes

* Allow generators to handle cases of List[NonOscalObject] as a field. (#280)

* Updated get_origin and other calls to ensure constrained lists are handled.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* Various updates including support for conint.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* Various updates including support for conint.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* Updated generators to deal with new corner case where field is List[NonOscaObject]

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* Cleanup fix_any.  now 17 fail and 148 pass

* Updates with 12 open UT&#39;s  (#282)

* Updated get_origin and other calls to ensure constrained lists are handled.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* Various updates including support for conint.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* Various updates including support for conint.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* Updated generators to deal with new corner case where field is List[NonOscaObject]

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* Update to ensure validator passes. Refactored some yaml examples to do so.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* More test fixes

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fixes for split_test

* More UT coverage (#283)

* Updated get_origin and other calls to ensure constrained lists are handled.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* Various updates including support for conint.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* Various updates including support for conint.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* Updated generators to deal with new corner case where field is List[NonOscaObject]

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* Update to ensure validator passes. Refactored some yaml examples to do so.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* More test fixes

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* Corrected more UT&#39;s to new OSCAL models.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* Corrected more UT&#39;s to new OSCAL models.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* Updated unit tests for oscal 1.0.0rc

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* Updated unit tests for oscal 1.0.0rc with corrected behaviour.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* Updated documentation.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* Added pytest-random-order to dependencies.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* Stripped out unused functions to boost test coverage.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

Co-authored-by: FrankSuits &lt;frankst@au1.ibm.com&gt; ([`992b317`](https://github.com/oscal-compass/compliance-trestle/commit/992b31743f4d1c4ce11d5b8c1ee69995856d0056))

* feat: Distributed load and trestle merge.(#272)

* fix: reference to inexistent function

* Allow certain aliases not to be stripped on get_stripped_contextual_model

* Update merge commands on examples

* Initial unit tests for merge

* add unit test for complex merge case

* latest change

* Non-recursive merge and recursive load of distributed model implemented.

* Load distributed implemented

* Testing distributed load. adding back test data, which were mistakenly deleted

* Load distributed working fully now. Need to clean up code and write unit tests.

* Merge implementation complete.

* Code lint and formating

* Fixed Unit Tests

* More merge UTs

* Format and lint

* Restoring phantom changes from develop

* Restoring phantom changes from develop

* Revert &#34;Format and lint&#34;

This reverts commit 73ef3c83d9f5a4d071f7a422556a420d781b1306.

* Revert &#34;Restoring phantom changes from develop&#34;

This reverts commit a2b695e8dcce2b4a802438a726aabc0e0e1b8d80.

* Revert &#34;Restoring phantom changes from develop&#34;

This reverts commit eec5c1bfe0c875af3e07bb77a85e8f4342f971c4.

* Fixed fs_test

* Merge clenup

* More merge UT

* UT for load_distributed

* More MergeCmd UT

* MyPy typing

* MyPy typing

* Format and lint

* Taking out test_merge_simple_list. Test failes becaues  [role1, role2] == [role2, role1]  is False

* Taking out test_merge_simple_list. Test failes becaues  [role1, role2] == [role2, role1]  is False

* Fixing UT

* Using sorted(Path.iterdir()) to ensure order of file iteration. Should fix UTs

* QA, code clean up, typing clean up and refractor

Co-authored-by: Bruno &lt;brunomar@au1.ibm.com&gt;
Co-authored-by: Nebula Alam &lt;anebula@au1.ibm.com&gt; ([`dceae85`](https://github.com/oscal-compass/compliance-trestle/commit/dceae854c9e96ef2e66931efa9a0263b0470003e))

* feat: Misc cleanups of code for typing, unsafe functions, and other issues. (#274)

* Adding more coverage for type checking and removing conflicts.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* feat: Updating to btest compatibility with python 3.9

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* Removed depricated &#34;warn&#34; function from use

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* Update to clean up unit tests.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* More typing coverage.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`0652392`](https://github.com/oscal-compass/compliance-trestle/commit/06523929944351ce90ba83a85d57f0b04b323660))

### Fix

* fix: correct semantic release behaviour ([`c25d5be`](https://github.com/oscal-compass/compliance-trestle/commit/c25d5be7448ee956cd848a1476b5c9c70d72ab33))

* fix: Changed split to not write empty files after split. Implemented circular split-merge test (#295)

Co-authored-by: Nebula Alam &lt;anebula@au1.ibm.com&gt; ([`1ebbeb2`](https://github.com/oscal-compass/compliance-trestle/commit/1ebbeb20db1e25852dd58f7fa7a4ed909e995ef0))

* fix: Correct semantic release behaviour.

Corrected semantic release behaviour. ([`caba993`](https://github.com/oscal-compass/compliance-trestle/commit/caba993013fed5b70ced84fc58d34345e042cb6c))

* fix: Refactor to use python and pytest internals for temporary paths and creating directories.

* Refactored to use tmp_path everywhere

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* Altered unit test to only use pytest inbuilt temporary directories.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* Adding more typing and clearing up redundant functionality.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`1d99ca2`](https://github.com/oscal-compass/compliance-trestle/commit/1d99ca2ac96d76dfa777a0c514be582b382504de))

* fix: Small typo fix.

Trivial spelling fix. ([`2168bb2`](https://github.com/oscal-compass/compliance-trestle/commit/2168bb2b4d8fa79fbf93687a41265379cba608b8))

### Unknown

* Merge branch &#39;main&#39; into develop ([`df99bf8`](https://github.com/oscal-compass/compliance-trestle/commit/df99bf83c4b3326969ab31b070f71b95d38ecee4))

* Merge pull request #289 from IBM/develop

feat: Force update of version for release ([`e716524`](https://github.com/oscal-compass/compliance-trestle/commit/e716524db01f65ad0f9167143126743ea5de4be9))

* Corrected semantic release behaviour.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`c147e94`](https://github.com/oscal-compass/compliance-trestle/commit/c147e9443993c37bb484a925e4a10c195c1eb1cd))

* Merge branch &#39;main&#39; into develop ([`2c97d6c`](https://github.com/oscal-compass/compliance-trestle/commit/2c97d6c2ad0bf029a417ecfef1866d258ace201b))

* Merge pull request #288 from IBM/develop

feat: Release to support OSCAL 1.0.0rc1 ([`cbb39c4`](https://github.com/oscal-compass/compliance-trestle/commit/cbb39c4455274e9e27f335e0699eac92be25de02))

* Merge branch &#39;main&#39; into develop ([`aad7018`](https://github.com/oscal-compass/compliance-trestle/commit/aad70181dfe4b8868345010fb5fd10000bcd329a))

* Merge pull request #261 from IBM/develop

Trestle release: task and import. ([`24de68c`](https://github.com/oscal-compass/compliance-trestle/commit/24de68ccd4a23ec306137cbdf931f1de03471eb5))

* Merge pull request #264 from IBM/docs/caching-spec

docs (caching): typos and format fixes, explicit prohibition on unencrypted HTTP ([`b3fda9a`](https://github.com/oscal-compass/compliance-trestle/commit/b3fda9a4598541aaac48b65b7ae2881df3b48ea8))

* Merge branch &#39;develop&#39; into docs/caching-spec ([`c927861`](https://github.com/oscal-compass/compliance-trestle/commit/c9278611acdb2aeb809b62763e4f1fe15b66f661))

* Specs now require HTTPS for fetching, while unencrypted HTTP is not allowed.
Signed-off-by: Jeff Tan &lt;jeffetan@au1.ibm.com&gt; ([`98aabdb`](https://github.com/oscal-compass/compliance-trestle/commit/98aabdbe643d958dcaac00f9c2ff4804e2cb7c93))

* Fixed a few typos.
Signed-off-by: Jeff Tan &lt;jeffetan@au1.ibm.com&gt; ([`474f693`](https://github.com/oscal-compass/compliance-trestle/commit/474f693e56878fb1d5716a42aad09b3bdf4f0fcc))

* Fixed table.
Signed-off-by: Jeff Tan &lt;jeffetan@au1.ibm.com&gt; ([`4e78f45`](https://github.com/oscal-compass/compliance-trestle/commit/4e78f4506bb03fb0768aaaa9ea908b0a652ca630))

* feature (remote): merged remote-sftp branch and resolved... ([`c193dce`](https://github.com/oscal-compass/compliance-trestle/commit/c193dce90ecbfe2bdfbd608ff931a6728b691142))

* Merge pull request #308 from IBM/feature/remote-sftp

Feature/remote-sftp looks good to reviewer. ([`be497fc`](https://github.com/oscal-compass/compliance-trestle/commit/be497fcda82dc8a14c1dea39e6157eb215d4af3b))

* feat (remote): for sftp fetcher, linting and format fixed.
Signed-off-by: Jeff Tan &lt;jeffetan@au1.ibm.com&gt; ([`37b3543`](https://github.com/oscal-compass/compliance-trestle/commit/37b3543c7f462229566825442128c3d4b21a8ae2))

* feat (remote): for sftp fetcher, added loading of ssh key file via env var SSH_KEY, and updated testing.
Signed-off-by: Jeff Tan &lt;jeffetan@au1.ibm.com&gt; ([`b1907c0`](https://github.com/oscal-compass/compliance-trestle/commit/b1907c078137e2106d87bde330f7b473a229b49b))

* feat (remote): added more unit testing for sftp fetcher
Signed-off-by: Jeff Tan &lt;jeffetan@au1.ibm.com&gt; ([`e0351e4`](https://github.com/oscal-compass/compliance-trestle/commit/e0351e4bb79aa929312e29644f08c7c70864513e))

* feat (remote): added unit tests for sftp fetcher
Signed-off-by: Jeff Tan &lt;jeffetan@au1.ibm.com&gt; ([`19ef19b`](https://github.com/oscal-compass/compliance-trestle/commit/19ef19bcb8338650344729a350744e5ad508370c))

* feat (remote): working sftp fetcher, live tested with active ssh-agent and password-less auth
Signed-off-by: Jeff Tan &lt;jeffetan@au1.ibm.com&gt; ([`cd0725d`](https://github.com/oscal-compass/compliance-trestle/commit/cd0725d0363e0ba9a8f3832cf03268c6d3c06c7c))

* feat (remote): added more validations for sftp fetcher, and one for https, with adjustments to unit testing
Signed-off-by: Jeff Tan &lt;jeffetan@au1.ibm.com&gt; ([`d0e8304`](https://github.com/oscal-compass/compliance-trestle/commit/d0e830422446e49b6379cabf31d595cc5cc595fd))

* feat (remote): started sftp fetcher with simple validation and test, initializing cache location, but no actual fetching yet.
Signed-off-by: Jeff Tan &lt;jeffetan@au1.ibm.com&gt; ([`0a75bcb`](https://github.com/oscal-compass/compliance-trestle/commit/0a75bcb8f39da55d137acc5fc616651a5718418c))

* feature (remote): misc tweaks resulting from merge... ([`98856b9`](https://github.com/oscal-compass/compliance-trestle/commit/98856b93e9b6f819dda23a8b7976fb06eecf491d))

* feature/remote: various updates to fetchers... ([`ff1596c`](https://github.com/oscal-compass/compliance-trestle/commit/ff1596cbdd3a2ed2c15a6c2c3723f2256331d7ac))

* Merged cache_test... ([`f94f0bd`](https://github.com/oscal-compass/compliance-trestle/commit/f94f0bda54065200f022994bda86b8da0d4c68d8))

* Merge pull request #281 from IBM/feature/remote-local

LocalFetcher can now refresh cache from file:/// or absolute path source. ([`c049fa5`](https://github.com/oscal-compass/compliance-trestle/commit/c049fa5e3b41a74b333ac652232a3562fd68faa9))

* feat (remote): generic handling of paths that should also work on Windows environments, linted.
Signed-off-by: Jeff Tan &lt;jeffetan@au1.ibm.com&gt; ([`a1d8e8f`](https://github.com/oscal-compass/compliance-trestle/commit/a1d8e8f9e626677606a335c1c68974615f6cc74f))

* feat (remote): generic handling of paths that should also work on Windows environments.
Signed-off-by: Jeff Tan &lt;jeffetan@au1.ibm.com&gt; ([`80f2b8d`](https://github.com/oscal-compass/compliance-trestle/commit/80f2b8d50f72e3ed6e1fee3d2b45719a5448c269))

* feat (remote): Adjustments for Windows environment.
Signed-off-by: Jeff Tan &lt;jeffetan@au1.ibm.com&gt; ([`3cdc31f`](https://github.com/oscal-compass/compliance-trestle/commit/3cdc31f3054cc5b232d79976c47f460bb0a67923))

* feat (remote): LocalFetcher can now refresh cache from file:/// or absolute path source.
Signed-off-by: Jeff Tan &lt;jeffetan@au1.ibm.com&gt; ([`dc3f809`](https://github.com/oscal-compass/compliance-trestle/commit/dc3f80909d15e5f61617233af5c3a1b7bc6d754a))

* Progress with GithubFetcher and HTTPSFetcher... ([`f03284e`](https://github.com/oscal-compass/compliance-trestle/commit/f03284e6b1e44a7634a249e9637f1b0ecb85c21b))

* feature (remote): Merged Jeff&#39;s changes pushed to feature/remote... ([`a0bfd41`](https://github.com/oscal-compass/compliance-trestle/commit/a0bfd41ac5fe0cfa3a95d59c47e2fd29ce76fe6e))

* Merge pull request #266 from IBM/feature/remote-jeff

feat (remote): New caching code and unit tests, and bringing remote work up to sync with develop today. ([`dfdf9b4`](https://github.com/oscal-compass/compliance-trestle/commit/dfdf9b4fd661a2afb6d51054c587fd38671640f3))

* feat (remote): Synchronizing with correct develop versions of test_utils, conftest, fs and trash.
Signed-off-by: Jeff Tan &lt;jeffetan@au1.ibm.com&gt; ([`360835a`](https://github.com/oscal-compass/compliance-trestle/commit/360835a7209712a67c3dd90e47e327a8478f2bcc))

* feat (remote): Adopting trestle.utils.fs
Signed-off-by: Jeff Tan &lt;jeffetan@au1.ibm.com&gt; ([`df792bc`](https://github.com/oscal-compass/compliance-trestle/commit/df792bcddf5f30af815319c43f120ba647f838a3))

* feat (remote): Extended feature/remote cache.py and its unit test.
Signed-off-by: Jeff Tan &lt;jeffetan@au1.ibm.com&gt; ([`4712eff`](https://github.com/oscal-compass/compliance-trestle/commit/4712effe78e36eb04d9568eb0634744d6949eabb))

* Merge branch &#39;develop&#39; into feature/remote
Signed-off-by: Jeff Tan &lt;jeffetan@au1.ibm.com&gt; ([`b2d3dc4`](https://github.com/oscal-compass/compliance-trestle/commit/b2d3dc4f9664c22d60d14a96975d2fc6d4fdd1c8))

* Merge branch &#39;main&#39; into develop ([`0b0b6c4`](https://github.com/oscal-compass/compliance-trestle/commit/0b0b6c4a3dad51bdce921099906347abc0a4d7df))

## v0.4.0 (2020-11-24)

### Chore

* chore: Remove references to master branch and run releases off of &#34;main&#34; (#259)

* Remove references to master branch and run releases off of &#34;main&#34;

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* Corrected broken github header.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`c81b4ba`](https://github.com/oscal-compass/compliance-trestle/commit/c81b4ba116726189d0ced5b2a52f470afe94d29e))

* chore: Cleanup of trestle init to ensure correct return codes(#232)

* fix: Improvements in typing and return codes.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* Initial trestle create

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* Added UT file

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* Added main file to allow running as &#34;python -m trestle&#34;

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* Commit to allow merging

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* Cleaned and as expected UT failures after merge

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* Updated such that all models can generate

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* Added unit tests for generators.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* Ready for review

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* Fixed merge error

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* chore: Refactored init to use pathlib where possible

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* chore: Refactored init to use pathlib where possible

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`3c25a21`](https://github.com/oscal-compass/compliance-trestle/commit/3c25a215a1cc1d27fb0ca99a606356221e2969dd))

* chore: Auto-update pre-commit hooks (#231)

Co-authored-by: github-actions[bot] &lt;41898282+github-actions[bot]@users.noreply.github.com&gt; ([`157c9bf`](https://github.com/oscal-compass/compliance-trestle/commit/157c9bf99c279855f1027d996132777c614b750c))

* chore: Auto-update pre-commit hooks (#222)

Co-authored-by: github-actions[bot] &lt;41898282+github-actions[bot]@users.noreply.github.com&gt; ([`026541d`](https://github.com/oscal-compass/compliance-trestle/commit/026541df894be37664da9823f8ce25f8f0d1276c))

### Feature

* feat: Trestle import and unit testing

* Bringing in clean import and test.
Signed-off-by: Jeff Tan &lt;jeffetan@au1.ibm.com&gt;

* Updated logging, removed unwanted trestle init in the test that was messing up the working directory from which I run pytest.
Signed-off-by: Jeff Tan &lt;jeffetan@au1.ibm.com&gt;

* Added argument and return types.
Signed-off-by: Jeff Tan &lt;jeffetan@au1.ibm.com&gt;

* Anticipating TrestleError or some specific error in try blocks now.
Signed-off-by: Jeff Tan &lt;jeffetan@au1.ibm.com&gt;

* Linted.
Signed-off-by: Jeff Tan &lt;jeffetan@au1.ibm.com&gt;

* Fixed error logs for clarity.
Signed-off-by: Jeff Tan &lt;jeffetan@au1.ibm.com&gt;

* Simplified unnecessary try blocks with assertion on return code.
Signed-off-by: Jeff Tan &lt;jeffetan@au1.ibm.com&gt;

* Added a test for attempting to import a non-top level element.
Signed-off-by: Jeff Tan &lt;jeffetan@au1.ibm.com&gt;

* Linting.
Signed-off-by: Jeff Tan &lt;jeffetan@au1.ibm.com&gt;

* Tightened testing around just _run() for most tests, and cleaned up testing code comments.
Signed-off-by: Jeff Tan &lt;jeffetan@au1.ibm.com&gt;

* Added exception handler for file PermissionError.
Signed-off-by: Jeff Tan &lt;jeffetan@au1.ibm.com&gt;

* Removed buffer I/O used tmp_trestle_dir.dirname to put import input outside of trestle project context, and used generators for sample data.
Signed-off-by: Jeff Tan &lt;jeffetan@au1.ibm.com&gt;

* Unnecessary str().
Signed-off-by: Jeff Tan &lt;jeffetan@au1.ibm.com&gt;

* Linting.
Signed-off-by: Jeff Tan &lt;jeffetan@au1.ibm.com&gt;

* Removing tempfile from test_import_cmd.
Signed-off-by: Jeff Tan &lt;jeffetan@au1.ibm.com&gt;

* Linted.
Signed-off-by: Jeff Tan &lt;jeffetan@au1.ibm.com&gt;

* Removed use of tempfile if generated NamedTemporaryFile will be opened outside test scope, as it breaks in Windows.
Signed-off-by: Jeff Tan &lt;jeffetan@au1.ibm.com&gt;

* Testing load file failures through mocks. Added JSONDecodeError handler in import code.
Signed-off-by: Jeff Tan &lt;jeffetan@au1.ibm.com&gt; ([`81b0a3c`](https://github.com/oscal-compass/compliance-trestle/commit/81b0a3c6d3815430d1203168084907dfc239cdc7))

* feat: Trestle remove commands including unit test coverage.

* trestle remove and tests

Signed-off-by: Jeff Tan &lt;jeffetan@au1.ibm.com&gt;

* sample minimal catalog used in trestle remove testing

Signed-off-by: Jeff Tan &lt;jeffetan@au1.ibm.com&gt;

* Handling errors without messy exit. Using logger instead of warnings.
Signed-off-by: Jeff Tan &lt;jefferson.tan@gmail.com&gt;

* Type hints for the return valies added.
Signed-off-by: Jeff Tan &lt;jefferson.tan@gmail.com&gt;

* Handling errors arising from file arg.
Signed-off-by: Jeff Tan &lt;jefferson.tan@gmail.com&gt;

* Corrected log text.
Signed-off-by: Jeff Tan &lt;jefferson.tan@gmail.com&gt;

* - Testing remove() failure correctly.
- Broke up _run() failures into smaller units.
- Covered all _run() failures except plan execute().

Signed-off-by: Jeff Tan &lt;jefferson.tan@gmail.com&gt;

* Now covering 100%, tests response to failure of add_plan.execute().
Signed-off-by: Jeff Tan &lt;jefferson.tan@gmail.com&gt; ([`a09e192`](https://github.com/oscal-compass/compliance-trestle/commit/a09e192b8a9ed2e8ccf362b38b4f9b2aecef54cd))

* feat: Validation of duplicates now uses object factory (#216)

* Validation of duplicates now using object factory

* flake8 fix

* refactored and simplified validation factory

* Fixed new flake8 B015 errors

* boost duplicates_validator coverage to 100 pct ([`cf00f8b`](https://github.com/oscal-compass/compliance-trestle/commit/cf00f8bb0ea4f0a7c039e1399525ede8d8d0ace8))

* feat: Completed trestle create implementation.

* Initial trestle create

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* Added UT file

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* Added main file to allow running as &#34;python -m trestle&#34;

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* Commit to allow merging

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* Cleaned and as expected UT failures after merge

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* Updated such that all models can generate

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* Added unit tests for generators.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* Ready for review

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`a73538f`](https://github.com/oscal-compass/compliance-trestle/commit/a73538f57f5bf4142c27f65a0b05834650f00cd7))

### Fix

* fix: Generalized error expected after parent_model.oscal_read(file_path.absolute()) to handle any and return clean complaint. (#245)

Signed-off-by: Jeff Tan &lt;jefferson.tan@gmail.com&gt; ([`b92ec8b`](https://github.com/oscal-compass/compliance-trestle/commit/b92ec8b40f15f121994eeb57b36e81a3a1b4c239))

* fix: Additional test for trestle add (#227)

* fix:add. Add now creates one action plan for all given element paths, instead of individual plans for each element paths provided with -e flag.

* Formatting and liniting

* Add now works with partial models. This prevents addition to models which has already been split from the parent model

* Implemented test for  for already split models.

* Changing directory back after test

* Return code in trestle add. Fixed test.

Co-authored-by: Nebula Alam &lt;anebula@au1.ibm.com&gt;
Co-authored-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`479413f`](https://github.com/oscal-compass/compliance-trestle/commit/479413f1e0d4f90ae3c89833f71ce3fbd7a3db69))

* fix: for issue 229, another Any] still present in file (#230)

* Fix for issue 229, another Any] still present in file

* remove print() and fix typo ([`428b270`](https://github.com/oscal-compass/compliance-trestle/commit/428b270861873d5983551cd5a3d980e6dc728700))

* fix: Improvements in typing and return codes. (#224)

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`c382cb5`](https://github.com/oscal-compass/compliance-trestle/commit/c382cb593bf8b2f2b69810650320fdea544ed803))

* fix: Refactor to adopt FileContentType consistently (#223)

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`793ea7c`](https://github.com/oscal-compass/compliance-trestle/commit/793ea7c353e4445b9a8911f3455656403cca0ca0))

* fix: handle anomalous GroupItems that were generating empty classes (#220) ([`8fae9dc`](https://github.com/oscal-compass/compliance-trestle/commit/8fae9dcc74f6067fe01fae0caee167e09a8b5d0f))

### Unknown

* Trestle release 

Merging from develop for a trestle release. ([`bc877fe`](https://github.com/oscal-compass/compliance-trestle/commit/bc877febbbcf4a9e8cd179d83f68ac3e1a390034))

* feature (remote): added furl to setup requirements and began Github fetch... ([`1555f42`](https://github.com/oscal-compass/compliance-trestle/commit/1555f4286d73d0e17382328183531d7c1f897813))

* Merge branch &#39;develop&#39; into feature/remote ([`582bae2`](https://github.com/oscal-compass/compliance-trestle/commit/582bae2abe077ee9a9c353f44131951c25df8beb))

* Initial implementation of trestle task interface and sample task for testing.

* Initial set of trestle task docs.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* Additional details for tasks.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* Initial implementation of trestle tasks. To be thoroughly tested.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* Initial implementation of trestle tasks. To be thoroughly tested.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* Stuff.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* Altered logging behaviour to use improved logger.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* Corrected unit tests

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* Ready for merge - first trestle tasks.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* Merged in removed and updated with appropriate logging changes

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* Corrected behaviour.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`d38d933`](https://github.com/oscal-compass/compliance-trestle/commit/d38d933b92e0f61f235532ade74d92e173d66349))

* Merge pull request #229 from IBM/fix/missing_main

Added missing main file for running as a module. ([`d8c0683`](https://github.com/oscal-compass/compliance-trestle/commit/d8c0683a36ea8835b9e50358fb161831df6840ad))

* Added missing main file for running as a module.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`93f8e0a`](https://github.com/oscal-compass/compliance-trestle/commit/93f8e0a90fcaaeac105fffb3c77360ee1d029333))

* fix:add. Add now creates one action plan for all given element paths, instead of individual plans for each element paths provided with -e flag.

* fix:add. Add now creates one action plan for all given element paths, instead of individual plans for each element paths provided with -e flag.

* Formatting and liniting

* Add now works with partial models. This prevents addition to models which has already been split from the parent model

Co-authored-by: Nebula Alam &lt;anebula@au1.ibm.com&gt;
Co-authored-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`f33eeda`](https://github.com/oscal-compass/compliance-trestle/commit/f33eeda6bf83c43269175fa03bbab4dddce4a87a))

* Added test skeleton

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`d839b9b`](https://github.com/oscal-compass/compliance-trestle/commit/d839b9bb1ad2243ed20d0f2dee3409ed0a4db88c))

* Initial implementation of trestle caching for local fs complete.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`d01dfb5`](https://github.com/oscal-compass/compliance-trestle/commit/d01dfb5f3991701cb06a1f7735d94aba8fa5e98e))

* Merge branch &#39;master&#39; into develop ([`a99b19c`](https://github.com/oscal-compass/compliance-trestle/commit/a99b19c096322e94d24977572691ca4a8c927251))

## v0.3.0 (2020-10-26)

### Chore

* chore: Auto-update pre-commit hooks (#210)

Co-authored-by: github-actions[bot] &lt;41898282+github-actions[bot]@users.noreply.github.com&gt; ([`daa70dc`](https://github.com/oscal-compass/compliance-trestle/commit/daa70dceaae62d1ae7576d19cb9c024deabf02cf))

* chore: Adding interface for representing assembly of oscal models. (#198)

* Created initial interface for exchanging oscal model trees

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* Added tests for interface and cleaned up code formatting

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* Updated interface name to better reflect funcionality.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* Updated unit tests to correct for name change.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`46934bc`](https://github.com/oscal-compass/compliance-trestle/commit/46934bc700c18d04f9e34d7783b1bf673428b0c1))

* chore: Auto-update pre-commit hooks (#191)

Co-authored-by: github-actions[bot] &lt;41898282+github-actions[bot]@users.noreply.github.com&gt;
Co-authored-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`412edc0`](https://github.com/oscal-compass/compliance-trestle/commit/412edc0a1cddedfb3f6b82cb3125d2b9f69917c2))

* chore: Separating pre-commit actions and creating an automatic update of precommit (#187)

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`52b4eb7`](https://github.com/oscal-compass/compliance-trestle/commit/52b4eb7943acdcd8a0dcc49070b58648b6fd7dc9))

* chore: Allow changelog to be automatically populated by semantic-release (#185)

Signed-off-by: Nebula Alam &lt;anebula@au1.ibm.com&gt; ([`1187d7c`](https://github.com/oscal-compass/compliance-trestle/commit/1187d7c7a42164ce7bf165b04117e66cd4d6ddd7))

* chore: Ensuring DCO bot does not limit core team access. (#183)

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`40adb2d`](https://github.com/oscal-compass/compliance-trestle/commit/40adb2d9a7c9ee06de86d39c9490d867bc8198d3))

* chore: Add github static analysis (#153)

Co-authored-by: Bruno &lt;bruno.assis.marques@gmail.com&gt; ([`3d27204`](https://github.com/oscal-compass/compliance-trestle/commit/3d272047c5014e836d93215f925ce0df7c5bdd1c))

### Documentation

* docs: Updated developer documentation with DCO and merge workflow.

* docs: Updated developer docs with workflow and DCO both requirements.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* docs: Updated developer docs with workflow and DCO both requirements.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`041a7aa`](https://github.com/oscal-compass/compliance-trestle/commit/041a7aa8b2183a261827e5ee9d7d562849329e12))

* docs: Initial caching structure documentation (#143)

* Initial cachinng structure documentation

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* Updated caching documentation

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* Updated caching documentation

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

Co-authored-by: Bruno &lt;bruno.assis.marques@gmail.com&gt; ([`d1a73f3`](https://github.com/oscal-compass/compliance-trestle/commit/d1a73f314d42201fb7b9cbe79775a41b465ef6c7))

* docs: Updated readme to document current level of support for file formats (#179)

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

Co-authored-by: Bruno &lt;bruno.assis.marques@gmail.com&gt; ([`1df2110`](https://github.com/oscal-compass/compliance-trestle/commit/1df2110eb9fb89816871ce70ceb72d5f3be18049))

* docs: change of trestle model directory structure (#169)

* update project model structure

* Update directory structure on examples

* Update test data examples on split and merge

Fixes #162

Signed-off-by:: Bruno &lt;brunomar@au1.ibm.com&gt; ([`ed2ab36`](https://github.com/oscal-compass/compliance-trestle/commit/ed2ab36c64ddb45297974bb851819322477c0fd2))

### Feature

* feat(trestle add): Implements `add` functionality for trestle cmd. (#184)

* Implement `trestle add` for adding child models with default values to parent models.
* Helper functions to get model type given parent element and target element path. 
* Helper to create object of given model with default values.
* Unit tests for the helpers and trestle add methods.
* Bug fix in `Element().py.set_at()` for setting collection type objects.

Authored-by: Nebula Alam &lt;anebula@au1.ibm.com&gt; ([`eb42656`](https://github.com/oscal-compass/compliance-trestle/commit/eb42656c60c0697ff2de806d4a57ee7b246363de))

### Fix

* fix: Versioning tag was malformed. (#199) (#200)

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`957fe0b`](https://github.com/oscal-compass/compliance-trestle/commit/957fe0bf08a358e5ab21eb93c60dba65cc486b24))

* fix: Versioning tag was malformed. (#199)

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`5c84d59`](https://github.com/oscal-compass/compliance-trestle/commit/5c84d59c539773b18709968405cbe77ce27e6a99))

* fix: support contextual element path like groups.* during split (#192)

Signed-off-by: Lenin Mehedy &lt;lenin.mehedy@au1.ibm.com&gt; ([`c9536b2`](https://github.com/oscal-compass/compliance-trestle/commit/c9536b2bcc6404fa9dab8787fcbf97e8590e4402))

* fix: correct directory names of sub models during split (#189)

based on the trestle spec, `catalog/groups/00000__group.json` file should be split into a directory called `catalog/groups/00000__group/` and original group file remaining in `catalog/groups/00000__groups.json`

Signed-off-by: Lenin Mehedy &lt;lenin.mehedy@au1.ibm.com&gt; ([`6b18237`](https://github.com/oscal-compass/compliance-trestle/commit/6b18237fda53f91f936fc122fdbf74da8e4db65e))

* fix: reference to inexistent function (#182)

Signed-off-by: Bruno &lt;brunomar@au1.ibm.com&gt; ([`9605a51`](https://github.com/oscal-compass/compliance-trestle/commit/9605a5101507e3d1c79218328424bdf115c435ca))

* fix: infer wrapper alias from input in Element constructor ([`82820fd`](https://github.com/oscal-compass/compliance-trestle/commit/82820fde423c1982a5aa02965d897f04093187bb))

* fix: explicitly use contextual_model argument in path parsing util function

This is to avoid calling `pathlib.Path.cwd()` inside the function that breaks unit tests or assumes caller has changed directory to a trestle project ([`1ae3b12`](https://github.com/oscal-compass/compliance-trestle/commit/1ae3b12e8a3786aa8f7516ca631070fb289be949))

* fix: do not create empty place holder file after splitting a dict or list ([`cb9fa8b`](https://github.com/oscal-compass/compliance-trestle/commit/cb9fa8be810c915198b094785ce581b89a54ce99))

* fix: create main model alias directory during split

If we split a catalog, the sub element files should be in `catalogs/` directory. If we split `catalog/medata.json`, it&#39;s sub elements should be put under `catalogs/metadata/` directory. ([`7656e42`](https://github.com/oscal-compass/compliance-trestle/commit/7656e420acedf5b2e61c5fb27b448196a362c521))

* fix: incorrect file indexing during split #148

When a list item is split the file index should have 5 digits instead of 4 digits. ([`ad7b2e6`](https://github.com/oscal-compass/compliance-trestle/commit/ad7b2e63125fa3508254bd0c579e072f1e260fad))

* fix: utility method to write/read Oscal List and Dict object to/from file correctly (#161)

* simplify oscal_read

* fix logic to handle list/dict files.

* simplify logic of to_json and support read and write of dict/list files

* add alias_to_classname function

* add support to generate OscalBaseModel wrapper models for get_stripped_contextual_model

* increase test coverage

* fix comment from comma-separated to dot-separator

* fix pip permission error when running check on windows

Fixes #120 

Signed-off-by: Bruno &lt;brunomar@au1.ibm.com&gt; ([`43c7bdf`](https://github.com/oscal-compass/compliance-trestle/commit/43c7bdf5c30d88056999776e5df5fc9957842122))

* fix: Updating fetch of NIST content.

* Initial set of pretty badges

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* Updated nist source and added oscal-content as a submodule. Also updated the gen-oscal script to ensure currency

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`85a852a`](https://github.com/oscal-compass/compliance-trestle/commit/85a852a20fa33c1546a7f6cc64201809fb845fea))

* fix: Merge pull request #158 from IBM/fix/issue_149b

chore: merging hotfix back into develop ([`75b11ca`](https://github.com/oscal-compass/compliance-trestle/commit/75b11ca91e0a23778511ac285b4655fbe12bd9f8))

### Refactor

* refactor: adjust contextual helper methods for new structure (#180)

Signed-off-by: Bruno &lt;brunomar@au1.ibm.com&gt; ([`5f14767`](https://github.com/oscal-compass/compliance-trestle/commit/5f14767166567f529e0dd28dcddb076c168ceece))

* refactor: rename fixture name for sameple_target to sample_target_def ([`788510b`](https://github.com/oscal-compass/compliance-trestle/commit/788510b08dd836e1dfce92520a8517cd345b524d))

### Unknown

* fix:add (#208)

Trestle `add` now creates one action plan for all given element paths, instead of individual plans for each element paths provided with -e flag.

Co-authored-by: Nebula Alam &lt;anebula@au1.ibm.com&gt;
Co-authored-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`bcbdae8`](https://github.com/oscal-compass/compliance-trestle/commit/bcbdae86a9ec8844208d9368b8b48429ed25c3ed))

* Merge branch &#39;master&#39; into develop ([`4d77545`](https://github.com/oscal-compass/compliance-trestle/commit/4d7754504591239eca3af9bdf54f452e90f5eb8d))

* Merge pull request #197 from IBM/develop

Merge for release ([`fe784d8`](https://github.com/oscal-compass/compliance-trestle/commit/fe784d84912bbd3c00b3b1651c9fd657abca05df))

* [ImgBot] Optimize images (#190)

/docs/assets/Canonical_trestle_auditree_workflows.png -- 236.06kb -&gt; 158.11kb (33.02%)

Signed-off-by: ImgBotApp &lt;ImgBotHelp@gmail.com&gt;

Co-authored-by: ImgBotApp &lt;ImgBotHelp@gmail.com&gt;
Co-authored-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`ad238c8`](https://github.com/oscal-compass/compliance-trestle/commit/ad238c84b5999f1c650109f7e61b276faf4d1b53))

* feature: introducing mandatory mypy typing. (#174)

* Basic mypy setup

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* Added code typing support to build pipeline checks

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* Partial completion of mypy first pass.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* Updated get_stripped_contextual_model

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* Partial update towards zero mypy errors

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* updates

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* Altered cicd to be permissive

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* Altered cicd to be permissive

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* Fixed UT&#39;s related to split

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* Updated mypy conf to be a balanced severity

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`ebde8e5`](https://github.com/oscal-compass/compliance-trestle/commit/ebde8e546bb5d3cb4ddb27f60b4ca0cbcd52f9c5))

* Feature/validate intra (#188)

* Initial implementation of has_no_duplicate_elements

* renamed find_values_by_name_generic to convey not just pydantic objects

* Simplify parsing tests and use new read/write oscal methods

* Manually edit duplicate uuid&#39;s

* add tests for duplicate uuids

* added tools and tests to find duplicate values of specified pydantic type

* better naming of test files and edited uuids

* better implementation of get_values_by_name using fields_set

* Prepare for cli validation

* initial connection to cli

* initial integration of validate test into cli

* Added validation test to cli and refactored

* refactored

* finalized dup uuid validation with doc

* get alias from class

Co-authored-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`b4b7090`](https://github.com/oscal-compass/compliance-trestle/commit/b4b709059b35f1b33860bec89c9aa5ecc836ec9c))

* feature: implement trestle trash and RemovePathAction #69 (#186)

* refactor: create trestle trash util module

* feature: implement move_dir_to_trash and tests

* feature: more functionalities in trestle trash module

* feature: unit tests for trash recovery methods

* feature: implement RemovePathAction ([`bcd19b5`](https://github.com/oscal-compass/compliance-trestle/commit/bcd19b561ce40af78fd9d95ff3cc17b782e37a3c))

* Merge pull request #171 from IBM/fix/sub_model_split_154

fix: subsequent sub model split #154 ([`02bc9e1`](https://github.com/oscal-compass/compliance-trestle/commit/02bc9e16be9d721ce372ecd308374a9509443451))

* Implement unit test and improve coverage #172 ([`10a441f`](https://github.com/oscal-compass/compliance-trestle/commit/10a441f68b68ac0982fde6330789f0df46330c43))

* remove unused function ([`561c430`](https://github.com/oscal-compass/compliance-trestle/commit/561c4304d6583a38e416ccab91123de5178c321f))

* Split should support chained element paths for multi-level split #172 ([`4e25e4f`](https://github.com/oscal-compass/compliance-trestle/commit/4e25e4f7cc0a50f17beab4cb8bcdaf12ca956c45))

* Merge branch &#39;develop&#39; into fix/sub_model_split_154 ([`4e8bb8c`](https://github.com/oscal-compass/compliance-trestle/commit/4e8bb8c135dc77a69b530970957b03c4220b5bd5))

* Stop generation of timestamp in oscal files, import conlist as needed, fix regex strings (#173) ([`c731c33`](https://github.com/oscal-compass/compliance-trestle/commit/c731c336edab83ff888b399be0a5f0f891d0528d))

* only support split of first level childrent of a model ([`ef933d0`](https://github.com/oscal-compass/compliance-trestle/commit/ef933d0c0beec7c1c5f056004c6b241fe6c38ef2))

* add fixture for sample catalog and split unit test for catalog model ([`c923a99`](https://github.com/oscal-compass/compliance-trestle/commit/c923a998c5c75cc274bb0483b1f887b4a0da6351))

* refactor split tests ([`84bcd9f`](https://github.com/oscal-compass/compliance-trestle/commit/84bcd9f239a3a05caa709de5113deccb685f3c58))

* fix unit tests ([`0d9bc0d`](https://github.com/oscal-compass/compliance-trestle/commit/0d9bc0d997734ce0824bba2bb44a0aa0b145c79b))

* Merge branch &#39;develop&#39; into fix/sub_model_split_154 ([`bc912ce`](https://github.com/oscal-compass/compliance-trestle/commit/bc912ce091aaaabcf6a8bd259a4fd1248b4f95ae))

* Merge pull request #160 from IBM/feature/clear_content_159

CreatePathAction should have an option to clean the content of a file if it exists #159 ([`19018e2`](https://github.com/oscal-compass/compliance-trestle/commit/19018e2c1cd969887d08bf79805f9382ac32e14d))

* Add unit test for directory ([`1338b1f`](https://github.com/oscal-compass/compliance-trestle/commit/1338b1fc4c2232ec6cfb1d0bcf5d177a46dcd1c7))

* Include an option to clear content in CreatePathAction

https://github.com/IBM/compliance-trestle/issues/159 ([`f31a800`](https://github.com/oscal-compass/compliance-trestle/commit/f31a8007c311784ce914811ff0e9ef70eb1e6438))

* Merge branch &#39;develop&#39; into fix/issue_149b ([`24a51f3`](https://github.com/oscal-compass/compliance-trestle/commit/24a51f380be2aedcde397b45dbcccda37cfb000a))

* Merge pull request #157 from IBM/master

Master ([`84e8882`](https://github.com/oscal-compass/compliance-trestle/commit/84e8882bfce7a82be75ec60aea35cdcc0ac187f9))

## v0.2.2 (2020-10-15)

### Fix

* fix: Merge pull request #155 from IBM/fix/issue_149b

Fix/issue 149b - convert Union[A, A] to Union[A, conlist(A, min_items=2)]

closes #149 ([`7ded03e`](https://github.com/oscal-compass/compliance-trestle/commit/7ded03e92e0b3fc8a6b9ef4e7fb4294bbd26b0b5))

### Unknown

* bugfix issue 149 - Union[A, A] -&gt; Union[A, conlist(A, min_items=2)] ([`4f6f6a9`](https://github.com/oscal-compass/compliance-trestle/commit/4f6f6a970dcf0919d3a33500544a54651df92b07))

## v0.2.1 (2020-10-14)

### Fix

* fix: Merge pull request #144 from IBM/fix/issue_138_b

fix for issue #138  forward references in assessment_results ([`153b752`](https://github.com/oscal-compass/compliance-trestle/commit/153b752b0de05baa616ac8d83a107eeaa30b0e63))

### Unknown

* fix for issue 138 forward references in assessment_results ([`f0aeaf3`](https://github.com/oscal-compass/compliance-trestle/commit/f0aeaf35be82203adb308ed6bfa24e7bf65caa29))

## v0.2.0 (2020-10-12)

### Documentation

* docs: Update readme to reflect alpha status. (#134)

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`8ef9762`](https://github.com/oscal-compass/compliance-trestle/commit/8ef9762ccb015d3a5e2b5c3e9d119e7cbca76c43))

### Fix

* fix: Coding formating failure on merge from master

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`3e00d5d`](https://github.com/oscal-compass/compliance-trestle/commit/3e00d5d76e2fd3018604b4f88a8bd83d07b35f60))

### Unknown

* Merge pull request #129 from IBM/develop

Release to master ([`e164c3d`](https://github.com/oscal-compass/compliance-trestle/commit/e164c3dc331c6b1abe6daf60de55276ab1e56b8a))

* Unit test for the bug fix ([`7da40fe`](https://github.com/oscal-compass/compliance-trestle/commit/7da40fee88489721c169386d3c578d668eef8021))

* Handle multiple element paths argument consistently during split #146 (#147) ([`8d7943a`](https://github.com/oscal-compass/compliance-trestle/commit/8d7943a537bb9e8191657245e6a2be2cdeddc729))

* add a few more helpers (#151) (#152)

* add is_valid_project_model_path, get_project_model_path

* move get_singular_alias to fs module

* update parse_element_arg to be context aware when using get_singular_alias

* refactor import of cmd_utils

Co-authored-by: Bruno &lt;brunomar@au1.ibm.com&gt; ([`f766486`](https://github.com/oscal-compass/compliance-trestle/commit/f766486eabe4e50bf3817eedf8cc65a2f50f839d))

* Merge pull request #141 from IBM/feature/split_merge_add

Trestle split and foundational functionalities ([`251079f`](https://github.com/oscal-compass/compliance-trestle/commit/251079fceba1bc80283a064dd6de304733c7c42b))

* Merge branch &#39;develop&#39; into feature/split_merge_add ([`5db28de`](https://github.com/oscal-compass/compliance-trestle/commit/5db28de545e200a0e4e90a279fc46b0a19a2205f))

* Extend functionality for detecting duplicate values in pydantic objects (#105)

* Initial implementation of has_no_duplicate_elements

* renamed find_values_by_name_generic to convey not just pydantic objects

* Simplify parsing tests and use new read/write oscal methods

* Manually edit duplicate uuid&#39;s

* add tests for duplicate uuids

* added tools and tests to find duplicate values of specified pydantic type

* better naming of test files and edited uuids

* better implementation of get_values_by_name using fields_set

* Prepare for cli validation

* initial connection to cli

* initial integration of validate test into cli

* Added validation test to cli and refactored

Co-authored-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`b0e3558`](https://github.com/oscal-compass/compliance-trestle/commit/b0e3558b3f1ce6332f7db199a017986eda27e362))

* Fixed regex escape seq. so can again block w605 errors - issue 115 (#135)

Co-authored-by: Lenin Mehedy &lt;lenin.mehedy@au1.ibm.com&gt; ([`c3b292f`](https://github.com/oscal-compass/compliance-trestle/commit/c3b292fe4deeeed1ebcd765d7e6777b8eb08fdfd))

* Merge pull request #131 from IBM/enhancement/5c

From develop, fix_any.py now adds a license header to output files. ([`4aaa89d`](https://github.com/oscal-compass/compliance-trestle/commit/4aaa89d420709311912d8bd51c617694e7f718b7))

* Merge branch &#39;develop&#39; into enhancement/5c ([`c0fe5f0`](https://github.com/oscal-compass/compliance-trestle/commit/c0fe5f00626d0b64c026ab31d24d45d3e0af8836))

* Merge branch &#39;develop&#39; into enhancement/5c ([`55230a7`](https://github.com/oscal-compass/compliance-trestle/commit/55230a7a5870c1f2596eac8c0757002fc8f68ce8))

* Regenerated models in trestle/oscal/ ([`31c9382`](https://github.com/oscal-compass/compliance-trestle/commit/31c9382cab3291b81e1fcd2f507e3603b47ba588))

* Fixed missing newlines for copyright text. ([`e4ffad6`](https://github.com/oscal-compass/compliance-trestle/commit/e4ffad6bb0ddee292a75e7358426f4e1ed687ad3))

* From develop, fix_any.py now adds a license header to output files. ([`ce4806d`](https://github.com/oscal-compass/compliance-trestle/commit/ce4806d80319fee334e395b7c31e5727806af3ab))

* Use get_stripped_contextual_model (#140) ([`b045583`](https://github.com/oscal-compass/compliance-trestle/commit/b045583e6d6ba7b411669208b68814e71cbe506b))

* add get_stripped_contextual_model helper (#137)

* add get_stripped_contextual_model helper

Co-authored-by: Bruno &lt;brunomar@au1.ibm.com&gt; ([`481f691`](https://github.com/oscal-compass/compliance-trestle/commit/481f6916745657befc96b04e9eded9c520f9b910))

* Merge pull request #139 from IBM/feature/split-cmd

Fix recursive model split for a chain of paths ([`88fd9c5`](https://github.com/oscal-compass/compliance-trestle/commit/88fd9c5579268f33ed59f103f9121bc0a7507fb3))

* Fixed typo ([`9b17ae3`](https://github.com/oscal-compass/compliance-trestle/commit/9b17ae35d9686d264875afe59bb3e0d05df42628))

* Update example in method description for clarity ([`6209113`](https://github.com/oscal-compass/compliance-trestle/commit/62091130e47c21dc2c52aad0dd684fd233aa1742))

* Fix typo and update comment ([`6fcd392`](https://github.com/oscal-compass/compliance-trestle/commit/6fcd3926cb8fdeac3e47e879cee7a5e5701201ae))

* Merge branch &#39;feature/split_merge_add&#39; into feature/split-cmd ([`21aa9e8`](https://github.com/oscal-compass/compliance-trestle/commit/21aa9e8ab6e9e2d030b1d260d6a53ddb923157f8))

* Catch exception during Plan simulation and always run rollback ([`7845f68`](https://github.com/oscal-compass/compliance-trestle/commit/7845f68e672f704e6c82a58ff450e10d9b539b71))

* Fix recursive model split for a chain of paths ([`ecfed54`](https://github.com/oscal-compass/compliance-trestle/commit/ecfed5432fb1a1eefb0e39d296044ea07f76af1f))

* Reuse to_json method to reduce code duplication ([`b2549cf`](https://github.com/oscal-compass/compliance-trestle/commit/b2549cf40cb54df30800ae7950b97b75ea5e6413))

* Fix parent model name in the element path during parsing ([`ebc8474`](https://github.com/oscal-compass/compliance-trestle/commit/ebc8474e6b873022a0f2cd221bfc3f31201f607e))

* Fix getting full element path recursively ([`897d2d2`](https://github.com/oscal-compass/compliance-trestle/commit/897d2d25cc9fcc56de0afb6a43d6705fd3bf380b))

* Merge branch &#39;feature/split_merge_add&#39; into feature/split-cmd ([`139983d`](https://github.com/oscal-compass/compliance-trestle/commit/139983dd5f6af84c26bed31f19ed7847ebe58f02))

* add get_singular_alias helper (#136)

* add get_singular_alias helper

Co-authored-by: Bruno &lt;brunomar@au1.ibm.com&gt; ([`984c94c`](https://github.com/oscal-compass/compliance-trestle/commit/984c94c3faa72ac506a1aa26f4555b2cd610afe1))

* Merge pull request #133 from IBM/feature/split_merge_add

Merge latest code into develop ([`1153584`](https://github.com/oscal-compass/compliance-trestle/commit/115358414db57195d5c3d0215899c16c69224dce))

* Merge branch &#39;develop&#39; into feature/split_merge_add ([`7800622`](https://github.com/oscal-compass/compliance-trestle/commit/7800622a537a6b882b66a3859fac72b048e0d95a))

* Implement multi-level recursive split ([`dac9e3e`](https://github.com/oscal-compass/compliance-trestle/commit/dac9e3e546eb135dbcff678b49ae33cdc734794c))

* Each element path must have its root model as the path prefix ([`e1cf697`](https://github.com/oscal-compass/compliance-trestle/commit/e1cf69767a015ac657b8c9fa17e810eeea60e019))

* Merge branch &#39;feature/split_merge_add&#39; into feature/split-cmd ([`c90533c`](https://github.com/oscal-compass/compliance-trestle/commit/c90533c873768e7b49edbadc932c59d9a32690bd))

* Merge develop ([`18d1086`](https://github.com/oscal-compass/compliance-trestle/commit/18d10865e90f0a6ac4171f3fe35bbc0e85ce3910))

* Merge branch &#39;master&#39; into develop ([`863ad75`](https://github.com/oscal-compass/compliance-trestle/commit/863ad75637c31de19908847d8a671e45d8beb084))

## v0.1.1 (2020-10-05)

### Fix

* fix: Corrected typing of parameter-settings in profile and ssp (#97)

* fix: Corrected typing of parameter-settings in profile.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* Added error which was missed in original hotfix

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`9a5ef55`](https://github.com/oscal-compass/compliance-trestle/commit/9a5ef55d9d504f3e32b73277f116172e05281081))

### Unknown

* Correcting missed pre-commit change that broke build process. (#102)

Signed-off-by: Nebula Alam &lt;anebula@au1.ibm.com&gt; ([`7c1820d`](https://github.com/oscal-compass/compliance-trestle/commit/7c1820dbfdd23c3ca0ed592b369a69f056b81c3f))

## v0.1.0 (2020-09-23)

### Chore

* chore: Depricating methods and adding unit tests.

Deprecated parser methods which are being replaced by methods inside of OscalBaseModel. Extra methods added to utils.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`0fd0d45`](https://github.com/oscal-compass/compliance-trestle/commit/0fd0d4536550d08b5639c9fe511acc30694c2056))

* chore: Add windows support to CICD and associated test



Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`b6f2203`](https://github.com/oscal-compass/compliance-trestle/commit/b6f2203c175d12a1820047ff310077ea27b1c983))

### Documentation

* docs: Updated documentation with a short description of target (#90)

* Updated documentation with a short description of target

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`bcd20dc`](https://github.com/oscal-compass/compliance-trestle/commit/bcd20dc0d117835347f9b9ee736ae4106fe12326))

### Feature

* feat: Merge pull request #65 from IBM/develop

Releasing trestle init along with updated object model. ([`0f8b637`](https://github.com/oscal-compass/compliance-trestle/commit/0f8b637d897689450907eca4e7add1dda2016dcd))

* feat: Windows support declared for trestle (#88)

* Updating setup.cfg to cover windows support and other classifier flags from trove

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* Corrected typo which snuck into build.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

Co-authored-by: NEBULA ALAM &lt;nebula.alam@gmail.com&gt; ([`56bdfa2`](https://github.com/oscal-compass/compliance-trestle/commit/56bdfa2b7e3d7365b516d79beae1ec2a2d0855e0))

### Fix

* fix: Fix forward references caused by fix_any.py issue #108 (#111)

* Initial implementation of has_no_duplicate_elements

* renamed find_values_by_name_generic to convey not just pydantic objects

* Simplify parsing tests and use new read/write oscal methods

* Manually edit duplicate uuid&#39;s

* add tests for duplicate uuids

* added tools and tests to find duplicate values of specified pydantic type

* better naming of test files and edited uuids

* better implementation of get_values_by_name using fields_set

* Prepare for cli validation

* Allow escape sequences for regex

* Fix forward references caused by fix_any.py ([`447a6ab`](https://github.com/oscal-compass/compliance-trestle/commit/447a6aba592eba8934a3aa477e48bd409b18cdd4))

### Unknown

* Edit and proofread README and CONTRIBUTING (#106)

* Edit and proofread README and CONTRIBUTING

* fixed typo implicitly

Co-authored-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`6473d92`](https://github.com/oscal-compass/compliance-trestle/commit/6473d9216af4f6a791332c3a3ac6abbd09bb0848))

* utils.py cleanup (#127)

* remove contextual functions from utils.py

Co-authored-by: Bruno &lt;brunomar@au1.ibm.com&gt; ([`7bcee56`](https://github.com/oscal-compass/compliance-trestle/commit/7bcee5654814ba38af99970e75b0b04f1f6b11b9))

* utils.py cleanup (#123)

* move functions to core/utils to solve circular dependencies

* move functions to core/utils to solve circular dependencies

* initial list of contextual_path is not mandatory

* make initial list of get_contextual_path function not mandatory

* add unit tests for a few utils functions

* implement get_contextual_model_type

* remove get_fields_by_alias and alias_to_fields_map duplication

Co-authored-by: Bruno &lt;brunomar@au1.ibm.com&gt; ([`f8cf921`](https://github.com/oscal-compass/compliance-trestle/commit/f8cf9213d95b79c7c2f00c2722245a9275e3a94e))

* Merge branch &#39;feature/split_merge_add&#39; into feature/split-cmd ([`49015cb`](https://github.com/oscal-compass/compliance-trestle/commit/49015cba8e28ca943e2116272cd9a9c02839f07c))

* remove get_fields_by_alias and alias_to_fields_map duplication (#121)

* implement get_contextual_model_type

* remove get_fields_by_alias and alias_to_fields_map duplication

Co-authored-by: Bruno &lt;brunomar@au1.ibm.com&gt; ([`9e59cea`](https://github.com/oscal-compass/compliance-trestle/commit/9e59ceaf8a7d6885fc88374b49acafc3201851bf))

* Merge branch &#39;feature/split_merge_add&#39; into feature/split-cmd ([`05e822b`](https://github.com/oscal-compass/compliance-trestle/commit/05e822b9d0af5c30743ee0d70efa9315142f26a2))

* implement get_contextual_model_type (#119)

* move functions to core/utils to solve circular dependencies

* move functions to core/utils to solve circular dependencies

* initial list of contextual_path is not mandatory

* make initial list of get_contextual_path function not mandatory

* add unit tests for a few utils functions

* implement get_contextual_model_type

Co-authored-by: Bruno &lt;brunomar@au1.ibm.com&gt; ([`1622abc`](https://github.com/oscal-compass/compliance-trestle/commit/1622abc16ebacd0adb75f5a5b31aeb4f69f4560a))

* Use yaml target-definition example as test data ([`b20de0c`](https://github.com/oscal-compass/compliance-trestle/commit/b20de0c3c4e3c591414bb3addf89cc54dcd85792))

* Merge branch &#39;feature/split_merge_add&#39; into feature/split-cmd ([`9b696bf`](https://github.com/oscal-compass/compliance-trestle/commit/9b696bfc0c32d2fbdb274891156b1bde21d3da41))

* Fix element and multilevel split command (#117)

* Fix typo

* Handle parent path of an element_path and handle the root model name

* Implement helper method to convert element_path to a file_path

* Implement helper method for root path of an element path

* Fix tests

* Fix mypy warnings

* Implement utility function to copy availble values from src to dest model

* Tentative tests for split_model as part of TDD

* Implement stripped_instance method

* Refactor FileContentType into a new file

* Fix to_root_path method

* First implementation of split_model with unit test

* Implement split of a multi item dict

* Fix file index for splitted list items

* Update trestle split run method to execute the plan

* Fix plan simulate method

* Fix trestle split run

* Fix splitted model creation

* Update comment

* Implement the ability to move file to trestle trash

* Fix bug in finding trestle project root

* Fix code lint

* Integration test for trestle split command

* Helper methods to get attribute value by field or field alias

* Element get_at should return value by field alias

* Fix typo

* Correct test method doc block

* Fix Element get_at for dictionary type

* Additional test case for list element for element.get_at

* Initial implementation of multi level recursive split ([`47a00f2`](https://github.com/oscal-compass/compliance-trestle/commit/47a00f2dc919163678195616e309ceca2d58ea6a))

* Merge branch &#39;feature/split_merge_add&#39; into feature/split-cmd ([`486c063`](https://github.com/oscal-compass/compliance-trestle/commit/486c063360293adc43d796f2811f7fb536ed4f88))

* Integration test for trestle split and fix to Element.get_at (#116) ([`16c4324`](https://github.com/oscal-compass/compliance-trestle/commit/16c432451d503d5c3850d0755c5e5d891dca2da4))

* Initial implementation of multi level recursive split ([`84d54d3`](https://github.com/oscal-compass/compliance-trestle/commit/84d54d3765cc1367ddd4bc5acbfc7f4a463c9d75))

* Additional test case for list element for element.get_at ([`5f39102`](https://github.com/oscal-compass/compliance-trestle/commit/5f3910277c45e9ec437e6392583a4e4450c97a67))

* Fix Element get_at for dictionary type ([`1c52b21`](https://github.com/oscal-compass/compliance-trestle/commit/1c52b21e5a2714dbd153f9350fc307fcd3cfc87a))

* Correct test method doc block ([`adda36d`](https://github.com/oscal-compass/compliance-trestle/commit/adda36d4f9be1860701b3937f65a4c00e02c077f))

* Fix typo ([`62e3234`](https://github.com/oscal-compass/compliance-trestle/commit/62e3234faedd17d7008f1fa4dd471dc40777260a))

* Element get_at should return value by field alias ([`27ad035`](https://github.com/oscal-compass/compliance-trestle/commit/27ad035cb7721bc83173fdceee38e55ea51b5481))

* Helper methods to get attribute value by field or field alias ([`0fb0b7f`](https://github.com/oscal-compass/compliance-trestle/commit/0fb0b7ffdf4f552d4c13732e524264455bd1e6f8))

* Integration test for trestle split command ([`dd1fecb`](https://github.com/oscal-compass/compliance-trestle/commit/dd1fecb95912349678a0be0243b39e73f2d917b6))

* Fix code lint ([`72bd5a5`](https://github.com/oscal-compass/compliance-trestle/commit/72bd5a58e5935dd7567e94d291d3410b20a727de))

* Fix bug in finding trestle project root ([`9141056`](https://github.com/oscal-compass/compliance-trestle/commit/914105652a7a99a636d113620f30745d33864547))

* Merge branch &#39;feature/split_merge_add&#39; into feature/split-cmd ([`13ecedd`](https://github.com/oscal-compass/compliance-trestle/commit/13ecedd3228a2bee736c217e3d32eb9db7cb6ec3))

* Add unit tests for some utils functions and rename a few of those functions (#112)

* move functions to core/utils to solve circular dependencies

* move functions to core/utils to solve circular dependencies

* initial list of contextual_path is not mandatory

* make initial list of get_contextual_path function not mandatory

* add unit tests for a few utils functions

Co-authored-by: Bruno &lt;brunomar@au1.ibm.com&gt; ([`e63ad1b`](https://github.com/oscal-compass/compliance-trestle/commit/e63ad1b8a42a32c14f2b4b8c49e3cdb12e8394d5))

* Implement utility function to move file to the Trestle trash directory (#114)

* Fix typo

* Handle parent path of an element_path and handle the root model name

* Implement helper method to convert element_path to a file_path

* Implement helper method for root path of an element path

* Fix tests

* Fix mypy warnings

* Implement utility function to copy availble values from src to dest model

* Tentative tests for split_model as part of TDD

* Implement stripped_instance method

* Refactor FileContentType into a new file

* Fix to_root_path method

* First implementation of split_model with unit test

* Implement split of a multi item dict

* Fix file index for splitted list items

* Update trestle split run method to execute the plan

* Fix plan simulate method

* Fix trestle split run

* Fix splitted model creation

* Update comment

* Implement the ability to move file to trestle trash ([`f75d9f2`](https://github.com/oscal-compass/compliance-trestle/commit/f75d9f2aa033bbe65cb8a3dfff90b47c74af17ee))

* fix FIXME on line 113 from split.py file ([`bf3252d`](https://github.com/oscal-compass/compliance-trestle/commit/bf3252d3252595ab66c28e4f17b3e791d628bb94))

* refactor class_to_oscal function ([`2aa8741`](https://github.com/oscal-compass/compliance-trestle/commit/2aa8741b50c45a42c409a84ed5506f3f473c83d7))

* Implement the ability to move file to trestle trash ([`8815c32`](https://github.com/oscal-compass/compliance-trestle/commit/8815c321d032d0278debf1422d962b7ef43babd8))

* Update comment ([`e4dae7c`](https://github.com/oscal-compass/compliance-trestle/commit/e4dae7c7a87b0745154e706dc4c3769d5c459c7e))

* Merge branch &#39;feature/split_merge_add&#39; into feature/split-cmd ([`5b47a79`](https://github.com/oscal-compass/compliance-trestle/commit/5b47a791a707561b19ae78fc1abdcb42e9cc41ec))

* Initial implementation of Trestle split command (#113)

* Fix typo

* Handle parent path of an element_path and handle the root model name

* Implement helper method to convert element_path to a file_path

* Implement helper method for root path of an element path

* Fix tests

* Fix mypy warnings

* Implement utility function to copy availble values from src to dest model

* Tentative tests for split_model as part of TDD

* Implement stripped_instance method

* Refactor FileContentType into a new file

* Fix to_root_path method

* First implementation of split_model with unit test

* Implement split of a multi item dict

* Fix file index for splitted list items

* Update trestle split run method to execute the plan

* Fix plan simulate method

* Fix trestle split run

* Fix splitted model creation ([`8958706`](https://github.com/oscal-compass/compliance-trestle/commit/895870647a1a120aab9ad20f81ecabdff4dd4d12))

* Merge branch &#39;feature/split_merge_add&#39; into feature/split-cmd ([`bfd7acd`](https://github.com/oscal-compass/compliance-trestle/commit/bfd7acd30886da1c5a370cadb33e12d99a0dbc10))

* feature: trestle merge -l

* move functions to core/utils to solve circular dependencies

* initial list of contextual_path is not mandatory

* make initial list of get_contextual_path function not mandatory

Co-authored-by: Bruno &lt;brunomar@au1.ibm.com&gt; ([`2f3d2d5`](https://github.com/oscal-compass/compliance-trestle/commit/2f3d2d558afc8bf7091b29bd96ddde9d6aeaf773))

* Support parent path and root model for ElementPath (#109) ([`eeba858`](https://github.com/oscal-compass/compliance-trestle/commit/eeba8586fd634faaff21629b102236a84e73a3b4))

* move utility functions from utils to cmd_utils ([`2699353`](https://github.com/oscal-compass/compliance-trestle/commit/26993530ce5e8fe156854cd043a9ce1a04581bfc))

* Fix splitted model creation ([`e2e0a6a`](https://github.com/oscal-compass/compliance-trestle/commit/e2e0a6aedf3f0bd2e515cfda26a4e2ea1cc61097))

* Fix trestle split run ([`ea6e6c9`](https://github.com/oscal-compass/compliance-trestle/commit/ea6e6c9bfa3dd05273dbdf821e7503d0701e36bc))

* Fix plan simulate method ([`c4ee0e5`](https://github.com/oscal-compass/compliance-trestle/commit/c4ee0e59bab0e5e92724b4f736b5c953d541e32b))

* Update trestle split run method to execute the plan ([`a461229`](https://github.com/oscal-compass/compliance-trestle/commit/a4612293f9ff4ca2824cc2f3dc4e78fe5a8a4f69))

* Fix file index for splitted list items ([`ebdbc0c`](https://github.com/oscal-compass/compliance-trestle/commit/ebdbc0ccccc3b914b0bc9ad2a76185c791bb8bb5))

* Implement split of a multi item dict ([`931ee02`](https://github.com/oscal-compass/compliance-trestle/commit/931ee0210b9b1937a0ee4f2faf6fd04b7c2b47e4))

* First implementation of split_model with unit test ([`2179245`](https://github.com/oscal-compass/compliance-trestle/commit/2179245335e44b54bbb3ac63661bb3bb1e75e737))

* Fix to_root_path method ([`83489f3`](https://github.com/oscal-compass/compliance-trestle/commit/83489f326901f556edeeaba10894b8ee74171f71))

* Refactor FileContentType into a new file ([`1d71a1e`](https://github.com/oscal-compass/compliance-trestle/commit/1d71a1e42d1eeaff6bafefcc167090a52f971ebe))

* Implement stripped_instance method ([`d20db23`](https://github.com/oscal-compass/compliance-trestle/commit/d20db23b9aced367c641eeaec673ace93686b8fd))

* Tentative tests for split_model as part of TDD ([`9844413`](https://github.com/oscal-compass/compliance-trestle/commit/9844413509e02a7f6a374e032338a9c3bdbb4614))

* Implement utility function to copy availble values from src to dest model ([`d590a34`](https://github.com/oscal-compass/compliance-trestle/commit/d590a34780a1a2215d71005b49e12be5552cd2af))

* Fix mypy warnings ([`66372e2`](https://github.com/oscal-compass/compliance-trestle/commit/66372e27ddbf052ae72adcd57b82e7e3d176ab45))

* Fix tests ([`377a869`](https://github.com/oscal-compass/compliance-trestle/commit/377a8691bda1f1dd448eb7ba241ba9029459afb3))

* Implement helper method for root path of an element path ([`61e9225`](https://github.com/oscal-compass/compliance-trestle/commit/61e9225ac517e2d20f043da33c085de829df3eb3))

* Implement helper method to convert element_path to a file_path ([`a3f4236`](https://github.com/oscal-compass/compliance-trestle/commit/a3f4236458060ab58fef82971fffeb51e36b8819))

* Handle parent path of an element_path and handle the root model name ([`ebcd9a4`](https://github.com/oscal-compass/compliance-trestle/commit/ebcd9a4c3446b9eebb8e8341c469de3ac1e6da29))

* Fix typo ([`c35b1dd`](https://github.com/oscal-compass/compliance-trestle/commit/c35b1dd58ff368e673d4428150c5eab4edb75340))

* Sync split, merge and add workstreams ([`5bbadf6`](https://github.com/oscal-compass/compliance-trestle/commit/5bbadf673160ab1018bbd07c35dc0224183519ab))

* Add utility functions for trestle merge ([`0b4c265`](https://github.com/oscal-compass/compliance-trestle/commit/0b4c265a417335acf03c8c478659b9425f44fe08))

* Add constants for utility functions ([`644bdff`](https://github.com/oscal-compass/compliance-trestle/commit/644bdff24abff07b05ec7cdc6043834286b0babd))

* inital code for merge ([`fa4d57a`](https://github.com/oscal-compass/compliance-trestle/commit/fa4d57a618ea31c1bd8bf92e1a38d391cbffabe7))

* Update map from model type to model modules ([`de1aece`](https://github.com/oscal-compass/compliance-trestle/commit/de1aece428bd66972c5d2a5642ec2c8c565a93ec))

* Add utility function for getting fields by alias ([`813eacc`](https://github.com/oscal-compass/compliance-trestle/commit/813eacc0a1a1366431e3be5e178cd3478086a097))

* Update map from model type to model modules ([`80a9cf3`](https://github.com/oscal-compass/compliance-trestle/commit/80a9cf3bdadb827fdfa4d84a794ff0b0a1d0f941))

* Merge branch &#39;develop&#39; of github.com:IBM/compliance-trestle into develop ([`d09fa02`](https://github.com/oscal-compass/compliance-trestle/commit/d09fa02aeb073ad7f8601d1e4a63d31f192f49f4))

* Foundation of Trestle Plan, Action and Elements (#93)

* Git ignore tmp directory

* Add arguments for split command

* Define classes for command plan, action and element

* Fix import order and update comments

* Add action rollback method interface

* Update command&#39;s plan API

* Implement the Command Plan class

* Implement __str__ method for Plan

* Implement WriteAction, WriteFileAction with unit tests

* Fix linting and format errors

* Implement AppendFileAction

* Fix lint error

* Update ActionType enum

* Implement initial version of Plan.execute()

* Cleanup dirs after unit test

* Add helper method to clear all actions in a plan

* Fixed Plan.rollback

* Rename module name to plural for semantic consistency

* Add unit test for element and element_path

* Allow element path to express array elements and wildcard

* Implement element.set_at method

* Update comment

* Fix AddAction

* Update comment

* Tidy up and add comments

* Convert get_sub_element_class to a class method for potential reuse

* Fix method signature

* Improve code coverage to 100% for elements.py

* Use pathlib and handle tmp_dir for tests automatically

* Fix auto cleanup of tmp directory after tests

* Reuse oscal_read and oscal_wrapper method

* Fix code-lint issues

* Add .vscode in gitignore

* Allow multiple model object types for sub-element

* Implement AddAction and tests

* Fix doc block

* Finalize implementation of actions

We renamed AddAction to UpdateAction and removed redundant ReadAction

* Fixed comment

* Corrected module doc string

* Fix code lint

* Implement unit tests for fs module

* Remove unused function

* Improve coverage for utils.fs module

* Implement helper method to get trestle project root in the path

* Use pathlib to create temp files and fix code-lint errors

* Update comment for clarity

* Fix code lint

* Implemenet CreatePathAction

* Fix index counter increment

* Fix and add error checks

* Update comment for clarity

* Refactor a test-utils method for reusability

* Impelement unit test for CreatePathAction with full coverage

* Fix code-format issue

* Remove redundant AppendFileAction and update WriteFileAction with checks

* Allow lazy check for file existence during WriteFileAction

This is to support the assumption that CreatePathAction in the Plan will must preceed the WriteFileAction

* CreatePathAction in the Plan should preceed the WriteFileAction

* Fix lint errors

* Fix typo

* Remove unnecessary equality check method

* Improve code coverage for err module

* Improve coverage

* Update comment

* Code skeleton for trestle split

* Implement parse_element_args method and unit tests ([`d95a764`](https://github.com/oscal-compass/compliance-trestle/commit/d95a764e7e4e9ec796e2782d3d022a8a76c6417b))

* Merge branch &#39;develop&#39; of github.com:IBM/compliance-trestle into develop ([`f1ef709`](https://github.com/oscal-compass/compliance-trestle/commit/f1ef709fd26bb50ba68fdd4b4300de48d26aecad))

* provide LUT to handle parameter_settings for fix_any.py (#98)

Co-authored-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`e574108`](https://github.com/oscal-compass/compliance-trestle/commit/e574108b9a58636b98c7680d0700c54b59373835))

* Fix/hotfix set parameter:Merging back into develop (#100)

* 0.1.0

Automatically generated by python-semantic-release

* fix: Corrected typing of parameter-settings in profile.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* Added error which was missed in original hotfix

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

Co-authored-by: semantic-release &lt;semantic-release&gt; ([`5b709a2`](https://github.com/oscal-compass/compliance-trestle/commit/5b709a25e4c7abd85a7b3e88e2ec510eb8fc9931))

* Update setup.cfg (#87)

Add URL to make it easier to find from pypi ([`90f9c6a`](https://github.com/oscal-compass/compliance-trestle/commit/90f9c6a8bca4849fb7b64f48049c747e62fb2028))

* feat:Merge pull request #86 from IBM/feature/object_manipulation

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`1ab68be`](https://github.com/oscal-compass/compliance-trestle/commit/1ab68be5d08c0949ab8d5dde42a31c436f9e4369))

* Separated push and PR actions (#84)

Signed-off-by: Nebula Alam &lt;anebula@au1.ibm.com&gt; ([`e54363c`](https://github.com/oscal-compass/compliance-trestle/commit/e54363c190ece3c7dca1774dc3159f18de9ad307))

* Removed unnecessary cleanup based on use of pytest tmpdir which automatically cleans files up

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`857280d`](https://github.com/oscal-compass/compliance-trestle/commit/857280d07eb1b4c93cb0c8f2b521da6c341a0091))

* Merge branch &#39;develop&#39; into chore/windows_CICD ([`8aab4e1`](https://github.com/oscal-compass/compliance-trestle/commit/8aab4e191e02edc714b13f9f6b02adf415cf6289))

* Convert gen_oscal.sh to py and fix test to run on windows (#77)

* convert gen_oscal.sh to gen_oscal.py and regenerate classes

* fix test that fails on windows re file creation when dir is readonly

* one char typo in fix_any prevented proper termination

* added yapf and flake8 checks on scripts dir ([`d11e797`](https://github.com/oscal-compass/compliance-trestle/commit/d11e79732495332a6a5b78b4093df38a8addc6cc))

* Remove os.sep

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`e20d3be`](https://github.com/oscal-compass/compliance-trestle/commit/e20d3beb10b8368588339f46f5cb5922a6012e20))

* Remerging code

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`5b56d39`](https://github.com/oscal-compass/compliance-trestle/commit/5b56d39d96505d19d0dd5fedfcedb8b102ff27ba))

* Updated pathing in tests to be platform independent

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`27702bd`](https://github.com/oscal-compass/compliance-trestle/commit/27702bd5cf28298180531b6f91ca035bddeb2687))

* Fix for wrap for input / output

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`01ce6bd`](https://github.com/oscal-compass/compliance-trestle/commit/01ce6bd946cc95b91d055bf9db4ed29f369bc91d))

* Update to use correct pathing var

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`a8d6048`](https://github.com/oscal-compass/compliance-trestle/commit/a8d6048a7c970482c18dbaf130e0654990d78be9))

* Updated tests to be platform independent

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`5b7f251`](https://github.com/oscal-compass/compliance-trestle/commit/5b7f251f25b1d50aa0cbe0056f17e604af91cec0))

* Actually use windows / mac os rather than say it on the build

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`4ffca6b`](https://github.com/oscal-compass/compliance-trestle/commit/4ffca6bf6a3f6defe1654bce9aa4cf39953d2fe3))

* Added matrix build to include various different OS steps

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`0dbdacc`](https://github.com/oscal-compass/compliance-trestle/commit/0dbdacc37e54d9a4d77f63f3c6ec928155bc610a))

* Merge branch &#39;develop&#39; of github.com:IBM/compliance-trestle into develop ([`17289b5`](https://github.com/oscal-compass/compliance-trestle/commit/17289b5f71b3d5642db53337b7c595dd2cf4ee8b))

* Merge branch &#39;master&#39; into develop ([`a94335b`](https://github.com/oscal-compass/compliance-trestle/commit/a94335bfc30886d706433ce0e891a2ef391b5e98))

* Merge branch &#39;master&#39; into develop ([`9078972`](https://github.com/oscal-compass/compliance-trestle/commit/9078972a4a5442af9f01597b61554cd1d92430a3))

## v0.0.3 (2020-09-16)

### Documentation

* docs: fix target-definition examples in trestle specifications (#50)

* docs: fix target-definition examples in trestle specifications
* docs: fix split command with -e groups[].controls[] and add example for config.ini
* docs: add trestle replicate to the list of subcommands

closes #49
signed-off-by: Bruno &lt;brunomar@au1.ibm.com&gt; ([`b84ff9b`](https://github.com/oscal-compass/compliance-trestle/commit/b84ff9b4082e001304550b259ae3a1f9d6a70ea7))

* docs: remove git references

Signed-off-by: Bruno &lt;brunomar@au1.ibm.com&gt; ([`0ddc553`](https://github.com/oscal-compass/compliance-trestle/commit/0ddc55383d370e7512870c6c077ffdae51312cb2))

* docs: add info about uuid

Signed-off-by: Bruno &lt;brunomar@au1.ibm.com&gt; ([`32a34a2`](https://github.com/oscal-compass/compliance-trestle/commit/32a34a2d2a3a3438f31fd78312f282002507f7a8))

* docs: add default decomposition headers

Added default decomposition headers.

Signed-off-by: Bruno &lt;brunomar@au1.ibm.com&gt; ([`d03ee39`](https://github.com/oscal-compass/compliance-trestle/commit/d03ee3996e8a986a4c0388058db42c2cd8253278))

* docs: add examples for split/merge commands

Add example of catalag being edited via trestle using trestle split and trestle merge commands. ([`40ab614`](https://github.com/oscal-compass/compliance-trestle/commit/40ab61404e2b9ec347c736153c3691fd19f8143f))

* docs: add specifications for trestle commands ([`698eff8`](https://github.com/oscal-compass/compliance-trestle/commit/698eff8a9bb60d3c9090ad74ad51e57c9bec3d76))

### Feature

* feat: implement trestle init command and update specs (#60)

* unit test for cli.py
* fix dependency conflict when running make install
* install requirements to resolve dependency conflict with attrs
* add initial structure for trestle commands
* modify initial specs for trestle split and merge
* add -f option to trestle split command
* add -f -d options to trestle merge command
* explain future behaviour of trestle split and merge
* add link to contents example of trestle split merge commands
* add trestle remove command
* update decomposition rules to new trestle split format
* update explanation on what to find under each folder
* update trestle split and merge commands
* use fs.load_file for support of both json and yaml files
* add coverage to .gitignore
* rename test folder to tests
* add resources from trestle.resources build package
* implement trestle init command by creating directory structure and initial config files
* add initial config file for trestle project
* add constants for trestle directories and config files
* add unit tests for init command
* add remove subcommand to the list
* move &#39;dist&#39; string to constants file

Closes #36 
Signed-off-by: Bruno &lt;brunomar@au1.ibm.com&gt; ([`6c6b000`](https://github.com/oscal-compass/compliance-trestle/commit/6c6b000795d605514de78198495a941d9d88910f))

### Fix

* fix: Merge pull request #47 from IBM/develop

Release PR: Updated to docs and a broken dependency ([`ab8ba4d`](https://github.com/oscal-compass/compliance-trestle/commit/ab8ba4d05ee9c41097233c3b0ca92fa6251b88c4))

* fix: Fix/issue 57 (#59)

Corrected fix_any.py to correctly behave with the Makefile stage for which it is run.

closes: #57 ([`1faf0a7`](https://github.com/oscal-compass/compliance-trestle/commit/1faf0a7a7795f6e29dd47bb14affdb6a6ea88b0d))

* fix: the Any problem in codegen classes.  

Creates a script which corrects current erroneous behavior in `datamodel-code-generator`. Updates pydantic models to ensure code-generated classes to be functionally correct for OSCAL.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

Co-authored-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`22ba2fc`](https://github.com/oscal-compass/compliance-trestle/commit/22ba2fc75baa11626b49ba709610b3bcaf59cea3))

* fix: fix conflict between attrs and markdown-it-py

fixed error caused when running pip install

fixes #44
Signed-off-by: Bruno &lt;brunomar@au1.ibm.com&gt; ([`b0d588f`](https://github.com/oscal-compass/compliance-trestle/commit/b0d588ff7880a36875dd4cce1ca58d24c6b341e4))

* fix: Issue templates are not being picked up by github. (#31)

Updated issue templates such that github will pick up for use in the UI.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`1382fbc`](https://github.com/oscal-compass/compliance-trestle/commit/1382fbce9db86cf54ac9de97cde4b32b2890e599))

### Unknown

* feature: Feature/object manipulation (#58)

Initial functionality for allowing creating of &#39;partial&#39; models for use in split / merge.

closes: #52

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`d76dbfa`](https://github.com/oscal-compass/compliance-trestle/commit/d76dbfa177d91e54716eb16d3194ceb59c789b7f))

* Merge pull request #45 from IBM/fix/attrs-dep-conflict

fix: fix conflict between attrs and markdown-it-py ([`53ae560`](https://github.com/oscal-compass/compliance-trestle/commit/53ae5604e4397993586499a277a66228bbb7e492))

* fix:Updated with missing proposed change template header

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

Co-authored-by: Bruno &lt;bruno.assis.marques@gmail.com&gt; ([`4bffa69`](https://github.com/oscal-compass/compliance-trestle/commit/4bffa6952873bb75b014d002a8ee23b1002e7933))

* Merge pull request #33 from IBM/docs/trestle-spec

docs: add specifications and examples for trestle commands ([`9369e7d`](https://github.com/oscal-compass/compliance-trestle/commit/9369e7dfb009dcf7b13099e94d4042673ad1ab85))

* Merge branch &#39;docs/trestle-spec&#39; of github.com:IBM/compliance-trestle into docs/trestle-spec ([`30c5803`](https://github.com/oscal-compass/compliance-trestle/commit/30c580323702bed936414f167d69ead94910b66b))

* Merge branch &#39;develop&#39; into docs/trestle-spec ([`db43023`](https://github.com/oscal-compass/compliance-trestle/commit/db43023bc3209bd108cb94fcc80d34c32a9e95d9))

## v0.0.2 (2020-09-10)

### Fix

* fix: force use of PAT token

fix: force use of PAT token ([`4b860d2`](https://github.com/oscal-compass/compliance-trestle/commit/4b860d27ff46c552d69d85fc5431bfc60a2526c8))

* fix: Sem release credentials changed

fix: Sem release credentials changed.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`4bb6f34`](https://github.com/oscal-compass/compliance-trestle/commit/4bb6f346d49fe422caa6c6a95ffa0fbd769739b1))

* fix: Attempting to fix semantic release

fix: Attempting to fix semantic release ([`6215249`](https://github.com/oscal-compass/compliance-trestle/commit/6215249fbae5000b20e866e4e6a9adf2a7d252f0))

* fix: Improved stage builds

fix: Improved stage builds
* Reverted semantic release to &#34;hand coded&#34; form.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* Simplified codecov.yml

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* Simplified codecov.yml

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* Even simplier semantc release

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* Updated testing to run checkout and install dev tools

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* Updated testing to run checkout and install dev tools

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`ac9e416`](https://github.com/oscal-compass/compliance-trestle/commit/ac9e4169039d6f59c4e2e42c6de2c1306bad0bf8))

* fix: Semantic release build issues

fix: Semantic release build issues

* Reverted semantic release to &#34;hand coded&#34; form.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* Simplified codecov.yml

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* Simplified codecov.yml

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* Even simplier semantc release

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`382aef7`](https://github.com/oscal-compass/compliance-trestle/commit/382aef7a286b918ea9bb6369159361153454d42a))

* fix: Reverted semantic release to hand coded form

* Reverted semantic release to &#34;hand coded&#34; form.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* Simplified codecov.yml

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* Simplified codecov.yml

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`e6b973d`](https://github.com/oscal-compass/compliance-trestle/commit/e6b973ded99ec9d49e25e1ab5b5003107be74241))

* fix: Added github PAT to avoid issues with semantic release

fix: Added github PAT to avoid issues with semantic release
* Adding codecov yaml

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt;

* fix: Added github PAT to avoid issues with semantic release

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`eaeff63`](https://github.com/oscal-compass/compliance-trestle/commit/eaeff63aa0a4f050c4a651af4052d4b7fe621363))

* fix: adding codecov

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`e1b5046`](https://github.com/oscal-compass/compliance-trestle/commit/e1b50464ed39da3f6a7ea20926fa8d4358d4286e))

* fix(workflow): new line at the end of test workflow

fix(workflow): new line at the end of test workflow

Fixing setup.cfg to run semantic-release on master branch.

Co-authored-by: Nebula Alam &lt;anebula@au1.ibm.com&gt; ([`95a0568`](https://github.com/oscal-compass/compliance-trestle/commit/95a0568f4d032e13c45fc0acda094c43f69ea8cf))

* fix(workflow): new line at the end of release workflow ([`1b5edeb`](https://github.com/oscal-compass/compliance-trestle/commit/1b5edebb49bc28eebae3e6b49b2120bb998da030))

### Unknown

* Fix/sem release 2 (#19)

fix(.github/workflows): Fix semantic release

* Updated actions for semantic release
* Corrected semantic release library
* Update to leverage recommended semantic release

Signed-off-by: Nebula Alam &lt;anebula@au1.ibm.com&gt; ([`dce88fb`](https://github.com/oscal-compass/compliance-trestle/commit/dce88fb36fd7f85230e18f5c13800b33e986af10))

* Updated actions for semantic release (#18)

fix(.github/workflows): Fix release workflow

fix python-test on github actions workflow to release to PYPI on successful build.

Signed-off-by: Chris Butler &lt;chris@thebutlers.me&gt; ([`95a9e5e`](https://github.com/oscal-compass/compliance-trestle/commit/95a9e5eaba5f7f60cac2727034dbed9a827cd0c4))

* chrore(trestle): Repo initialisation (#1)

Migrating project from internal IBM github. ([`7c9b92a`](https://github.com/oscal-compass/compliance-trestle/commit/7c9b92a993b37e1a213c2d13245830e733e09c7f))

* Initial commit ([`59e4db0`](https://github.com/oscal-compass/compliance-trestle/commit/59e4db084e169ad5c9b139d68a59037a8d32aba8))
