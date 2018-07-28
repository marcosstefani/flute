from files.model import Model

def new_model( name, fields=None, uniques=None ):
    model = Model( name, fields, uniques=uniques )
    return model