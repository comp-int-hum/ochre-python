# OCHRE: The Open Computational Humanities Research Ecosystem

This package can be installed via `pip`:

```
pip install pyochre
```

It has three submodules that correspond more or less to basic concepts in computational humanities research:

- primary_sources :: 
- machine_learning ::
- scholarly_knowledge ::

In addition to using the package as a library in one's own code, each submodule can be executed as a command-line script that provides quick ways to perform common tasks.  For instance:

```
python -m pyochre.scholarly_knowledge --help
```

prints information on how to use the `scholarly_knowledge` script.

## Primary sources

A primary source consists of the *domain*, describing types of entities and their potential properties and relationships, and the *data*, which are the actual instantiations of those types of entities, their specific properties and relationships.  For practical reasons, when a property is associated with a substantial amount of information (like a long document, image, video, etc), there is a third aspect of primary sources, *materials*, allowing them to be stored and accessed efficiently.

As a simple abstract example, primary sources of campaign contribution information might have a *domain* capturing that there are entity types *Politician*, *Office*, *Donation*, and *Organization*, that a *Politician* has text property *givenName*, relationship *runningFor* with *Office*, another property *headShot* that should be a unique identifier (that will select a file in the *materials*) and so forth.  The *domain* might have thousands of entities of each type, e.g. a *Politician* with *givenName* of "Dan", *runningFor* an *Office* with its own properties, and a *headShot* value of "some_long_random_value".  Finally, the *materials* might contain lots of image files, one of them named "some_long_random_value".



### Simple start

There are several pre-made methods for creating new primary sources for common situations.  The fundamental goal is to take some files in particular formats, and extract all the entities, relationships, and properties.

### Details

We represent both *domain* and *data* using the [RDF framework](https://www.w3.org/TR/rdf11-concepts/).  Only the *domain* is strictly necessary when creating a new primary source: *data* and *materials* can be added later, or incrementally.  The simplest way to create a new primary source is using the script:

```
python -m pyochre.primary_sources create --domain_file domain.ttl --name "My Research Area"
```

This would create new primary sources named "My Research Area", whose *domain* structure is described in the RDF [Turtle format](https://www.w3.org/TR/turtle/), with no *data* or *materials* yet.

#### Domain

The *domain* of the primary sources is expressed using RDF, and has several goals:

- Map closely to human understanding and intuition
- Avoid introducing debatable scholarly inferences
- Define and constrain the form of information in the primary sources
- Provide links from the *domain* into the broader space of human knowledge

Each of these requires careful consideration by the scholar, and can be sensitive to the field, the specific research, and available resources.


[SHACL vocabulary](https://www.w3.org/TR/2017/REC-shacl-20170720/)

### Converting various formats


The technical details and advanced methods are described further below, but on the simplest level, a CSV file can be converted by simply running:

```
python -m pyochre.primary_sources convert --format csv --input spreadsheet.csv --
```

#### How formats are converted

The general pattern for converting a non-RDF document is: as the format is read certain "events" fire, each of which is an opportunity to generate RDF triples based on the event and the current location in the document.

##### Events

Each event is either the *start* or *end* of something, a *tag*, and a dictionary of *attributes*.  For instance, an event indicating the end of a single cell in a CSV file might be:

```
("end", "cell", {"n" : "day", "value" : "Monday"})
```

A location is the sequence of "start" events enclosing the current event, such as:

```
[
  ("start", "table", {"n" : "some_file.csv"}),
  ("start", "row", {"n" : "22"})
]
```

In plain English, this pair of event and location says "We are on row 22 of a CSV file named 'some_file.csv' and have just finished reading its cell corresponding to the column 'day' with value 'Monday'".  No matter the format (CSV, XML, etc), events have the same structure (two strings and a dictionary).  The possible values for *tag* will depend on the format (HTML won't ever have a "row" tag, but might have "div", "body", etc), as will the contents of the *attributes* dictionary.

##### Specification

The goal, therefore, is to specify how to take an (event, location) pair, and create zero or more RDF triples.  This involves specifying rules that 1) can be determined to match such a pair, and 2) if they match, create one or more RDF triples from the information in the pair.  Rules are specified in JSON, and have the form:

```schema
{
  "metadata" : (arbitrary dictionary),
  "namespaces" : (dictionary from prefix to URI),
  "predefined" : (list of triples),
  "rules" : (list of rules)
}
```


```rule
{
  "match" : (none|list of match specs),
  "create" : (list of creation specs)
}
```



```match
{
  "event_type" : (none|list of matching event types, i.e. "start" and/or "end"),
  "tag" : (none|list of matching tags),
  "attributes" : (dict of attribute names to matching values in form (none|list of matching values)),
  "location" : (none|list of match specs)
}
```


```creation
{
  "subject" : (value_spec),
  "predicate" : (value_spec),
  "object" : (value_spec),
  "type" : (one of "domain", "data", "materials")
}
```

```value_spec 
{
  "type" : (uri|literal|bnode),
  "value" : (mustache),
  "xml:lang" : (mustache),
  "datatype" : (mustache)
}
```
