import sys
sys.path.append('..')

import os
import unittest
from flute.util import current_dir

from flute import mvcs, new_model, create_model

class TestApp( unittest.TestCase ):

    def test_initialize( self ):
        model = new_model('Model')
        mvcs(model)

        self.assertTrue( os.path.isdir( current_dir + '/app' ) )
        self.assertTrue( os.path.isdir( current_dir + '/config' ) )
        self.assertTrue( os.path.isdir(os.path.join(current_dir, "app/model")))
        self.assertTrue( os.path.isdir(os.path.join(current_dir, "app/controller")))
        self.assertTrue( os.path.isfile( current_dir + '/settings.json' ) )
        self.assertTrue( os.path.isfile( current_dir + '/app.py' ) )
        self.assertTrue( os.path.isfile( os.path.join(current_dir, "app/model/Model.py") ))
        self.assertTrue( os.path.isfile( os.path.join(current_dir, "app/controller/controller.py") ) )


if __name__ == '__main__':
    unittest.main()
