
## LEXER

## PARSER
##### PACKRAT PARSER
- Results of all paths that are taken are memoized.
- A parse function result should always be an AST. Avoid returning a parse tree.
- A parse function result should not hold values, but references to token elements.

## SEMANTIC ANALYSIS


## STATIC ANALYSIS
- Analysis artifacts
    - Reference graphs
    - Type instantiations
    - Function instantiations

- Indices and Slices

    - Negative indices
        ```py
        subarray = array[:-2]
        value = array[:-2]
        ```

        ##### IMPLEMENTATION

        Since bound checks are going to be made anyway, we should find a way to make positive indices as fast as they would have been and negative indices a check slower.

        ```py
        if -1 < index > len(array): # positive indices
            value = array[index]
        elif 0 > index >= -len(array): # negative indices
            value = array[len(array) + index]
        else: # out of bounds indices
            raise OutOfBoundsError('...')
        ```

- Lists

    - Uninitialized list
        ```py
        ls = []
        print(ls) # Uninitialized empty list
        ```

        ```py
        def func(ls):
            ls.append('hi')

        ls = []
        func(ls)
        ```

        ##### IMPLEMENTATION

        If a list is uninitialized, we wait until it is first used. Its type is inferred based on how it is used.

        If it is passed to a function, its type is determined by the argument type, otherwise it is determined by its usage in the function's body.

- Variable

    - No special declaration syntax
        ```py
        num = 45
        print(num)

        def func():
            nonlocal num
            num = 56
            print(num)

        func()
        ```


    - Shadowing
        ```py
        num = 45
        num = "hi"
        ```

        #### IMPLEMENTATION

        A local variable can be shadowed. In the above example, the second `num` is a totally different variable from the first `num`.

        Global variables cannot be shadowed.


- Generators

- Closures

- Decorators

- Callable Objects

- Typing

    - Duck typing
        ```py
        def foo(bar):
            bar.name
        ```

        ##### IMPLEMENTATION

        Structural typing can be used in place of duck typing.

        Methods are actually functions instantiations with interface that conform to their arguments structures.

        ```py
        """
        cat: Cat [ name: str ]
        john: Person [ age: int, name: str ]
        hibiscus: Plant [ name: int, age: int ]
        """

        foo(cat)
        foo(john)
        foo(hibiscus)

        """
        INSTANTIATIONS

        foo: (Object [ str ])
        foo: (Object [ .., str ])
        foo: (Object [ int, .. ])
        """
        ```

    - Type unsafety
        * Control flow
            ```py
            if condition:
                identity = 45
            else:
                identity = 'XNF452423'

            """
            identity: int | str
            """
            ```

        * Lists covariance

            ```py
            animals: Animal = []

            animals.append(Cat())
            animals.append(Dog())

            print(animals[0])

            """
            animals: list[Cat | Dog]
            """
            ```


        ##### IMPLEMENTATION

        Variables with uncertain types don't make it far because to use them with any function require that any field or method accessed through them exists across the types.

        ```py
        if condition:
            identity = 45
        else:
            identity = 'XNF452423'

        """
        identity: int | str
        """

        """
        ERROR!

        identity -= 5 # str doesn't have a `-` operand
        """

        if type(identity) == int:
            identity = 5
        else:
            identity = 7

        """
        identity: int
        """
        ```

        ```py
        animals: Animal = [Cat(), Dog()]

        """
        animals: list [
            len: usize,
            capacity: usize,
            buffer: buffer [
                0: Bundle[type: usize, cat: ref Cat],
                1: Bundle[type: usize, cat: ref Dog],
                ...
            ]
        ]
        """

        animal = animals[0]

        """
        animal: Cat | Dog
        """

        if animal := cast(Cat):
            animal.meow()
        ```

    #### IMPLEMENTATION

    Viper is all about structural typing. It sees type unsafety and covariance as intersection types and inheritance as union types.


#### FEATURES IN PYTHON THAT BREAK STATIC GUARANTEES OR PREVENT STATIC OPTIMIZATIONS

- Eval
    - Use of eval
        ```py
        eval('2 + 3')
        ```

- Introspection

    - Modifying the source bytecode
        ```py
        ...
        ```

- Type annotations

    - Type annotations don't affect the program
        ```py
        num: int = 50
        num = "Hello"
        ```

        Python doesn't take advantage of type annotations.

- Fields

    - Deleting fields
        ```py
        del john.name
        ```

- Tuples

    - Spreading within tuples
        ```py
        (head, *tail)
        ```

- Functions

    - Spreading dictionary as keyword arguments
        ```py
        func(**dictionary)
        ```

    - Spreading other iterables apart from tuple as arguments
        ```py
        func(*ls)
        ```

- Imports

    - Resolving imported modules at runtime
        ```py
        name, age = "John", 45

        from objects import Person

        john = Person(name)
        ```

- Variable

    - Shadowing a global or class variable.
        ```py
        num = 10
        print(num)

        def func():
            nonlocal num
            num = 0.005
            print(num)

        func()


        class Person:
            specie = 'homo sapiens'

            def change_specie(cls):
                cls.specie = 500

        Person.change_specie()
        ```

        #### IMPLEMENTATION

        A global and class variables types are determined at declaration point and cannot change. They can't be shadowed.


- Integers

    - Abitrary-precision integers
        ```py
        num = 9_223_372_036_854_775_807 + 1
        ```

        #### IMPLEMENTATION

        `int`s are represented as 64-bit integers.

