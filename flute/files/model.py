# -*- coding: utf-8 -*-
"""
    snake-charmer.files.model
    ~~~~~~~~~~~~

    File with classes that represent a MODEL in the MVCS structure.

    :copyright: (c) 2018 by Marcos Stefani Rosa.
    :license: BSD, see LICENSE for more details.
"""

import operator

from .util import create_dir, create_file, tabs

class Field:
    """
        Class that represents the fields of a future table that will be mapped by 
        the Model class within that same file.
    """
    def __init__( self, name, dtype, unique=False, nullable=True, pkey=False, autoinc=True, fkey=None ):
        self.name = name
        self.dtype = dtype
        self.unique = unique
        self.nullable = nullable
        self.pkey = pkey
        self.autoinc = autoinc
        self.fkey = fkey

    name = property( operator.attrgetter( "_name" ) )

    @name.setter
    def name( self, n ):
        if not n:
            raise Exception( "name cannot be empty" )
        self._name = n

    dtype = property( operator.attrgetter( "_dtype" ) )

    @dtype.setter
    def dtype( self, t ):
        if not t:
            raise Exception( "dtype cannot be empty" )
        self._dtype = t

    """
        Transforms the contents of a Field into a String that represents the 
        writing of the field definition in the contents of the file that will 
        be generated.
    """
    def definition( self ):
        result = tabs( 1 ) + "{name} = db.Column( db.{dtype}".format( name = self.name, dtype = self.dtype )

        # primary key
        if self.pkey:
            result = result + ", primary_key={pkey}, autoincrement={autoinc}".format( pkey = self.pkey, autoinc = self.autoinc )

        # foreign key
        elif self.fkey:
            result = result + ", db.ForeignKey( '" + self.fkey + "' ) )\n"
            name = self.fkey.split('.')[0]
            result = result + tabs( 1 ) + "{name} = db.relationship( '{cname}' )".format( name = name, cname = _caps(name) )

        # other properties
        else:
            if self.unique:
                result = result + ", unique={unique}".format( unique = self.unique )
            result = result + ", nullable={nullable}".format( nullable = self.nullable )
        result = result + " )"

        return result

    def json( self ):
        return ( {
            'name': self.name,
            'type': self.dtype,
            'unique': self.unique,
            'nullable': self.nullable,
            'pkey': self.pkey,
            'autoinc': self.autoinc,
            'fkey': self.fkey
        } )

