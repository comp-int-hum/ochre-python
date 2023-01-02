#####
OCHRE
#####

****************************************************
The Open Computational Humanities Research Ecosystem
****************************************************

The Open Computational Humanities Research Ecosystem (OCHRE) provides the server infrastructure and client libraries to experiment with complex machine learning and rich humanistic scholarship.

.. _installation:

============
Installation
============

This package can be installed via `pip`::

  $ pip install pyochre

However, it's advisable to employ Python `virtual environments <https://docs.python.org/3/library/venv.html>`_ (here and in other situations), in which case you would run something like the following in a new empty directory::

  $ python3 -m venv local
  $ source local/bin/activate
  $ pip install pyochre

and run `deactivate` to exit the virtual environment, `source local/bin/acticate` to enter it again.

The simple package doesn't include certain dependencies that are important for deploying a dedicated server, but is designed to be fully functional without requiring significant modification.  There are three extra options that can be included, `ldap`, `postgres`, and `torchserve`.  For instance, to include the full set of options, the command is::

  $ pip install pyochre[ldap,postgres,torchserve]

Note that these options may require additional effort, such as non-Python dependencies that need to be installed independently.  For most situations, the simple package is the right choice.

.. _library:

=================
Library structure
=================

The package has five submodules:

**pyochre.utils**
  Various functions and classes that are generally useful in many places throughout the package

**pyochre.server**
  The OCHRE server, an orchestrated set of servers and frontends that manages the complexity of interdisciplinary computational research

**pyochre.primary_sources**
  Formal domain descriptions, data, and multimedia materials

**pyochre.machine_learning**
  Training, applying, and fine-tuning models with well-defined signatures

**pyochre.scholarly_knowledge**
  Labeling data, specifying conceptual frameworks, and comparing hypotheses

The latter three submodules correspond to basic concepts in computational humanities research, and constitute the "client library" that will be most relevant for the majority of users.

Additionally, the `pyochre.primary_sources`, `pyochre.machine_learning`, `pyochre.scholarly_knowledge`, and `pyochre.server` submodules can each be executed as scripts, for instance::

  $ python -m pyochre.scholarly_knowledge --help

will print usage information about the `pyochre.scholarly_knowledge` script.  See the Scripts_ section for detailed information on how to use these tools.

.. _concepts:

=======================
Concepts and background
=======================

.. _primary_sources:

---------------
Primary sources
---------------

A primary source consists of the *domain*, describing types of entities and their potential properties and relationships, and the *data*, which are the actual instantiations of those types of entities, their specific properties and relationships.  For practical reasons, when a property is associated with a substantial amount of information (like a long document, image, video, etc), there is a third aspect of primary sources, *materials*, allowing them to be stored and accessed efficiently.

As a simple abstract example, primary sources of campaign contribution information might have a *domain* capturing that there are entity types *Politician*, *Office*, *Donation*, and *Organization*, that a *Politician* has text property *givenName*, relationship *runningFor* with *Office*, another property *headShot* that should be a unique identifier (that will select a file in the *materials*) and so forth.  The *domain* might have thousands of entities of each type, e.g. a *Politician* with *givenName* of "Dan", *runningFor* an *Office* with its own properties, and a *headShot* value of "some_long_random_value".  Finally, the *materials* might contain lots of image files, one of them named "some_long_random_value".

Both *domain* and *data* are represented using the `RDF framework <https://www.w3.org/TR/rdf11-concepts/>`_, and the representation has several goals:

- Map closely to human understanding and intuition
- Avoid introducing debatable scholarly inferences
- Define and constrain the form of information in the primary sources
- Provide links from the *domain* into the broader space of human knowledge

Each of these requires careful consideration by the scholar, and can be sensitive to the field, the specific research, and available resources.

OCHRE uses `Wikidata <https://www.wikidata.org/wiki/Wikidata:Main_Page>`_ `entities <https://www.wikidata.org/w/index.php?search=&title=Special:Search&profile=advanced&fulltext=1&ns0=1>`_ and `properties <https://www.wikidata.org/w/index.php?search=&title=Special%3ASearch&profile=advanced&fulltext=1&ns120=1>`_ for semantic links to broader human knowledge.

