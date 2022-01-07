from models import Contact

Contact1 = Contact(
    id=1,
    first_name='Clark',
    last_name='Kent',
    address='123 main st',
    email='ckent@email.com',
    city='Metropolis',
    state='NY',
    zip_code='54321'
)

Contact2 = Contact(
    id=2,
    first_name='Bruce',
    last_name='Wayne',
    address='456 main st',
    email='bwayne@email.com',
    city='Gotham',
    state='NY',
    zip_code='54345'
)

db = [Contact1, Contact2]
