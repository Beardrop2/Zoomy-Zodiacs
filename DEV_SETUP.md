# Github repo

It should go without saying, you need to clone the repo from github to your machine.

```
git clone https://github.com/Beardrop2/Zoomy-Zodiacs
```

<!--- change later if "all" instead of "most" --->
Most of the rest of these commands should be run inside the repo folder

# PDM - dependency and venv manager

> PDM, as described, is a modern Python package and dependency manager supporting the latest PEP standards. But it is more than a package manager. It boosts your development workflow in various aspects.

\- [PDM introduction](https://pdm-project.org/en/latest/)

## Steps
<!--
    I've walked through 'Create venv and install dependencies' and 'Enable venv' on a windows system
    (and probably done the exact steps in 'Install')
    But I've used the hacky subshell fix for the execution policy

    update this as testing is done (preferably with enough detail to reproduce)
    TESTED:
    - Windows
        - Powershell (pdm 2.16.1 installed with pipx)
            - Hacky PDM subshell fix for execution policy to enable venv

    UNTESTED:
    - Windows
        - Powershell
            - Enable venv properly
    - Linux
        - Bash (probably main case)
        - Zsh, fish (less common)
-->

- [Install](#install-pdm)
- [Create venv and install dependencies](#create-venv-and-install-dependencies)
- [Enable venv](#enable-venv)

### Install PDM
Installation instructions from the PDM website can be found [here](https://pdm-project.org/en/latest/#installation)

To install PDM using pip:

<!-- Haven't tested this, should work? Might not be added to $PATH on windows? -->
```sh
pip install pdm
```

To install PDM using the setup script,

for linux:

```bash
curl -sSL https://pdm-project.org/install-pdm.py | python3 -
```

for windows:

<!--- what's the correct alias for powershell syntax highlighting? --->
```sh
(Invoke-WebRequest -Uri https://pdm-project.org/install-pdm.py -UseBasicParsing).Content | py -
```

#### Optional: shell completion

for bash:

```sh
pdm completion bash > /etc/bash_completion.d/pdm.bash-completion
```

for powershell:

```sh
# Create a directory to store completion scripts
mkdir $PROFILE\..\Completions
echo @'
Get-ChildItem "$PROFILE\..\Completions\" | ForEach-Object {
    . $_.FullName
}
'@ | Out-File -Append -Encoding utf8 $PROFILE
# Generate script
Set-ExecutionPolicy Unrestricted -Scope CurrentUser
pdm completion powershell | Out-File -Encoding utf8 $PROFILE\..\Completions\pdm_completion.ps1
```

Instructions for Zsd and Fish shell completion are available in the [PDM installation instructions](https://pdm-project.org/en/latest/#shell-completion)

More installation methods are available in the installation instructions from the PDM website (homebrew, scoop, uv, pipx, pip, asdf, inside project using pyprojectx wrapper)

### Create venv and install dependencies

once pdm is installed, run

```sh
pdm install
```

to install the dependencies from the pdm lockfile (this will create a virtual environment named `in-project` in .venv/ if it has not already been created)

this will install `ruff` and `precommit` as well as the dependencies for the bot

### Enable venv

Instructions available [on the pdm website](https://pdm-project.org/en/latest/usage/venv/#activate-a-virtualenv)

To enable the venv,

for bash/csh/zsh:

```
$ eval $(pdm venv activate in-project)
(test-project-for-test) $  # Virtualenv entered
```

for powershell:

```
PS1> Invoke-Expression (pdm venv activate in-project)
```

if powershell just prints `C:\Users\...\.venv\Scripts\Activate.ps1`, your [Execution Policy](https:/go.microsoft.com/fwlink/?LinkID=135170) may not allow running scripts with powershell. To confirm, running `& "C:\Users\...\.venv\Scripts\Activate.ps1"` using the outputted path should give an `UnauthorizedAccess` exception

if this happens, you can either change your execution policy, or use pdm to create a subshell:

<!-- this is a hacky workaround, I don't know if it raises issues, please check or add disclaimer -->
to get a subshell with the environment enabled, run:
```sh
PS1> pdm run powershell.exe
```

# Pre-commit - lint before committing
Pre-commit runs before committing through [git hooks](https://git-scm.com/book/en/v2/Customizing-Git-Git-Hooks)

See [the section in README.md](./README.md#pre-commit-run-linting-before-committing)

The pre-commit configuration is located in .pre-commit-config.yaml

The pre-commit python package should have been installed (executable on your machine and available on path) by pdm. The install step below refers to installing the git hooks to run before committing according to the pre-commit configuration in .pre-commit-config.yaml

## Steps

<!-- tested on Windows machine with pdm powershell subshell. I can't think of a reason this wouldn't work as long as the pre-commit executable is in path, so I don't think a testing log is necessary -->

- [Install](#install-pre-commit)

## Install pre-commit

To install pre-commit to your git hooks:
```sh
pre-commit install
```

You can additionally run `pre-commit` without any arguments to run the pre-commit hooks without committing a change

# Ruff - formatting

Ruff should have been installed by pdm earlier, during `pdm install`

It will be run during pre-commit, but you can run `ruff format` from the terminal
