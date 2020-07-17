"""Extension command that provides functionality for sanitizing a single file.

.. module:: _sanitize_file
    :synopsis: Extension command that provides functionality for
        sanitizing a single file.
"""

import argparse
import pathlib
from typing import List, Mapping, Optional

import repobee_plug as plug

from repobee_sanitizer import _sanitize


PLUGIN_NAME = "sanitizer"


class SanitizeFile(plug.Plugin):
    def _sanitize_file(
        self, args: argparse.Namespace, api: plug.API
    ) -> Optional[Mapping[str, List[plug.Result]]]:
        """A callback function that runs the sanitization protocol on a given
        file

        Args:
            args: Parsed and processed args from the RepoBee CLI.
            api: A platform API instance.
        Returns:
            A mapping (str -> List[plug.Result]) that RepoBee's CLI can use for
            output.
        """
        result = _sanitize.sanitize_file(args.infile)
        args.outfile.write_text(result, encoding="utf8")

    @plug.repobee_hook
    def create_extension_command(self) -> plug.ExtensionCommand:
        parser = plug.ExtensionParser()
        parser.add_argument(
            "infile", help="File to sanitize", type=pathlib.Path,
        )
        parser.add_argument(
            "outfile", help="Output path", type=pathlib.Path,
        )
        return plug.ExtensionCommand(
            parser=parser,
            name="sanitize-file",
            help="Sanitizes files",
            description=(
                "Iterate over files, removing"
                "code between certain START- and END-markers"
                ", also supporting REPLACE-WITH markers."
                "This allows a file to contain two versions"
                "at the same time"
            ),
            callback=self._sanitize_file,
        )
