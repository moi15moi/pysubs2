"""
pysubs2.formats.substation tests

"""

from textwrap import dedent
from pysubs2 import SSAFile, SSAEvent, SSAStyle, make_time, Color, Alignment
from pysubs2.substation import color_to_ass_rgba, color_to_ssa_rgb, rgba_to_color, MAX_REPRESENTABLE_TIME, SubstationFormat
import pytest
import sys

SIMPLE_ASS_REF = """
[Script Info]
; Script generated by pysubs2
; https://pypi.python.org/pypi/pysubs2
WrapStyle: 0
ScaledBorderAndShadow: yes
Collisions: Normal
My Custom Info: Some: Test, String.
ScriptType: v4.00+

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Arial,20.0,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,0,0,0,0,100.0,100.0,0.0,0.0,1,2.0,2.0,2,10,10,10,1
Style: topleft,Arial,20.0,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,-1,0,0,0,100.0,100.0,0.0,0.0,1,2.0,2.0,7,10,10,10,1
Style: left,Arial,20.0,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,0,0,0,0,100.0,100.0,0.0,0.0,1,2.0,2.0,4,10,10,10,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 0,0:00:00.00,0:01:00.00,Default,,0,0,0,,An, example, subtitle.
Comment: 0,0:00:00.00,0:01:00.00,Default,,0,0,0,,You can't see this one.
Dialogue: 0,0:01:00.00,0:02:00.00,Default,,0,0,0,,Subtitle number\\Ntwo.
"""

SIMPLE_SSA_REF = """\
[Script Info]
; Script generated by pysubs2
; https://pypi.python.org/pypi/pysubs2
WrapStyle: 0
ScaledBorderAndShadow: yes
Collisions: Normal
My Custom Info: Some: Test, String.
ScriptType: v4.00

[V4 Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, TertiaryColour, BackColour, Bold, Italic, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, AlphaLevel, Encoding
Style: Default,Arial,20.0,16777215,255,0,0,0,0,1,2.0,2.0,2,10,10,10,0,1
Style: topleft,Arial,20.0,16777215,255,0,0,-1,0,1,2.0,2.0,5,10,10,10,0,1
Style: left,Arial,20.0,16777215,255,0,0,0,0,1,2.0,2.0,9,10,10,10,0,1

[Events]
Format: Marked, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: Marked=0,0:00:00.00,0:01:00.00,Default,,0,0,0,,An, example, subtitle.
Comment: Marked=0,0:00:00.00,0:01:00.00,Default,,0,0,0,,You can't see this one.
Dialogue: Marked=0,0:01:00.00,0:02:00.00,Default,,0,0,0,,Subtitle number\\Ntwo.
"""

AEGISUB_PROJECT_GARBAGE_FILE = """\
[Script Info]
; Script generated by Aegisub 3.2.2
; http://www.aegisub.org/
Title: Default Aegisub file
ScriptType: v4.00+
WrapStyle: 0
ScaledBorderAndShadow: yes
YCbCr Matrix: None
PlayResX: 640
PlayResY: 480

[Aegisub Project Garbage]
Last Style Storage: Default
Video File: ?dummy:23.976000:40000:640:480:47:163:254:
Video AR Value: 1.333333
Video Zoom Percent: 0.500000
Active Line: 2

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Arial,20,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,2,2,2,10,10,10,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 0,0:00:00.00,0:00:05.00,Default,,0,0,0,,Test for new Aegisub Project section
"""

NEGATIVE_TIMESTAMP_ASS_REF = """
[Script Info]
; Script generated by pysubs2
; https://pypi.python.org/pypi/pysubs2
WrapStyle: 0
ScaledBorderAndShadow: yes
Collisions: Normal
My Custom Info: Some: Test, String.
ScriptType: v4.00+

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Arial,20.0,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,0,0,0,0,100.0,100.0,0.0,0.0,1,2.0,2.0,2,10,10,10,1
Style: topleft,Arial,20.0,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,-1,0,0,0,100.0,100.0,0.0,0.0,1,2.0,2.0,7,10,10,10,1
Style: left,Arial,20.0,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,0,0,0,0,100.0,100.0,0.0,0.0,1,2.0,2.0,4,10,10,10,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 0,-1:59:54.93,0:01:00.00,Default,,0,0,0,,An, example, subtitle.
Comment: 0,0:00:00.00,0:01:00.00,Default,,0,0,0,,You can't see this one.
Dialogue: 0,0:01:00.00,0:02:00.00,Default,,0,0,0,,Subtitle number\\Ntwo.
"""

