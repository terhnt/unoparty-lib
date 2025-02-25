# Security Issues

* If you’ve identified a potential **security issue**, please contact us
  directly at <support@unoparty.io>.


# Reporting an Issue

* Check to see if the issue has already been reported.

* Run with verbose logging and paste the relevant log output.

* List the exact version/commit being run, as well as the platform the software
  is running on.


# Making a Pull Request

* Make (almost) all pull requests against the `develop` branch.

* All original code should follow [PEP8](https://www.python.org/dev/peps/pep-0008/).

* Code contributions should be well‐commented.

* Commit messages should be neatly formatted and descriptive, with a summary line.

* Commits should be organized into logical units.

* Verify that your fork passes all tests. The test suite is invoked with `$
  py.test-3.4` in the `unopartylib` directory of the repository. The
`ethereum-serpent` dependency is satisfied by running `setup.py install
--with-serpent` and `sudo pip2 install ethereum-serpent==1.6.7`.
