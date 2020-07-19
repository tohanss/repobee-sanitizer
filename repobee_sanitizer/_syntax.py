"""Functions and constants relating to the syntax of repobee-sanitizer.

.. module:: _syntaxhelpers
    :synopsis: Functions and constants relating to the syntax of
        repobee-sanitizer.
"""
import enum
import pathlib
from typing import List, Optional

import re
import repobee_plug as plug

from repobee_sanitizer import _fileutils


class Markers(enum.Enum):
    """The markers that define sanitizer blocks."""

    START = "REPOBEE-SANITIZER-START"
    REPLACE = "REPOBEE-SANITIZER-REPLACE-WITH"
    END = "REPOBEE-SANITIZER-END"
    SHRED = "REPOBEE-SANITIZER-SHRED"


def check_syntax(lines: List[str]) -> None:
    """Checks if the input adheres to proper sanitizer syntax using proper
    markers:

    The grammar is defined below in EBNF-like manner. Note that the syntax is
    not context- free as prefixes are defined on a per-block basis, so it's not
    possible to perfectly describe the syntax with EBNF.

    .. code-block:: raw

        FILE ::=
            SHRED_MARKER MARKERLESS_LINE |
            (MARKERLESS_LINE* ((BLOCK | PREFIXED_BLOCK) MARKERLESS_LINE*)+)
        BLOCK ::=
            START_MARKER
            MARKERLESS_LINE*
            (REPLACE_MARKER
            MARKERLESS_LINE*)?
            END_MARKER
        PREFIXED_BLOCK ::=
            PREFIX START_MARKER
            MARKERLESS_LINE*
            (PREFIX REPLACE_MARKER
            (PREFIX MARKERLESS_LINE)*)?
            PREFIX END_MARKER
        START_MARKER ::= "REPOBEE-SANITIZER-START\n"
        REPLACE_MARKER ::= "REPOBEE-SANITIZER-REPLACE-WITH\n"
        END_MARKER ::= "REPOBEE-SANITIZER-END\n"
        SHRED_MARKER :: = "REPOBEE-SANITIZER-SHRED"
        MARKERLESS_LINE ::= line without sanitizer markers
        PREFIX ::= a sequence of characters that is defined for each block
            as any sequence that appears before the START_MARKER of that
            particular PREFIXED_BLOCK.


    Args:
        lines: List containing every line of a text file as one element in the
            list.
    Raises:
        plug.PlugError: Invalid Syntax.
    """
    last = Markers.END.value
    prefix = ""
    has_blocks = _contained_marker(lines[0]) == Markers.SHRED

    errors = _check_shred_syntax(lines)
    if errors:
        raise plug.PlugError(errors)

    for line_number, line in enumerate(lines, start=1):
        if Markers.START.value in line:
            has_blocks = True
            if last != Markers.END.value:
                errors.append(
                    f"Line {line_number}: "
                    "START block must begin file or follow an END block"
                )
            prefix = re.match(rf"(.*?){Markers.START.value}", line).group(1)
            last = Markers.START.value
        elif Markers.REPLACE.value in line:
            if last != Markers.START.value:
                errors.append(
                    f"Line {line_number}: "
                    "REPLACE-WITH block must follow START block"
                )
            last = Markers.REPLACE.value
        elif Markers.END.value in line:
            if last not in [Markers.START.value, Markers.REPLACE.value]:
                errors.append(
                    f"Line {line_number}: "
                    "END block must follow START or REPLACE block"
                )
            last = Markers.END.value

        if (
            last == Markers.REPLACE.value or Markers.END.value in line
        ) and not line.startswith(prefix):
            errors.append(f"Line {line_number}: Missing prefix")

    if last != Markers.END.value:
        errors.append("Final block must be an END block")

    if not has_blocks:
        errors.append("There are no markers in the file")

    if errors:
        raise plug.PlugError(errors)


def file_is_dirty(
    relpath: _fileutils.RelativePath, repo_root: pathlib.Path
) -> bool:
    """Checks if a file contains any markers, therefore telling us if it needs
    to be sanitized or not.

    Args:
        repo_root: The root directory of the repository containing the file.
        relpath: The file's relative path to repo_root.
    Returns:
        A boolean value. True if the file is dirty, false if not.
    """
    if relpath.is_binary:
        return False

    content = relpath.read_text_relative_to(repo_root).split("\n")
    for line in content:
        for marker in Markers:
            if marker.value in line:
                return True
    return False


def _check_shred_syntax(lines: List[str]) -> List[str]:
    """Tells us whether or not the text has valid usage of the shred marker.
    Valid syntax is, if a shred marker is on the first line of text then on
    every line other than the first, there should be no markers. If there is
    no shred marker on the first line, then there should not be one later.

    Args:
        lines: The file to check syntax for as a list of one string per
        line.
    Returns:
        A list including all found errors
    """
    errors = []
    has_shred_marker = (
        _contained_marker(lines[0] if lines else "") == Markers.SHRED
    )
    for line_number, line in enumerate(lines, start=1):
        marker = _contained_marker(line)
        if marker == Markers.SHRED and line_number != 1:
            errors.append(
                f"Line {line_number}: SHRED marker only allowed on line 1"
            )
        elif marker and marker != Markers.SHRED and has_shred_marker:
            errors.append(
                f"Line {line_number}: Marker is dissallowed after SHRED "
                "marker"
            )

    return errors


def _contained_marker(line: str) -> Optional[Markers]:
    for marker in Markers:
        if marker.value in line:
            return marker
    return None
