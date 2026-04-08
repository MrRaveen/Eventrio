from mongoengine import Document, StringField

class Posts(Document):
    meta = {'collection': 'posts'}
    
    postTitle = StringField(required=True)
    description = StringField()
    imageUrl = StringField()
    projectID = StringField()
