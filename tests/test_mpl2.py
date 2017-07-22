from __future__ import unicode_literals

from textwrap import dedent
from nose.tools import assert_raises

from pysubs2 import SSAFile, SSAEvent, make_time


def test_simple_parsing():
    test_input1 = "[123][456] Line 1"
    subs1 = SSAFile.from_string(test_input1)
    assert len(subs1) == 1
    assert subs1[0] == SSAEvent(start=make_time(ms=12300), end=make_time(ms=45600), text="Line 1")

    test_input2 = "[123][456] / Line 1|   Line 2/2"
    subs2 = SSAFile.from_string(test_input2)
    assert len(subs2) == 1
    assert subs2[0] == SSAEvent(start=make_time(ms=12300), end=make_time(ms=45600), text="{\i1}Line 1{\i0}\\NLine2/2")

    test_input3 = dedent("""
    [123][456] Line 1
    [321][456] / Line 2|   Line 3
    (123)(456)This line should not be parsed
    This line should also not be parsed
    
    [789][1234] /Line 4""")

    subs3 = SSAFile.from_string(test_input3)
    assert len(subs3) == 3
    assert subs3[0] == SSAEvent(start=make_time(ms=12300), end=make_time(ms=45600), text="Line 1")
    assert subs3[1] == SSAEvent(start=make_time(ms=32100), end=make_time(ms=45600), text="{\i1}Line 2{\i0}\\NLine 3")
    assert subs3[2] == SSAEvent(start=make_time(ms=78900), end=make_time(ms=123400), text="{\i1}Line 4{\i0}")
