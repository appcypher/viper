
## LEXER

## PARSER

Viper parser is a PEG packrat parser.

- Results of all paths that are taken are memoized.
- A parse function result should always be an AST. Avoid returning a parse tree.
- A parse function result should not hold values, but references to token elements.

## SEMANTIC ANALYSIS

- Philosophy

    Viper has certain world-views that make the semantic analysis phase easier to understand and implement.

    - Every function, method and operator is seen as a normal function.
    - Every object has a structure and classes are how we describe or classify those structures. We only think in terms of classes when an object's structure is a subset of a class's structure.
    - Inheritance / variance is an abstraction we only care about for validation purposes. Relationship between objects are only seen in terms of how similar their structure is.

- Analysis artifacts

    - Scope tree

        - Object end-of-lifetime list

            Each scope contain a list of objects end-of-lifetime.
            Reference is followed only in the object's declaration scope and each object's end-of-lifetime point is adjusted as new references to it are encountered.

        - Type frames

            A type frame is created for each function.
            This type frame holds information about the type flow in the function's scope.
            To instantiate a type frame, we need to validate that the types used in the scope truly have an associated function instantiation.

        - Type mro lists (C3 linearization)

        - Type instantiations

        - Function instantiations

            Viper sees all operators and methods as functions. There is no difference at the semantic level.

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

        Global variables and fields cannot be shadowed.


- Fields

    - Adding new fields
        ```py
        class Person:
            def __init__(self, name):
                self.name = name

        john = Person("John")
        john.age = 45
        ```

        ##### IMPLEMENTATION

        The fields of an object is the collection of fields attached to the object through its entire lifetime.

        ```py
        """
        john: Object [ name: str, age: int ]
        """
        ```



- Generators

- Closures

    ```py
    def higher_order():

        x = 0

        def closure():
            x = 10
    ```

- Decorators

- Callable objects

- Type inference

