# EUREC4A Metadata Structure
The EUREC4A metadata occurs in several different formats and formatting levels, depending on the use case.
The metadata is built from a set of metadata objects. Each object is an instance of a particular kind of metdata object, such as a `person`, or a `platform`, and each specific object (e.g., Tobi or HALO) is identified uniquely (by an id) that is then used across all metadata objects.  This allows objects to refer to each other.

## formatting levels

Input formats are intended as the only source of truth of the metadata. In the input formats, no information should be duplicated, such that inconsistencies can be avoided. The input formats should also be human readable, as the maintenance of the metadata will be carried out by humans and the use of git and text file diffs is envisioned as the primary way of updating metadata.

An intermediate format will be constructed from the input formats.
This is intended to be machine readable and should become the most regular format.
Ideally, this will become available as one large, automatically updated file which contains all available metadata information.  
This should also be the primary format read by users who want to access the metadata programmatically.

The third level are reports, which can be generated automatically from the intermediate level.
The reports are derived from the intermediate format, and presented or styled (e.g. using HTML) such that the information becomes easy to read by humans who want to inform themselves about the field campaign activities, without any need for programming knowledge.

## objects
The currently specified metadata objects are:

* person
* peoples_role
* institution
* institutional_role
* platform
* platform_configuration
* instrument
* instrument_configuration
* variable

### individual objects

#### person
| key   | type | required | description   |
| ---   | ---  | ---      | ---           |
| name  | str  | ✓        | full name     |
| email | str  |          | email address |

#### peoples_role
| key  | type | required | description      |
| ---  | ---  | ---      | ---              |
| name | str  | ✓        | name of the role |

Note that is is ok to define the object in YAML by only writing the name as a string, without defining a `map`.

#### institution
| key     | type      | required | description |
| ---     | ---       | ---      | ---         |
| name    | str       | ✓        | name        |
| city    | str       |          | city        |
| country | str       |          | country     |
| part_of | object id |          | reference to another institution, use if this institution is a part of a larger institution|

#### institutional_role
| key  | type | required | description      |
| ---  | ---  | ---      | ---              |
| name | str  | ✓        | name of the role |

Note that is is ok to define the object in YAML by only writing the name as a string, without defining a `map`.

#### platform
| key      | type         | required | description                                           |
| ---      | ---          | ---      | ---                                                   |
| name     | str          | ✓        | platform (long) name                                  |
| aliases  | [str]        |          | other common names of the same platform               |
| kinds    | [str]        | ✓        | classification of the platform                        |
| contacts | {id: [role]} |          | people or institutions relevant for the platform      |
| uris     | [str]        |          | list of uris refering to additional information       |
| color    | hex color    |          | preferred color to use when referring to the platform |

##### Notes
* each platform can belong to multiple `kinds`. Kinds should be listed in decreasing order of specificity.
* `contacts` may reference either a `person` or an `institution`. The list of roles must refer to the corresponding set of roles. The roles describe in which function the person or institution is related to the platform.
* `uris` may currently by http(s) urls or dois
* `color` must be given as RGB hex code, i.e. `#RRGGBB`.

#### platform_configuration
| key              | type                 | required | description |
| ---              | ---                  | ---      | ---         |
| configuration of | platform id          | ✓        |             |
| name             | str                  |          |             |
| timeframe        | {from: ..., to: ...} |          |             |

#### instrument
| key         | type         | required | description                                           |
| ---         | ---          | ---      | ---                                                   |
| name        | str          | ✓        |                                                       |
| kinds       | [str]        | ✓        |                                                       |
| description | str          |          | free text describing the instrument                   |
| contacts    | {id: [role]} |          | people or institutions relevant for the platform      |
| uris        | [str]        |          | list of uris refering to additional information       |
| color       | hex color    |          | preferred color to use when referring to the platform |

#### instrument_configuration
| key              | type                      | required | description |
| ---              | ---                       | ---      | ---         |
| configuration of | instrument id             | ✓        |             |
| part of          | platform_configuration id |          |             |
| name             | str                       |          |             |

#### variable
| key         | type                        | required | description |
| ---         | ---                         | ---      | ---         |
| name        | str                         | ✓        |             |
| measured by | instrument_configuration id | ✓        |             |


## input formats
EUREC4A metadata can be provided in several formats, which are still in development.
The only currently implemented input format is a collection of [YAML](https://yaml.org) files, which are stored in the [metadata](metadata) folder of this repository.
Another format will most likely be metadata which is embedded in published field campaign data, which references metadata from the YAML repository.

### YAML input format
YAML files can be placed in any order inside the [metadata](metadata) folder and its subfolders.
There is no specified folder structure and file naming convention, except that the filenames have to end with `.yaml`.
Each YAML file must have a `map` as its top-level element.
The keys of this map describe the type of the objects listed as its value and are generally the plural of the object type.
Valid keys are:

* `people` for object type `person`
* `peoples_roles` for object type `peoples_role`
* `institutions` for object type `institution`
* `institutional_roles` for object type `institutional_role`
* `platforms` for object type `platform`
* `platform_configurations` for object type `platform_configuration`
* `instruments` for object type `instrument`
* `instrument_configurations` for object type `instrument_configuration`
* `variables` for object type `variable`

The second level of the YAML files must be a `map` which relates object ids to objects (i.e., the collection of metadata assoicated with that object) of the aforementioned type.
Please have a look at the [metadata](metadata) folder for examples.

#### inline objects

Some objects which belong to other objects may be defined within other objects in order to reduce the complexity of writing the YAML files.
This is possible for:

* `platform_configuration` within `platform`
* `instrument_configuration` within `instrument`
* `variable` within `instrument_configuration`

### intermediate format
A proof of concept intermediate format listing can be generated with:

```bash
cd python
python3 -c 'import eurec4a.meta as m; m.print_metadata_from_folder("../metadata")'
```

### reports
A proof of concept report can be generated with:

```bash
cd python
python3 -m eurec4a.generate_reports -o <output folder>
```
