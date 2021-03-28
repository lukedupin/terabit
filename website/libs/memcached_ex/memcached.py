"Memcached cache backend"

import pickle
import re
import time

from django.core.cache.backends.base import (
    DEFAULT_TIMEOUT, BaseCache
)


class BaseMemcachedCache(BaseCache):
    def __init__(self, server, params, library, value_not_found_exception):
        super().__init__(params)
        if isinstance(server, str):
            self._servers = re.split('[;,]', server)
        else:
            self._servers = server

        # The exception type to catch from the underlying library for a key
        # that was not found. This is a ValueError for python-memcache,
        # pylibmc.NotFound for pylibmc, and cmemcache will return None without
        # raising an exception.
        self.LibraryValueNotFoundException = value_not_found_exception

        self._lib = library
        self._options = params.get('OPTIONS') or {}

    @property
    def _cache(self):
        """
        Implement transparent thread-safe access to a memcached client.
        """
        if getattr(self, '_client', None) is None:
            self._client = self._lib.Client(self._servers, **self._options)

        return self._client

    def get_backend_timeout(self, timeout=DEFAULT_TIMEOUT):
        """
        Memcached deals with long (> 30 days) timeouts in a special
        way. Call this function to obtain a safe value for your timeout.
        """
        if timeout == DEFAULT_TIMEOUT:
            timeout = self.default_timeout

        if timeout is None:
            # Using 0 in memcache sets a non-expiring timeout.
            return 0
        elif int(timeout) == 0:
            # Other cache backends treat 0 as set-and-expire. To achieve this
            # in memcache backends, a negative timeout must be passed.
            timeout = -1

        if timeout > 2592000:  # 60*60*24*30, 30 days
            # See https://github.com/memcached/memcached/wiki/Programming#expiration
            # "Expiration times can be set from 0, meaning "never expire", to
            # 30 days. Any time higher than 30 days is interpreted as a Unix
            # timestamp date. If you want to expire an object on January 1st of
            # next year, this is how you do that."
            #
            # This means that we have to switch to absolute timestamps.
            timeout += int(time.time())
        return int(timeout)

    def add(self, key, value, timeout=DEFAULT_TIMEOUT, version=None):
        return self._cache.add(key, value, self.get_backend_timeout(timeout))

    def get(self, key, default=None, version=None):
        value = self._cache.get(key)
        return value if value is not None else default

    def set(self, key, value, timeout=DEFAULT_TIMEOUT, version=None):
        if not self._cache.set(key, value, self.get_backend_timeout(timeout)):
            # make sure the key doesn't keep its old value in case of failure to set (memcached's 1MB limit)
            self._cache.delete(key)

    def rw(self, key, value, timeout=DEFAULT_TIMEOUT, version=None):
        return self._cache.rw( key, value, self.get_backend_timeout(timeout))

    def delete(self, key, version=None):
        return bool(self._cache.delete(key))

    def close(self, **kwargs):
        # Many clients don't clean up connections properly.
        self._cache.disconnect_all()

    def clear(self):
        self._cache.flush_all()


class MemcachedCache(BaseMemcachedCache):
    "An implementation of a cache binding using python-memcached"
    def __init__(self, server, params):
        from website.libs.memcached_ex import memcache_ex
        super().__init__(server, params, library=memcache_ex, value_not_found_exception=ValueError)

    @property
    def _cache(self):
        if getattr(self, '_client', None) is None:
            client_kwargs = {'pickleProtocol': pickle.HIGHEST_PROTOCOL}
            client_kwargs.update(self._options)
            self._client = self._lib.Client(self._servers, **client_kwargs)
        return self._client
