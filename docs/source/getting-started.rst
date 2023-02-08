.. -*- encoding: utf-8; -*-


Getting Started
===============

.. warning:: if you're using asyncio, read :ref:`the last section
	     <9. AsyncIOchronously doing stuff>` first.


1. Trying again
---------------

Let's say we have to query a buggy webserver, which, once in a while, resets
the client connection.

Let's say, when that happens, we want to immediately re-perform the same
request to that server.

To do that easily, we would just have to use the :py:func:`~kaioretry.retry`
decorator, when defining the function.


.. code-block:: python
   :caption: Basic usage (1): try again.
   :name: same-player-shoot-again
   :emphasize-lines: 3

    from kaioretry import retry

    @retry(tries=2)
    def query_some_buggy_server(url):
        ...


This way, if the `query_some_buggy_server` function raises an exception, the
decorator will immediately call `query_some_buggy_server` again.

Since we specified `tries=2`, then a single new try will be performed in case
of failure. (It's `tries=2` does not mean `retries=2`)


2. Trying until it works
------------------------

Now, let's hypothesize that the server is reeeeeaaally buggy, but you know it
randomly works.

Your solution here is to retry until it works, no matter how many attempts it
takes.


.. code-block:: python
   :caption: Basic usage (1): try until it works.
   :name: just-make-it-work
   :emphasize-lines: 5

    from kaioretry import retry

    # tries=-1 is the default. For the same purpose,
    # any negative value would do.
    @retry(tries=-1)
    def query_some_buggy_server(url):
        ...

.. note::

   `tries` default value is -1. It means that by default `retry` will call the
   function again and again..... and agaaaaaaain, until it succeeds.


3. Catching specific exceptions
-------------------------------

For the sake of continuity, let's now consider the fact, that you *know* that,
when the server fails, a :py:class:`ConnectionError` is raised, and nothing
else.

You would be, then, well advised not to retry, on, say, a
:py:class:`KeyError`, which would likely represent a flaw in your own code,
like typo, or a (in)valid answer you did not expect.

To achieve this, you would have to specify the exception class that will
trigger another try, by using the `exceptions` parameter.

.. code-block:: python
   :caption: Exceptions (1): only retry on a specific error.
   :name: retry-on-given-error
   :emphasize-lines: 5

    from requests import ConnectionError

    # Remember, tries=-1 is the default, so, even in explicit is better than
    # implicit, you do not have to repeat default values.
    @retry(exceptions=ConnectionError)
    def query_some_buggy_server(url):
        ...


.. note:: The `exceptions` parameter default value is :py:class:`Exception`,
          which means that KaioRetry will loop for any error encountered by
          the decorated function.


Now, if you discover that the buggy server also generates some time
out... Then brace yourself, and just add it to the `exceptions` parameter
value.


.. code-block:: python
   :caption: Exceptions (2): only retry on some specific errors
   :name: retry-on-given-errors
   :emphasize-lines: 3

    from requests import ConnectionError, ReadTimeout

    @retry(exceptions=(ConnectionError, ReadTimeout))
    def query_that_damn_server(url):
        ...


4. Adding a delay between tries
-------------------------------

This being said, it is, I think, most of the time, advisable to wait a bit
between attempting again, after a failure. We dont want to spam to death an
already sick server, do we? This is made possible through the the ``delay``
parameter.

Let's introduce a 2 seconds delay between each try, by using the `delay`
parameter.


.. code-block:: python
   :caption: Basic Usage (3): only
   :name: delay
   :emphasize-lines: 3

    from requests import ConnectionError

    @retry(exceptions=ConnectionError, tries=2, delay=1)
    def query_that_damn_server(url):
        ...


.. note:: ``delay`` value is expressed in seconds. Either whole seconds
	  (:py:class:`int`) or whole seconds-and-then-some
	  (:py:class:`float`).

.. note:: `delay` default value is 0, which means no wait between tries.

.. warning:: `delay` cannot be negative, for obvious reasons. (like breaking
             the space-time continuum)


5. Increasing logs to analyse the retry process
-----------------------------------------------

You can actually check the time spent waiting between each tries, by
simply increasing the log level.

So from the previous example:


.. code-block:: text
   :caption: Increase verbosity
   :emphasize-lines: 3-7

    >>> logging.basicConfig(stream=sys.stdout, encoding='utf-8', level=logging.DEBUG)
    >>> query_that_damn_server()
    Retry(ConnectionError, Context(tries=2, delay=(0<=(1+0)*1<=None))): ConnectionError caught while running query_that_damn_server: reset by peer
    5c474e70-2d0d-44dd-90a9-745d9a21bb2e: 1 tries remaining
    5c474e70-2d0d-44dd-90a9-745d9a21bb2e: sleeping 1 seconds
    Retry(ConnectionError, Context(tries=2, delay=(0<=(1+0)*1<=None))): ConnectionError caught while running query_that_damn_server: reset by peer
    Retry(ConnectionError, Context(tries=2, delay=(0<=(1+0)*1<=None))): query_that_damn_server failed to complete

.. note:: you can set your own :py:class:`~logging.Logger` by using the
          `logger` parameter.

.. note:: The uuid in the log lines will change every time the decorated
          version of the function is called, allowing you to keep track of the
          retry series.


6. Non-constant delay
---------------------

If you want to increase, bit by bit, the delay value after each try, you give
a non-zero value to the `jitter` parameter.

For instance, if we want the delay between tries to be 1 second, then 2
seconds, then 3, etc. then we will set an initial value of 1 (`delay=1`) and
an increase value of 1 (`jitter=1`).


.. code-block:: python
   :caption: Basic delay: 1, 2, 3, 4, 5, 6...
   :name: delay-and-jitter
   :emphasize-lines: 3

    from requests import ConnectionError

    @retry(exceptions=ConnectionError, tries=10, delay=1, jitter=1)
    def query_that_damn_server(url):
        ...

.. note::

   jitter default value is 0, which means that, by default, `delay` stays put
   and keep its initial value.

.. note::

   Also, note that while `jitter` is permitted to be negative (which would
   imply `delay` becoming smaller and smaller), `delay` will internally be
   kept positive.


7. Exponential delay increase!
------------------------------


Another way to alter `delay` between each call is to use the `backoff`
parameter. `delay` will be multiplied by `backoff`.


.. code-block:: python
   :caption: Basic delay: 1, 2, 4, 8, 16, 32...
   :name: delay-and-backoff
   :emphasize-lines: 3

    from requests import ConnectionError

    @retry(exceptions=ConnectionError, tries=10, delay=1, backoff=2)
    def query_that_damn_server(url):
        ...

.. note:: `backoff` default value is 1, which means by default, things stay
          the same.

.. note:: Also, it is possible to set `backoff` to a :py:class:`float` value.

.. note:: *Also also*, it is also possible to set `backoff` to a value between
   0 and 1, which would make `delay` shrink after each try.

.. note:: *ALSO also also*, combinations of `jitter` and `backoff` are
   permitted. `backoff` will multiply `delay` *before* `jitter` is added.

.. warning:: As previously reminded, at run time, `delay` value will never be
             less than zero.


8. Setting boundaries
---------------------

Two extra parameters are available to control `delay`: `min_delay` and
`max_delay`. If `max_delay` is set then, it will become the upper limit for
`delay` value. The `min_delay` parameter is the lower limit of `delay` and
`delay` will never be updated to less than `min_delay`


.. code-block:: python
   :caption: min'n'max.
   :name: min-max
   :emphasize-lines: 3-4

    from requests import ConnectionError

    @retry(exceptions=ConnectionError, tries=10, delay=1, backoff=2,
           min_delay=1, max_delay=10)
    def query_that_damn_server(url):
        ...


.. note:: If `max_delay` is unset or `None`, and if you're not
	  careful, then... things could take a while to complete.

.. note:: Consistently with `delay`'s own constraints, `min_delay` cannot be
          set to a negative number.


9. AsyncIOchronously doing stuff
--------------------------------

Let's say you're a smart cookie and you use the :py:mod:`asyncio` framework
everywhere (just like I do). You know that, for that purpose, using a
synchronous decorator over a coroutine function will not work. Maybe you've
experienced it already (just like I have).

So you want an asyncIO-friendly retry decorator, without changing too much of
your code?

Madame, Monsieur, Others, voila:

.. centered:: The :py:func:`~kaioretry.aioretry` decorator!


.. code-block:: python
   :caption: aioretry basic usage
   :name: aioretry-usage
   :emphasize-lines: 4

   from aiohttp import ClientConnectionError
   from kaioretry import aioretry                 # And voila

   @aioretry(exceptions=ClientConnectionError)    # Tadaaa
   async def my_fantabulous_but_error_raising_coroutine():
       ...


The :py:func:`~kaioretry.aioretry` decorator produces coroutine
functions. Besides that, it will work exactly like
:py:func:`~kaioretry.retry`: it accepts the same parameters, performs the same
internal magic.


.. note:: :py:func:`~kaioretry.aioretry` uses :py:func:`asyncio.sleep` instead
	  of :py:func:`time.sleep`. Duh.


10. Regular/Sync functions in an AsyncIO context
------------------------------------------------

.. note:: TL;DR: Always use :py:func:`~kaioretry.aioretry` in an AsyncIO
          context. Even for regular functions. :py:func:`~kaioretry.aioretry`
          will turn regular functions into coroutine functions and you will
          have to await them.

.. warning:: You should never use :py:func:`~kaioretry.retry` in an
             :py:mod:`asyncio` context. Even for for regular (non-coroutines)
             functions.

.. warning:: Never.

.. warning:: This is a warning box abuse, right?


Anyway. "`Why?`" will you ask. It's quite simple. :py:func:`time.sleep` also
freezes the event loop.

You see, AsyncIO is a cooperative, event-driven framework.

It's cooperative, because every time a coroutine function does an `await` on
something, what it does in fact is notifying the scheduler (the event loop),
in a friendly way, that it can give the priority to something else, for now.

By calling :py:func:`time.sleep` in a coroutine function, you will prevent
said coroutine function to perform the next `await`. During the time it
sleeps, the coroutine function will not be able to hand over to the event
loop. Thus freezing the whole scheduling process. Not the best way to
cooperate, if you ask me.

That's why AsyncIO comes with its own sleep primitive,
:py:func:`asyncio.sleep`, which is awaitable.

:py:func:`~kaioretry.aioretry` will work on a regular function... but it will
turn it into a coroutine function, and you will have to `await` it. In return
it will not freeze your process.

Sounds fair? Sounded fair enough to me when I wrote that.


.. code-block:: python
   :caption: e.g: consider these 2 stupid functions
   :name: sync-vs-async

   from kaioretry import retry, aioretry

   @retry
   def f():
       return 1

   @aioretry()
   def g():
       return 1


.. code-block:: python
   :caption: Now if we run them...
   :name: sync-vs-async-run
   :emphasize-lines: 5

   >>> f()
   1
   >>> # f is as stupid as you can guess.
   >>> g()
   <coroutine object g at 0x7f3dab722bd0>
   >>> # g has become a coroutine function, though.
   >>> # We have to await it,
   >>> # Or feed it to asyncio.run.
   >>> asyncio.run(g())
   1


I hope this is not too confusing for you. Good luck. :]

Let me know if you can explain this better. Pull requests are always welcome.


.. warning:: if you came here from the very top of the page and dont know where
             to start, you should go back to :ref:`the top <1. Trying again>`.
