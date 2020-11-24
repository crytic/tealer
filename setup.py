from setuptools import setup, find_packages

setup(
    name="teal-analyzer",
    description="Teal analyzer.",
    # url="https://github.com/crytic/teal",
    author="Trail of Bits",
    version="0.0.0",
    packages=find_packages(),
    python_requires=">=3.6",
    license="AGPL-3.0",
    long_description=open("README.md").read(),
    entry_points={"console_scripts": ["teal-analyzer = teal_analyzer.__main__:main"]},
)
