.. _contributing-to-documentation:

=================================
Contributing to the Documentation
=================================

One of the best ways that you can help is by improving this documentation.  Here we explain
the documentation system, how to build the documents locally, and how to submit your changes.


Documentation system overview
=============================

The documentation source files are `stored in Github <https://github.com/Onikore/dronekit2/tree/main/docs>`_.
The content is written in plain-text files (file-extension :file:`.rst`) using
`reStructuredText <https://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html>`_ markup, and is compiled into HTML using the
`Sphinx Documentation Generator <https://www.sphinx-doc.org/>`_, themed with `furo <https://pradyunsg.me/furo/>`_.

Submitting changes
==================

The process and requirements for submitting changes to the documentation are **the same** as when 
:ref:`contributing to the source code <contributing_api>`. 

As when submitting source code you should fork the main project Github repository and 
contribute changes back to the project using pull requests. The changes should be tested
locally (by :ref:`building the docs <contributing_building_docs>`) before being submitted.

See :ref:`contributing_api` for more information. 

.. _contributing_building_docs:

Building the docs
=================

Building the documentation just needs a Python 3.9+ environment - no VM required:

* `Fork the dronekit2 repo <https://github.com/Onikore/dronekit2>`_
* Clone your fork of the Github repository anywhere on your machine: ::

    git clone https://github.com/YOUR-USERNAME/dronekit2.git

* From the root of your clone, install the package with its ``docs`` extra
  (Sphinx and the furo theme) and build the HTML: ::

    cd dronekit2
    pip install -e ".[docs]"
    cd docs
    make html

  The files will be built by :program:`Sphinx`, and will appear in
  :file:`<clone-path>/dronekit2/docs/_build/html/`. To preview, simply open them in a
  Web browser (start at :file:`index.html`).

* Repeat ``make html`` as many times as needed while editing. To start from a clean build:
  ::

    make clean
    make html

.. note::

    On Windows without ``make`` available, use Sphinx directly instead of the Makefile: ::

        sphinx-build -b html . _build/html

    (run from inside the ``docs`` directory).


Style guide
===========

.. tip:: 

    This guide is evolving. The most important guidance we can give is 
    to *copy the existing style of reference, guide and example material*!


#. Use US English for spelling.

#. Use emphasis sparingly (italic, bold, underline). 

#. Use `Sphinx semantic markup <https://www.sphinx-doc.org/en/master/usage/restructuredtext/roles.html>`_ to mark up *types* of text (key-presses, file names etc.)

#. Use double backticks (``) around ``inline code`` items.