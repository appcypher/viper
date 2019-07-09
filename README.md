<div align="center">
    <a href="#" target="_blank">
        <img src="https://image.flaticon.com/icons/svg/296/296589.svg" alt="Viper Logo" width="140" height="140"></img>
    </a>
</div>


<h1 align="center">VIPER</h1>


#### Introduction
A Python compiler that supports Python 3.7+ syntax. Viper will support two (2) modes of compilation. Each with varying levels of compatibility with CPython.

- Strict Mode

    This mode is makes compatibility tradeoffs but delivers a better performance using static analysis techniques like type inference and lifetime analysis. Dynamic semantics are not allowed in strict mode.

- Dynamic Mode

    Dynamic mode (also called compatibility mode) is expected to be mostly compatible (not bytecode-compatible) with CPython, therefore it does not necessarily give any performance benefits. On the other hand, providing type annotations should result in better performance.

#### Modes
- Strict Mode

```sh
viper sample.py
```

- Dynamic Mode

```sh
viper sample.py --enable-dynamic-mode
```


#### Non-goals
- While this project aims to be compatible with the Python 3.7+ source code, it will not be compatible with CPython's bytecode. As a result, it won't work as expected with packages that rely bytecode introspections. A  notble example is the PonyORM package.


#### Issues
- Python code with eval.

```
stdlib.wasm (host env = wasabi | wasi)
compiler.wasm (export func compile(string) -> wasm)
eval.wasm (import ... from stdlib.wasm and compiler.wasm)

viper compiles all into single wasm binary.
```
