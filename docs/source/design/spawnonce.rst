.. _design-version2:

Just Keep The Process Alive
^^^^^^^^^^^^^^^^^^^^^^^^^^^

The 'spawn' startmethod is said to be be 'rather slow compared to using fork or forkserver.'(:py:class:`multiprocessing.Process`). The tests with the first multi processor parallel code verion where every Process() spawned, just lasts for a onetime only run, not only seems to support this statement, but also to provide reasons to suspect some intelligent caching, because the time to need to do the a 7k fit drops from 9 seconds the first time, to a bit more than three seconds the last time, which might not be the actual minimum. Altering the code into a second, hopefully much faster version, where processes will be created only once and kept alive for the lifetime of the script, seems therefore an interesting option.

How to reuse the a spawned process
----------------------------------

A process that has been spawned on a processor can be kept 'alive' by:

1. Write a custom class which extends the multoprocessing.Process class
2. Override the constructor of Process with at least two parameters: an input queue and a output queue.
3. Override the run() method of Process and keep this method alive by a 'forever loop' or a conditional loop.
4. As Python serializes all necessary stuff to run the process, trying to keep the numbers of bytes needed to be serialized for each fit cycle as low a possible.
5. It is preferable to be able to terminate, stop or exit a process which is not of use anymore. The multiprocessing docs advises not to use Process.terminate on processes which have shared resources. When using queues, as in this case, it is key to first remove all items from queues before joining the process at hand. The docs give two options:

    a. An option given by docs is the child process to call 'Queue.cancel_join_thread' on the queues to prevent deadlock.
    b. The last example of multiprocessing docs shows how to use queues with worker processes, collect the result and finally quitting all workers. The interesting piece of code: the use of the Python keyword :py:func:`iter`:
    
    .. code-block:: python

        def worker(input, output):
        for func, args in iter(input.get, 'STOP'):
            result = calculate(func, args)
            output.put(result)

    Here, :py:func:`iter` has been used with two parameters. The first parameter of 'iter' is a callable object to  interate on. The second parameter is a so called 'sentinel'. The moment the iterator's __next__() function will return a value equal to the sentinal, 'StopIteraton' will be raised, and the loop with :py:func:`iter` will finish.

    The second options seems the better option, because looping will last until that one special message  from parent process to child process has been.