The `SHACL vocabulary <https://www.w3.org/TR/2017/REC-shacl-20170720/>`_ is used in domain representations to constrain how entities and properties are arranged in a given primary source.
  
.. _machine_learning:

----------------
Machine learning
----------------

Machine learning models, in the most general sense, are *functions* that take in some sort of information as input, and produce another sort of information as output.  By describing the structure and semantics (or the "signature") of these inputs and outputs for a given model, OCHRE can determine how a model can be adapted ("trained" or "fine-tuned") on new primary sources, or applied to them to infer new information.  Focusing on the structural and semantics of model input and output, there are several goals for representation:

- Both input and output signatures should allow expressive specification of graph structure
- Provenance of training data for a fitted model to facilitate parameter re-use etc
- Output of a model, in combination with its signatures and the corresponding inputs, should allow creation of annotations of the same form as described in `Scholarly knowledge`__.

OCHRE has provisionally adopted the `MLSchema specification <http://ml-schema.github.io/documentation/ML%20Schema.html>`_ to describe models, though real-world experience will determine if it is sufficiently expressive.

Ideally, signatures are generated as models are assembled and trained.  In particular, OCHRE will be integrating the `Starcoder project <https://github.com/starcoder/starcoder-python>`_ to automatically generate, train, and reuse `graph neural networks <https://en.wikipedia.org/wiki/Graph_neural_network>`_ based on primary sources and scholarly knowledge, with signatures capturing the structural and semantic relationships.

Existing techniques like topic models, pretrained object recognition, and so forth, are being translated into simple signatures that provide a starting point for OCHRE.

.. __: scholarly_knowledge_
.. _scholarly_knowledge:

-------------------
Scholarly knowledge
-------------------

Colloquially, "scholarly knowledge" corresponds to information not clearly immanent in primary sources themselves according to the research context.  This can be a rather subtle distinction, because it depends on the aims of the scholar and the norms of the field.  As a simple example, scholars often work with materials that have been classified in some way: for Cuneiform tablets, this might be according to language, genre, material, kingdom, and so forth.  These classifications differ greatly in certainty, tangibility, agreement, and relevance for a given scholarly effort.

Trying to "get behind" *all* of this sort of scholarly knowledge is generally a lost cause: the closest situation might be something like archaeological fieldwork, but even that is not straightforward.  Instead, OCHRE encourages scholars to find stable, canonical materials and explicitly reify them as "primary sources", in the sense of "this is what a scholar in my position treats as the foundation to build on".  This view of "primary sources" will often include information like the classifications mentioned earlier, but the fact that the "material" was determined by a spectrogram thousands of years after an inscription was made can be represented in the primary source representation itself.

Therefore, in OCHRE, "scholarly knowledge" roughly refers to structured information that is added and interacted with *via* OCHRE and *by* a specific, identifiable *agent*.

Scholarly knowledge can take an infinite variety of forms, much like primary sources themselves, and so OCHRE again uses the `RDF framework <https://www.w3.org/TR/rdf11-concepts/>`_ for its representation.  Even moreso that with model signatures, the details of this representation will need to evolve with real-world experience.

-------------------------------------
Additional resources being considered
-------------------------------------

There are several existing standards being considered for OCHRE's various representational needs: the `PROV ontology <https://www.w3.org/TR/2013/REC-prov-o-20130430/>`_ for describing the provenance of primary sources, models, and annotations

.. _scripts:

=================
The OCHRE Scripts
=================

.. _primary_sources_script:

---------------
Primary sources
---------------

The general pattern for converting a non-RDF document is: as a format is parsed, certain "events" fire, each of which is an opportunity to generate RDF triples based on the event and the current location in the document.

Each event indicates what has just been parsed by sending a *tag*, *content*, and a dictionary of *attributes* (only *tag* is certain to have a value).  The particular tags and attributes will be specific to the format and data.  For instance, the event that fires for a cell in a CSV file in the column "day" with value "Monday" would send the tag "cell", the content "Monday", and the attribute dictionary::

  {"id" : "day"}

