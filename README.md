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

