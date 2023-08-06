#####
OCHRE
#####

****************************************************
The Open Computational Humanities Research Ecosystem
****************************************************

The Open Computational Humanities Research Ecosystem (OCHRE) provides the server infrastructure and client library to experiment with complex machine learning and rich humanistic primary sources.

.. _installation:

============
Installation
============

This package can be installed via `pip`.  It's advisable to employ Python `virtual environments <https://docs.python.org/3/library/venv.html>`_ (here and in other situations).  If you will be using the package as a library in your own code, you might create a new directory and set it up by running something like the following::

  $ mkdir my_new_project
  $ cd my_new_project
  $ python3 -m venv local
  $ source local/bin/activate
  $ pip install git+https://github.com/comp-int-hum/ochre-python.git

If you're planning to edit the package code itself, you might check out the current version from the git repository and "live install" the package by running something like::

  $ git clone https://github.com/comp-int-hum/ochre-python.git
  $ cd ochre-python
  $ python3 -m venv local
  $ source local/bin/activate
  $ pip install -e .
  
In either case, run `deactivate` to exit the virtual environment, `source local/bin/acticate` to enter it again.

The package is designed to be fully functional without requiring significant effort, but by default doesn't include certain dependencies that are important for deploying a substantial server.  To install the more production-grade dependencies there are three extra options that can be included: `ldap`, `postgres`, and `torchserve`.  For instance, to include the full set of options, the command is::

  $ pip install git+https://github.com/comp-int-hum/ochre-python.git[ldap,postgres,torchserve]

Note that these options may require additional effort, such as non-Python dependencies that need to be installed independently.  For most situations, the simple package is the right choice.

.. _configuration:

=============
Configuration
=============

Most users will treat OCHRE as a way of interacting with an existing OCHRE server, so before it will function, OCHRE needs to be told how to connect to the server.  When OCHRE is invoked as a script, it looks in the current directory for a file named `env`.  Minimally, this file should contain the following settings::

  PROTOCOL=https
  HOSTNAME=cdh.jhu.edu
  PORT=8443
  USER=my_username
  PASSWORD=my_password

This would direct the script to connect to the OCHRE server at `https://cdh.jhu.edu:8441` as the user "my_username" and with password "my_password".  In fact, the `env` file can override any of the settings listed in the `env.py <https://github.com/comp-int-hum/ochre-python/blob/main/src/pyochre/env.py>`_ file, but these are the only settings needed unless you are running your own OCHRE server.

.. _command:

================
Command-line use
================

OCHRE can be interacted with from the command-line in fairly sophisticated ways.  The basic pattern for a command is "python -m pyochre NOUN VERB OPTIONS": using the "-h" option (help), you can explore the nouns (types of things on the OCHRE server) and verbs (ways of manipulating them)::

  $ python -m pyochre -h
  usage: python -m pyochre [-h]
                         {Slide,ResearchArtifact,Annotation,Query,PrimarySource,MachineLearningModel,User,Documentation}
  positional arguments:
  {Slide,ResearchArtifact,Annotation,Query,PrimarySource,MachineLearningModel,User,Documentation}

  options:
    -h, --help            show this help message and exit

So, the server can hold primary sources, annotations, machine learning models, etc.  To see how a primary source can be manipulated (its verbs), run::

  $ python -m pyochre PrimarySource -h
  usage: python -m pyochre PrimarySource [-h]
                                       {list,create,retrieve,update,partialUpdate,destroy,data,domain,clear,createHathiTrust}
                                       ...
				       
  positional arguments:
    {list,create,retrieve,update,partialUpdate,destroy,data,domain,clear,createHathiTrust}
      list
      create
      retrieve
      update
      partialUpdate
      destroy
      data
      domain
      clear
      createHathiTrust    Create a primary source from a HathiTrust collection file.
  
  options:
    -h, --help            show this help message and exit

You can see what arguments are needed to invoke a particular verb::

  $ python -m pyochre PrimarySource createHathiTrust -h
  usage: python -m pyochre PrimarySource createHathiTrust [-h] --name NAME --collection_file COLLECTION_FILE

  options:
    -h, --help            show this help message and exit
    --name NAME
    --collection_file COLLECTION_FILE
                          A collection CSV file downloaded from the HathiTrust interface

Finally, you can actually invoke the verb with appropriate arguments::

  $ python -m pyochre PrimarySource createHathiTrust --name "My primary source" --collection_file some_collection.csv
  
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

.. OCHRE has provisionally adopted the `MLSchema specification <http://ml-schema.github.io/documentation/ML%20Schema.html>`_ to describe models, though real-world experience will determine if it is sufficiently expressive.

Ideally, signatures are generated as models are assembled and trained.  In particular, OCHRE will be integrating the `Starcoder project <https://github.com/starcoder/starcoder-python>`_ to automatically generate, train, and reuse `graph neural networks <https://en.wikipedia.org/wiki/Graph_neural_network>`_ based on primary sources and scholarly knowledge, with signatures capturing the structural and semantic relationships.

^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Model signatures and input/output
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Inputs and outputs of an OCHRE model are RDF graphs that satisfy the respective signatures of the model.

A model's input signature is a canonical SPARQL query that produces appropriate graphs for its structure.  When invoked on a given input, the model may also be passed an initial SPARQL query to rewrite the input before the canonical query is applied, thus allowing for a great deal of flexibility.

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

Note that everything created on an OCHRE server has a *name* and a *creator* which, which together must be unique for the type of thing (primary source, model, etc).  When referring to a model just by name, OCHRE assumes you mean *your* model of that name, but it's also possible to specify another user, e.g. "--model_name 'Some model' --model_creator_name 'Sarah'".

