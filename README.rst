##################
python-chrisclient
##################

A python client for the ChRIS API.

.. image:: https://travis-ci.org/FNNDSC/python-chrisclient.svg?branch=master
    :target: https://travis-ci.org/FNNDSC/python-chrisclient

Quick Overview
--------------

This repository contains various python scripts and modules that provide a rich client experience for interacting with a ``CUBE`` backend instance. Interaction is typically either via the command line interface (CLI) or directly in python using relevant modules.

Overview
--------

At time of writing (late 2020), two scripts/modules are in production:

- a plugin search utility
- a plugin run schedule utility

Note that in the instructions below, the details of a ``CUBE`` instance are passed in a JSON structure using the ``--onCUBE`` flag. In many cases you might only want to pass the address of a ``CUBE`` instance. For this purpose, the ``--onCUBEaddress`` can be used that will only set the address and keep other default information intact.

Installation
------------

Use the ``PyPI``, Luke!

.. code-block:: bash

   pip install -U python-chrisclient

Search
------

The plugin space (plugin ``id`` and plugin ``instance id`` ) in a ``CUBE`` instance can be searched using the ``chrispl-search`` script. This returns information either in tabular text form or a richer JSON payload. The ``search.py`` module is of course suitable for inclusion into other scripts/projects.

Search Examples
~~~~~~~~~~~~~~~

Find the plugin ``ID`` given a ``name`` substring search term
=============================================================

A common use case of the search script is to return the plugin ID for a plugin name substring:

.. code-block:: bash

    chrispl-search  --for id,name                   \
                    --using name=surfer             \
                    --onCUBE '{
                        "protocol":     "http",
                        "port":         "8000",
                        "address":      "%HOSTIP",
                        "user":         "chris",
                        "password":     "chris1234"}'

(note the above ``onCUBE`` specification assumes an instance on the ``localhost``. The special construction, ``%HOSTIP`` (if specified) will be replaced by the actual IP of the host machine. This construct is useful in some cases where the string ``localhost`` might have issues on proxied networks.)

The above call will return the plugin ``id`` as well as the complete name for all plugins that have a substring of ``surfer`` in their ``name``:

.. code-block:: console

    (searchSubstr:name=surfer)  id 12  name pl-freesurfer_pp
    (searchSubstr:name=surfer)  id 11  name pl-fastsurfer_inference

Find a list of all plugins registered to a ``CUBE`` instance
=============================================================

.. code-block:: bash

    chrispl-search  --for name,id,type          \
                    --using name=''             \
                    --onCUBE '{
                        "protocol":     "http",
                        "port":         "8000",
                        "address":      "%HOSTIP",
                        "user":         "chris",
                        "password":     "chris1234"}'

will return

.. code-block:: console

    (searchSubstr:name=)      name pl-pfdo_med2img           id 17  type ds
    (searchSubstr:name=)      name pl-pfdo_mgz2img           id 16  type ds
    (searchSubstr:name=)      name pl-mgz2lut_report         id 15  type ds
    (searchSubstr:name=)      name pl-z2labelmap             id 13  type ds
    (searchSubstr:name=)      name pl-freesurfer_pp          id 12  type ds
    (searchSubstr:name=)      name pl-fastsurfer_inference   id 11  type ds
    (searchSubstr:name=)      name pl-fshack                 id 10  type ds
    (searchSubstr:name=)      name pl-mpcs                   id 9   type ds
    (searchSubstr:name=)      name pl-pfdicom_tagsub         id 8   type ds
    (searchSubstr:name=)      name pl-pfdicom_tagextract     id 7   type ds
    (searchSubstr:name=)      name pl-s3push                 id 6   type ds
    (searchSubstr:name=)      name pl-dsdircopy              id 5   type ds
    (searchSubstr:name=)      name pl-s3retrieve             id 3   type ds
    (searchSubstr:name=)      name pl-simpledsapp            id 2   type ds
    (searchSubstr:name=)      name pl-lungct                 id 18  type fs
    (searchSubstr:name=)      name pl-mri10yr06mo01da_normal id 14  type fs
    (searchSubstr:name=)      name pl-dircopy                id 4   type fs
    (searchSubstr:name=)      name pl-simplefsapp            id 1   type fs

Search plugin *instances*
==========================

The actual space of executed plugin instances can also be searched. For instance, find the *instance IDs* of all plugins with name substring ``surfer`` and list their ``status``. Note that to search the *instance* space, the ``--across plugininstances`` is specified:

