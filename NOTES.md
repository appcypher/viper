
## LEXER
## PARSER
## SEMANTIC ANALYSIS


## STATIC ANALYSIS
#### HOW TO ACHIEVE SOME LEVEL OF DYNAMISM

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
        def function(ls):
            ls.append('hi')

        ls = []
        function(ls)
        ```

        ##### IMPLEMENTATION

        If a list is uninitialized, we wait until it is first used. Its type is inferred based on how it is used.

        If it is passed to a function, its type is determined by the argument type, otherwise it is determined by its usage in the function's body.

- Variable

    - No special declaration syntax
        ```py
        num = 45
        print(num)

        def function():
            nonlocal num
            num = 56
            print(num)

        function()
        ```


    - Shadowing
        ```py
        num = 45
        num = "hi"
        ```

- Functions

    - ...

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
        function(**dictionary)
        ```

    - Spreading other iterables apart from tuple as arguments
        ```py
        function(*ls)
        ```

- Imports

    - Resolving imported modules at runtime
        ```py
        name, age = "John", 45

        from objects import Person

        john = Person(name)
        ```

- Variable

    - Changing variable type
        ```py
        num = 10
        print(num)

        def function():
            nonlocal num
            num = 0.005
            print(num)

        function()
        ```

        A variable's type is determined at declaration point, except uninitialized lists where type is known at first element insertion.

- Integers

    - Abitrary-precision integers
        ```py
        num = 9_223_372_036_854_775_807 + 1
        ```

        `int`s are represented as 64-bit integers.

## GARBAGE COLLECTION
## CODE GENERATION
## STANDARD LIBRARY

## POSSIBLE ADDITIONS
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
            return 0
        else:
            return 5
    , array)

    map(
        array,
        lambda x:
            if x == 1:
                return 0
            else:
                return 5
    )
    ```

- const keyword
    ```py
    const pi = 3.141
    ```

- regex literal
    ```py
    regex = /\d+/
    ```

- new versions of certain functions and objects by default
    ```py
    map, sum,

    map(array, lambda x: x + 1)
    ```

- ref keyword
    ```py
    num = ref 56
    ```

- dereferencing syntax
    ```py
    num2 = 'num
    ```

- symbols
    ```py
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
