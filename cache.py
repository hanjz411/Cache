""""
Wallaroo Labs Assignment 
Jeffrey Han
"""

import logging
import threading
from time import time
from collections import OrderedDict, namedtuple

_CachedObjectInfo = namedtuple('CachedObjectInfo', ['name', 'hits', 'ttl', 'timestamp'])

class CachedObject(object):
    def __init__(self, name, obj, ttl=0):
        """
        Initializes a new cached object

        Args:
            name               (str): Human readable name for the cached entry
            obj               (type): Object to be cached
            ttl                (int): The TTL in seconds for the cached object (expiration)

        """
        self.hits = 0
        self.name = name
        self.obj = obj
        self.ttl = ttl
        self.timestamp = time()

class CacheInventory(object):
    """
    Store for cached objects

    """
    def __init__(self, maxsize=0, housekeeping=0):
        """
        Initializes a new cache inventory

        Args:
            maxsize      (int): Upperbound limit on the number of items
                                that will be stored in the cache inventory
            housekeeping (int): Time in minutes to perform periodic
                                cache housekeeping

        """
        if maxsize < 0:
            print("Illegal cache inventory size")

        if housekeeping < 0:
            print("Illegal garbage collection period")

        self._cache = OrderedDict()
        self.maxsize = maxsize
        self.housekeeping = housekeeping * 60.0
        self.lock = threading.RLock()
        self._schedule_housekeeper()

    def __len__(self):
        with self.lock:
            return len(self._cache)

    def __contains__(self, key):
        with self.lock:
            if key not in self._cache:
                return False

            item = self._cache[key]
            return not self._has_expired(item)

    def _has_expired(self, item):
        """
        Checks if a cached item has expired and removes it if needed

        Args:
            item (CachedObject): A cached object to lookup

        Returns:
            bool: True if the item has expired, False otherwise

        """
        with self.lock:
            if item.ttl != 0:
                if time() > item.timestamp + item.ttl:
                    print("Object %d has expired and will be removed from cache", self.info(item.name))
                    logging.debug("Object %s has expired and will be removed from cache", self.info(item.name)                )
                    self._cache.pop(item.name)
                    return True
                return False

    def _schedule_housekeeper(self):
        """
        Schedules the next run of the housekeeper

        """
        if self.housekeeping > 0:
            t = threading.Timer(
                interval=self.housekeeping,
                function=self._housekeeper
            )
            t.setDaemon(True)
            t.start()

    def _housekeeper(self):
        """
        Remove expired entries from the cache on regular basis

        """
        with self.lock:
            expired = 0
            print("Starting cache housekeeping [%d items(s) in cache]", len(self._cache))
            logging.info("Starting cache housekeeper [%d item(s) in cache]", len(self._cache)            )

            items = list(self._cache.values())
            for item in items:
                if self._has_expired(item):
                    expired += 1

            print("Cache housekeeping completed [%d item(s) removed from cache]", expired)
            logging.info("Cache housekeeper completed [%d item(s) removed from cache]", expired)
            self._schedule_housekeeper()

    def add(self, obj):
        """
        Add an item to the cache inventory

        If the upperbound limit has been reached then the last item
        is being removed from the inventory.

        Args:
            obj (CachedObject): A CachedObject instance to be added

        """
        if not isinstance(obj, CachedObject):
            print("Need a valid instance to add in the cache")

        with self.lock:
            if 0 < self.maxsize == len(self._cache):
                popped = self._cache.popitem(last=False) 
                print("Cache maxsize reached, removing %s", popped) 
                logging.debug("Cache maxsize reached, removing %s", popped)               

            self._cache[obj.name] = obj
            print("Adding object to cache %s", self.info(name=obj.name))
            logging.debug("Adding object to cache %s", self.info(name=obj.name))

    def get(self, name):
        """
        Retrieve an object from the cache inventory

        Args:
            name (str): Name of the cache item to retrieve

        Returns:
            The cached object if found, None otherwise

        """
        with self.lock:
            if name not in self._cache:
                return None

            item = self._cache[name]
            if self._has_expired(item):
                return None

            item.hits += 1
            print("Returning object from cache %s", self.info(name=item.name))
            logging.debug("Returning object from cache %s", self.info(name=item.name))

            return item.obj

    def delete(self, name):
        """
        Deletes an object from the cache inventory

        Args:
            name (str): Name of the item in cache to delete 

        """

        with self.lock:
            if name not in self._cache:
                print("Item not found in cache")
                return None
            else:
                print("Removing object from cache %s", name)
                logging.debug("Removing object from cache %s", name)
                del self._cache[name]

        return None

    def clear(self):
        """
        Remove all items from the cache

        """
        with self.lock:
            self._cache.clear()

    def info(self, name):
        """
        Get info about a cached object

        Args:
            name (str): Name of the cached object

        """
        with self.lock:
            if name not in self._cache:
                return None

            item = self._cache[name]
            return _CachedObjectInfo(item.name, item.hits, item.ttl, item.timestamp)


test = CacheInventory(3, 1)
item1 = CachedObject(1, 2)
item2 = CachedObject(2, 4)
item3 = CachedObject(3, 6, 2)
item4 = CachedObject(4, 5)

test.add(item1)
test.add(item2)
test.add(item3)
test.add(item4)
print(test.get(4))
test.delete(4)
print(test.get(4))



