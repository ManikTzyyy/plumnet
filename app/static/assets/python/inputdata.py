from polls.models import Server
from faker import Faker
import random

fake = Faker()

for i in range(20):  # jumlah data dummy
    Server.objects.create(
        name=fake.hostname(),
        host=fake.ipv4(),
        username=fake.user_name(),
        password=fake.password(),
        genieacs=random.choice([fake.ipv4(), None])  # kadang kosong, kadang ada
    )
