import os
import json
import shutil

current_dir = os.getcwd()

def create_dir( dir ):
    full_dir = current_dir + dir
    if not os.path.isdir( full_dir ):
        try:
            os.makedirs( full_dir )
        except OSError:
            raise Exception( "could not create folder, check current user's permissions" )
    
    return full_dir

def remove( name ):
    full_name = current_dir + name
    if os.path.isfile( full_name ):
        try:
            os.remove( full_name )
        except OSError:
            raise Exception( "could not remove this file, check current user's permissions" )
    else:
        try:
            shutil.rmtree( full_name )
        except OSError:
            raise Exception( "could not remove this folder, check current user's permissions" )
        
    return full_name

def create_file( full_name, content ):
    if os.path.isfile( full_name ):
        overwrite = ''
        while overwrite.lower() not in ('y', 'n', 'yes', 'no'):
            overwrite = input( "File ({}) already exists, do you want to overwrite it? (y,n): ".format( full_name ) )
        if overwrite.lower()[0] == 'y':
            os.remove( full_name )
    
    if not os.path.isfile( full_name ):
        f = open( full_name, "w+" )
        for x in range( 0, len( content ) ):
            f.write( content[x] )
        f.close()

def create_app():
    create_dir( '/app' )
    
    _create_settings()
    _create_config()
    _create_main()

def delete_app():
    remove( '/app' )
    remove( '/config' )
    remove( '/settings.json' )
    remove( '/app.py' )

def _create_settings():
    content = "{\n"
    content = content + tabs( 1 ) + '"config": ' + '"dev",\n'
    content = content + tabs( 1 ) + '"host": ' + '"localhost",\n'
    content = content + tabs( 1 ) + '"port": ' + "8080,\n"
    content = content + tabs( 1 ) + '"debug": ' + "true\n"
    content = content + "}"

    create_file( current_dir + '/settings.json', content )

def _create_config():
    config_dir = create_dir( '/config' )
    content = "# doc: http://flask-sqlalchemy.pocoo.org/2.3/config/ \n\n"
    content = content + "SQLALCHEMY_DATABASE_URI = 'sqlite:///dev.db'\n"
    content = content + "SQLALCHEMY_TRACK_MODIFICATIONS = False\n"
    content = content + "# DEBUG = True\n"
    content = content + "# DATABASE_CONNECT_OPTIONS = {}\n"
    content = content + "# THREADS_PER_PAGE = 2"

    create_file( config_dir + '/dev.py', content )

    content = "# doc: http://flask-sqlalchemy.pocoo.org/2.3/config/ \n\n"
    content = content + "# SQLALCHEMY_DATABASE_URI = ''\n"
    content = content + "# DEBUG = True\n"
    content = content + "# DATABASE_CONNECT_OPTIONS = {}\n"
    content = content + "# THREADS_PER_PAGE = 2"

    create_file( config_dir + '/prod.py', content )

def _create_main():
    filename = current_dir + '/settings.json'

    datastore = read_json( filename )
    content = "from app import app\n"
    content = content + "app.run( host='" + datastore['host'] + "', port=" + str(datastore['port']) + ", debug=" + str(datastore['debug']) + " )"

    create_file( current_dir + '/app.py', content )

def tabs( number ):
    return number * "    "

def read_json( filename ):
    result = None

    with open( filename ) as f:
        result = json.load( f )
    return result
