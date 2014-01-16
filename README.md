# jsondb

## Links and misc info

[Documentation][_docs]

develop: [![Build Status](https://travis-ci.org/paulollivier/jsondb.png?branch=develop)](https://travis-ci.org/paulollivier/jsondb) [![Coverage Status](https://coveralls.io/repos/paulollivier/jsondb/badge.png?branch=develop)](https://coveralls.io/r/paulollivier/jsondb?branch=develop)

master: [![Build Status](https://travis-ci.org/paulollivier/jsondb.png?branch=master)](https://travis-ci.org/paulollivier/jsondb)

## What is my purpose into existence?

Maybe a DB engine with JSON as storage is good. Not much for perfs, but i think that for small projects, where we may need to edit data manually, it may be acceptable and convenient to use...

We will see.

## Ok, so we have a json db. Now what?

well, we could have a *relational* db.

We must find a way to say *get object a, which has child b where the value of b.arg = "hello"*.

Proposition: add a `child_reqs={"a.b.arg": "hello", {"and so": "on"}}` param to `JSONdb.get()`.

[_docs]: http://jsondb.readthedocs.org/
