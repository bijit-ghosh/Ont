"""Execute selected unittest scenarios with machine-readable counts."""
import json
import sys
import unittest

suite=unittest.TestSuite()
for name in sys.argv[1:]:suite.addTests(unittest.defaultTestLoader.loadTestsFromName(name))
result=unittest.TextTestRunner(verbosity=2).run(suite)
summary={'tests':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'skipped':len(result.skipped),'expected_failures':len(result.expectedFailures),'unexpected_successes':len(result.unexpectedSuccesses)}
print('ONT_EVAL_RESULT='+json.dumps(summary))
raise SystemExit(0 if result.wasSuccessful() and result.testsRun>0 and not result.skipped and not result.expectedFailures else 1)
