Catchphrase
:::::::::::

Catchphrase provides software components to build
parser-based interactive fiction for the web.

Catchphrase is a Python library, and part of the `Turberfield` namespace.

For a demonstration of such a project, see the repository `tea-and-sympathy`_.
You are free to download and experiment with that example.

This framework makes heavy use of the turberfield-dialogue_ library.
The documentation is at an early stage.

Framework
+++++++++

* A drama_ class to encapsulate game logic.
* A parser_ system which maps text phrases to drama methods and parameters.
* A presenter_ class which combines static dialogue with drama output.
* Renderer_ functions to animate the output in HTML or plain text.

Drama
=====

Drama objects dynamically generate dialogue.

Subclasses will override these methods:

* build
* interpret

Drama methods must declare by annotation the types of their keyword parameters.
They must also provide a docstring to define the format of the text commands which apply to them.

Parser
======

The parser module provides functions to help drama objects respond to text input.

The CommandParser class interrogates drama methods to determine what parameters they require.
Based on this information, and the declaration made in method docstrings, the parser generates
all commands understood in the current context of the drama.

Presenter
=========

The Presenter combines static dialogue with the generated output from a Drama object.

* Prepare a turberfield-dialogue_ Folder object.
* Create a Presenter from the Folder and the drama output.
* Call the `animate` method to generate web frames ready for rendering.

Renderer
========

The Renderer is a namespace for functions which generate HTML5 elements from Presenter frames.
There is also support for plain text output.

.. _turberfield-dialogue: https://github.com/tundish/turberfield-dialogue
.. _tea-and-sympathy: https://github.com/tundish/tea-and-sympathy
