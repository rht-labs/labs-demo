Labs Stats
==========

This role updates labs demo stats after each successful run.

Requirements
------------

Mongodb must already be installed and running at the target server and loaded with the following schema.

```
{"name": "runs", "count": 0}
{"name": "unique_users", "count": 0}
```

To populate the database with the aforementioned schema, please create a new .json file with the above as the content and run

```
mongoimport --db <database_name> --collection GlobalStats --drop --file ~/path/to/file.json
```

Role Variables
--------------

- `labs_username`: The labs username that we want to record in the database (currently pulled from `demo_username`).
- `db_user`: The database username that has write access to the database.
- `db_password`: The database user password.

Running the Playbook
--------------------

`$ ansible-playbook playbooks/prep-demo.yml --ask-become-pass` if become is enabled