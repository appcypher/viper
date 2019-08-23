
## LEXER

## PARSER

Unlike CPython's LL(1) parser, Viper uses a packrat parser and the language's grammar is specified in PEG notation.

- Results of all paths that are taken are memoized.
- A parse function result should always be an AST. Avoid returning a parse tree.
- A parse function result should not hold values, but references to token elements.

## SEMANTIC ANALYSIS

- Philosophy

    Viper has certain worldviews that make the semantic analysis phase easier to understand and implement.

    - A function, in Viper implementation parlance, is a regular function, a method, a closure or an operator.
    - Every object has a structure and classes are how we describe or classify those structures. We only think in terms of classes when we need to compare an object's structure with a class' blueprint structure.
    - Inheritance / variance is an abstraction we only care about for validation/type-checking purposes. Relationship between objects are only seen in terms of how similar their structures are.
    - Global variables are variables that persist throughout the lifetime of a program. Global variables include variables declared at the top-level, class fields and variables from a parent scope referenced by a closure.

- Analysis artifacts

    - Scope tree

        - Object end-of-lifetime (EOL) list

            Each scope contain a list of objects' EOL.
            Starting from the declaration scope, each object's EOL point is adjusted as new references to it are encountered in the declaration scope or in a parent's scope.

        - Type frames

            A type frame is created for each function.
            This type frame holds a list of functions called in the function's scope.
            To instantiate a type frame, we need to validate that the types in the scope truly have an associated function instantiation. Validations for existing instantiations are skipped.

            An instantiation [shouldn't clone the AST](https://github.com/crystal-lang/crystal/issues/4864#issue-251536917).

        - Type method resolution order (MRO) lists (C3 linearization)

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
        value = 0

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

        """
        ERROR

        print(ls)
        """

        def func(ls):
            ls.append('hi')

        func(ls)
        ```

        ##### IMPLEMENTATION

        If a list is uninitialized, we wait until it is first used. Its type is inferred based on how it is used.

        If it is passed as an argument to a function, its type is determined by the argument type, otherwise it is determined by its usage in the function's body.

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

        A local variable can be shadowed. In the above example, the second `num` is a totally different variable from the first `num`. However, global variables and fields cannot be shadowed.


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

        The fields of an object is the collection of fields attached to the object through its entire lifetime. The only exception is global variables. They can't be given new fields.

        ```py
        """
        john: Object [ name: str, age: int ]
        """
        ```



- Generators

- Closures

    `closure = func(*args, ref env)`

    ```py
    def higher_order():
        x = 0

        def closure():
            x = 10
    ```

    Variables referenced within the closure can be optimized (moved into the closure) if not used, referenced or returned by parent function or sibling closures. This way, the `env` reference can be omitted.

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

        Functions are actually instantiations with abis that conform to argument binary structures.

        ```py
        """
        cat: Cat [ name: str ]
        john: Person [ age: int, name: str ]
        hibiscus: Plant [ name: int, age: int ]
        elephant: Herbivore [ name: int ]
        """

        foo(cat)
        foo(john)
        foo(hibiscus)
        foo(elephant)

        """
        INSTANTIATIONS

        foo: (Object [ str ])
        foo: (Object [ .., str ])
        foo: (Object [ int, .. ])
        """
        ```

    - Type unsafety
        * Type union
            ```py
            identity: int | str

            if condition:
                identity = 45
            else:
                identity = 'XNF452423'

            """
            identity: int | str
            """
            ```

        * Covariance

            A subtype value can be assigned where a supertype value is expected.

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

            - Inheritance
                ```py
                class Vehicle:
                    # ...
                    def clone(self) -> Vehicle:
                        return Vehicle(*self.fields)

                class Toyota(Vehicle):
                    # ...
                    def clone(self) -> Toyota:
                        return Toyota(*vars(self))

                cars: list{Vehicle} = [Toyota(), Mazda()]

                cars[0].clone()

                """
                animals: list{Cat | Dog}
                """
                ```

        * Contravariance

            - Functions
                ```py
                typealias IdentityFunc{T}: (T) -> T

                def identity_animal(x: Animal):
                    return x

                def identity_cat(x: Cat):
                    return x

                compare: IdentityFunc{Cat} = identity_animal

                """
                ERROR

                compare: IdentityFunc{Animal} = identity_cat
                """
                ```


        ##### IMPLEMENTATION

        Variables with uncertain types don't make it far because to use them with any function require that any field or method accessed through them exists across the types.

        ```py
        identity: int | str

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

        if animal := cast{Cat}(animal):
            animal.meow()
        ```

    #### IMPLEMENTATION

    Viper is all about structural typing. It sees type unsafety and covariance as union types and inheritance as intersection types.




#### FEATURES IN PYTHON THAT BREAK STATIC GUARANTEES OR PREVENT STATIC OPTIMIZATIONS

- Eval / exec
    - Use of eval / exec
        ```py
        eval('2 + 3')
        ```

- Introspection

    - Viper doesn't have a bytecode IR, but it does have a wasm codegen that one can introspect.
        ```py
        from dis import dis

        dis(some_func)
        ```

- Declaration

    - Declaration of classes and functions work a bit different in Viper.

        Because Viper needs to determine a class and function at compile-time, it doesn't support dynamic loading of classes or functions the way Python does. It also doesn't provide a lot of hooks found in builtin module

- Type annotations

    - Type annotations is used in semantic analysis

        CPython doesn't take advantage of type annotations.

        ```py
        num: int = 50

        """
        ERROR

        num = "Hello"
        """
        ```

- Fields

    - Deleting fields isn't supported
        ```py
        """
        ERROR

        del john.name
        """
        ```

    - `vars` and `__dict__` return named tuples
        ```py
        print(vars(john)) # (name='John', age=45)
        ```

- Tuples

    - A tuple can only be indexed with a signed integer literal
        ```py
        tup = (1, 2, 3)
        tup[0]

        """
        ERROR

        tup[n]
        """
        ```

    - A tuple element can be modified in Viper
        ```py
        tup = (1, 2, 3)
        tup[0] = 4
        ```

    - Directly or indirectly, a tuple can't be used spread or appended to itself.

        Basically anything that makes assigning a reference/name with its previous tuple value possible is not allowed. Only identity assignment is allowed. It's a recursive problem, that static analyzers generally can't resolve and hate.

        ```py
        tup1 = (1, 2)
        tup2 = (5, 6)

        for i in range(x):
            tup3 = (1, *tup1)
            tup2 = (*tup3, *tup1)

        # Identity assignment is allowed
        tup3 = tup3
        tup3 = (*tup3)

        """
        ERROR

        for i in range(x):
            tup2 = (*tup2, *tup1)

        for i in range(x):
            tup2 = tup2 + tup1

        for i in range(x):
            tup3 = (*tup2, 1)
            tup2 = (tup3, tup1)
        """
        ```


- Functions

    - Vipers doesn't support spreading any iterable except tuples and named tupeles as arguments to a function
        ```py
        dc = { 'name': 'John', 'age': 45 }
        ls = [1, 2, 3]
        tup = (1, 2, 3)
        named_tup = (one=1, two=2, three=3)

        some_func(*tup)
        some_func(*named_tup)

        """
        ERROR

        some_func(**dc)
        some_func(*ls)
        """
        ```

- Imports

    - Viper resolves imported modules at compile-time
        ```py
        name, age = "John", 45

        from objects import Person

        john = Person(name)
        ```

- Variable

    - Viper doesn't support shadowing global variables or instance fields.
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

        The types of global variables and instance fields are determined at declaration point and cannot change so they can't be shadowed. The reason this isn't allowed is because it makes the program hard to reason about, increases compilation time and makes incremental compilation hard to achieve.

         The full list of variable types that cannot be shadowed
        - global variables
        - instance and class fields
        - variables from outer scope referenced in a closure


- Integers

    - `int`s are represented as 64-bit signed integers.
        This means ints overflow when they exceed `-4_611_686_018_427_387_904 < x < 4_611_686_018_427_387_903` bounds.

        ```py
        num = 4_611_686_018_427_387_902 + 1
        print(num) # -4_611_686_018_427_387_903
        ```

- StopIteration and KeyError

    - Exception handling as a means of control flow is expensive.
        ```py
        for i in range(10):
            print(25)
        ```

        Viper optimizes StopIteration and KeyError exception handlers where possible.

- Concurrency

    - Global interpreter lock

        Viper is not affected by the GIL.

    - Async / await

        Async / await can be built on top of go-type green threads.

        ```py
        async def foo(id):
            sleep(3)
            print(f'Done sleeping {id}')

        foo(1)
        foo(2)
        foo(3)
        ```


- settrace

    - Viper doesn't support modifying variables before the frame is run

        ```py
        """
        ERROR

        import sys.settrace
        sys.settrace(value_changer)
        """
        ```

- Async / await

    - Unawaited async function may not get executed in CPython

        NOTE: The following semantic documentation may change.

        Viper's async / await is very different from Python's. Unawaited asynchronous functions are executed on separate green threads.


- Source file

    - Multiple encoding support
        Unlike CPython, Viper only support utf-8 files.


- Scoping rules

    - Viper has different scoping rule. `if-elif-else`, `for-else`, `try-except-ensure` and `while-else` blocks all have their own scopes

- Literal

    - Viper does not support upper case letters to signify literal base
        ```py
        bin_n = 0b10101
        oct_n = 0o17867
        hex_n = 0x1FFFE

        """
        ERROR

        bin_n = 0B10101
        oct_n = 0O17867
        hex_n = 0X1FFFE
        """
        ```

    - Viper doesn't support the wide entire uppercase / reversed prefixes Python support in prefix strings.
        ```py
        r"Hello"
        u"Hello"
        f"Hello"
        b"Hello"
        rb"Hello"
        rf"Hello"

        """
        ERROR

        R"Hello"
        U"Hello"
        F"Hello"
        B"Hello"
        rB"Hello"
        Rb"Hello"
        RB"Hello"
        rF"Hello"
        Rf"Hello"
        RF"Hello"
        """
        ```

    - Viper uses `im` for imaginary numbers
        ```py
        imag = 3 + 4im
        ```

        - Instead of the 'j' suffix, Viper expects a 'im' suffix

## CODE GENERATION

- WebAssembly

## STANDARD LIBRARY

## POSSIBLE ADDITIONS

- Character
    ```py
    ch0 = `a
    ch1 = `\n
    ch2 = `\uff
    ch3 = `\890

    string = ch0 + ch1

    if `a <= ch <= `z:
        print(ch)
    ```

- Regex literal
    ```js
    regex = /\d+/
    ```

- Type annotation revamp
    ```py
    # Type anotation
    index: int = 9

    # Type argument
    nums: list{int} = []

    # Optional type
    age: int? = 45

    # Function type
    fn: (int, int) -> int = sum

    # Tuple type
    value: (int, int) = (1, 2, 3)

    # Union type
    identity: int | str = 'XNY7V40'

    # Intersection type
    pegasus: Horse & Bird = Pegasus()

    # Type reltionship
    Person < Mammal
    Mammal > Person
    Person == Person

    # Interface (In draft). Similar to Go2's contracts
    where!(T > Mammal, U == Person)
    interface Equal{T, U}(Eq):
        def __eq__(T, U): pass

    # Generics
    class Person{T, U: Equal}(A, B):
        def __init__(self, name: T):
            self.name = name

        def __eq__(self, name: T, other_name: U):
            return name == other_name

    def get_person{T}(name: T):
        return Person{T}(name)

    jane = get_person{str}('Jane Doe')
    ```

- Type alias
    ```py
    typealias IdentityFunc{T}: (T) -> T
    ```

- None handling
    ```py
    def get_optional() -> char?:


    if identity := get_optional():
        print(identity)

    ch = get_optional()

    """
    ERROR

    ord(ch) # ord function exists for char but not None
    """

    codepoint = ord(ch) if ch else None
    codepoint = ord(ch?)
    ```

- Algebraic data types
    ```py
    enum Option{T}:
        Ok(value: T)
        Err()
        None

    identity: Option{str} = Option.None

    match identity:
        Option.Some(value) => value
        Option.Err() => raise Error()
        * => pass

    identity: int | str = 'XNY7V40'

    match identity:
        *: int => value
        *: str => value
    ```

- Additional reserved keywords
    ```py
    const, ref, ptr, val, match, let, var, enum, true, false, interface, where, macro, typealias
    ```

- Consistent use of underscores
    ```py
    dictionary.from_keys('a, b, c')
    ```

- UFCS
    ```py
    ls = [1, 2, 3, 4]
    len(ls)
    ls.len()
    ```

- Multiline lambda
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

- `const` keyword
    ```py
    const pi = 3.141

    def map(const array, const f):
        t = []
        for i in array:
            t.append(f(i))
        return t
    ```

- New versions of certain functions and objects by default
    ```py
    map, sum,

    map(array, lambda x: x + 1)
    ```

- Explicit reference
    ```rust
    num2 = ref num
    num3 = num2
    ```

- Pointers
    ```nim
    num2 = ptr num
    num2 += 1
    num3 = val num2
    ```

- Symbols
    ```julia
    sym = $symbol
    ```

- New named_tuple syntax
    ```py
    named_tup = (name="James", age=10)
    named_tup.name
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

- Pattern matching
    ```py
    match x:
        Person(name, age) => 1
        [x, y = 5, z] => y
        (x, y = 5, 10, *z) => x
        {x, y = 5, 10, *z} => x
        { x: 'x', y: 'y',  **z} => x
        10 or 11 and 12 => x
        0:89 => 10
        * => 11
    ```

- Partial application
    ```py
    add2 = add(2, ..)
    add10 = add(.., 10)
    ```


- Cast function
    ```py
    animals = [Cat(), Dog()]

    """
    ERROR

    animals[0].meow() # Need to cast to a type
    """

    cast{Cat}(animals[0]).meow()
    ```

- Overloading functions and methods based on arity and types
    ```py
    class Person:
        def __init__(self, name):
            self.name = name

        def __init__(self, name, age):
            self.name = name
            self.age = age

        def __init__(self, name, age: int):
            self.name = name
            self.age = age
    ```

- Hygenic macros
    ```py
    macro hello_macro($func: Identifier [ $(, $expr: Expression)* ] ):
        print('|| HELLO MACRO ||')
        $func( $( expr, )* )

    hello_macro!(foo, [1, 2, 3])
    ```

    Syntax may clash with format specifiers !r, !s, !a.

    ```py
    f"He said his name is {name!r}."
    ```

    NOTE: Susceptible to change.

- Coefficient expression [IN PROGRESS]
    ```py
    n = 4
    2n
    (2)n
    2(n)
    ```

- Abritary precision integer and float literal
    ```py
    integer = b`123457890123456789012345678901234567890
    floating: BigFloat = b`123457890123456.789012345678901234e-567890

    type(integer) == BigInteger
    ```

- Hexadecimal, binary and octal floating point literal
    ```py
    decf = 12.3e+1
    hexf = 0x1f.3e+1
    octf = 0o16.3e+1
    binf = 0b11.3e+1
    ```

## GARBAGE COLLECTION
In Swift, variables are deallocated in their declaration stack frames or parents of that. Never a child frame of the declaration scope. Viper takes a similar approach.

- Automatic Reference Counting (ARC)

    Typical ARC implementation cannot break reference cycles.

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
    - avalanche of children refs decrement
    """

    print('Hello!')
    ```

    Since lifetimes can be tracked statically, I don't see the runtime benefit of ARC.

- Static Reference Tracking (SRT)

    SRT is a garbage collection technique that tracks objects' lifetimes at compile-time.

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
        Parent_0 [ &parent, ]
        Child_0 [ &child, &parent ]
        """

        child.parent = parent

        """
        Parent_0 [ &parent, &child ]
        Child_0 [ &child, &parent ]
        """

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

        In this case, the main coroutine can't release the `parent` and `child` objects
        because they are referenced in the `foo` coroutines. Here we have to maintain a fork count to track the object's lifetime associated with each coroutine that referenced it.


    **Creating statically-unknown number of objects dynamically**

    Creating statically-unknown number of objects dynamically isn't an issue for SRT because objects are bound to statically-known names at compile-time. With the exception of temporary objects whose lifetimes are well-defined and statically determinable.

    The issue of garbage collection comes into play when we are able to extend an objects lifetime beyond the declaration stack frame. This is amenable to static analysis, however, because such objects are required to be associated with statically-known names.

    ```py
    for i in range(some_number):
        """ Creation of temporary object """
        foo(Value())
        """ Destruction of temporary object """
    ```

    **Pointer aliasing**

    Raw pointer aliasing affects all GC techniques. SRT, Tracing GCs, ARC. That is why we have references. They are an abstraction over pointers, something our GCs understand. Raw pointer misuse is a problem for any GC technique.

    **Reference into a list**

    If there is a reference to a list item, the entire list is not freed until all references to it and/or its elements are dead.

    ```py
    scores = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

    fourth = scores[3]

    some = scores[3:7]
    ```
