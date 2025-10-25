from pathlib import Path


def get_version():
    version_path = Path(__file__).parent.parent.joinpath("__version__")
    with open(version_path, "r") as f:
        return f.read().strip()


__version__ = get_version()
""" The version of the `pinecone` package"""
