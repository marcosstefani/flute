import os
from files.util import create_dir, create_app, delete_app

def new():
    create_app()

def clear():
    sure = ''
    while sure.lower() not in ('y', 'n', 'yes', 'no'):
        sure = input( "Are you sure you want to delete the app? (y,n): " )
    if sure.lower()[0] == 'y':
        delete_app()
