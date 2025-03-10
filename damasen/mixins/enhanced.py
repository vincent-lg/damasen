"""Mixin for enhanced objects with data.

This mixin allows to generate objects from Python files and enhance
them with data files, both of which are considered external to the project
and can be set/updated by the user.

"""

import importlib.util
from pathlib import Path
import sys
from typing import Any, Type

from parse import parse, Result


class EnhancedWithData:

    """A mixin to load external Python modules and enhance them with data."""

    specifications = {}

    @classmethod
    def load_one(
        cls, py_file: Path | str | None, data_file: Path | str | None
    ) -> Type[Any]:
        """Dynamically load a Python file with a data file.

        Args:
            py_file (Path or str): the path (with the .py extension).
            data_file (Path or str): the data file associated (.txt).

        This method will try to load a Python file and a data file.
        Either of these can be missing (be sure to set the paths to `None`).
        However, a loaded class should always have a base class: if there's
        no Python module to load from, a child of the base class will be
        created automatically and fed (if possible) the data file.

        If the Python file exiss (and is not None), it should contain
        a class inheriting from the base class.
        If the data file exists (and is not None), it is read and
        the string content will be fed to the class' `extend_from_data`,
        which should be a class method. Should the Python file be missing
        and a child of the base class be created, its method will also
        be called, so be sure to have it defined in the base class.

        Returns:
            extracted (type): the extracted class from the read module.

        """
        cwd = Path.cwd()
        if py_file is not None:
            py_file = Path(py_file) if isinstance(py_file, str) else py_file

            if not py_file.is_absolute():
                py_file = cwd / py_file

        if data_file is not None:
            data_file = Path(data_file) if isinstance(data_file, str) else data_file

            if not data_file.is_absolute():
                data_file = cwd / data_file

        # If there's a Python file, try to import it.
        if py_file is not None and py_file.exists():
            rel_py_file = py_file.relative_to(cwd)
            module_address = ".".join(rel_py_file.parent.parts)
            module_address += "." + py_file.stem
            module_path = str(py_file)
            spec = importlib.util.spec_from_file_location(module_address, module_path)
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_address] = module
            spec.loader.exec_module(module)

            # Now try to locate the child class
            found = None
            for obj in module.__dict__.values():
                if (
                    isinstance(obj, type)
                    and obj is not cls
                    and issubclass(obj, cls)
                ):
                    if found is None:
                        found = obj
                    else:
                        raise ValueError(
                            f"while reading {module_address}: several classes "
                            f"are children of {cls} (at least "
                            f"{found} and {obj})"
                        )

            loaded = found
        elif not cls.allow_no_python_file:
            raise ValueError(f"a python module should be defined in {py_file}")
        else:
            loaded = type(f"Dynamic.{cls.__name__}", (cls,), {})

        # Get the data, if any.
        if data_file is not None and data_file.exists():
            with data_file.open("r", encoding="utf-8") as file:
                contents = file.read()

            loaded.extend_from_data(contents)
        elif not cls.allow_no_data_file:
            raise ValueError(f"a data file should be defined in {data_file}")

        return loaded

    @classmethod
    def load_all(
        cls, py_path: str | Path | None, data_path: str | Path | None
    ) -> list[Type[Any]]:
        """Load all the modules and data in a given directory tree."""
        cwd = Path.cwd()
        if py_path is not None:
            py_path = Path(py_path) if isinstance(py_path, str) else py_path

            if not py_path.is_absolute():
                py_path = cwd / py_path

        if data_path is not None:
            data_path = Path(data_path) if isinstance(data_path, str) else data_path

            if not data_path.is_absolute():
                data_path = cwd / data_path


        paths = set()
        for pattern, path in (("*.py", py_path), ("*.txt", data_path)):
            for file_path in path.rglob(pattern):
                rel_path = file_path.parent.relative_to(path) / file_path.stem
                paths.add(rel_path)

        classes = []
        for path in paths:
            py_file = py_path / path.parent / (path.stem + ".py")
            data_file = data_path / path.parent / (path.stem + ".txt")
            loaded = cls.load_one(py_file, data_file)
            classes.append(loaded)

        return classes

    @classmethod
    def extend_from_data(cls, data):
        """Extend a class with some data.

        By default, we use the definitions to parse a pseudo language
        to configure the class.

        """
        category = ()

        for line in data.splitlines():
            if not line.strip():
                continue

            line = line.lstrip()
            specifications = cls.specifications
            for key in category:
                spec = specifications.get(key)
                if spec is None:
                    spec = specifications[...]
                specifications = spec

            # end is a special case
            if line == "end":
                if category:
                    category = category[:-1]
                else:
                    raise ValueError("Syntax error: cannot terminate category")
            elif line.endswith(":"):
                # It's a category. Check that it's allowed.
                key = line.removesuffix(":")
                if not isinstance(specifications.get(key), dict):
                    raise ValueError(f"unknown category: {key}")
                category = category + (key,)
            else:
                key = line.split(" ")[0]
                option_spec = specifications.get(key)
                if option_spec is None:
                    option_spec = specifications.get(...)

                if option_spec is None:
                    raise ValueError(f"not a supported option: {key!r}")
                elif isinstance(option_spec, dict):
                    raise ValueError(f"this is a category: {key}")

                if (
                    result := cls.parse_option(
                        category, option_spec, key, line
                    )
                ) is not None:
                    cls.write_option(category, key, result)

    @classmethod
    def parse_option(
        cls, category: tuple[str], spec: str, key: str, line: str
    ) -> Result:
        """Try to parse an option given in a format.

        Args:
            category (tuple): the tuple of keys leading to this option.
            spec (str): the type specification for this key.
            key (str): the option name.
            line (str): the line to parse.

        """
        match spec:
            case "any":
                format = f"{key} {{}}"
            case "int":
                format = f"{key} {{:d}}"
            case "float":
                format = f"{key} {{:f}}"
            case "number":
                format = f"{key} {{:g}}"
            case "interval":
                format = f"{key} between {{:d}} and {{:d}}"
            case _:
                raise ValueError(f"unknown type spec: {spec!r}")

        if result := parse(format, line):
            if len(result.fixed) == 1:
                return result.fixed[0]
            else:
                return result.fixed
        else:
            raise ValueError(
                f"invalid format for {key!r}: expecting {format!r}"
            )

    @classmethod
    def write_option(cls, category: tuple[str], key: str, value: Any) -> None:
        """Write an option in the class.

        Args:
            category (tuple of str): the categories.
            key (str): the option key.
            value (any): the value to write.

        """
        if category:
            dictionary = None
            for cat in category:
                if dictionary is None:
                    dictionary = {}
                    setattr(cls, cat, dictionary)
                else:
                    if cat not in dictionary:
                        dictionary[cat] = {}

                    dictionary = dictionary[cat]

            dictionary[key] = value
        else:
            setattr(cls, key, value)
