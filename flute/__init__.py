import os
from .model import Model
from .util import precondition, create_dir, create_app, delete_app, create_model

def new_app():
    create_app()

def clear_app():
    sure = ''
    while sure.lower() not in ( 'y', 'n', 'yes', 'no' ):
        sure = input( "Are you sure you want to delete the app? (y,n): " )
    if sure.lower()[0] == 'y':
        delete_app()

def new_model( name, fields=None, uniques=None ):
    model = Model( name, fields, uniques=uniques )
    return model

def _create_model( model ):
    precondition( isinstance( model, Model ) ), "To create a model, an object of type Model must be passed.")
    create_model( model )

def mvcs( model ):
    _create_model( model )