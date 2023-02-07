What and why is that?
=====================

.. _retry: https://github.com/invl/retry


Introduction
------------

KaioRetry is (yet another?) retry decorator implementation, which is clearly
inspired by the venerable retry_ module and is actually backward compatible
with it.

I say *backward* because, while retry_ clearly did the job for me for a
time, at some point I've encountered a big limitation: it did not work
with asyncio coroutines. And the last commit is like 6 years old.

I found a few alternatives [#]_ [#]_ [#]_ [#]_ [#]_ but all of them had downsides
and were not up to my standard and nor my needs.

What I wanted was to have a single module (to reduce the number of
dependencies), to have the same API to decorate either sync or async functions
(less things to remember), something that would have been maintained a bit.

So I started this project. With two things in mind:

1. It should be backward compatible with retry_, and
2. The code duplication, between the `sync` and `async` versions of the
   decorator, should be smartly kept to a very very veeeeeery strict
   minimum. It's a work in progress though.

Anyway, if you're reading this documentation, it means I took my sweet time to
write it [#]_. *After* proving my implementation worked.

.. [#] https://github.com/kaelzhang/python-aioretry
.. [#] https://github.com/lxl0928/retrying-async/blob/master/retrying_async.py
.. [#] https://gist.github.com/ultrafunkamsterdam/db2a0ff6d4ea189b893b9d24374f33e0
.. [#] https://gist.github.com/alairock/a0235eae85c62f0f0f7b81bec8aa378a
.. [#] Google's first page on aioretry, heh, basically.
.. [#] Captain obvious is obvious.
