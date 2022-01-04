from setuptools import setup, find_packages

with open("README.md") as f:
    long_description = f.read()

setup(
    name="tealer",
    description="Teal analyzer.",
    url="https://github.com/crytic/tealer",
    author="Trail of Bits",
    version="0.0.2",
    packages=find_packages(),
    python_requires=">=3.6",
    install_requires=[
        "prettytable>=0.7.2",
    ],
    extras_require={"dev": ["pylint==2.8.2", "black==21.10b0", "mypy==0.910"]},
    license="AGPL-3.0",
    long_description=long_description,
    entry_points={"console_scripts": ["tealer = tealer.__main__:main"]},
)