.. code-block:: bash

    chrispl-search --for id,status,plugin_name          \
                   --using plugin_name=surfer           \
                   --across plugininstances             \
                   --onCUBE '{
                        "protocol":     "http",
                        "port":         "8000",
                        "address":      "%HOSTIP",
                        "user":         "chris",
                        "password":     "chris1234"}'

which will return something similar to:

.. code-block:: console

    (searchSubstr:plugin_name=surfer)  id 12 status finishedSuccessfully  plugin_name pl-freesurfer_pp
    (searchSubstr:plugin_name=surfer)  id 11 status finishedSuccessfully  plugin_name pl-freesurfer_pp
    (searchSubstr:plugin_name=surfer)  id 10 status finishedSuccessfully  plugin_name pl-freesurfer_pp
    (searchSubstr:plugin_name=surfer)  id 9  status finishedSuccessfully  plugin_name pl-freesurfer_pp

Search plugin *files*
=====================

The actual list of file data associated with the outputs of a plugin instance can also be searched. For instance, find the names of files by searching for the *fname* across ``files`` using ``plugin_inst_id`` of ``2``:

.. code-block:: bash

    chrispl-search --for fname                              \
                   --using plugin_inst_id=2                 \
                   --across files                           \
                   --onCUBEaddress megalodon.local

which will return something similar to:

.. code-block:: console

    (searchSubstr:plugin_name=surfer)  id 12 status finishedSuccessfully  plugin_name pl-freesurfer_pp
    (searchSubstr:plugin_name=surfer)  id 11 status finishedSuccessfully  plugin_name pl-freesurfer_pp
    (searchSubstr:plugin_name=surfer)  id 10 status finishedSuccessfully  plugin_name pl-freesurfer_pp
    (searchSubstr:plugin_name=surfer)  id 9  status finishedSuccessfully  plugin_name pl-freesurfer_pp


Run
---

Plugins can be run/scheduled on a CUBE instance using the ``chrispl-run`` script. The CLI parameters are broadly similar to ``chrispl-search`` with some semantic changes more pertinent to the run call -- the ``for`` search is fixed to the plugin ``id`` and the search ``--pluginSpec`` becomes the ``--using`` CLI.

Run Examples
~~~~~~~~~~~~

Run an FS plugin, ``pl-mri10yr06mo01da_normal``
===============================================

.. code-block:: console

    chrispl-run --plugin name=pl-mri10yr06mo01da_normal \
                --onCUBE '{
                    "protocol":     "http",
                    "port":         "8000",
                    "address":      "%HOSTIP",
                    "user":         "chris",
                    "password":     "chris1234"}'

This plugin does not require any specific CLI args when run in the default state. Once posted to CUBE, a string is returned to the shell:

.. code-block:: console

    (name=pl-mri10yr06mo01da_normal) id 14

Indicating that the plugin instance ID of the plugin in ``CUBE`` is ``14`` (for example).

For convenience, let's set:

.. code-block:: console

    CUBE='{
        "protocol":     "http",
        "port":         "8000",
        "address":      "%HOSTIP",
        "user":         "chris",
        "password":     "chris1234"
    }'

This return construct lends itself easily to scripting:

.. code-block:: console

    ROOTNODE=$(./chrispl-run --plugin name=pl-mri10yr06mo01da_normal --onCUBE "$CUBE" | awk '{print $3}')

or with some formatting:

.. code-block:: console

    ROOTNODE=$(
        chrispl-run --plugin name=pl-mri10yr06mo01da_normal     \
                    --onCUBE="$CUBE"                            |
                         awk '{print $3}'
    )

Run a DS plugin, ``pl-freesurfer_pp``, that builds on the previous node
=======================================================================

In this manner, a workflow can be constructed. First construct the arguments for the next plugin:

.. code-block:: console

    ARGS="                              \
    --ageSpec=10-06-01;                 \
    --copySpec=sag,cor,tra,stats,3D;    \
    --previous_id=$ROOTNODE             \
    "

and now schedule the run:

.. code-block:: console

    chrispl-run --plugin name="pl-freesurfer_pp"    \
                --args="$ARGS"                      \
                --onCUBE="$CUBE"

which will return:

.. code-block:: console

    (name=pl-freesurfer_pp)        id 19

As before, this can be captured and used for subsequent chaining:

.. code-block:: console

    FSNODE=$(
        chrispl-run --plugin name=pl-freesurfer_pp  \
                    --args="$ARGS"                  \
                    --onCUBE="$CUBE"                |
                         awk '{print $3}'
    )

Additional Reading
------------------

Consult the ChRIS_docs ``workflow`` directory for examples of workflows built using these tools.

*-30-*


