"""
Simple tests for lexer.py.
Run with:  python test_lexer.py
"""

from lexer import lexer, without_line_breaks, LexError


def classes(code):
    """
    The list of classifications for a piece of code (easy to compare).
    Every line ends with a Line Break token, so we drop the last one to keep the tests short.
    """
    result = [token[1] for token in lexer(code)]
    if result and result[-1] == "Line Break":
        result.pop()
    return result


def test_string_is_split_in_three():
    tokens = without_line_breaks(lexer('"hello world"'))
    assert [t[0] for t in tokens] == ['"', "hello world", '"']
    assert [t[1] for t in tokens] == ["String Delimiter", "YARN Literal", "String Delimiter"]


def test_empty_string():
    assert classes('""') == ["String Delimiter", "YARN Literal", "String Delimiter"]


def test_keywords_inside_string_are_ignored():
    assert len(without_line_breaks(lexer('"I HAS A BTW TLDR"'))) == 3


def test_classification_names():
    assert classes("HAI") == ["Code Delimiter"]
    assert classes("SUM OF 1 AN 2") == ["Arithmetic Operation", "NUMBR Literal", "Operand Separator", "NUMBR Literal"]
    assert classes("VISIBLE") == ["Output Keyword"]


def test_numbers_and_troof():
    assert classes("5 -3 2.5 WIN FAIL") == ["NUMBR Literal", "NUMBR Literal", "NUMBAR Literal",
                                            "TROOF Literal", "TROOF Literal"]


def test_keyword_inside_a_longer_word_is_an_identifier():
    assert classes("WINNER") == ["Identifier"]


def test_single_comment_is_ignored_but_line_break_stays():
    assert classes("I HAS A x BTW note\nVISIBLE x") == [
        "Variable Declaration", "Identifier", "Line Break", "Output Keyword", "Identifier"]


def test_multi_line_comment_is_ignored():
    assert classes("HAI\nOBTW\nI HAS A hidden\nTLDR\nKTHXBYE") == ["Code Delimiter", "Line Break", "Code Delimiter"]


def test_blank_lines_give_one_line_break():
    assert classes("HAI\n\n\nKTHXBYE") == ["Code Delimiter", "Line Break", "Code Delimiter"]


def test_comma_is_a_soft_line_break():
    assert classes("x R 1, VISIBLE x")[3] == "Soft Line Break"


def test_line_numbers():
    tokens = lexer("HAI\n\nVISIBLE x")
    visible = [t for t in tokens if t[0] == "VISIBLE"][0]
    assert visible[2] == 3


def test_without_line_breaks():
    shown = without_line_breaks(lexer("HAI\nKTHXBYE"))
    assert [t[0] for t in shown] == ["HAI", "KTHXBYE"]


def raises_error(code):
    """True if lexing the code raises a LexError."""
    try:
        lexer(code)
    except LexError:
        return True
    return False


def test_errors():
    assert raises_error("HAI\nI HAS A x ITZ 5 @")   # unknown character (used to hang forever)
    assert raises_error('VISIBLE "no closing quote')
    try:
        lexer('VISIBLE "no closing quote')
    except LexError as error:
        assert "closing quote" in str(error)
    assert raises_error("OBTW\nnever closed")
    assert raises_error("12abc")
    assert raises_error("I HAS A x OBTW hi\nTLDR")        # OBTW must be alone on its line
    assert raises_error("OBTW\nhi\nTLDR I HAS A x")      # TLDR must be alone on its line
    assert raises_error("TLDR")                             # TLDR without OBTW


def test_sample_file():
    with open("sample.lol", encoding="utf-8") as file:
        tokens = lexer(file.read())
    lexemes = [t[0] for t in tokens]
    assert "HAI" in lexemes
    assert "KTHXBYE" in lexemes


# Run every test function above and report the result.
if __name__ == "__main__":
    all_tests = [value for name, value in list(globals().items()) if name.startswith("test_")]
    for test in all_tests:
        test()
        print("passed:", test.__name__)
    print(f"All {len(all_tests)} tests passed.")
