"""Single source of the version, resolved from installed package metadata.

The real version comes from the git tag at build time (hatch-vcs); this just reads
back whatever pip installed. No number is hardcoded anywhere in the repo.
"""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("jouyaar")
except PackageNotFoundError:  # running from a source tree that was never installed
    __version__ = "0.0.0+dev"