Along with the tag and attributes, the event sends its *location*, which for most formats is the list of "parent" events the current event is happening under.  If the above event was happening while processing the 22nd row of a file called "some_file.csv", the location might be (ignore for the moment the "uid" entries)::

  [
    {"tag" : "table", "content" : "", "attributes" : {"id" : "some_file.csv"}, "uid" : "43k2"},
    {"tag" : "row", "content" : "", "attributes" : {"id" : "22"}, "uid" : "213j"}
  ]

No matter the format (CSV, XML, etc), events have the same structure, and in fact the event just described might be this JSON object::

  {
    "tag" : "cell",
    "attributes" : {"id" : "day", "value" : "Monday"},
    "location" : [
      {"tag" : "table", "attributes" : {"id" : "some_file.csv"}, "uid" : "43k2"},
      {"tag" : "row", "attributes" : {"id" : "22"}, "uid" : "213j"}
    ],
    "uid" : "t98f"
  }
  
Again, the possible values for *tag* will depend on the format (HTML won't ever have a "row" tag, but might have "div", "body", etc), as will the *attributes* dictionary.

The goal is to decide what RDF triples to generate when seeing an event.  This involves specifying rules that 1) can be determined if they match the event, and 2) describe the RDF triple(s) to create from it.  Here is an example of a match portion::

  {
    "tag" : ["cell"],
    "attributes" : {"id" : ["day"]}
  }

Note how it constrains the tag and the attribute "id" by giving a list of acceptable values.
  
Here is an example of a creation portion with some placeholders for readability, that creates the two triples (S, P1, O1) and (S, P2, O2) when its rule matches::
    
  {
    "subject" : S,
    "predicate_objects" : [
      {
        "predicate" : P1,
	"object" : O1
      },
      {
        "predicate" : P2,
	"object" : O2
      }
    ]
  }
    
The placeholders are a bit more interesting: they tell OCHRE how to create an RDF node based on the event.  Here is an example that creates an RDF integer literal node that doesn't depend at all on the event::

  {
    "type" : "literal",
    "datatype" : "integer",
    "value" : "27"
  }

Here is an example that also creates an integer literal node, but based on the event::

  {
    "type" : "literal",
    "datatype" : "integer",
    "value" : "{content}"
  }

In the CSV example, if the rule were matching rows, this would correspond to the row number.  This curly-braces interpolation can also be used to refer to attributes and locations in the event, and mixed arbitrarily with bare strings, allowing the extraction of fairly sophisticated patterns.

Here is an example that creates a URI node, directly specifying the Wikidata entry for "photograph"::

  {
    "type" : "uri",
    "value" : "wd:Q125191"
  }

Importantly, most entities in a primary source will not have a clear corresponding entity in Wikidata (e.g. there may be a long list of photos, so the above example is useful for saying "this is an instance of a photo", but not for referring to *this* or *that* specific photo).  To handle this, every time an event occurs, OCHRE creates a *unique identifier* based on the event.  This unique identifier is the "uid" seen in the full event example above, and can be interpolated as-needed to derive unique URIs.  For instance::

  {
    "type" : "uri",
    "value" : "ochre:{uid}"
  }

is an entity in the OCHRE namespace corresponding to the particular event being processed.

Finally, OCHRE keeps track of the sequential number of each tag value within one tier of the input, and this number can be interpolated with "index".  For example, if the input involves processing sentences, each of which are a sequence of words, the string "{index}" within a word-rule will give the current word's number within its sentence, starting from 0.

^^^^^^^^^
Materials
^^^^^^^^^

The mechanisms described above are for generating RDF.  There is also the need to connect parts of RDF to *materials*, larger files that don't belong directly in the RDF graph, such as JPGs, audio recordings, and long documents.  To accomplish this, there is special information that can be added to an entry in a "predicate_object" list::

  {
    "predicate" : P,
    "object" : O,
    "file" : "path/some_file_{attributes['name']}.jpg",
    "file_type" : "image/jpg"
  }

