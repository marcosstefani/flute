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
    _create_templates()
    _create_statics()

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
    app_dir = current_dir + '/app'

    filename = app_dir + '/__init__.py'

    content = "from flask import Flask, render_template\n"
    content = content + "from flask_sqlalchemy import SQLAlchemy\n\n"
    content = content + "app = Flask( __name__ )\n"
    content = content + "app.config.from_object( 'config." + datastore['config'] + "' )\n"
    content = content + "db = SQLAlchemy( app )\n\n"
    content = content + "@app.route( '/' )\n"
    content = content + "def index():\n"
    content = content + tabs( 1 ) + "return render_template( 'home.html' )\n\n"

    content = content + _error_string( 403, "forbidden" )
    content = content + _error_string( 404, "page_not_found" )
    content = content + _error_string( 500, "internal_server_error" )

    content = content + "db.create_all()"

    create_file( filename, content )

def _create_templates():
    template_dir = create_dir( "/app/templates" )

    filename = template_dir + "/base.html"
    content = "<!DOCTYPE html>\n"
    content = content + "<html>\n"
    content = content + "<head>\n"
    content = content + tabs( 1 ) + "<title>{{ title }} | Project Dream Team</title>\n"
    content = content + tabs( 1 ) + "<link rel='stylesheet' type='text/css' href='//cloud.typography.com/746852/739588/css/fonts.css'>\n"
    content = content + tabs( 1 ) + "<link rel='stylesheet' href='https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css' integrity='sha384-Gn5384xqQ1aoWXA+058RXPxPg6fy4IWvTNh0E263XmFcJlSAwiGgFAW/dAiS6JXm' crossorigin='anonymous'>\n"
    content = content + tabs( 1 ) + "<link href='https://maxcdn.bootstrapcdn.com/font-awesome/4.7.0/css/font-awesome.min.css' rel='stylesheet'>\n"
    content = content + tabs( 1 ) + "<link href='{{ url_for('static', filename='css/style.css') }}' rel='stylesheet'>\n"
    content = content + tabs( 1 ) + "<!-- <link rel='shortcut icon' href='{{ url_for('static', filename='img/favicon.ico') }}'> -->\n"
    content = content + "</head>\n"
    content = content + "<body>\n"
    content = content + tabs( 1 ) + "{% block body %} {% endblock %}\n"
    content = content + "</body>\n"
    content = content + "</html>\n"
    create_file( filename, content )

    filename = template_dir + "/error.html"
    content = '{% extends "base.html" %}\n'
    content = content + '{% block title %}{{ title }}{% endblock %}\n'
    content = content + '{% block body %}\n'
    content = content + '<div class="error-container">\n'
    content = content + tabs( 1 ) + '<h1>{{ number }}</h1>\n'
    content = content + tabs( 1 ) + '<p class="return">{{ title }}</p>\n'
    content = content + '</div>\n'
    content = content + '{% endblock %}\n'
    create_file( filename, content )
  
    filename = template_dir + "/home.html"
    content = '{% extends "base.html" %}\n'
    content = content + '{% block title %}{{ title }}{% endblock %}\n'
    content = content + '{% block body %}\n'
    content = content + '<nav class="navbar navbar-light bg-light">\n'
    content = content + tabs( 1 ) + '<a class="navbar-brand" href="#">\n'
    content = content + tabs( 2 ) + '<img src="https://i.imgsafe.org/3c/3cf10be9ce.png" width="30" height="30" class="d-inline-block align-top" alt="">Flute</a>\n'
    content = content + '</nav>\n'
    content = content + '{% endblock %}\n'
    create_file( filename, content )

def _create_statics():
    css_dir = create_dir( "/app/static/css" )
    filename = css_dir + "/style.css"
    content = 'html,body{margin:0;padding:0;height:100%}body{font-family:"Whitney SSm A","Whitney SSm B","Helvetica Neue",Helvetica,Arial,Sans-Serif;background-color:#b1cac0;'
    content = content + 'color:#2b3a34;-moz-font-smoothing:antialiased;-webkit-font-smoothing:antialiased}.error-container{text-align:center;height:100%}'
    content = content + '@media (max-width:480px){.error-container{position:relative;top:50%;height:initial;-webkit-transform:translateY(-50%);-ms-transform:translateY(-50%);'
    content = content + 'transform:translateY(-50%)}}.error-container h1{margin:0;font-size:130px;font-weight:300}@media (min-width:480px){.error-container h1{position:relative;'
    content = content + 'top:50%;-webkit-transform:translateY(-50%);-ms-transform:translateY(-50%);transform:translateY(-50%)}}@media (min-width:768px){.error-container '
    content = content + 'h1{font-size:220px}}.return{color:#2b3a34;font-weight:400;letter-spacing:-.04em;margin:0}@media (min-width:480px){.return{position:absolute;width:100%;'
    content = content + 'bottom:30px}}.return a{padding-bottom:1px;color:#2b3a34;text-decoration:none;border-bottom:1px solid rgba(255,255,255,.6);'
    content = content + '-webkit-transition:border-color 0.1s ease-in;transition:border-color 0.1s ease-in}.return a:hover{border-bottom-color:#2b3a34}'
    create_file( filename, content )

def _error_string( number, name ):
    result = "@app.errorhandler( " + str( number ) + " )\n"
    result = result + "def " + name + "( error ):\n"
    result = result + tabs( 1 ) + "return render_template('error.html', number= " + str( number ) + ", title='" + caps( name, spl=True ) + "'), " + str( number ) + "\n\n"
    return result

def tabs( number ):
    return number * "    "

def caps( text, spl=False ):
    result = text.replace( "-", " " )
    result = result.replace( "_", " " )
    split = result.split()
    result = ""

    for i in range( len( split ) ):
        space = ""
        if spl:
            space = " "
        result = result + space + split[i].capitalize()

    return result

def read_json( filename ):
    result = None

    with open( filename ) as f:
        result = json.load( f )
    return result
