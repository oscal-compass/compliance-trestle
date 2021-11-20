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
$ python -V</code>
Python 3.8.3</code>
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
(venv.trestle)$ pip install compliance-trestle
Looking in indexes: https://pypi.org/simple,...

```

## *Confirm trestle is installed properly*

- Check trestle viability (and view help).

```bash
(venv.trestle)$ trestle -h
usage: trestle [-h]
               {init,create,split,merge,replicate,add,remove,validate,import,task,assemble,version}
               ...
```

<details>
<summary>Full help text</summary>

```bash

Manage OSCAL files in a human friendly manner.

positional arguments:
  {init,create,split,merge,replicate,add,remove,validate,import,task,assemble,version}
    init                Initialize a trestle working directory.
    create              Create a sample OSCAL model in trestle project.
    split               Split subcomponents on a trestle model.
    merge               Merge subcomponents on a trestle model.
    replicate           Replicate a top level model within the trestle directory structure.
    add                 Add a subcomponent to an existing model.
    remove              Remove a subcomponent to an existing model.
    validate            Validate contents of a trestle model in different modes.
    import              Import an existing full OSCAL model into the trestle project.
    task                Run arbitrary trestle tasks in a simple and extensible methodology.
    assemble            Assemble all subcomponents from a specified trestle
                        model into a single JSON/YAML file under dist.
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