- StopIteration

    - Using StopIteration error as an indication of an exhausted iterable
        ```py
        for i in range(10):
            print(25)
        ```

        #### IMPLEMENTATION

        Viper optimizes raising StopIteration errors away in for loops.


- Method resolution order
    ```py
    ```

    #### IMPLEMENTATION

    I really do not like Python's C3 linearization mro, but I'm going with it anyway.

## CODE GENERATION

- WebAssembly

## STANDARD LIBRARY

## POSSIBLE ADDITIONS

- Type annotation revamp
    ```py
    index: int = 9

    nums: list{int} = []

    age: int? = 45

    fn: (int, int) -> int = sum

    value: (int, int) = (1, 2, 3)

    mappings: dict{int, int} = dict()

    identity: int | str = 'XNY7V40'

    pegasus: Horse & Bird = Pegasus()

    class Person{T}(A, B):
        def __init__(self, name: T):
            self.name = name

    john = Person{str}('John Doe')

    def get_person{T}(name: T):
        return Person{T}(name)

    jane = get_person{str}('Jane Doe')
    ```

- Algebraic data types
    ```py
    type Option{T}:
        Ok(value: T) | Err() | None

    identity: Option{str} = None

    match identity:
        Some(value) => value
        Err() => raise Error()
        .. => pass

    identity: int | str = 'XNY7V40'

    match identity:
        *: int => value
        *: str => value
    ```

- Additional reserved keywords
    ```py
    const, ref, val, match, let, var, enum
    ```

- UFCS
    ```py
    ls = [1, 2, 3, 4]
    len(ls)
    ls.len()
    ```

- multiline lambda
    ```py
    map(
    lambda x:
        if x == 1:
            0
        else:
            5
    , array)

    map(
        array,
        lambda x:
            if x == 1:
                0
            else:
                5
    )
    ```

- const keyword
    ```py
    const pi = 3.141
    ```

- regex literal
    ```js
    regex = /\d+/
    ```

- new versions of certain functions and objects by default
    ```py
    map, sum,

    map(array, lambda x: x + 1)
    ```

- explicit referencing
    ```rust
    num2 = ref num
    ```

- dereferencing
    ```scala
    num3 = val num2
    ```

- symbols
    ```julia
    sym = $symbol
    ```

- statement assignment
    ```py
    value = (
        if name == 'Steve':
            20
        else:
            30
    )

    return (
        if name == 'Steve':
            20
        else:
            30
    )
    ```

- introducing more primitive types
    ```py
    u8, u16, u32, u64, usize
    i8, i16, i32, i64, isize
    f32, f64
    ```

- match statement
    ```py
    match x:
        Person(name, age) => 1
        [x, y = 5, z: int] => y
        [x, y = 5, z: str] => y
        (x, y = 5, 10, *z) => x
        {x, y = 5, 10, *z} => x
        dict { x, y['y'],  *z} => x
        10 or 11 and 12 => x
        0:89 => 10
        * => 11
    ```

- currying
    ```py
    add2 = add(2, ..)
    add10 = add(.., 10)
    ```


## GARBAGE COLLECTION
In the following code sample, it is evident that the object that `c` points to is last referenced at the call to `bar`, therefore it needs to be deallocated somewhere after the last point of reference.

```py
def foo():
    c = 'Hello'
    bar(c)
    """
    DEALLOCATE
    c
    """
    for i in array:
       print(i)
```

1. *Final Functions*

    Came up with a new deallocation strategy on August 4, 2018. This deallocation scheme relies on final functions _(will be explained below)_. With final functions, all that is needed is a metadata on each heap object specifying whether it can be freed or not. A function containing the entire lifetime of an object can then specify whether such object can be freed by an inner final/non-final function call.

    A final function is a function that doesn't pass its argument to another function call nor return it.

    <!-- Scope Reference Tracking

    ```py
    def qux(x): Final
        foo(x)
        foo(x)
        bar(x)

    def bar(x): Final
        foo(x)
        next_final_function_should_free(x)
        foo(x)

    def foo(x): Final
        x
        free(x)
    ``` -->

    Asynchronous Scope Reference Tracking

    ```py
    def qux(x):
        foo(x)
        foo(x)
        bar(x)

    def thud(x):
        foo(x)
        bar(x)
        foo(x)

    def fred(x):
        waldo(x)
        waldo(x)

    #--------------

    def waldo(x):
        corge(x)

    def corge(x):
        bar(x)
        bar(x)

    def bar(x):
        foo(x)
        foo(x)

    #--------------

    def foo(x): # Last function
        x + 1

    #------ DEFINITION SCOPE --------

    qux(x)
    free_after(3, x)
    thud(x)

    ```

    free directive is given at the highest scope where the variable is used

    This deallocation scheme is nice because it does not add an additional argument to a function signature and call to free function only happens in final functions. And given that it doesn't loop through heapvars, it is likely to be more efficient than deallocation bundle scheme.

#### Notes
* There can only be one subject pointer to an object.

* References can only be passed by assignment or by argument.

* Subject pointers are discarded when associated objects are no longer needed.

* When there is no concurrency, deallocation points of objects can be entirely determined at compile-time.

* When concurrency is involved, a count is maintained for concurrent coroutines that share an object and once one of the coroutine no longer needs an object, it decrements the count and checks if it can deallocate the object.
