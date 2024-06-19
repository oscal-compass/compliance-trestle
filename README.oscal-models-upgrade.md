## Developers Guide to trestle upgrade commensurate with OSCAL models upgrade

This is a general guide on how to go about upgrading compliance-trestle to support a new version of OSCAL models.

The steps are as follows:

<ol>
<li> Create  in GitHub repo <i style="color:darkgrey;">(remote)</i>
<li> Clone upgrade branch into <span style="color:darkgreen;">/trestle-upgrade</span> folder <i style="color:darkgrey;">(local <- remote)</i>
<li> Download revised and new OSCAL models into folder <span style="color:darkgreen;">/trestle-upgrade/release-schemas</span> <i style="color:darkgrey;">(local <- remote)</i>
<ul>
<li> See <a href="https://github.com/usnistgov/OSCAL/releases">https://github.com/usnistgov/OSCAL/releases</a>
</ul>
<li> Create & source python virtual environment <span style="color:darkgreen;">venv.trestle-upgrade</span> <i style="color:darkgrey;">(local)</i>
<li> Orient current folder to <span style="color:darkgreen;">/trestle-upgrade</span> <i style="color:darkgrey;">(local)</i>
<li> Run <span style="color:blue;">make develop</span> <i style="color:darkgrey;">(local)</i>
<li> Make necessary code changes:
<ul>
<li> Run <span style="color:blue;">python scripts/gen_oscal.py</span> <i style="color:darkgrey;">(local)</i>
<li> Run <span style="color:blue;">make test-all</span> <i style="color:darkgrey;">(local)</i>
<li> Fix errors and failures via modification of code generation modules and existing trestle modules, as appropriate case-by-case <i style="color:darkgrey;">(local)</i>
<li> Repeat until all errors and failures are fixed <i style="color:darkgrey;">(local)</i>
</ul>
<li> Run <span style="color:blue;">make code-format</span> <i style="color:darkgrey;">(local)</i>
<li> Run <span style="color:blue;">make code-lint</span> <i style="color:darkgrey;">(local)</i>
<li> Push <span style="color:darkgreen;">/trestle-upgrade</span> folder changes back to GitHub repo <i style="color:darkgrey;">(local -> remote)</i>
<li> Create PR for trestle-upgrade branch -> develop branch <i style="color:darkgrey;">(remote)</i>
<li> Get PR approval <i style="color:darkgrey;">(remote)</i>
<li> Merge PR into develop branch <i style="color:darkgrey;">(remote)</i>
<li> Create PR for develop branch -> main branch <i style="color:darkgrey;">(remote)</i>
<li> Create <span style="color:red;">breaking change</span> <i style="color:darkgrey;">(remote)</i>
<li> Get PR approval <i style="color:darkgrey;">(remote)</i>
<li> Merge develop branch into main branch <i style="color:darkgrey;">(remote)</i>
</ol>

______________________________________________________________________

##### Overview of process to take OSCAL models and upgrade trestle Python code

<img src="images/trestle-OSCAL-upgrade.png" style="width:600px;height:500px;border: 1px solid #000;padding:10px;">
