import setuptools
from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent

setup(
    name="steptohdf5",
    version="0.2.4",  # no leading "v"
    description="Convert STEP and other CAD files to HDF5-based mesh archives",
    long_description=(here / "README.md").read_text(encoding="utf-8"),
    long_description_content_type="text/markdown",
    author="Better Step",
    url="https://github.com/better-step/cadmesh",
    project_urls={
        "Source": "https://github.com/better-step/cadmesh",
        "Tracker": "https://github.com/better-step/cadmesh/issues",
    },
    license="GPL-3.0",
    classifiers=[
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python :: 3.8",
        "Operating System :: OS Independent",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Information Analysis",
    ],

    package_dir={"": "src"},
    packages=find_packages(where="src"),
    include_package_data=True,
    zip_safe=False,

    python_requires=">=3.8",
    install_requires=[
        "numpy",
        "h5py",
        "meshio",
        "joblib",
        "tqdm",
    ],
    extras_require={
        "occ": ["pythonocc-core>=7.4.0"],
    },

    # point at your real 'main' function
    entry_points={
        "console_scripts": [
            "steptohdf5 = cadmesh.cloud_conversion:main",
        ],
    }
)
