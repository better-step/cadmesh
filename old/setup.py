
from setuptools import setup


with open("README.md", "r") as fh:
    long_description = fh.read()


setup(
    name="cadmesh",
    version="0.1",
    author="Sebastian Koch",
    author_email="",
    description="Meshing CAD files",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/skoch9/cadmesh/",
    packages=['cadmesh'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MPL-2.0 License"
    ],
    test_suite="test"
)
