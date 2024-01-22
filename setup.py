from setuptools import setup, find_packages

with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="tealer",
    description="Teal analyzer.",
    url="https://github.com/crytic/tealer",
    author="Trail of Bits",
    version="0.1.1",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "prettytable>=0.7.2",
        "py-algorand-sdk",
        "pycryptodomex",
        "requests",
        "pyyaml",
        "setuptools",
    ],
    extras_require={"dev": ["pylint==2.13.4", "black==22.3.0", "mypy==0.942", "pytest-cov"]},
    license="AGPL-3.0",
    long_description=long_description,
    long_description_content_type="text/markdown",
    entry_points={"console_scripts": ["tealer = tealer.__main__:main"]},
)
