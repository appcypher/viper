<div align="center">
    <a href="#" target="_blank">
        <img src="https://image.flaticon.com/icons/svg/296/296589.svg" alt="Viper Logo" width="140" height="140"></img>
    </a>
</div>


<h1 align="center">VIPER</h1>


## Introduction
Viper is a compiler that compiles a restricted subset of Python to WebAssembly. Viper only supports Python3 syntax.

A possible long-term goal is to provide an option to compile dynamic CPython-compatible code, which is totally dependent on how well the idea is recieved.


## How does this differ from RPython, Nuitka or MicroPython
MicroPython is a well-optimized Python interpreter (with some JIT support) while Nuitka compiles Python to C. These two projects still allow dynamic aspects of Python, which means their performances will typically not reach the level of statically-typed languages.

RPython, on the other hand, is similar to this project, but the developers have [made it clear](https://rpython.readthedocs.io/en/latest/faq.html#do-i-have-to-rewrite-my-programs-in-rpython) several times their goal is not to make RPython a standalone language.


## Non-goals
Total semantic compatibility with CPython isn't a goal. For example, viper represents `int`s as 64-bit integers.


## Possible CLI
```sh
viper sample.vy
```

```sh
viper sample.py
```

