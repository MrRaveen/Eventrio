- python virtual environment
 pip install -r requirements.txt
 source venv/bin/activate
- stripe
```
ravinjayasanka@vlte6:~$ stripe --version
stripe version 1.40.3
ravinjayasanka@vlte6:~$ stripe login
Post "https://dashboard.stripe.com/stripecli/auth": dial tcp: lookup dashboard.stripe.com on 127.0.0.53:53: read udp 127.0.0.1:47099->127.0.0.53:53: i/o timeout
ravinjayasanka@vlte6:~$ sudo systemctl restart systemd-resolved
[sudo] password for ravinjayasanka: 
ravinjayasanka@vlte6:~$ stripe login
Your pairing code is: honest-warmth-gold-evenly
This pairing code verifies your authentication with Stripe.
Press Enter to open the browser or visit https://dashboard.stripe.com/stripecli/confirm_auth?t=4gwxEpUpjvfao2B4dowhbGRjOnHzbA4G (^C to quit)
> Done! The Stripe CLI is configured for Hackster sandbox with account id acct_1TKjYfFJHq1Pj9am
Please note: this key will expire after 90 days, at which point you'll need to re-authenticate.
ravinjayasanka@vlte6:~$ 

stripe listen --forward-to localhost:5000/payment/webhook

```