from setuptools import setup, find_packages

setup(
    name="tealer-rekeyTo-plugin",
    description="tealer plugin for detecting paths with missing rekeyTo in stateless contracts.",
    author="Trail of Bits",
    version="0.0.1",
    packages=find_packages(),
    python_requires=">=3.6",
    install_requires=["tealer"],
    entry_points={
        "teal_analyzer.plugin": "rekey_to_plugin=tealer_rekey_plugin:make_plugin",
    },
)
