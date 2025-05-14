from pathlib import Path
from setuptools import setup, find_packages

# -----------------------------------------------------------------------------
# NOTE
# ----
# Newer tools read the metadata from pyproject.toml.  This setup.py remains
# for compatibility with conda-build <3.23 and legacy environments.
# -----------------------------------------------------------------------------
setup(
    name="steptohdf5",
    version="0.2.0",
    description="Convert STEP / STP CAD files to HDF5-based mesh archives",
    long_description=Path("README.md").read_text(encoding="utf-8"),
    long_description_content_type="text/markdown",
    author="Better Step",
    url="https://github.com/better-step/cadmesh",
    license="GPL-3.0-only",
    python_requires=">=3.8",

    package_dir={"": "src"},
    packages=find_packages(where="src"),
    include_package_data=True,

    install_requires=[
        "numpy>=1.22",
        "h5py",
        "meshio",
        "meshplot",
        "joblib",
        "tqdm",
    ],
    extras_require={
        "occ": ["pythonocc-core>=7.4.0"],
        "full": ["pythonocc-core>=7.4.0", "igl"],
    },
    entry_points={
        "console_scripts": [
            "steptohdf5 = steptohdf5.cli:main",
        ]
    },
    classifiers=[
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Operating System :: OS Independent",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Visualization",
    ],
)