.. _primary_sources_script:

---------------
Primary sources
---------------

^^^^
Data
^^^^

The general pattern for creating a new OCHRE primary source is to first convert data to XML (if it isn't already), and then define and apply an `XML stylesheet <https://www.w3.org/TR/1999/REC-xslt-19991116>`_ to convert the XML to RDF.  OCHRE can perform the first step for CSV and JSON.  The second step requires a basic understanding of XML stylesheets (often called "XSL" or "XSLT"), and considerable care in deciding how to connect information in the primary source to the growing `OCHRE ontology <https://github.com/comp-int-hum/ochre-python/blob/main/src/pyochre/data/ochre.ttl>`_.  Several examples of real-world stylesheets are available, such as `a JSON-based transformation of Chaucer <https://github.com/comp-int-hum/ochre-python/blob/main/examples/chaucer_transform.xml>`_ and `a CSV-based transformation of the Cuneiform Digital Library Initiative <https://github.com/comp-int-hum/ochre-python/blob/main/examples/cdli_transform.xml>`_.

^^^^^^^^^
Materials
^^^^^^^^^

The stylesheet generates RDF, but there is often the need to connect parts of RDF to *materials*: larger files that don't belong directly in the RDF graph, such as JPGs, audio recordings, and long-form documents.  To accomplish this, a stylesheet can use the "ochre:hasMaterialId" property.

When the *pyochre.primary_sources* script encounters an "ochre:hasMaterialId" property, it looks for its value on the local filesystem.  If found, it creates a unique identifier *I* based on the file's contents, uses that identifier as the property value, and uploads the file to OCHRE such that the identifier resolves to it.  If no such file is found on the local filesystem, the identifier is left as-is, or the property is removed entirely, depending on arguments to the script.

^^^^^^
Domain
^^^^^^

The final component in a primary source is a domain description that captures the structure of the data.  In most cases, this will be automatically derived from the data by enumerating the *types of entities* and the *properties* that occur between instances of them.

^^^^^^^
Queries
^^^^^^^

.. _machine_learning_script:

----------------
Machine learning
----------------

The ultimate aim is for OCHRE to generate and employ complex machine learning models.  There are several paths to adding a new model to an OCHRE server via the *pyochre.machine_learning* script.  Ultimately, all models are transformed into `MAR archives <https://github.com/pytorch/serve/tree/master/model-archiver#artifact-details>`_, which are then efficiently served from the `TorchServe <https://pytorch.org/serve/>`_ framework.

^^^^^^^^^^^^
Topic models
^^^^^^^^^^^^

Topic models can be created by specifying a `SPARQL query <https://www.w3.org/TR/2013/REC-sparql11-overview-20130321/>`_ that selects text, and potentially spatial and temporal information::

  $ python -m pyochre.machine_learning create --name "Chaucer topic model" topic_model --query_name "Chaucer query" --primary_source_name Chaucer --topic_count 10

The query may either have a `SELECT` statement of the form::

  SELECT ?doc_identifier WHERE
  
with `doc_identifier` indicating documents on the OCHRE server, or with a `SELECT` statement of the form::

  SELECT ?doc_number ?word ?title ?author ?temporal ?lat ?long WHERE

Only `doc_number` and `word` are required to have values (an integer and string, respectively).  If they have values, `title` and `author` should be strings, `temporal` should be an `xsd:dateTime`, and `lat` and `long` should be real numbers indicating a coordinate in the `WGS84` projection (typically the values of a `geo:lat` or `geo:long` property, respectively).
  
^^^^^^^^^^^^^^^^^^
Huggingface models
^^^^^^^^^^^^^^^^^^

Models on Huggingface are importable directly if they have a corresponding `pipeline <https://huggingface.co/docs/transformers/main_classes/pipelines>`_::

  $ python -m pyochre.machine_learning create --name "Speech transcriber" huggingface --huggingface_name openai/whisper-tiny.en

^^^^^^^^^^^^^^^^
StarCoder models
^^^^^^^^^^^^^^^^

The most ambitious approach is to create a model tailored to the structure of a particular primary source.

^^^^^^^^^^^^^^^^^^^^^
Existing MAR archives
^^^^^^^^^^^^^^^^^^^^^

The most flexible approach is to pass in the location of a pre-existing MAR file and a signature describing its input and output semantics::

  $ python -m pyochre.machine_learning create --mar_file https://torchserve.pytorch.org/mar_files/maskrcnn.mar --name "CNN object detection" --signature_file maskrcnn_signature.ttl

It's unlikely this is what you want, though: constructing a MAR file directly is challenging enough, without even considering the details of OCHRE compatibility!


.. _scholarly_knowledge_script:

-------------------
Scholarly knowledge
-------------------

.. _server_script:

------
Server
------

The package also contains the server side of OCHRE under the `pyochre.server` submodule.  When invoked as a script, it functions in most ways as a standard [Django](https://docs.djangoproject.com/en/4.2/) project's `manage.py` script::

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

------------------------------------
Handling a new primary source format
------------------------------------

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

  $ python -m pyochre.server runserver

Should start the OCHRE server, and the site should work near-identically to when it's officially deployed.

=================
Technical details
=================

--------------
Site structure
--------------

The OCHRE site is composed together dynamically as the user navigates, and this requires making sure that identifiers for different parts of a page are unique.  This is made more complex because the site is *lazy*, and generates each piece when it comes into view by requesting the corresponding HTML fragment from the API using HTMX.


-------
Caching
-------