AEGISUB_PROJECT_GARBAGE_FILE_WITHOUT_SPACE_AFTER_COLON = """\
[Script Info]
; Script generated by Aegisub 3.2.2
; http://www.aegisub.org/
Title:Default Aegisub file
ScriptType:v4.00+
WrapStyle:0
ScaledBorderAndShadow:yes
YCbCr Matrix:None
PlayResX:640
PlayResY:480

[Aegisub Project Garbage]
Last Style Storage:Default
Video File:?dummy:23.976000:40000:640:480:47:163:254:
Video AR Value:1.333333
Video Zoom Percent:0.500000
Active Line:2

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Arial,20,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,2,2,2,10,10,10,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 0,0:00:00.00,0:00:05.00,Default,,0,0,0,,Test for new Aegisub Project section
"""

HEX_COLOR_IN_SSA = """\
[Script Info]
;SrtEdit 6.3.2012.1001
;Copyright(C) 2005-2012 Yuan Weiguo

Title: 
Original Script: 
Original Translation: 
Original Timing: 
Original Editing: 
Script Updated By: 
Update Details: 
ScriptType: v4.00
Collisions: Normal
PlayResX: 640
PlayResY: 480
Timer: 100.0000
Synch Point: 
WrapStyle: 0
ScaledBorderAndShadow: no

[V4 Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, TertiaryColour, BackColour, Bold, Italic, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, AlphaLevel, Encoding
Style: Default,SimHei,30,&HFFFFFF,&H00FFFF,&H000000,&H000000,-1,0,1,2,3,2,20,20,20,0,1

[Events]
Format: Marked, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: Marked=0,0:01:30.30,0:01:35.30,Default,NTP,0000,0000,0000,!Effect,-脫逃-
"""

ASS_WITH_MALFORMED_STYLE = """\
[Script Info]
Title: file
Original Script: <unknown>
ScriptType: v4.00+
Collisions: Normal
PlayResX: 384
PlayResY: 288
PlayDepth: 0
Timer: 100.0
WrapStyle: 0
Audio File: file.ogg

[v4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default, Arial, 20, &H00FFFFFF, &H00000000, &H00000000, &H00000000, 0, 0, 0, 0, 100, 100, 0, 0, 1, 2, 0, 2, 15, 15, 15, 0

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 0,0:00:00.00,0:00:01.10,Default,Иные 0,0000,0000,0000,,Hello
"""

ASS_WITH_MALFORMED_STYLE_INVALID_ALIGNMENT = """\
[Script Info]
Title: file
Original Script: <unknown>
ScriptType: v4.00+
Collisions: Normal
PlayResX: 384
PlayResY: 288
PlayDepth: 0
Timer: 100.0
WrapStyle: 0
Audio File: file.ogg

[v4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Arial,20.0,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,0,0,0,0,100.0,100.0,0.0,0.0,1,2.0,2.0,123,10,10,10,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 0,0:00:00.00,0:00:01.10,Default,Иные 0,0000,0000,0000,,Hello
"""

ASS_WITHOUT_FRACTIONS_OF_SECOND_REF = """
[Script Info]
; Script generated by pysubs2
; https://pypi.python.org/pypi/pysubs2
WrapStyle: 0
ScaledBorderAndShadow: yes
Collisions: Normal
My Custom Info: Some: Test, String.
ScriptType: v4.00+

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Arial,20.0,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,0,0,0,0,100.0,100.0,0.0,0.0,1,2.0,2.0,2,10,10,10,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 0,-1:59:54.93,0:01:00.00,Default,,0,0,0,,Negative timestamp line.
Dialogue: 0,0:00:23.45,0:01:23.45,Default,,0,0,0,,Correct timestamp line.
Dialogue: 0,0:00:23,0:01:23,Default,,0,0,0,,Timestamp with missing fractions line.
"""

ASS_WITH_SHORT_MINUTES_SECONDS_REF = r"""
[Script Info]
Title: karaoke
ScriptType: v4.00+
WrapStyle: 0
ScaledBorderAndShadow: yes
Collisions: Normal

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Arial,20,&H00FFFFFF,&H000088EF,&H00000000,&H00666666,-1,0,0,0,100,100,0,0,1,3,0,8,10,10,10,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text

Dialogue: 1,0:0:0.04,0:0:4.00,Default,,0000,0000,0000,,{\k100}{\k33}SUN{\k4}{\k42}DAY {\k4}{\k38}MON{\k4}{\k29}DAY {\k4}{\k33}CHU-{\k4}{\k21}CHU {\k4}{\k21}TUES{\k4}{\k50}DAY
Dialogue: 1,0:0:3.42,0:0:7.88,Default,,0000,0000,0000,,{\k100}{\k4}me{\k4}{\k8}ku{\k4}{\k38}t{\k4}{\k17}te {\k4}{\k17}CA{\k4}{\k33}LEN{\k4}{\k29}DAR {\k4}{\k38}GIRL {\k4}{\k8}wa{\k4}{\k8}ta{\k4}{\k13}shi {\k4}{\k17}no {\k4}{\k13}mai{\k4}{\k8}ni{\k8}{\k33}chi
"""


