# Inner function
To understand how sys.meta_path works, you must understand the exact sequence of events Python executes when it encounters an import statement. It operates as a strict pipeline of delegations.

Here is the mechanical breakdown of that pipeline and how the interception occurs.

- The Cache (sys.modules)
When you execute import flask, Python first checks sys.modules. This is a dictionary caching all previously imported modules.

If flask is in the cache, Python uses it immediately.

If it is not, Python moves to the resolution phase.

- The Resolution Phase (sys.meta_path)
If the module is not cached, Python consults sys.meta_path. This is a simple list of "Finder" objects. By default, Python populates this list with three built-in Finders:

BuiltinImporter: Checks if the module is built into the CPython interpreter (e.g., sys, time).

FrozenImporter: Checks for frozen modules (compiled bytecode bundled with the interpreter).

PathFinder: The standard finder that scans your hard drive using the directories listed in sys.path (where site-packages lives).

Python asks each Finder in sequence: "Can you find 'flask'?"

- Finders and Specs
A Finder does not execute or load the module's code; it acts purely as a scout. When queried, a Finder must return one of two things:

None: This means "I don't know where this is." Python moves to the next Finder in the list.

A ModuleSpec (Spec): This is the blueprint. It contains the exact file path and designates a "Loader" object responsible for actually reading the file and executing the Python code.

In a standard Flask import, the first two Finders return None. The PathFinder successfully locates Flask in your site-packages, returns the Spec, and Python halts the search and loads the code.

- The Interception Mechanism
The vulnerability (or flexibility) of this system is that sys.meta_path is a mutable list.

By defining a custom Finder class and using sys.meta_path.insert(0, RedirectFinder), you place your scout at the absolute front of the line.

Python asks your RedirectFinder first: "Can you find 'flask'?"

Instead of searching the hard drive, your Finder programmatically generates and returns a Spec pointing directly to my_fake_flask.py.

Because your Finder returned a valid Spec, Python halts the search. It never reaches the PathFinder and never scans sys.path. It immediately executes your fake file, fully convinced it has imported the real Flask.

Below is an interactive simulation demonstrating the execution flow of a standard import versus an intercepted import.

