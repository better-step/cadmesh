import setuptools
from setuptools import setup


# with open("README.md", "r", encoding="utf-8") as fh:
#     long_description = fh.read()


from setuptools import setup, find_packages

setup(
    name="steptohdf5",
    version="v0.2.2",
    description="Convert STEP and other CAD files to HDF5-based mesh archives",
    long_description=open("README.md", encoding="utf-8").read(),
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
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Operating System :: OS Independent",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Information Analysis",
    ],
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.8",
    install_requires=[
        "numpy",
        "h5py",
        "meshio",
        "joblib",
        "tqdm"
    ],
    extras_require={
        # Users on CPython-3.10+ can do: `pip install steptohdf5[occ]`
        "occ": ["pythonocc-core>=7.4.0"],
    },
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "steptohdf5 = steptohdf5.cli:main",
        ]
    },
)



