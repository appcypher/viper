from compiler.parser.parser import Parser


def test_parser_memoizes_called_parser_functions_successfully():
    parser = Parser.from_code("identifier")
    result = parser.parse_name()

    assert result == 0
    assert parser.cache == {
        -1: {"parse_name": 0}
    }