class Model:
    """
        Class representing the model in the MVCS structure
    """
    def __init__( self, name, fields=None, uniques=None ):
        f = []
        if fields:
            f = _transform_fields( fields )
        self.name = name
        self.fields = f
        self.uniques = uniques

    name = property( operator.attrgetter( "_name" ) )

    @name.setter
    def name( self, n ):
        if not n:
            raise Exception( "name cannot be empty" )
        self._name = n

    fields = property( operator.attrgetter( "_fields" ) )

    @fields.setter
    def fields( self, f ):
        if not ( f is None ):
            if not isinstance( f, list ):
                raise Exception( "fields must be of list type" )

            for i in range( len( f ) ):
                if not isinstance( f[i], ( Field, tuple ) ):
                    raise Exception( "fields must contain objects of type Field or tuple" )

        self._fields = f

    def add_field( self, field ):
        self.fields.append( _transform_field ( field ) )

    def remove_field( self, field_name ):
        for i in range( len( self.fields ) ):
            if self.fields[i].name == field_name:
                del self.fields[i]
                break

    def clear_fields( self ):
        del self.fields[:]

    def show_fields( self ):
        result = []
        for i in range( len( self.fields ) ):
            result.append( self.fields[i].json() )
        return result
    
    def add_fields( self, fields ):
        if fields:
            for i in _transform_fields( fields ):
                if i not in self.fields:
                    self.fields.append( i )

    def create( self ):
        create_dir( '/app' )
        model_dir = create_dir( '/model' )
        full_name = model_dir + '/' + self.name + '.py'
        create_file( full_name, self.value() )

    def value( self ):
        txt = "from db import db\n\n"
        txt = txt + "class {name}( db.Model ):\n".format( name = _caps( self.name ) )
        txt = txt + tabs( 1 ) + "__tablename__ = '{name}'\n\n".format( name = self.name )

        pkey_field = list([x for x in self.fields if x.pkey == True])
        fkey_fields = list([x for x in self.fields if (not x.fkey is None) and x.pkey == False])
        fields = list([x for x in self.fields if x.fkey is None and x.pkey == False])

        if pkey_field:
            for f in range( len( pkey_field ) ):
                txt = txt + pkey_field[f].definition() + '\n'

        if fields:
            for f in range( len( fields ) ):
                txt = txt + fields[f].definition() + '\n'

        if fkey_fields:
            txt = txt + '\n'
            for f in range( len( fkey_fields ) ):
                txt = txt + fkey_fields[f].definition() + '\n'

        if not (self.uniques is None):
            txt = txt + "\n"
            for u in range( len( self.uniques ) ):
                uk = self.uniques[u]
                txt = txt + tabs( 1 ) + "db.UniqueConstraint( "
                for i in range( len( uk ) ):
                    txt = txt + "'{name}', ".format(name = uk[i])
                txt = txt + "name='ukey_" + str(u + 1) + "' )\n"
        
        txt = txt + self._constructor() + self._main_functions()

        return txt

    def _constructor( self ):
        result = "\n" + tabs( 1 ) + "def __init__( self"
        
        for f in range( len( self.fields ) ):
            field = self.fields[f].name
            result = result + ", {fname}".format( fname = field )
        result = result + " )\n"

        for f in range( len( self.fields ) ):
            field = self.fields[f].name
            result = result + tabs( 2 ) + "self.{fname} = {fname}\n".format( fname = field )

        return result

    def _main_functions( self ):
        kpri = []
        kfor = []

        # return json with properties
        result = "\n" + tabs( 1 ) + "def json( self ):\n"
        result = result + tabs( 2 ) + "return {\n"
        for f in range( len( self.fields ) ):
            field = self.fields[f].name
            # separe pkey
            if self.fields[f].pkey:
                kpri.append( field )
            # separe fkey
            if self.fields[f].fkey:
                kfor.append( field )
            result = result + tabs( 3 ) + "'{fname}': self.{fname}".format( fname = field )
            # I put the comma until it's the last record
            if f < (len( self.fields ) - 1):
                result = result + ','
            result = result + "\n"
        result = result + tabs( 2 ) + "}\n"

        # save to database
        result = result + "\n" + tabs( 1 ) + "def save( self ):\n"
        result = result + tabs( 2 ) + "db.session.add( self )\n"
        result = result + tabs( 2 ) + "db.session.commit()\n"

        # delete from database
        result = result + "\n" + tabs( 1 ) + "def delete( self ):\n"
        result = result + tabs( 2 ) + "db.session.delete( self )\n"
        result = result + tabs( 2 ) + "db.session.commit()\n"

        if kpri:
            # find by primary key
            result = result + "\n" + tabs( 1 ) + "@classmethod\n"
            result = result + tabs( 1 ) + "def find_one( cls"
            for k in range( len( kpri ) ):
                field = kpri[k]
                result = result + ", _" + field
            result = result + " ):\n"

            result = result + tabs( 2 ) + "return cls.query.filter_by(\n"
            for k in range( len( kpri ) ):
                field = kpri[k]
                result = result + tabs( 3 ) + "{fname}=_{fname}".format( fname = field )
                if f < (len( kpri ) - 1):
                    result = result + ','
                result = result + "\n"
            result = result + tabs( 2 ) + ").first()\n"

        if kfor:
            # find by foreign key
            for f in range( len( kfor ) ):
                field = kfor[f]
                result = result + "\n" + tabs( 1 ) + "@classmethod\n"
                result = result + tabs( 1 ) + "def find_by_" + field + "( cls, " + field + " ):\n"
                result = result + tabs( 2 ) + "result = []\n"
                result = result + tabs( 2 ) + "filter_all = cls.query.filter_by(\n"
                result = result + tabs( 3 ) + "{fname}={fname}".format( fname = field )
                result = result + "\n"
            result = result + tabs( 2 ) + ").all()\n"
            result = result + tabs( 2 ) + "for r in range( len( filter_all ) ):\n"
            result = result + tabs( 3 ) + "filter_one = filter_all[r]\n"
            result = result + tabs( 3 ) + "result.append( filter_all.json() )\n"
            result = result + tabs( 2 ) + "return result\n"

        return result

def _caps( text ):
    result = text.replace( "-", " " )
    result = result.replace( "_", " " )
    split = result.split()
    result = ""

    for i in range( len( split ) ):
        result = result + split[i].capitalize()

    return result

# transform from tuple to Field type
def field_assembler( obj ):
    # preconditions
    if not obj:
        raise Exception( "param cannot be empty" )

    if not isinstance( obj, tuple ):
        raise Exception( "param must be of tuple type" )

    if len( obj ) < 2:
        raise Exception( "the first two arguments are mandatory (name, type)" )

    f = None
    if len( obj ) == 2:
        f = Field(obj[0], obj[1])

    else:
        prop = obj[2]
        if not isinstance( prop, list ):
            raise Exception( "the third argument must be a list of properties and is not required")

        if ( not 'unique' in prop ) and ( not 'notnull' in prop ) and ( 'pkey' in prop ):
            if ( 'autoinc' in prop ):
                f = Field( obj[0], obj[1], pkey=True, autoinc=True )

            else:
                f = Field( obj[0], obj[1], pkey=True, autoinc=False )

        elif ( 'unique' in prop ) and ( 'notnull' in prop ):
            f = Field( obj[0], obj[1], unique=True, nullable=False )

        elif ( 'unique' in prop ):
            f = Field( obj[0], obj[1], unique=True, nullable=True )

        elif ( 'notnull' in prop ):
            f = Field( obj[0], obj[1], nullable=False )

        elif ( not 'unique' in prop ) and ( not 'notnull' in prop ) and ( not 'pkey' in prop ) and ( 'autoinc' in prop ):
            raise Exception( "autoinc should only be informed if it is set with the pkey property" )

        elif ( 'fkey' in prop ):
            if len( obj ) < 4:
                raise Exception( "to inform fkey there must be one more parameter informing the object.field" )

            else:
                if isinstance(obj[3], str):
                    f = Field( obj[0], obj[1], fkey=obj[3] )

                else:
                    raise Exception( "fields must be of str type" )

    return f

def _transform_fields( fields ):
    """
        check if the type of data passed and based on this make the decision 
        to transform the data to ensure that in any case the result is the same.
    """
    result = []
    for v in fields:
        result.append( _transform_field( v ) )

    return result

def _transform_field( field ):
    if isinstance( field, tuple ):
        return field_assembler( field )
    else:
        return field
