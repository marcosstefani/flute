import os
from . model import Model
from . util import create_dir, create_app, delete_app

def new_app():
    create_app()

def app_clear():
    sure = ''
    while sure.lower() not in ('y', 'n', 'yes', 'no'):
        sure = input( "Are you sure you want to delete the app? (y,n): " )
    if sure.lower()[0] == 'y':
        delete_app()

def new_model( name, fields=None, uniques=None ):
    model = Model( name, fields, uniques=uniques )
    return model
