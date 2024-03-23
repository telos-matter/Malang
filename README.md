# Malang &nbsp; ![DEVELOPMENT STATUS: version 3 pre-release](https://badgen.net/badge/DEVELOPMENT%20STATUS/version%203%20pre-release/green)
**Ma**th **lang**uage

Programming / computing using, literally, only algebraic operations.

That is, any program that you write in the language, becomes a mathematical operation that, when computed / evaluated, gives the expected result of the program.

You can read the [wiki](https://github.com/telos-matter/Malang/wiki) to understand the **what** and the **how**. But in here I will discuss the

# Why?
Well mainly because it was a fun / interesting project.

I got the idea while watching this [YouTube video](https://www.youtube.com/watch?v=j5s0h42GfvM) that talks about this Prime generating formula. It seemed really fascinating and it was something new to me and I was really intrigued by this idea that a mathematical formula can have features similar to that in programming languages.
And so I experimented a bit with the idea to see if I can do anything with it, and if I remember correctly, one of the first things I was able to come up with was the `not` gate. And that got me like so: 🤯.

And so the desire of being able to mimic programming language features in math slowly turned into wanting to make it into an actual programming language that is _compiled_ to that.

And while developing it I was always fixated on the idea / concept that
> I want the numbers and operations to do everything and not the _compiler_ or something else.

And indeed I managed to do so.

Is there any practical real-life use for this programming language? At the moment no, and it's not even turing complete. But it is **my** project and it was really **fun** developing it.

***

# Requirements
Nothing, just `python 3.10` or newer.

# How-to
After cloning the repo, you can run files using [malang.py](malang.py) like so:
```console
$ python malang.py file_to_run
```

Don't forget the check out the couple of options available when running a file by using:
```console
$ python malang.py -h
```

# Examples
Some examples are available in the [examples dir](examples). A favorite is the [FizzBuzz](examples/fizzBuzz.mlg) example, as that it uses all the interessting aspects of the language.

You can run it like so:
```console
$ python malang.py -i examples/fizzBuzz 15
```

# Syntax support
I made a VSCode extension that provides syntax highlighting / support for the language, but I haven't published it. Will maybe do so later on, or if someone is interested.

***

> **Note:** do mention this repo in case of any public use.
