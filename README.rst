<<<<<<< Updated upstream
===========================
automojo-interop-ext-tasker
===========================

Automation Mojo - Tasker Interop Extensions

Overview
========
automojo-interop-ext-tasker is a core component of the Automation Mojo technology stack. It provides robust, reusable foundation code designed to enable and orchestrate complex software automation tasks.

Installation
============
Using Poetry:

.. code-block:: bash

    poetry add automojo-interop-ext-tasker

Development
===========
This repository provides a standard Poetry environment.

1. Activate virtual environment:
   Run `poetry shell` and `poetry install`
2. Test Execution:
   Run `poetry run pytest`

References
==========
- `User Guide <userguide/userguide.rst>`
- `Coding Standards <userguide/10-00-coding-standards.rst>`
=======
===========================================
Automation Mojo Interop Extension: Tasker
===========================================

The ``automojo-interop-ext-tasker`` package is a tasker extension for the ``automojo-interop`` and ``automojo-landscaping`` frameworks. It adds the protocol, server, and client plumbing required to run distributed "tasking" work on remote nodes coordinated through a tasker daemon, and plugs into the host packages through the extension mechanism in ``automojo-extension``.

Highlights
==========

- Core tasking abstractions under ``interop/protocols/tasker/``: ``ITaskingSequencer``, ``TaskerController``, ``TaskerServer``, ``TaskerServerManager``, ``TaskerService``, ``TaskerDaemon``, ``TaskerSession``, ``TaskerNode``, and related event/scope/promise types.
- ``TaskerAspects`` object for behaviour control (retry, timeout, action pattern).
- Linux-specific subpackage for host-level integration.
- Tasker-aware client coordinator under ``landscaping/clients/taskers/`` so tasker nodes appear as first-class landscape resources.
- ``examples/`` hello-world tasking reference.

Repository Structure
====================

- ``development/`` - Runtime environment scripts.
- ``repository-setup/`` - Repository homing and setup scripts.
- ``source/packages/`` - Package source code.
- ``source/testroots/testbase/`` - TestBase test roots.
- ``source/examples/`` - Example tasking usage.
- ``userguide/`` - Standards, conventions, and documentation.

Environment Setup
=================

When working in a Codex container:

.. code-block:: bash

   ./development/setup-agent-container

For local development:

.. code-block:: bash

   ./repository-setup/rehome-repository
   ./development/setup-envrionment

Running Tests
=============

Activate the virtual environment:

.. code-block:: bash

   source .venv/bin/activate

Run the single-host test suite:

.. code-block:: bash

   testbase testing run --root source/testroots/testbase --includes=automojo.tests.singlehost --output=./.output

Standards and Conventions
=========================

- Naming conventions: ``userguide/10-02-naming-conventions.rst``
- Code organization: ``userguide/10-01-code-organization.rst``
- Coding standards: ``userguide/10-00-coding-standards.rst``

Additional Resources
====================

- User guide entry point: ``userguide/userguide.rst``
>>>>>>> Stashed changes
