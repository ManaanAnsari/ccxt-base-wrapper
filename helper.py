def strToBool(var):
    '''
    when called from swagger bool value is mainly in string like 'true' 'false' we convert it to 
    python bool type here 
    '''
    if var is not None:
        if isinstance(var, str):
            var = True if var.lower() == "true" else False
            return var
        
        elif isinstance(var, bool):
            return var
    return None
