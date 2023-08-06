# The OCHRE web frontend

OCHRE is built on top of the Django Rest Framework, which ensures consistency across the client library, the REST API, and the web frontend described in this document.  To avoid chasing the long tail of UX development, the web frontend aims for simplicity and uniformity, with the assumption that fancier, bespoke websites will be developed independently for specific projects using the REST API.  Here, we describe the basic structures and mechanisms that the OCHRE frontend operates with, particularly the "interactive" aspects.

## The characteristic layout

### Accordions and tabs

Almost every substantial part of the frontend is organized as vertical *accordions*.  If an entry in an accordion has several different facets to it, these may be broken up into horizontal *tabs*.  Accordions can be nested, with each level corresponding to things of the same type: for instance, an accordion might have an entry for each dataset, with each entry an accordion with the models trained on the respective dataset.  And each model might have a tab for interacting with it, another to see information on its parameters, and so forth.

### Performing actions

Again, an accordion corresponds to a particular type of object (data sets, models, users, annotations, etc).  If you are logged into OCHRE and have sufficient permissions, some accordions will also have icons on the righthand side.  These each open a pop-up to take some action:

- a plus: create a new instance of the sort of object the accordion holds
- a pen and pad: edit this object
- a lock: modify the permissions of this object
- a trash bin: delete this object
- a document: add/edit human-readable information about this location

## Top-level pages

The frontend has the following top-level pages:

- About
- People
- Research
- Wiki
- Interaction

## Tracking the hierarchy of pages and lazy rendering

