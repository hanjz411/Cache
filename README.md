# Designing a Simple Cache

A cache is a hardware/software component that stores data so that future requests for that data can be served faster. Basically, it is a key/value store to access frequently required data. Instead of accessing a database or compute every time, we can store it in a cache for easy retrieval. 

For this cache, we made an in-memory cache, or using shared memory within the application. To scale for large number of requests/second, we can horizontally scale our resources and nodes to increase throughput. 

Since a cache should have a maximum size, we will need an eviction method. We used a Doubly-Linked-List (implemented using a Python OrderedDict) and a Hashmap to implement a Least-Recently-Used Cache (LRU) 

We use a DLL for easy manipulation of the last used item. However, traversing through this list is expensive and costly, so we supplement it with a Hashmap for easy lookup of nodes. 

While we have fast lookup times - O(1) access, this method is very space intensive and we will need to store the size of the cache. This also utilized two distinct data structures. 

To make this threadsafe, we've added a mutex, or lock to ensure that no other threads/processes can modify it's resources. 

To implement an expiration or Time-To-Live (TTL) for each node, we add an optional TTL parameter and timestamp when the node is added. Next, we introduce a housekeeping/garbage collection method that will be scheduled to check if there are any expired items and subsequently remove them. 
