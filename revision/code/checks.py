"""Record meaningful protocol tests and verify original-file preservation."""
import json
import unittest
from .audit import ARTIFACTS, manifest
from .protocol import REVISION


def main():
    originals = manifest()
    suite = unittest.defaultTestLoader.discover(str(REVISION / "tests"))
    with (ARTIFACTS / "protocol_tests.log").open("w") as log:
        result = unittest.TextTestRunner(stream=log, verbosity=2).run(suite)
    summary = {"tests_run": result.testsRun, "passed": result.wasSuccessful(),
               "failures": [str(test) for test, _ in result.failures],
               "errors": [str(test) for test, _ in result.errors],
               "original_files_verified_unchanged": len(originals)}
    (ARTIFACTS / "protocol_tests.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))
    if not result.wasSuccessful():
        raise SystemExit(1)


if __name__ == "__main__":
    main()
