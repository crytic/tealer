from setuptools import setup, find_packages

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
    extras_require={"dev": ["pytest", "pylint==2.8.2", "black==20.8b1", "mypy"]},
    license="AGPL-3.0",
    long_description=open("README.md").read(),
    entry_points={"console_scripts": ["tealer = tealer.__main__:main"]},
)
