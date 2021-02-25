Catchphrase
:::::::::::

Catchphrase provides software components to build
parser-based interactive fiction for the web.

Catchphrase is a Python library, and part of the `Turberfield` namespace.

For a demonstration of such a project, see the repository `tea_and_sympathy`_.
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

Drama objects are responsible for the game logic of your story.
Any calculations, computations and state transitions get done there.

I recommend the following techniques for organising your Drama code:

* Write unit tests for the dramas in your story, to drive out the bugs in your story logic.
* Partition your code into loosely-coupled modules, allowing you to share and re-use that logic.
* Use Python multiple inheritance to layer story-specific behaviour on top of mundane mechanics.

Dramas work by implementing a generator method for a group of semantically similar
free-text commands. Each method declares the syntax of those commands in its docstring.

The responsibility of a Drama method is also to yield strings of dialogue.
You splice these into the main narrative dialogue of your story.

Drama methods can add or discard themselves or other methods from active duty.
In this way complex scenarios can be achieved while minimising the potential for unplanned
behaviour in game logic.

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
.. _tea_and_sympathy: https://github.com/tundish/tea_and_sympathy