- Typing

    - Duck typing
        ```py
        def foo(bar):
            bar.name
        ```

        ##### IMPLEMENTATION

        Structural typing can be used in place of duck typing. In fact, Viper sees type and object relationships structurally.

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

        * Covariance

            Viper is a covariance-based language. A subtype value can be assigned where a supertype value is expected.

            - Variables and fields
                ```py
                animals: Animal

                if condition:
                    animals = Cat()

                """
                animals: Animal | Cat
                """
                ```

            - Function arguments
                ```py
                def get_name(animal: Animal):
                    return animal.name

                cat: Cat = Cat()

                get_name(cat)

                """
                get_name: (Object [ str, .. ])
                """
                ```

            - List elements
                ```py
                animals: Animal = []

                animals.append(Cat())
                animals.append(Dog())

                print(animals[0])

                """
                animals: list{Cat | Dog}
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
            buffer: ref buffer [
                0: ref Object [type: usize, cat: Cat],
                1: ref Object [type: usize, cat: Dog],
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

    Viper is all about structural typing. It sees type unsafety and covariance as union types and inheritance as union types.




#### FEATURES IN PYTHON THAT BREAK STATIC GUARANTEES OR PREVENT STATIC OPTIMIZATIONS

- Eval / exec
    - Use of eval / exec
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

    - Shadowing a global variable or a field.
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

        The types of global variables, fields are determined at declaration point and cannot change so they can't be shadowed. The reason this isn't allowed is because it can lead to unintuitive behaviors and is hard to optimize.
        
        The full list of variable types that cannot be shadowed
        - global variables
        - instance and class fields
        - variables from outer scope referenced in a closure


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


- Concurrency

    - Global interpreter lock

        Viper is not affected by the GIL.

    - Async / await

        #### IMPLEMENTATION

        Async / await can be built on top of go-type green threads.


- settrace

    - Modifying variables before the frame is run

    ```py
    sys.settrace(value_changer)
    ```

    Viper does not support this.

- Async / await

    - Unawaited async function may not get executed

        NOTE: The following semantic documentation may change.

        Viper's async / await is very different from Python's. Unawaited asynchronous functions run on a separate lightweight thread.

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

- Regex literal
    ```js
    regex = /\d+/
    ```

- New versions of certain functions and objects by default
    ```py
    map, sum,

    map(array, lambda x: x + 1)
    ```

- Explicit referencing
    ```rust
    num2 = ref num
    ```

- Dereferencing
    ```scala
    num3 = val num2
    ```

- Symbols
    ```julia
    sym = $symbol
    ```

- Statement assignment
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

- Introducing more primitive types
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

- Partial application
    ```py
    add2 = add(2, ..)
    add10 = add(.., 10)
    ```


- cast function
    ```py
    animals = [Cat(), Dog()]

    """
    ERROR

    animals[0].meow() # Need to cast to a type
    """

    cast{Cat}(animals[0]).meow()
    ```

## GARBAGE COLLECTION
In Swift and perhaps other languages, variables are deallocated in the scope of their declaration.

- Automatic Reference Counting

    Automatic Reference Counting with the ability to detect and break reference cycles.

    ```py
    parent = Parent()

    """
    Parent_0 = 1
    """

    child = Child()

    """
    Parent_0 = 1
    child = 1
    """

    parent.child = child

    """
    Parent_0 = 1
    Child_0 = 2
    """

    child.parent = parent

    """
    DEALLOCATION POINT

    Parent_0 = 2
    Child_0 = 2

    Parent_0 decrements .child refs to 1
    Child_0 decrements .parent refs to 1

    problem:
    - both are still not destroyed
    - recursive avalanche of children refs decrementing
    """

    print('Hello!')
    ```

    I don't see the benefit of this approach of keeping counts since we can track references of variables statically.

- Static Reference Tracking

    Static Reference Tracking (STR) is a garbage collection technique that tracks objects lifetime at compile-time.

    - Non-concurrent programs

        ```py
        parent = Parent()

        """
        Parent_0 [ &parent ]
        """

        child = Child()

        """
        Parent_0 [ &parent ]
        child [ &child ]
        """

        parent.child = child

        """
        Parent_0 [ &parent, &child ]
        Child_0 [ &child, &parent]
        """

        child.parent = parent

        """
        DEALLOCATION

        end of reference parent (*parent = null)
        end of reference child (*child = null)

        deallocate Parent_0 []
        deallocate Child_0 []
        """

        print('Hello!')
        ```

    - Concurrent programs

        Ordinary SRT is not well-suited for non-concurrent programs because there is no statically-known order to how threads execute.

        ```py
        async def foo(parent, child):
            print(parent, child)

        parent = Parent()
        child = Child()
        parent.child = child
        child.parent = parent

        for i in range(2):
            """
            increment Parent_0 (.forks += 1) [ &parent, &child ]
            increment Child_0 (.forks += 1) [ &child, &parent ]
            """
            foo(parent, child)

        print(parent, child)

        """
        COROUTINES

            0     1     2
            =================
            __main__
            |
            ---- foo
            |     |
            ---------- foo
            |     |     |
            .     .     .

        DECREMENT IN MAIN COROUTINE

        end of reference parent (*parent = null)
        end of reference child (*child = null)

        decrement Parent_0 (.forks -= 1) []
        decrement Child_0 (.forks -= 1) []

        DECREMENT IN OTHER COROUTINES

        Each forked coroutine will have an epilogue that decrements the objects they reference.
        """
        ```

        In this case, the main coroutine can't release the parent, child objects
        because they are used in the `foo` coroutine. Here we have to maintain a fork count to track the object's lifetime associated with each coroutine that referenced it.


    **Creating statically-unknown number of objects dynamically**

    The reason this isn't a issue is because objects that aren't bound to statically known names are temporary variables and their lifetimes are very predictable.

    The issue of reference tracking comes into play when we are able to extend an objects lifetime by assigning them a static name.

    ```py
    for i in range(some_number):
        """ Creation of temporary object """
        foo(Value())
        """ Desctruction of temporary object """
    ```

    **Reference into a list**

    If there is a reference to alist item, the entire list is not freed.

    ```py
    scores = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

    fourth = scores[3]

    some = scores[3:7]
    ```
