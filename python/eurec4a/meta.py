import os
import yaml
from yaml.loader import SafeLoader, BaseLoader
from .uri import parse_uri

class Annotated:
    def __init__(self, child, start, end):
        self.child = child
        self.start = start
        self.end = end

    def replace(self, new):
        return type(self)(new, self.start, self.end)

class AnnotatedScalar(Annotated):
    def collapse(self):
        return self.child

class AnnotatedSequence(Annotated):
    def collapse(self):
        return type(self.child)(c.collapse() for c in self.child)

class AnnotatedMapping(Annotated):
    def collapse(self):
        return type(self.child)((k.collapse(), v.collapse()) for k, v in self.child.items())

    def __contains__(self, element):
        return element in {k.collapse() for k in self.child.keys()}

    def __getitem__(self, element):
        for k, v in self.child.items():
            if k.collapse() == element:
                return v
        raise IndexError(element)

class AnnotatingLoader(BaseLoader):
    def construct_scalar(self, node):
        value = super(AnnotatingLoader, self).construct_scalar(node)
        return AnnotatedScalar(value, node.start_mark, node.end_mark)

    def construct_sequence(self, node):
        value = super(AnnotatingLoader, self).construct_sequence(node)
        return AnnotatedSequence(value, node.start_mark, node.end_mark)

    def construct_mapping(self, node):
        value = super(AnnotatingLoader, self).construct_mapping(node)
        return AnnotatedMapping(value, node.start_mark, node.end_mark)


def simple_loader(object_type):
    def loader(id, data, location):
        if "configurations" in data:
            configurations = data["configurations"]
            sub_location = location.move_to(configurations.start.line,
                                            configurations.start.column)
            sub_loader = get_loader("{}_configurations".format(object_type), sub_location)
            for name, configuration in configurations.child.items():
                name = name.replace("{}_{}".format(id.collapse(), name.collapse()))
                sub_location = location.move_to(configuration.start.line,
                                                configuration.start.column)
                configuration.child[name.replace("configuration of")] = id
                yield from sub_loader(name, configuration, sub_location)

        data = data.collapse()
        data["id"] = id.collapse()
        data["type"] = object_type
        if "uris" in data:
            data["uris"] = [parse_uri(uri) for uri in data["uris"]]

        if "configurations" in data:
            del data["configurations"]
        yield data, location
    return loader


def role_loader(object_type):
    def loader(id, data, location):
        data = {
            "id": id.collapse(),
            "type": object_type,
            "name": data.collapse()
        }
        yield data, location
    return loader

LOADERS = {
    "people": simple_loader("person"),
    "peoples_roles": role_loader("peoples_role"),
    "institutions": simple_loader("institution"),
    "institutional_roles": role_loader("institutional_role"),
    "platforms": simple_loader("platform"),
    "platform_configurations": simple_loader("platform_configuration"),
    "instruments": simple_loader("instrument"),
    "instrument_configurations": simple_loader("instrument_configuration"),
    "variables": simple_loader("variable"),
}

class FileLocation:
    def __init__(self, filename, line, col):
        self.filename = filename
        self.line = line
        self.col = col

    def move_to(self, line, col):
        return FileLocation(self.filename, line, col)

    def __str__(self):
        return "{}:{}:{}".format(self.filename, self.line, self.col)

class ParseError(BaseException):
    pass

class UnknownObjectError(ParseError):
    def __init__(self, name, location):
        self.name = name
        self.location = location
    def __str__(self):
        return "unknown object: \"{}\" at {}".format(self.name, self.location)

class DuplicateObjectError(ParseError):
    def __init__(self, id, location1, location2):
        self.id = id
        self.location1 = location1
        self.location2 = location2
    def __str__(self):
        return "object \"{}\" has been defined twice: at {} and {}".format(self.id, self.location1, self.location2)


def get_loader(loader_type, location):
    try:
        return LOADERS[loader_type]
    except KeyError as exc:
        raise UnknownObjectError(loader_type, location) from exc


def load_metadata_file(filename):
    with open(filename) as f:
        metadata = yaml.load(f, Loader=AnnotatingLoader)
    for loader_type, objects in metadata.child.items():
        location = FileLocation(filename, loader_type.start.line, loader_type.start.column)
        loader = get_loader(loader_type.collapse(), location)
        for k, v in objects.child.items():
            location = FileLocation(filename, v.start.line, v.start.column)
            yield from loader(k, v, location)

def _load_metadata_from_folder(folder):
    for root, dirs, files in os.walk(folder):
        for filename in files:
            if filename.endswith(".yaml"):
                path = os.path.join(root, filename)
                yield from load_metadata_file(path)

def load_metadata_from_folder(folder):
    metadata = {}
    locations = {}
    for entry, location in _load_metadata_from_folder(folder):
        if entry["id"] in metadata:
            raise DuplicateObjectError(entry["id"], locations[entry["id"]], location)
        metadata[entry["id"]] = entry
        locations[entry["id"]] = location
    return metadata

def print_metadata_from_folder(folder):
    try:
        per_file_metadata = load_metadata_from_folder(folder)
    except ParseError as error:
        print(error)
        return
    for data in per_file_metadata.values():
        print(data)

def print_instruments_from_folder(folder):
    try:
        per_file_metadata = load_metadata_from_folder(folder)
    except ParseError as error:
        print(error)
        return
    for data in per_file_metadata.values():
        if data["type"] != "instrument":
            continue
        print(data["name"])

