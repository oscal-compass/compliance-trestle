# Install trestle in a python virtual environment

There are a few things you need to to start using trestle:

- Make sure you have a working and recent Python environment
- Set up a Python virtual environment
- Download and install trestle
- Confirm it is working properly
- Create a trestle workspace

## *Confirm you have python installed*

- Ensure you have a modern [Python](https://www.python.org/downloads/) (3.7, 3.8, 3.9).

```bash
$ python -V
Python 3.8.3
```

## *Setup a virtual environment*

There are many ways to do this on Windows, Mac and Linux and with different Python installations, so please consult
the documentation associated with your platform.  Below is how it works on a typical Linux platform.

```bash
$ cd
$ python -m venv venv.trestle
$ source venv.trestle/bin/activate
(venv.trestle)$

```

- Ensure you have a modern [pip](https://pip.pypa.io/en/stable/installing/) (19.x or greater).

```bash
(venv.trestle)$ python -m pip --version
pip 19.2.3 from /home...
```

You should probably upgrade your pip to the latest version with:

```bash
(venv.trestle)$ python -m pip install --upgrade pip
```

Details can be found at [Installation - pip documentation](https://pip.pypa.io/en/stable/installing/#upgrading-pip)

## *Install trestle*

- Install [compliance-trestle](https://ibm.github.io/compliance-trestle/).

```bash
(venv.trestle)$ python -m pip install compliance-trestle
Looking in indexes: https://pypi.org/simple,...

```

## *Confirm trestle is installed properly*

- Check trestle viability (and view help).

```bash
(venv.trestle)$ trestle -h
usage: trestle [-h]
               {assemble,author,create,describe,href,import,init,merge,partial-object-validate,remove,replicate,split,task,validate,version}
               ...
```

<details markdown>

<summary>Full help text</summary>

```bash

Manage OSCAL files in a human friendly manner.

positional arguments:
  {assemble,author,create,describe,href,import,init,merge,partial-object-validate,remove,replicate,split,task,validate,version}
    assemble            Assemble all subcomponents from a specified trestle model into a single JSON/YAML file under
                        dist.
    author              trestle author, a collection of commands for authoring compliance content outside of OSCAL.
    create              Create a sample OSCAL model in trestle project or create new elements within a given model.
    describe            Describe contents of a model file including optional element path.
    href                Change href of import in profile to point to catalog in trestle project. This command is
                        needed when generating an SSP with a profile that imports a catalog from a temporary location
                        different from the final intended location of the catalog. Omit the href argument to see the
                        list of current imports in the profile.
    import              Import an existing full OSCAL model into the trestle project.
    init                Initialize a trestle working directory.
    merge               Merge subcomponents on a trestle model.
    partial-object-validate
                        Direct validation any oscal object in a file, including list objects.
    remove              Remove a subcomponent to an existing model.
    replicate           Replicate a top level model within the trestle directory structure.
    split               Split subcomponents on a trestle model.
    task                Run arbitrary trestle tasks in a simple and extensible methodology.
    validate            Validate contents of a trestle model in different modes.
    version             Output version info for trestle and OSCAL.

optional arguments:
  -h, --help            show this help message and exit

```

</details>

## *Create a trestle workspace*

- Create trestle workspace.

```bash
(venv.trestle)$ mkdir trestle.workspace
(venv.trestle)$ cd trestle.workspace
(venv.trestle)$ trestle init
Initialized trestle project successfully in /home/<user>/trestle.workspace
```

Congratulations! You now have a working trestle workspace for safe manipulation of OSCAL documents!