When the *pyochre.primary_sources* script encounters a "file" like this, it looks for it on the local filesystem.  If found, it creates a unique identifier *I* based on the file's contents, and adds an additional RDF triple that links it to the object in the predicate_object rule (roughly, (O, hasMaterialId, I)) indicating "the entity O has an associated file identified with the id I".  Then, after OCHRE creates the RDF graph, it also uploads all such files in the appropriate fashion.
  
.. _machine_learning_script:

----------------
Machine learning
----------------

While the ultimate aim is for OCHRE to employ and generate complex models, there are already several simple types of models that can be incorporated via the *pyochre.machine_learning* script.  Ultimately, all models are transformed into `MAR archives <https://github.com/pytorch/serve/tree/master/model-archiver#artifact-details>`_, so other than the case of `Existing MAR archives`_, these situations are essentially different ways of *building* such an archive for a particular type of model.

^^^^^^^^^^^^^^^^^^^^^
Existing MAR archives
^^^^^^^^^^^^^^^^^^^^^

The simplest scenario::

  $ python -m pyochre.machine_learning create --mar_url https://torchserve.pytorch.org/mar_files/maskrcnn.mar --name "Object detection" --signature_file https://github.com/comp-int-hum/ochre-python/raw/main/examples/object_detection_signature.ttl

^^^^^^^^^^^^
Topic models
^^^^^^^^^^^^

^^^^^^^^^^^^^^^^^^
Huggingface models
^^^^^^^^^^^^^^^^^^

^^^^^^^^^^^^^
Custom models
^^^^^^^^^^^^^

.. _scholarly_knowledge_script:

-------------------
Scholarly knowledge
-------------------

.. _server_script:

------
Server
------

The package also contains the server side of OCHRE under the `pyochre.server` submodule.  When invoked as a script, it functions in most ways as a standard [Django](https://docs.djangoproject.com/en/4.1/) project's `manage.py` script::

  $ python -m pyochre.server --help

The database for the server can be initialized and initial user created by running::

  $ python -m pyochre.server migrate
  $ python -m pyochre.server createcachetable
  $ python -m pyochre.server collectstatic
  $ python -m pyochre.server shell_plus
  >> u = User.objects.create(username="joe", email="joe@somewhere.net", is_staff=True, is_superuser=True)
  >> u.set_password("CHANGE_ME")
  >> u.save()

Finally, start the server with::
  
  $ python -m pyochre.server runserver

At this point you should be able to browse to http://localhost:8000 and interact with the site.  Note that it will only be accessible on the local computer and this is by design: it is running without encryption, and using infrastructure that won't scale well and doesn't implement some important functionality.

.. _advanced_topics:

===============
Advanced topics
===============

--------------------------------------
Converting a new primary source format
--------------------------------------

---------------------------------------
Running a full "production"-like server
---------------------------------------

To run a full-functioning (though resource-constrained) OCHRE server on your personal computer you'll need to take a few more steps than the simple procedure described in the Server_ section.

First, install either `Docker <https://www.docker.com/>`_ or `Podman <https://podman.io/>`_, depending on what's available or easiest for your operating system.  In what follows, substitute "docker" for "podman" if you installed the former.

Second, start containers for the Jena RDF database and the Redis cache::

  $ podman run -d --rm --name jena -p 3030:3030 -e ADMIN_PASSWORD=CHANGE_ME docker.io/stain/jena-fuseki
  $ podman run -d --rm --name redis -p 6379:6379 docker.io/library/redis

Third, the Celery execution server and Torchserve model server each need to run alongside the OCHRE server.  The simplest way to accomplish this is to open two more terminals, navigate to the virtual environment directory where OCHRE is installed, run::

  $ source local/bin/activate

to enter the same virtual environment as the OCHRE package, and then run the following commands, one in each terminal::

  $ celery -A pyochre.server.ochre worker -l DEBUG
  $ torchserve --model-store ~/ochre/models/ --foreground --no-config-snapshots

At this point, with the two containers running (can be verified with `podman ps`), and Celery and TorchServe running in separate terminals, running::

  $ USE_JENA=True USE_TORCHSERVE=True python -m pyochre.server runserver

Should start the OCHRE server, and the site should work near-identically to when it's officially deployed.

