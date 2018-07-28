import os
from files.model import Model
from files.util import create_dir, create_app, delete_app

class Snake:
    def new_app( self ):
        create_app()
    
    def app_clear( self ):
        sure = ''
        while sure.lower() not in ('y', 'n', 'yes', 'no'):
            sure = input( "Are you sure you want to delete the app? (y,n): " )
        if sure.lower()[0] == 'y':
            delete_app()


    def new_model( self, name, fields=None, uniques=None ):
        model = Model( name, fields, uniques=uniques )
        return model
