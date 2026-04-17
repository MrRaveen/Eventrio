from mongoengine import Document, StringField

class Posts(Document):
    meta = {'collection': 'posts'}
    postID = StringField(required=True)
    postTitle = StringField(required=True)
    description = StringField()
    imageUrl = StringField()
    projectID = StringField()
    orgID = StringField()
