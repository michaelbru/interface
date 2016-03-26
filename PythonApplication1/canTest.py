import unittest
import sys 
from CanOpenImpl import *

class ProblemCanSet(unittest.TestCase):
    def setUp(self):
        pass

    def testNewCanImpl(self):
        can = CanOpenKvaserImpl()




if __name__=='__main__':
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ProblemCanSet))
    unittest.TextTestRunner(verbosity=2, stream=sys.stdout).run(suite) 