import os
import certifi
import dns.resolver
from mongoengine import connect

def init_db():
    # Force dnspython to use Google DNS to bypass local systemd-resolved SRV timeouts
    dns.resolver.default_resolver = dns.resolver.Resolver(configure=False)
    dns.resolver.default_resolver.nameservers = ['8.8.8.8', '8.8.4.4']

    MONGO_URI = os.environ.get('MONGO_URI')
    connect(
        db='EventrioOfficial',
        host=MONGO_URI,
        tlsCAFile=certifi.where(),
        alias='default'
    )