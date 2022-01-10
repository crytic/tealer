# Tealer plugin example

Tealer supports plugins, additional detectors and printers can be added to tealer in the form of plugins.
This repo contains template and an actual implementation of tealer plugin.

## Architecture

- plugin have to define a entrypoint in `setup.py`. entrypoint should be defined with group set to `teal_analyzer.plugin` and it should return the tuple containing list of detectors and list of printers when called i.e `Tuple[List[Type[AbstractDetector]], List[Type[AbstractPrinter]]]`
- Detectors should be subclasses of `AbstractDetector`. Detectors have to override `detect` method and return output in one of the supported formats.
- Printers should be subclasses of `AbstractPrinter` and have to override `print` method.

see `template` folder for skeleton of the plugin
- `setup.py`: Contains the plugin information.
- `tealer_plugin/__init__.py`: Contains `make_plugin` function which has to return list of detectors and printers.
-  `tealer_plugin/detectors/example.py`: Contains detector plugin skeleton.

plugin can be installed after updating the files in the template by running:

```
python setup.py develop
```

`rekey_plugin` contains actual implementation of a plugin.

It is recommended to use a Python virtual environment (for example: [virtualenvwrapper](https://virtualenvwrapper.readthedocs.io/en/latest/)).