def build_ref():
    subs = SSAFile()
    subs.info["My Custom Info"] = "Some: Test, String."
    subs.styles["topleft"] = SSAStyle(alignment=Alignment.TOP_LEFT, bold=True)
    subs.styles["left"] = SSAStyle(alignment=Alignment.MIDDLE_LEFT)
    subs.append(SSAEvent(start=0, end=make_time(m=1), text="An, example, subtitle."))
    subs.append(SSAEvent(start=0, end=make_time(m=1), type="Comment", text="You can't see this one."))
    subs.append(SSAEvent(start=make_time(m=1), end=make_time(m=2), text="Subtitle number\\Ntwo."))
    return subs

def test_simple_write():
    subs = build_ref()
    assert subs.to_string("ass").strip() == SIMPLE_ASS_REF.strip()
    assert subs.to_string("ssa").strip() == SIMPLE_SSA_REF.strip()

def test_simple_read():
    ref = build_ref()
    subs1 = SSAFile.from_string(SIMPLE_ASS_REF)
    subs2 = SSAFile.from_string(SIMPLE_SSA_REF)

    assert ref.equals(subs1)
    assert ref.equals(subs2)

def test_color_parsing():
    solid_color = Color(r=1, g=2, b=3)
    transparent_color = Color(r=1, g=2, b=3, a=4)

    assert rgba_to_color(color_to_ssa_rgb(solid_color)) == solid_color
    assert rgba_to_color(color_to_ass_rgba(solid_color)) == solid_color
    assert rgba_to_color(color_to_ass_rgba(transparent_color)) == transparent_color

    assert rgba_to_color("&HAABBCCDD") == Color(r=0xDD, g=0xCC, b=0xBB, a=0xAA)
    assert color_to_ass_rgba(Color(r=0xDD, g=0xCC, b=0xBB, a=0xAA)) == "&HAABBCCDD"

def test_aegisub_project_garbage():
    subs = SSAFile.from_string(AEGISUB_PROJECT_GARBAGE_FILE)
    garbage_section = dedent("""
        [Aegisub Project Garbage]
        Last Style Storage: Default
        Video File: ?dummy:23.976000:40000:640:480:47:163:254:
        Video AR Value: 1.333333
        Video Zoom Percent: 0.500000
        Active Line: 2""")

    assert garbage_section in subs.to_string("ass")

def test_ascii_str_fields():
    # see issue #12
    STYLE_NAME = b"top-style"

    subs = SSAFile()
    line = SSAEvent(style=STYLE_NAME)
    subs.events.append(line)
    style = SSAStyle()
    subs.styles[STYLE_NAME] = style

    # if sys.version_info.major == 2:
    #     # in Python 2, saving subtitles with non-unicode fields is tolerated
    #     # as long as they do not fall outside of ASCII range
    #     subs.to_string("ass")
    # else:
    #     # in Python 3, we are strict and enforce Unicode
    with pytest.raises(TypeError):
        subs.to_string("ass")

def test_non_ascii_str_fields():
    # see issue #12
    STYLE_NAME = "my-style"
    FONT_NAME = b"NonAsciiString\xff"

    subs = SSAFile()
    line = SSAEvent(style=STYLE_NAME)
    subs.events.append(line)
    style = SSAStyle(fontname=FONT_NAME)
    subs.styles[STYLE_NAME] = style

    # in all Pythons, saving subtitles with non-unicode fields
    # fails when they are not in ASCII range
    with pytest.raises(TypeError):
        subs.to_string("ass")

def test_negative_timestamp_read():
    ref = build_ref()
    subs = SSAFile.from_string(NEGATIVE_TIMESTAMP_ASS_REF)

    # negative timestamp is read correctly
    assert subs[0].start == -make_time(1, 59, 54, 930)

    # negative times are flushed to zero on output
    assert ref.to_string("ass") == subs.to_string("ass")

def test_overflow_timestamp_write():
    ref = build_ref()
    ref[0].end = make_time(h=1000)
    with pytest.warns(RuntimeWarning):
        text = ref.to_string("ass")
    subs = SSAFile.from_string(text)
    assert subs[0].end == MAX_REPRESENTABLE_TIME

