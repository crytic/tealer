from setuptools import setup, find_packages

setup(
    name="tealer-plugin",
    description="plugin example for tealer",
    author="Trail of Bits",
    version="0.0",
    packages=find_packages(),
    python_requires=">=3.6",
    install_requires=["tealer"],
    entry_points={
        "teal_analyzer.plugin": "tealer_plugin=tealer_plugin:make_plugin",
    },
)
