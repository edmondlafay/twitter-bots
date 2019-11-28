# Twitter bots Module Repository
Twitter bots in python that listen to twitter and reacts.

---------------

If you want to learn more about ``setup.py`` files, check out `this repository https://github.com/kennethreitz/setup.py.

---------------

## Install pyenv

Install tools and headers needed to build CPythons

```
    sudo apt-get update -y
    sudo apt-get install -y build-essential libbz2-dev libssl-dev libreadline-dev libffi-dev libsqlite3-dev tk-dev
```

Run the installer script (installs pyenv and some very useful pyenv plugins by the original author; see here for more)

```
    curl -L https://github.com/pyenv/pyenv-installer/raw/master/bin/pyenv-installer | bash
```

Add init lines to your ~/.profile or ~/.bashrc (it mentions it at the end of the install script):

```
    export PATH="$HOME/.pyenv/bin:$PATH"
    eval "$(pyenv init -)"
    eval "$(pyenv virtualenv-init -)"
```

Restart your shell (close & open or exec $SHELL) or reload the profile script. (with e.g. `source ~/.bashrc`)

Done!

## Setting up an environment

To not touch the system Python (generally a bad idea; OS-level services might be relying on some specific library versions, etc.) make your own environment, it's easy! Even better, no sudo, for it or pip installs!

Install your preferred Python version (this will download the source and build it for your user, no input required)
```
pyenv install 3.6.0
```
Make it a virtualenv so you can make others later if you want
```
pyenv virtualenv 3.6.0 general
```
Make it globally active (for your user)
```
pyenv global general
```
Do what you want to with the Python/pip, etc. It's yours.

If you want to clean out your libraries later, you could delete the virtualenv (pyenv uninstall general) or make a new one (pyenv virtualenv 3.6.0 other_proj). You can also have environments active per-directory: pyenv local other_proj will drop a .python-version file into your current folder and any time you invoke Python or pip-installed Python utilities from it or under it, they will be shimmed by pyenv.


install project using 
``pip install .``

Credentials for the api should be stored in a '.credentials.yml' file at the root of the project.
The structure should look like this :

```
twitter:
  bot_name:
    api_key: api_key123
    api_secret: api_secret123
    access_token: access_token123
    access_secret: access_secret123
```