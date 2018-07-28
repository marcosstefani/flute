import unittest
import os

import app_test
import model_test

loader = unittest.TestLoader()
suite  = unittest.TestSuite()

suite.addTests( loader.loadTestsFromModule( app_test ) )
suite.addTests( loader.loadTestsFromModule( model_test ) )

runner = unittest.TextTestRunner(verbosity=3)
result = runner.run(suite)