

EstudaIA

production



Agent















EstudaAI
Deployments
Variables
Metrics
Console
Settings
Unexposed service
US East
1 Replica



History

Hide Skipped
















EstudaAI
/
306e608f
Crashed

2026-08-16 02:57 GMT-3
Get Help
Details
Build Logs
Deploy Logs
Network Logs
Filter and search logs


You reached the start of the range
2026-08-16 02:57
Starting Container
  File "/usr/local/lib/python3.12/site-packages/starlette/routing.py", line 648, in lifespan
    async with self.lifespan_context(app) as maybe_state:
  File "/usr/local/lib/python3.12/contextlib.py", line 210, in __aenter__
               ^^^^^^^^^^^^^^^^^^^^^^^^^^
    return await anext(self.gen)
  File "/usr/local/lib/python3.12/contextlib.py", line 210, in __aenter__
           ^^^^^^^^^^^^^^^^^^^^^
  File "/app/core/api.py", line 36, in startup_event
    async with engine.begin() as conn:
               ^^^^^^^^^^^^^^
    async with original_context(app) as maybe_original_state:
  File "/usr/local/lib/python3.12/site-packages/fastapi/routing.py", line 6375, in _startup
               ^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/site-packages/fastapi/routing.py", line 265, in __aenter__
    await handler()
    await self._router._startup()
    return await anext(self.gen)
           ^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/site-packages/fastapi/routing.py", line 240, in merged_lifespan
INFO:     Started server process [2]
INFO:     Waiting for application startup.
ERROR:    Traceback (most recent call last):
    return self.pool.connect()
  File "/usr/local/lib/python3.12/site-packages/sqlalchemy/util/_concurrency_py3k.py", line 201, in greenlet_spawn
    result = context.throw(*sys.exc_info())
  File "/usr/local/lib/python3.12/site-packages/sqlalchemy/engine/base.py", line 3295, in connect
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    return self._connection_cls(self)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^
    return await self.start(is_ctxmanager=True)
  File "/usr/local/lib/python3.12/site-packages/sqlalchemy/engine/base.py", line 144, in __init__
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/site-packages/sqlalchemy/ext/asyncio/engine.py", line 1068, in begin
    self._dbapi_connection = engine.raw_connection()
  File "/usr/local/lib/python3.12/site-packages/sqlalchemy/ext/asyncio/engine.py", line 275, in start
                             ^^^^^^^^^^^^^^^^^^^^^^^
    await greenlet_spawn(self.sync_engine.connect)
    async with conn:
  File "/usr/local/lib/python3.12/site-packages/sqlalchemy/engine/base.py", line 3319, in raw_connection
               ^^^^
  File "/usr/local/lib/python3.12/site-packages/sqlalchemy/ext/asyncio/base.py", line 121, in __aenter__
           ^^^^^^^^^^^^^^^^^^^
           ^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/site-packages/sqlalchemy/pool/base.py", line 448, in connect
         ^^^^^^^^^^^^^^^^^^^
    return _ConnectionFairy._checkout(self)
  File "/usr/local/lib/python3.12/site-packages/sqlalchemy/util/langhelpers.py", line 122, in __exit__
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    raise exc_value.with_traceback(exc_tb)
  File "/usr/local/lib/python3.12/site-packages/sqlalchemy/pool/base.py", line 1272, in _checkout
  File "/usr/local/lib/python3.12/site-packages/sqlalchemy/pool/impl.py", line 176, in _do_get
    fairy = _ConnectionRecord.checkout(pool)
    return self._create_connection()
            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
           ^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/site-packages/sqlalchemy/pool/base.py", line 712, in checkout
  File "/usr/local/lib/python3.12/site-packages/sqlalchemy/pool/base.py", line 389, in _create_connection
    rec = pool._do_get()
    return _ConnectionRecord(self)
          ^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/site-packages/sqlalchemy/pool/impl.py", line 178, in _do_get
    with util.safe_reraise():
  File "/usr/local/lib/python3.12/site-packages/sqlalchemy/pool/base.py", line 674, in __init__
    self.__connect()
  File "/usr/local/lib/python3.12/site-packages/sqlalchemy/pool/base.py", line 900, in __connect
    with util.safe_reraise():
         ^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/site-packages/sqlalchemy/util/langhelpers.py", line 122, in __exit__
    raise exc_value.with_traceback(exc_tb)
  File "/usr/local/lib/python3.12/site-packages/sqlalchemy/pool/base.py", line 896, in __connect
    self.dbapi_connection = connection = pool._invoke_creator(self)
                                         ^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/site-packages/sqlalchemy/engine/create.py", line 667, in connect
    return dialect.connect(*cargs_tup, **cparams)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/site-packages/sqlalchemy/engine/default.py", line 630, in connect
    return self.loaded_dbapi.connect(*cargs, **cparams)  # type: ignore[no-any-return]  # NOQA: E501
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/site-packages/sqlalchemy/dialects/postgresql/asyncpg.py", line 955, in connect
    await_only(creator_fn(*arg, **kw)),
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/site-packages/sqlalchemy/util/_concurrency_py3k.py", line 132, in await_only
  File "/usr/local/lib/python3.12/site-packages/asyncpg/connect_utils.py", line 1099, in __connect_addr
    return current.parent.switch(awaitable)  # type: ignore[no-any-return,attr-defined] # noqa: E501
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/site-packages/sqlalchemy/util/_concurrency_py3k.py", line 196, in greenlet_spawn
    value = await result
            ^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/site-packages/asyncpg/connection.py", line 2443, in connect
    return await connect_utils._connect(
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/site-packages/asyncpg/connect_utils.py", line 1249, in _connect
    raise last_error or exceptions.TargetServerAttributeNotMatched(
  File "/usr/local/lib/python3.12/site-packages/asyncpg/connect_utils.py", line 1218, in _connect
    conn = await _connect_addr(
           ^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/site-packages/asyncpg/connect_utils.py", line 1054, in _connect_addr
    return await __connect_addr(params, True, *args)
    tr, pr = await connector
             ^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/site-packages/asyncpg/connect_utils.py", line 969, in _create_ssl_connection
    tr, pr = await loop.create_connection(
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/asyncio/base_events.py", line 1083, in create_connection
    infos = await self._ensure_resolved(
            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/asyncio/base_events.py", line 1466, in _ensure_resolved
    return await loop.getaddrinfo(host, port, family=family, type=type,
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/asyncio/base_events.py", line 905, in getaddrinfo
    return await self.run_in_executor(
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/concurrent/futures/thread.py", line 59, in run
    result = self.fn(*self.args, **self.kwargs)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/socket.py", line 978, in getaddrinfo
    for res in _socket.getaddrinfo(host, port, family, type, proto, flags):
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^


02:59
