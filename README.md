# retux

[![PyPI](https://img.shields.io/pypi/v/retux?style=plastic)](https://pypi.org/project/retux)
[![Python version](https://img.shields.io/pypi/pyversions/retux.svg?style=plastic)](#)
[![Code style](https://img.shields.io/badge/code%20style-black-black?style=plastic)](#)
[![Discord](https://img.shields.io/discord/993549800911941672?style=plastic)](https://dsc.gg/retux)

A Discord API wrapper built with good intentions.

## Introduction

Nowadays, bot developers are offered to use libraries that introduce
unnecessary complexity through abstraction, slightly expensive performance
and boilerplate code. retux tries to define itself off of similar ideals,
but with a fair approach.

Over time, I found it painful and frustrating to use various Discord libraries
due to their reliance on good faith of a programmer to do things exactly the
way they intended. That is why, with retux, I wanted to create something better
with these philosophies.

### Simple to understand.

*Spend less time debugging your code, and more time writing what you want.*

A majority of programmers and bot developers alike I've met have all complained
about the lack of simplicity in a dependency. It's important to let bot developers
understand what's going on. retux tackles this by giving ample documentation wherever
it can (even if it's verbose) and follows with being **easy to use.**

### Easy to use.

*End-user facing code shouldn't contain unnecessary complexity to provide the bare
minimum.*

Bot developers spend a lot of time trying to implement their features by whatever the
library provides. Granted, a Discord library is nothing more than a wrapper for the API
given, but it is almost expected that libraries take the extra step in providing an easily
accessible set of tools and containers.

### Versatile.

*Recycle current existing code paradigms elsewhere, so you can borrow assets off of one
another.*

Developers **love** the ability to reuse and recycle existing code elsewhere. A Discord library should be no
different and open to giving the bot developer as much artistic freedom as they so desire.

### Safe.

*Bot developers are human after all. We'll correct your mistakes for you so that you can keep
chugging along.*

As society makes more technological advancements, it's become a concern of my own that any
dependency, even a Discord library should consider looking into the possibility of ensuring
runtime safety. With retux, your end-user facing code is generously checked and potentially
sanitised if inputted wrongly to the API. You should be able to make code *work*, not
fight for technical correctness.

## Is this another fork?

Despite the recent trend for developers to begin forking and maintaining their own Discord
libraries akin to [discord.py](https://github.com/Rapptz/discord.py), our library is entirely
separate from any other and does not rely on other API wrappers. While one could argue that
other competing libraries are better than one another, we respect each one's design decisions
and disagree to implementation.

## When will version 1.0 come out?

There is currently **no set date for version 1.0**. When a
release date has been decided upon, we will let you know. :)
