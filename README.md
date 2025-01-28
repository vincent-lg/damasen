# Damasen

This project holds the Damasen code, an accessible Crawl-like.

## Installing from source

Damasen requires Python 3.12. Please install it first.

When installed, you need [poetry](https://python-poetry.org/docs/). On Windows, you usually need to run these steps:

1.  Install `pipx`:

    If `pip` is available on your path:

        pip install --user pipx

    Adapt if needed. The recommended command now is `python -m pip install --user pipx`, but it depends on how Python was installed.

    It is possible (even most likely) the above finishes with a WARNING looking similar to this:

    > WARNING: The script pipx.exe is installed in `<USER folder>\AppData\Roaming\Python\Python3x\Scripts` which is not on PATH

    If so, instead of just running the `pipx` command, copy the path and append `pipx.exe` to it. For instance:

        <USER folder>\AppData\Roaming\Python\Python3x\Scripts\pipx.exe ensurepath

    Or, if `pipx.exe` is already on your path:

        pipx.exe ensurepath

    This will add both the above mentioned path and the %USERPROFILE%\.local\bin folder to your search path. Restart your terminal session and verify pipx does run.

        pipx --version

    Refer to the [pipx documentation](https://pipx.pypa.io/stable/installation/) if needed.

2.  Install poetry itself. Run the command:

        pipx install poetry

3.  Run Poetry. Everything Poetry needs is explained in the `pyproject.toml` file. Just `cd` to the folder containing it.

    There are two options here, and I recommend option 1:

    1.  Create a virtual environment. This should save time and shorten the commands to use afterward. Simply run:

            python -m venv pyenv

        (Assuming Python 3.12 can be found under the python command).

            pyenv\scripts\activate

        Then you can run the command to install Poetry:

            poetry install --no-root

        > Note : this might look a bit long since Poetry creates a virtual environment automatically. Read on for the reason why this is the recommended approach.

    2.  Use the automatic virtual environment: this step is simple, instead of creating a virtual environment, let Poetry do it for you. Simply run:

        poetry install --no-root

## Running from source

To run, you must start the package `damasen`. If you have created a virtual environment manually, the command is as simple as:

    python -m damasen

If you have let Poetry create the virtual environment, the command is a bit longer:

    poetry run python -m damasen

## Building Damasen to get an executable

If you have created a virtual environment manually, you can build an executable with:

    python build.py

Again, if you have let Poetry handle the creation of the virtual environment, the command would be:

    poetry run python build.py

In any case, this might take awhile. Do not panic. Nuitka is compiling your code (converting it to C++ and running various optimizations). This usually takes awhile (meaning easily 10 minutes on my computer). If, after half an hour, there's still no response, you might want to break the script (by pressing CTRL + C). You might get an error. If not, perhaps try to run the comand manually (this would be something like `python -m nuitka damasen`) to see if you've been asked a question. Nuitka should be able to work, but it would need an external compiler and sometimes fail to download a temporary one.

If after some time you get the message:

    Building with Nuitka... Done.

You will find a folder called `damasen.dist`. In it you should have a file `damasen.exe`. You can execute it and hopefully see a window appear.

