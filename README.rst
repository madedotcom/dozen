Dozen: A library for declarative 12factor config
================================================

When writing 12-factor applications, we often need to write lengthy, tedious code for parsing environment variables.

Dozen is a simple, declarative library for mapping environment variables to configuration types.

    >>> import dozen
    >>> import os
    >>>
    >>> # Given some variables in the environment
    >>> os.environ.update({
    >>>     'USE_ENVIRONMENT': 'true',
    >>>     'SOME_STRING': 'my value',
    >>>     'PORT': '2345'
    >>> })
    >>>
    >>> # ... and a template for our config
    >>> class MyConfig(dozen.Template):
    >>>     use_environment: bool
    >>>     some_string: str
    >>>     port: int
    >>>
    >>> # dozen returns populated instances of our template from env vars
    >>> cfg = MyConfig.build()
    >>> assert cfg.use_environment is True
    >>> assert cfg.some_string == 'my value'
    >>> assert cfg.port == 2345

Sometimes we want to treat a value as optional, and give it a default value.

    >>> os.environ.clear()
    >>>
    >>> class DefaultConfig(dozen.Template):
    >>>     use_environment: bool = True
    >>>     some_string: str = "cheese"
    >>>     some_optional_string: str = None
    >>>     port: int = 73
    >>>
    >>> cfg = DefaultConfig.build(env=dict())
    >>> assert cfg.use_environment is True
    >>> assert cfg.some_string == 'cheese'
    >>> assert cfg.port == 73

For backing services, we often want to set addresses as env vars

    >>> import dozen
    >>> import os
    >>>
    >>> # Given some variables in the environment
    >>> os.environ.update({
    >>>     'MYAPP_WEB_HOST': 'app.example.org',
    >>>     'MYAPP_WEB_PORT': '8080',
    >>> })
    >>>
    >>> # ... and a template for our config
    >>> class MyConfig(dozen.Template):
    >>>     web: dozen.service()
    >>>     api: dozen.service(default_host='api.example.org', default_port=9000)
    >>>
    >>> # dozen returns populated instances of our template from env vars
    >>> cfg = MyConfig.build(prefix='myapp')
    >>> assert cfg.web.host == 'app.example.org'
    >>> assert cfg.web.port == 8080
    >>> assert cfg.api.host == 'api.example.org'
    >>> assert cfg.api.port == 9000


