pylons-monkeypatch
====================

Collection of monkey patches for Pylons projects.

This package contains the following functionality:

- beaker_cache

beaker_cache
--------------------

This fixes an inconsistency between Pylons' development standard and
Beaker's cache policy.

In Pylons projects, `abort()` function is commonly used, such as
`abort(404)` when a resource is not available.  Since it actually
raises an exception, if a controller decorated with `beaker_cache`
decorator calls `abort()`, the cache is unchanged at this time.  On
the other hand, Beaker may return older cache contents in some cases,
for example when the lock is busy. The combination of them leads a
situation that very old content is returned in some rare condition.

An implementation in this package catches an exception from
`create_func` (typically a controller method), and clears the old cache
after an HTTPException is raised.
