from mongoengine import Document, StringField, ListField

class Organizations(Document):
    meta = {'collection': 'organizations'}
    
    orgName = StringField(required=True)
    address = StringField()
    createdBy = StringField(required=True)
    industry = ListField(StringField(choices=(
        'IT', 'Health care', 'Sports', 'Business events', 
        'Casual', 'Education (school)', 'Competitions'
    )))
    userRole = ListField(StringField(choices=(
        'manager', 'student', 'business owner', 
        'event planner', 'teacher', 'sport coach'
    )))
