from setuptools import setup, find_packages

setup(
    name="tealer",
    description="Teal analyzer.",
    url="https://github.com/crytic/tealer",
    author="Trail of Bits",
    version="0.0.3",
    packages=find_packages(),
    python_requires=">=3.6",
    install_requires=[
        "prettytable>=0.7.2",
    ],
    license="AGPL-3.0",
    long_description=open("README.md").read(),
    entry_points={"console_scripts": ["tealer = tealer.__main__:main"]},
)
