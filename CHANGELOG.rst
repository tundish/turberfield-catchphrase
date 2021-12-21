..  Titling
    ##++::==~~--''``

.. This is a reStructuredText file.

Change Log
::::::::::

0.25.0
======

* Add rendering for video FX.

0.24.0
======

* Presenter functions become class methods.
* Renderer functions become class methods.
* Create render method for video elements.
* Repin to turberfield-dialogue 0.39.0.

0.23.0
======

* relax requirement for Folder object when building a `Presenter`.

0.22.0
======

* Update dependency pinning.

0.21.0
======

* Store memories in reverse order.
* Allow positional arguments to `build_presenter`.
* No longer update `facts` with command history.
* Implement late-bound attribute access from annotations.
* Use `group_by_type` utility function.
* Always set state from a memory.

0.20.0
======

* Refactor Mediator class
* Refactor Presenter class
* Retrieve casting from dialogue and pass in as Mediator parameter.
* Record tuples store methods by name in history.

0.19.0
======

* Align with turberfield-dialogue 0.32.0

0.18.0
======

* Relax dependency back to Python 3.8
* Fix for changes in Condition from turberfield-dialogue 0.31.0

0.17.0
======

* Revised treatment of conditionals in `Presenter.animate`.
  They are now combined with an implicit *and* condition, where previously it was *or*.

0.16.0
======

* Fix a bug in escaping tooltip in rendered controls.
* Update links to TaS after repo name change.
* `Drama.build` now takes an optional `ensemble` parameter.
* `build_presenter` returns a single value. The Presenter object has its index set as an attribute.

0.15.0
======

* Resite Action and Parameter for use by a Story.
* Refactor `render_animated_frame_to_html`.

0.14.0
======

* Update pinned dependency on turberfield-dialogue.
* Pass keyword arguments through build_presenter in order to control drama dialogue.
* `build_from_text` method now stores text in the returned Presenter object.
* Drama stores history in reverse order to allow access from condition directives.
* Simplified several Drama methods.

0.13.0
======

* Introduce Record type for storing Drama history.
* When a Drama is generating dialogue, set a class on the blockquote according to the most recent method call.
* Add `build_presenter` factory method to create a Presenter.

0.12.0
======

* `Drama.match` yields the original text when a command is unmatched.

0.11.0
======

* Add `dwell` property to Presenter.
* Add `pause` property to Presenter.

0.10.0
======

* Refactor to `Drama.write_dialogue`.
* Resited some methods from Presenter to Drama.
* Better unit testing of Drama methods.
* Flake fixes

0.9.0
=====

* Moved `build_dialogue` to Drama class.
* Added `safe_substitute` method.

0.8.0
=====

* Enable passing prompt into render.

0.7.0
=====

* Rendering now better supports grid layout.

0.6.0
=====

* Refactored Performer build functions.
* Add dialogue metadata to publisher object.

0.5.0
=====

* Some refactoring to the render module.
* Fix a bug in calculating page media refresh time.
* Add base style `catchphrase.css`.

0.4.0
=====

* Numerous fixes in step with Tea and Sympathy.
* Added the `render` module.
* First release to PyPI.

0.3.0
=====

* Added `Presenter.build_shots`.

0.2.0
=====

* `Presenter` now has an `allows` method.
   Like that of `Performer`, but more capable.

0.1.0
======

* First sketchy release.
