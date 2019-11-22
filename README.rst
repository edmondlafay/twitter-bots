Twitter bots Module Repository
========================

Twitter bots in python that listen to twitter and reacts.

---------------

If you want to learn more about ``setup.py`` files, check out `this repository <https://github.com/kennethreitz/setup.py>`_.

install using 
```pip install .```

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