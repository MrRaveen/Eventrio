- basic context
```
"Eventrio is an advanced, AI-driven event planning and management platform designed to automate the complexities of organizing events from conception to execution. Developed with a Python and Flask backend and a MongoDB database, the application features a sophisticated AI Planner that orchestrates specialized agents—including a Planning Agent, Media Agent, and Social Media Agent—to handle tasks such as event creation, task scheduling, promotional content generation, and media asset production. By integrating with powerful tools like the Google GenAI SDK, Google Calendar, and Google Docs, Eventrio provides a seamless workflow for users to autonomously manage events, track progress through interactive dashboards, and engage with real-time AI assistance, ultimately transforming how professional and personal events are orchestrated. "

read above paragraph and prepare to answer my questions. do not try to impress me. just tell me the truth.
```
- python setup process
```
 pip install -r requirements.txt
 source venv/bin/activate
```

- stripe setup part
```
stripe --version

stripe login

sudo systemctl restart systemd-resolved

stripe login
Your pairing code is: honest-warmth-gold-evenly

stripe listen --forward-to localhost:5000/payment/webhook
```

- Coding notes 
- Creating a document
```
new_org = Organizations(
            orgName=validatedJson.orgName,
            address=validatedJson.address,
            createdBy=user_id,
            industry=[validatedJson.industry.value],
            userRole=[validatedJson.userRole.value]
        )
        new_org.save()
```

- Getting a document
```
user = userAcc.objects(sub=user_id).first()
```

- deleting a document
```
user = userAcc.objects(sub=user_id).first()
if user:
    user.delete()
```

- deleting a bunch of documents
``` 
Organizations.objects(status='inactive').delete()
```

