import os

from setuptools import setup


if __name__ == "__main__":
    # Version is determined using the dunamai tool https://github.com/mtkennerly/dunamai

    version = os.getenv(
        "PYTEST_GIT_SELECTOR_VERSION", ""
    )  # VERSION is set by the python-publish job

    if not version:  # building locally
        version = "0.0.0.dev0"
    setup(version=version)
