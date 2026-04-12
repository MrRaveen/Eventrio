from mongoengine import Document, StringField

class Participants(Document):
    meta = {'collection': 'participants'}
    
    name = StringField(required=True)
    email = StringField(required=True)
    eventID = StringField(required=True)
    orgID = StringField(required=True)
