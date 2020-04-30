## EUREC4A
Shared code and standards designed to ease the EUREC4A data analysis


### Identifiers
The data repository, will be built around a controlled vocabulary consisting of a hierarchy of identifiers.  We also encourage the use of these identifiers in building file names and for inclusion as file meda-data.  We hope that doing so will help all of us see and more effectively use the diversity of data that has been collected, and also ease collaboration.

The identifiers are as follows, not every identifier will apply to every instance of the data:

  * **campaign-ID:**  EUREC4A
  * **project-ID:**  An optional identifier to allow groups to give additional specificity to a set of measurements collected with different platforms, for instance ATOMIC
  * **platform-ID:**  An identifier drawn from a controlled vocabulary specifying a platform from which the data was collected.  See [EUREC4A_platforms.yml](EUREC4A_platforms.yml) which maps platform_IDs to platform meta-data.
  * **instrument-ID:**  Specifies an instrument from which a measurement has been made.  Ideally similar instruments from different platforms will adopt similar identifiers. Level 2 data will often have a platform-ID and instrument-ID, but in some cases an instrument and platform may be synoymous.  
  * **product-ID:**  An optional identifier to be used with the instrument-ID to allow groups the flexibility to group measurements in different ways, i.e., SAFIRE_Aerosol might designate a bundle of aerosol instruments run by SAFIRE.
  * **variable-ID:** A specific quantity. Usually this will be the output from a sensor, but it could also be a derived or composite variable.  Examples might be a voltage on a power supply, a temperature reading, a radar reflectivity, the latitude and longitude of a track, or maybe the divergence from a sounding circle. 
  * **time-ID:** For some data it may be useful to indicate the time of the measurement or the time-range of the data included in the file.  This will adopt the form yyyyddmmTHHMMSS-yyyyddmmTHHMMSS, or e.g., yyyymmdd for a single instance. 
 * **version-ID:** The data versioning, in the form vN.M with N and M integers. Using version 0 for preliminary data is encouraged.

The EUREC4A data base will use the platform-ID as the first level of data granualrity. Depending on the platform, additional levels of granularity (sub-directories) may be included and labeled by some (possibly empty) subset of instrument-ID, product-ID or variable-ID.  It will not organize data by project-ID, nor by time-ID.

### File naming conventions

Filenames should be composed of a hierarchical application of the applicable subset of the controlled vocabularly, with IDs separated by underscores.  Hyphens can be used for IDs composed of compound words.  Hence the structure would be:

`campaign-ID_project-ID_platform-ID_instrument-ID_variable-ID_time-ID_version-ID.nc`

Examples could be
  - EUREC4A_Meteor_Track_v0.2.nc
  - EUREC4A_ATR_Safire_Radiation_20200202_v2.2.nc  
  - EUREC4A_ATOMIC_SWIFT-12_T05_20200120-20200212_v1.0.nc
  - EUREC4A_Dropsonde_Circles_Divergence_v3.3.nc

We envision every file beginning with the Campaign_ID and ends with the Version_ID and includes at least one further ID to add content specificity.

### File metadata

File meta data should include all the identifiers, i.e., Platform_ID: "ATR", Campaign_ID: "EUREC4A" and additionally contain contact information of the person or organization responsible for the file (its creator). Often the contact will be the PI for the platform (or instrument) or the creator for the derived product.  YAML databases are being provided for the EUREC4A community as a whole for the platforms [EUREC4A_platforms.yml](EUREC4A_platforms.yml)). Instrument groups are encouraged to provide a similar meta-data template to help others in the use and crediting of their data.

### Coordinates and variables

We suggest a controlled vocabulary for position information, i.e., time (seconds since YYYY-MM-DDTHH:MM:SS, lat (degree_north), lon (degree_east), height (m), depth (m).  Again coordination among instrument scientists so that similar instruments across different platforms have the same name would be desirable.
