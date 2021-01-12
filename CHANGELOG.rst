..  Titling
    ##++::==~~--''``

.. This is a reStructuredText file.

Change Log
::::::::::

0.13.0
======

* Introduce Record type for storing Drama history.
* When a Drama is generating dialogue, set a class on the blockquote according to the most recent method call.

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
