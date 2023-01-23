# KaioRetry

KaioRetry is (yet another) retry decorator implementation, which is
clearly inspired by the original
[retry](https://pypi.org/project/retry) module and is actually
backward compatible with it.

I say *backward* because, while `retry` clearly did the job for me for a
time, at some point I've encountered a big limitation: it did not work
with asyncio coroutines. And it's been unmaintained for 6 years.

I found a few alternatives for that but none of them were both sync
and async and since I did not wanted to use 2 differents modules for
the same goal, I've decided to write this one, with the rule that the
code duplication, between the sync and async versions, should be
smartly kept to a very very strict minimum.

And here we are then.


## TODO List

* Add logging features
* Stop messing up the stack trace
* Complete Unit tests coverage.
* Add unit tests pipelines
* Add sphinx-generated documentation
* Write a decent README
* Publish documentation on readthedocs
* Publish package to pypi
* Lower requirements to python 3.10 if possible (and i feel like it)
* Lower requirements to python 3.9 if possible (and i feel like it)
