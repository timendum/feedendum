import importlib.metadata

__version__ = "dev"
try:
    importlib.metadata.version("feedendum")
except importlib.metadata.PackageNotFoundError:
    pass
