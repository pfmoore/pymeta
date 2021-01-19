from packaging.tags import Tag, parse_tag
from packaging.version import Version
from packaging.utils import canonicalize_name, NormalizedName

from typing import FrozenSet, NewType, Optional, Tuple, Union

class InvalidWheelFilename(ValueError):
    """
    An invalid wheel filename was found, users should refer to PEP 427.
    """


class InvalidSdistFilename(ValueError):
    """
    An invalid sdist filename was found, users should refer to the packaging user guide.
    """

def parse_wheel_filename(filename):
    # type: (str) -> Tuple[NormalizedName, Version, Optional[str], FrozenSet[Tag]]
    if not filename.endswith(".whl"):
        raise InvalidWheelFilename(
            "Invalid wheel filename (extension must be '.whl'): {0}".format(filename)
        )

    filename = filename[:-4]
    dashes = filename.count("-")
    if dashes not in (4, 5):
        raise InvalidWheelFilename(
            "Invalid wheel filename (wrong number of parts): {0}".format(filename)
        )

    parts = filename.split("-", dashes - 2)
    name = canonicalize_name(parts[0])
    version = Version(parts[1])
    if dashes == 5:
        # Build number must start with a digit
        build_part = parts[2]
        if not build_part[0].isdigit():
            raise InvalidWheelFilename(
                "Invalid build number: {0} in '{1}'".format(build_part, filename)
            )
        build = build_part  # type: Optional[str]
    else:
        build = None
    tags = parse_tag(parts[-1])
    return (name, version, build, tags)


def parse_sdist_filename(filename):
    # type: (str) -> Tuple[NormalizedName, Version]
    if not filename.endswith(".tar.gz"):
        raise InvalidSdistFilename(
            "Invalid sdist filename (extension must be '.tar.gz'): {0}".format(filename)
        )

    # We are requiring a PEP 440 version, which cannot contain dashes,
    # so we split on the last dash.
    name_part, sep, version_part = filename[:-7].rpartition("-")
    if not sep:
        raise InvalidSdistFilename("Invalid sdist filename: {0}".format(filename))

    name = canonicalize_name(name_part)
    version = Version(version_part)
    return (name, version)
