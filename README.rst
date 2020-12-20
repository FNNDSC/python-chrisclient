##################
python-chrisclient
##################

A python client for the ChRIS API.

.. image:: https://travis-ci.org/FNNDSC/python-chrisclient.svg?branch=master
    :target: https://travis-ci.org/FNNDSC/python-chrisclient

Quick Overview
--------------

This repository contains various python scripts and modules that provide a rich client experience in interacting with a ``CUBE`` backend instance. Interaction is typically either via the command line interface (CLI) or directly in python using relevant modules.

Overview
--------

At time of writing (late 2020), two scripts/modules are in production:

- a plugin search utility
- a plugin run schedule utility

Installation
------------

Use the ``PyPI``, Luke!

.. code-block:: bash

   pip install -U python-chrisclient

Search
------

The plugin space (actual plugin data and scheduled/run plugins) in a ``CUBE`` instance can be searched using the ``chrispl-search`` script. This returns information either in tabular text form or a richer JSON payload. The ``search.py`` module is of course suitable for inclusion into other scripts/projects.

Examples
~~~~~~~~

Find the plugin ``ID`` given a ``name`` substring search term
=============================================================

A common use case of the search script is to return the plugin ID for a plugin name substring:

.. code-block:: bash

    chrispl-search --for id,name --using name=surfer --CUBE '
    {
                "protocol":     "http",
                "port":         "8000",
                "address":      "%HOSTIP",
                "user":         "chris",
                "password":     "chris1234",
    }
    '

(note the above ``CUBE`` specification assumes an instance on the ``localhost``. The special construction, ``%HOSTIP`` (if specified) will be replaced by the actual IP of the host machine. This construct is useful in some cases where the string ``localhost`` might have issues on proxied networks.)

will return the plugin ID and complete name for all plugins that have a substring of ``surfer`` in their ``name``:

.. code-block:: console

    (searchSubstr:name=surfer)  id 12  name pl-freesurfer_pp
    (searchSubstr:name=surfer)  id 11  name pl-fastsurfer_inference

Find a list of all plugins registered to a ``CUBE`` instance
=============================================================

.. code-block:: bash

    chrispl-search --for name,id,type --using name='' --CUBE '
    {
                "protocol":     "http",
                "port":         "8000",
                "address":      "%HOSTIP",
                "user":         "chris",
                "password":     "chris1234",
    }
    '

will return

..code-block:: bash

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

The actual space of executed plugin instances can also be searched. For instance, find the *instance IDs* of all plugins with name substring ``surfer`` and list their ``status``. Note that to search the *instance* space, the ``--searchURL plugins/instances`` is specified:

..code-block:: bash

    chrispl-search --for id,status,plugin_name --using plugin_name=surfer --searchURL plugins/instances 

which can return something like:

..code-block:: bash

    (searchSubstr:plugin_name=surfer)  id 12 status finishedSuccessfully  plugin_name pl-freesurfer_pp
    (searchSubstr:plugin_name=surfer)  id 11 status finishedSuccessfully  plugin_name pl-freesurfer_pp
    (searchSubstr:plugin_name=surfer)  id 10 status finishedSuccessfully  plugin_name pl-freesurfer_pp
    (searchSubstr:plugin_name=surfer)  id 9  status finishedSuccessfully  plugin_name pl-freesurfer_pp

Ends.

