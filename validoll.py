"""
Validoll

Simple yet effective minimalistic validation and data-processing tool
Credits to github.com/sancau | 2017
"""


class ValidationError(Exception):
    pass


class ResolveError(Exception):
    pass


def raise_validation_error(e):  # a shortcut to use in lambdas
    raise ValidationError(e)


def raise_resolve_error(e):  # a shortcut to use in lambdas
    raise ResolveError(e)


def validate(data, schema, strict=True):
    output = {}

    validation_errors = []

    if not isinstance(data, dict):
        raise ValidationError('Given object is not of type <dict>: {}'.format(data))

    unknown = set(data.keys()) - set(schema.keys())
    if unknown and strict:
        validation_errors.append(
            'Found unknown fields while strict mode is on. '
            'Fields: {}'.format([i for i in unknown]))
    else:
        output.update({key: data[key] for key in unknown})

    for k, v in schema.items():
        if k not in data:
            if v.get('required', None):
                validation_errors.append('{} is required in {}'.format(k, data))
            continue

        defined_type = v.get('type', None)
        if defined_type and not isinstance(data[k], defined_type):
            validation_errors.append(
                'Field <{}> has a wrong type. Expected {}. '.format(k, defined_type) +
                'Got {} instead.'.format(type(data[k]))
            )

        else:
            new_name = v.get('rename', k)
            resolve = v.get('resolve', lambda x: x)
            try:
                if not v.get('drop', None):
                    output[new_name] = resolve(data[k])
            except Exception as e:
                raise ResolveError(
                    'Inner ex. while resolving <{}> ({}): {}'.format(k, type(e), e))

    if validation_errors:
        raise ValidationError(validation_errors)

    return output


def validate_collection(collection, schema, invalid_handler=None, strict=True):
    # data validation
    valid = []
    invalid = []
    for obj in collection:
        try:
            validated = validate(obj, schema, strict)
            valid.append(validated)
        except ValidationError as e:
            print(e)
            obj['validation_errors'] = e
            invalid.append(obj)
        except ResolveError as e:
            print(e)
            obj['validation_errors'] = e
            invalid.append(obj)

    # validation results logging
    vlen = len(valid)
    invlen = len(invalid)
    print('Got {} valid and normalized objects. {} objects are invalid.'.format(vlen, invlen))

    if invalid_handler:
        invalid_handler(invalid)

    return valid, invalid



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
