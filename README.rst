Dozen: A library for declarative 12factor config
================================================

When writing 12-factor applications, we often need to write lengthy, tedious code for parsing environment variables.

Dozen is a simple, declarative library for mapping environment variables to configuration types.

    >>> import dozen
    >>> import os
    >>> 
    >>> os.environ.update({
    >>>     'USE_ENVIRONMENT': 'true',
    >>>     'SOME_STRING': 'my value',
    >>>     'PORT': '2345'
    >>> })
    >>>
    >>> class MyConfig(dozen.Template):
    >>>     use_environment: bool
    >>>     some_string: str
    >>>     port: int

    >>> cfg = MyConfig.build()
    >>> assert cfg.use_environment is True
    >>> assert cfg.some_string == 'my value'
    >>> assert cfg.port == 2345

