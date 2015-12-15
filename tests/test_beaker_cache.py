# -*- coding: utf-8 -*-

from __future__ import print_function

import anydbm as dbm
import pickle
from contextlib import closing

from paste.registry import RegistryManager
from paste.httpexceptions import HTTPException
import paste.fixture
import webhelpers
from beaker.util import encoded_path
import pylons
from pylons.wsgiapp import PylonsApp, PylonsBaseWSGIApp
from pylons.error import error_template
from pylons.middleware import (
    error_mapper,
    ErrorDocuments,
    ErrorHandler,
)
from pylons.controllers.util import abort
# from pylons.decorators.cache import beaker_cache
from pylons_monkeypatch.beaker_cache import beaker_cache

data_dir = 'data_dir'


class BeakerCacheController(object):
    @beaker_cache(expire=0, type='dbm', data_dir=data_dir)
    def index(self):
        resource = pylons.request.environ.get('resource')
        if resource is None:
            abort(404)
        return "200 OK"


class BaseWSGIApp(PylonsBaseWSGIApp):
    def __call__(self, environ, start_response):
        self.setup_app_env(environ, start_response)
        controller = BeakerCacheController()
        try:
            content = controller.index()
        except HTTPException, httpe:
            response = httpe.response(environ)
            response._exception = True
            registry = environ['paste.registry']
            registry.replace(pylons.response, response)
        else:
            pylons.response.content = content
        response = pylons.response._current_obj()
        return response(environ, start_response)


def load_environment(global_conf, app_conf):
    pylons.config.init_app(global_conf, app_conf, package='yourproj')
    pylons.config['pylons.h'] = webhelpers


def make_app():
    global_conf = {}
    app_conf = {}

    load_environment(global_conf, app_conf)

    # The Pylons WSGI app
    app = PylonsApp(base_wsgi_app=BaseWSGIApp, use_routes=False)

    # Handle Python exceptions
    app = ErrorHandler(app, global_conf, error_template=error_template,
                       **pylons.config['pylons.errorware'])

    # Display error documents for 401, 403, 404 status codes (and
    # 500 when debug is disabled)
    app = ErrorDocuments(app, global_conf, mapper=error_mapper, **app_conf)

    # Establish the Registry for this application
    app = RegistryManager(app)

    return app


def test_beaker_cache():
    func = BeakerCacheController.index
    cache_name = '%s.%s' % (func.__module__, func.__name__)
    path = encoded_path(data_dir + "/container_dbm",
                        [cache_name],
                        extension=".dbm",
                        digest_filenames=True)
    cache_key = '[][]'

    wsgiapp = make_app()
    app = paste.fixture.TestApp(wsgiapp)

    response = app.get('/', extra_environ={'resource': "XYZ"})
    assert response.status == 200
    assert response.body == "200 OK"
    with closing(dbm.open(path)) as db:
        assert cache_key in db
        storedtime, expiretime, value = pickle.loads(db[cache_key])
        assert value["status"] == 200
        assert value["content"] == "200 OK"

    response = app.get('/', status=404)
    assert response.status == 404
    with closing(dbm.open(path)) as db:
        assert cache_key not in db
