from mongoengine import (StringField,
                         DateTimeField,
                         Document)


class Test(Document):
    name        = StringField(required=True)
    description = StringField(required=True)
    start       = DateTimeField(required=True)
    end         = DateTimeField(required=True)
    devEUI      = StringField(required=True)
