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
- [Install](#install-pdm)
- [Create venv and install dependencies](#create-venv-and-install-dependencies)
- [Enable venv](#enable-venv)

### Install PDM
Installation instructions from the PDM website can be found [here](https://pdm-project.org/en/latest/#installation)

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
