import sys
import os
sys.path.append('..')

import unittest
from files.model import Field, Model, field_assembler
from files.util import current_dir, create_app, delete_app

class TestModel( unittest.TestCase ):
    def test_field( self ):
        fname = 'login'
        ftype = 'String(100)'
        field = Field( fname, ftype )
        self.assertEqual( "    login = db.Column( db.String(100), nullable=True )", field.definition() )

        funique = True
        fnull = False
        field = Field( fname, ftype, unique=funique, nullable=fnull )
        self.assertEqual( "    login = db.Column( db.String(100), unique=True, nullable=False )", field.definition() )

        fpk = True
        field = Field( fname, ftype, pkey=fpk )
        res1 = field.definition()
        self.assertEqual( "    login = db.Column( db.String(100), primary_key=True, autoincrement=True )", res1 )
        field = Field( fname, ftype, unique=funique, nullable=fnull, pkey=fpk )
        res2 = field.definition()
        self.assertEqual( res1, res2 )

        fautoinc = False
        field = Field( fname, ftype, pkey=fpk, autoinc=fautoinc )
        self.assertEqual( "    login = db.Column( db.String(100), primary_key=True, autoincrement=False )", field.definition() )

        f = field_assembler( ('login', 'String(100)') )
        self.assertEqual( "    login = db.Column( db.String(100), nullable=True )", f.definition() )

        f = field_assembler( ('login', 'String(100)', ['unique']) )
        self.assertEqual( "    login = db.Column( db.String(100), unique=True, nullable=True )", f.definition() )

        f = field_assembler( ('login', 'String(100)', ['unique','notnull']) )
        self.assertEqual( "    login = db.Column( db.String(100), unique=True, nullable=False )", f.definition() )

        f = field_assembler( ('login', 'String(100)', ['pkey','autoinc']) )
        self.assertEqual( "    login = db.Column( db.String(100), primary_key=True, autoincrement=True )", f.definition() )

        f = field_assembler( ('login', 'String(100)', ['pkey']) )
        self.assertEqual( "    login = db.Column( db.String(100), primary_key=True, autoincrement=False )", f.definition() )

    def test_model( self ):
        name = 'company'
        fields =  [ 
            ('id', 'Integer', ['pkey', 'autoinc']),
            ('name', 'String(200)', ['notnull']),
            ('email', 'String(200)', ['unique', 'notnull']),
            ('active', 'Boolean'),
        ]
        model = Model( name, fields )
        value = model.value()
        self.assertIn( 'class Company( db.Model ):', value )
        self.assertIn( '    id = db.Column( db.Integer, primary_key=True, autoincrement=True )', value )
        self.assertIn( '    name = db.Column( db.String(200), nullable=False )', value )
        self.assertIn( '    email = db.Column( db.String(200), unique=True, nullable=False )', value )
        self.assertIn( '    active = db.Column( db.Boolean, nullable=True )', value )

        name = 'user'
        fields = [
            ('id', 'Integer', ['pkey', 'autoinc']),
            ('username', 'String(80)', ['unique', 'notnull']),
            ('email', 'String(100)', ['notnull']),
            ('company_id', 'Integer', ['fkey'], 'company.id')
        ]
        model = Model( name, fields )
        value = model.value()
        self.assertIn( "    company_id = db.Column( db.Integer, db.ForeignKey( 'company.id' ) )", value )
        self.assertIn( "    company = db.relationship( 'Company' ) )", value )

        uniques = [
            ['username', 'company_id'], 
            ['email']
        ]
        model = Model( name, fields, uniques=uniques )
        value = model.value()
        self.assertIn( "    db.UniqueConstraint( 'username', 'company_id', name='ukey_1' )", value )
        self.assertIn( "    db.UniqueConstraint( 'email', name='ukey_2' )", value )
        self.assertIn( "def __init__( self, id, username, email, company_id )", value )
        self.assertIn( "self.username = username", value )
        self.assertIn( "self.company_id = company_id", value )
        self.assertNotIn( "self.company = company", value )
        
        model.remove_field( 'email' )
        self.assertNotIn( "'name': 'email'", model.show_fields() )
        model.add_field( ('email', 'String(200)', ['unique', 'notnull']) )

        value = model.value()
        self.assertIn( '    email = db.Column( db.String(200), unique=True, nullable=False )', value )
        
        model.clear_fields()
        self.assertEqual( 0, len (model.fields ) )
        model.add_fields( fields )
        self.assertEqual( len( fields ), len (model.fields ) )
    
    def test_initial( self ):
        create_app()
        self.assertTrue( os.path.isdir( current_dir + '/app' ) )
        self.assertTrue( os.path.isdir( current_dir + '/config' ) )
        self.assertTrue( os.path.isfile( current_dir + '/settings.json' ) )
        self.assertTrue( os.path.isfile( current_dir + '/app.py' ) )
        delete_app()
        self.assertTrue( not os.path.isdir( current_dir + '/app' ) )
        self.assertTrue( not os.path.isdir( current_dir + '/config' ) )
        self.assertTrue( not os.path.isfile( current_dir + '/settings.json' ) )
        self.assertTrue( not os.path.isfile( current_dir + '/app.py' ) )

if __name__ == '__main__':
    unittest.main()
