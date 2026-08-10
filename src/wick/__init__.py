from importlib.metadata import PackageNotFoundError, version

from .pipeline import Answer, OfflineAssistant

__all__ = ["Answer", "OfflineAssistant"]

try:
    # Read from the installed metadata so it can't drift from pyproject.toml.
    __version__ = version("wick-offline")
except PackageNotFoundError:
    __version__ = "0.0.0+source"
