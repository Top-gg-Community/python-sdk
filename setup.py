import os
import pathlib
import re
import types

from setuptools import find_packages, setup

HERE = pathlib.Path(__file__).parent

txt = (HERE / "topgg" / "__init__.py").read_text("utf-8")

groups = {}

for match in re.finditer(r'__(?P<identifier>.*)__\s*=\s*"(?P<value>[^"]+)"\r?', txt):
    group = match.groupdict()
    groups[group["identifier"]] = group["value"]

metadata = types.SimpleNamespace(**groups)

on_rtd = os.getenv("READTHEDOCS") == "True"

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

if on_rtd:
    requirements.append("sphinxcontrib-napoleon")
    requirements.append("sphinx-rtd-dark-mode")

with open("README.rst") as f:
    readme = f.read()

setup(
    name="topggpy",
    author=f"{metadata.author}, Top.gg",
    author_email="shivaco.osu@gmail.com",
    url="https://github.com/top-gg/python-sdk",
    version=metadata.version,
    packages=find_packages(),
    license=metadata.license,
    description="A simple API wrapper for Top.gg written in Python.",
    long_description=readme,
    package_data={"topgg": ["py.typed"]},
    include_package_data=True,
    python_requires=">= 3.6",
    install_requires=requirements,
    keywords="discord bot server list discordservers serverlist discordbots botlist topgg top.gg",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Topic :: Internet",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities",
    ],
)
