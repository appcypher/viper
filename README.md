<div align="center">
    <a href="#" target="_blank">
        <img src="https://image.flaticon.com/icons/svg/296/296589.svg" alt="Viper Logo" width="140" height="140"></img>
    </a>
</div>


<h1 align="center">VIPER</h1>


#### Introduction
A Python compiler that supports Python 3.7 syntax. Viper will support two (2) modes of compilation. Each with varying levels of compatibility with CPython.

- Strict Mode

    This mode is makes compatibility tradeoffs but delivers a better performance using static analysis techniques like type inference and lifetime analysis. Performance improves further when types are provided.

- Dynamic Mode

    This (also compatibility mode) is expected to be compatible with CPython, therefore it does not necessarily give any performance benefits. However, providing type annotations should result in better performance.