def test_centisecond_rounding():
    ref = SSAFile()
    ref.append(SSAEvent(start=make_time(h=1, m=1, ms=4), end=make_time(h=1, m=1, ms=5)))
    text = ref.to_string("ass")
    subs = SSAFile.from_string(text)
    assert subs[0].start == make_time(h=1, m=1, ms=0)
    assert subs[0].end == make_time(h=1, m=1, ms=10)

def test_no_space_after_colon_in_metadata_section():
    # see issue #14
    ref = SSAFile.from_string(AEGISUB_PROJECT_GARBAGE_FILE)
    subs = SSAFile.from_string(AEGISUB_PROJECT_GARBAGE_FILE_WITHOUT_SPACE_AFTER_COLON)

    assert ref.equals(subs)
    assert ref.aegisub_project == subs.aegisub_project

def test_hex_color_in_ssa():
    # see issue #32
    subs = SSAFile.from_string(HEX_COLOR_IN_SSA)
    style = subs.styles["Default"]
    assert style.primarycolor == Color(r=0xff, g=0xff, b=0xff)
    assert style.secondarycolor == Color(r=0xff, g=0xff, b=0x00)


def test_ass_with_malformed_style():
    # see issue #45
    subs = SSAFile.from_string(ASS_WITH_MALFORMED_STYLE)
    assert subs[0].text == "Hello"
    assert subs.styles["Default"].fontname == "Arial"


def test_ass_with_missing_fractions_in_timestamp():
    # see issue #50
    subs = SSAFile.from_string(ASS_WITHOUT_FRACTIONS_OF_SECOND_REF)

    # negative timestamp
    assert subs[0].start == -make_time(1, 59, 54, 930)
    assert subs[0].end == make_time(0, 1, 0, 0)

    # correct timestamp
    assert subs[1].start == make_time(0, 0, 23, 450)
    assert subs[1].end == make_time(0, 1, 23, 450)

    # timestamp with missing fractions
    assert subs[2].start == make_time(0, 0, 23, 0)
    assert subs[2].end == make_time(0, 1, 23, 0)


def test_ass_with_short_minutes_seconds_in_timestamp():
    # see pull request #54

    subs = SSAFile.from_string(ASS_WITH_SHORT_MINUTES_SECONDS_REF)

    assert subs[0].start == make_time(0, 0, 0, 40)
    assert subs[0].end == make_time(0, 0, 4, 0)

    assert subs[1].start == make_time(0, 0, 3, 420)
    assert subs[1].end == make_time(0, 0, 7, 880)


@pytest.mark.filterwarnings("ignore:.*should be an Alignment instance.*:DeprecationWarning")
def test_alignment_given_as_integer():
    subs = SSAFile()
    subs.info["My Custom Info"] = "Some: Test, String."
    subs.styles["topleft"] = SSAStyle(alignment=7, bold=True)
    subs.styles["left"] = SSAStyle(alignment=4)
    subs.append(SSAEvent(start=0, end=make_time(m=1), text="An, example, subtitle."))
    subs.append(SSAEvent(start=0, end=make_time(m=1), type="Comment", text="You can't see this one."))
    subs.append(SSAEvent(start=make_time(m=1), end=make_time(m=2), text="Subtitle number\\Ntwo."))

    assert subs.to_string("ass").strip() == SIMPLE_ASS_REF.strip()
    assert subs.to_string("ssa").strip() == SIMPLE_SSA_REF.strip()


def test_reading_invalid_alignment_raises_warning():
    with pytest.warns(RuntimeWarning):
        subs = SSAFile.from_string(ASS_WITH_MALFORMED_STYLE_INVALID_ALIGNMENT)
    assert subs.styles["Default"].alignment == Alignment.BOTTOM_CENTER


def test_ass_ms_to_timestamp():
    # see issue #76

    assert SubstationFormat.ms_to_timestamp(4659990) == "1:17:39.99"
    assert SubstationFormat.ms_to_timestamp(4659991) == "1:17:39.99"
    assert SubstationFormat.ms_to_timestamp(4659992) == "1:17:39.99"
    assert SubstationFormat.ms_to_timestamp(4659993) == "1:17:39.99"
    assert SubstationFormat.ms_to_timestamp(4659994) == "1:17:39.99"
    assert SubstationFormat.ms_to_timestamp(4659995) == "1:17:40.00"
    assert SubstationFormat.ms_to_timestamp(4659996) == "1:17:40.00"
    assert SubstationFormat.ms_to_timestamp(4659997) == "1:17:40.00"
    assert SubstationFormat.ms_to_timestamp(4659998) == "1:17:40.00"
    assert SubstationFormat.ms_to_timestamp(4659999) == "1:17:40.00"