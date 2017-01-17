"""
VALIDOLL

Simple yet effective minimalistic validation and data-preprocessing tool

Credits to github.com/sancau | 2017
"""


"""
SOURCE ^^
"""


class ValidationError(Exception):
    pass


class ResolveError(Exception):
    pass



def validate(data, schema, strict=False):
    output = {}

    unknown = set(data.keys()) - set(schema.keys())
    if unknown and strict:
        raise ValidationError(
            'Found unknown fields while strict mode is on. '
            'Fields: {}'.format([i for i in unknown]))
    else:
        output.update({key: data[key] for key in unknown}) 

    for k, v in schema.items():
        if not k in data:
            if v.get('required', None):
                raise ValidationError('{} is required in {}'.format(k, data))
            else:
                continue
        
        defined_type = v.get('type', None)
        if defined_type and not isinstance(data[k], defined_type):
            raise ValidationError(
                'Field <{}> has a wrong type. Expected {}. '.format(k, defined_type) +
                'Got {} instead.'.format(type(data[k]))
            )

        else:
            new_name = v.get('rename', k)
            resolve = v.get('resolve', lambda x: x)
            try:
                output[new_name] = resolve(data[k])
            except Exception as e:
                raise ResolveError(
                    'Inner ex. while resolving <{}> ({}): {}'.format(k, type(e), e))

    return output


"""
USAGE EXAMPLE
"""

data = {
    'MATERIAL': 5050.25,
    'DATE': '20161214',
    'PLANT': 'X005'
}


schema = {
    'MATERIAL': {
        'type': float,
        'rename': 'sap_good_id',
        'resolve': int,
        'required': True
    },
    'DATE': {
        'type': str,
        'rename': 'date',
        'resolve': lambda x: '-'.join([x[:4], x[4:6], x[6:]]),
        'required': True
    },
    'PLANT': {
        'type': str,
        'rename': 'sap_wh_id',
    }
}


try:
    doc = validate(data, schema, strict=True)
except ValidationError as e:
    print(e)
except ResolveError as e:
    print(e)
else:
    print('Yay! This is valid and processed:', doc)
