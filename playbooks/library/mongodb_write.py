#!/usr/bin/python

DOCUMENTATION = '''
---
module: mongodb_write
short_description: Writes to a MongoDB database.
description:
    - Writes to a MongoDB database.
options:
'''

import sys
try:
    from pymongo.errors import ConnectionFailure
    from pymongo.errors import OperationFailure
    from pymongo import version as PyMongoVersion
    from pymongo import MongoClient
except ImportError:
    try:  # for older PyMongo 2.2
        from pymongo import Connection as MongoClient
    except ImportError:
        pymongo_found = False
    else:
        pymongo_found = True
else:
    pymongo_found = True

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.pycompat24 import get_exception
from ansible.module_utils.six.moves import 
from distutils.version import LooseVersion

# =========================================
# MongoDB module specific support methods.
#

def check_compatibility(module, client):
    """Check the compatibility between the driver and the database.
       See: https://docs.mongodb.com/ecosystem/drivers/driver-compatibility-reference/#python-driver-compatibility
    Args:
        module: Ansible module.
        client (cursor): Mongodb cursor on admin database.
    """
    loose_srv_version = LooseVersion(client.server_info()['version'])
    loose_driver_version = LooseVersion(PyMongoVersion)

    if loose_srv_version >= LooseVersion('3.2') and loose_driver_version < LooseVersion('3.2'):
        module.fail_json(msg=' (Note: you must use pymongo 3.2+ with MongoDB >= 3.2)')

    elif loose_srv_version >= LooseVersion('3.0') and loose_driver_version <= LooseVersion('2.8'):
        module.fail_json(msg=' (Note: you must use pymongo 2.8+ with MongoDB 3.0)')

    elif loose_srv_version >= LooseVersion('2.6') and loose_driver_version <= LooseVersion('2.7'):
        module.fail_json(msg=' (Note: you must use pymongo 2.7+ with MongoDB 2.6)')

    elif LooseVersion(PyMongoVersion) <= LooseVersion('2.5'):
        module.fail_json(msg=' (Note: you must be on mongodb 2.4+ and pymongo 2.5+ to use the roles param)')

def check_database_found(module, client, db_name):
	pass

def load_mongocnf():
    config = configparser.RawConfigParser()
    mongocnf = os.path.expanduser('~/.mongodb.cnf')

    try:
        config.readfp(open(mongocnf))
        creds = dict(
            user=config.get('client', 'user'),
            password=config.get('client', 'pass')
        )
    except (configparser.NoOptionError, IOError):
        return False

    return creds

def insert(module, client, db_name, db_object, data):
	db = client[db_name]

    db[db_object].insert(data)

def update_one(module, client, db_name, db_object, data):
	db = client[db_name]

    db[db_object].update_one(data, upsert=False)

def upsert(module, client, db_name, db_object, data):
	pass

# =========================================
# Module execution.
#

def main():
	module = AnsibleModule(
		argument_spec = dict(
			login_user=dict(default=None),
			login_password=dict(default=None, no_log=True),
			login_host=dict(default='localhost'),
			login_port=dict(default='27017'),
			login_database=dict(default=None),
			database=dict(required=True, aliases=['db']),
			db_object=dict(required=True),
			action=dict(required=True, default='insert', choices=['insert', 'update', 'upsert']),
			)
		)

	if not pymongo_found:
		module.fail_json(msg='the python pymongo module is required')

	login_user = module.params['login_user']
	login_password = module.params['login_user']
	login_host = module.params['login_host']
	login_port = module.params['login_port']
	login_database = module.params['login_database']

	db_name = module.params['database']
	db_object = module.params['db_object']
	action = module.params['action']

	try:
        connection_params = {
            "host": login_host,
            "port": int(login_port),
        }

        client = MongoClient(**connection_params)

        # NOTE: this check must be done ASAP.
        # We don't need to be authenticated.
        check_compatibility(module, client)

        if login_user is None and login_password is None:
            mongocnf_creds = load_mongocnf()
            if mongocnf_creds is not False:
                login_user = mongocnf_creds['user']
                login_password = mongocnf_creds['password']
        elif login_password is None or login_user is None:
            module.fail_json(msg='when supplying login arguments, both login_user and login_password must be provided')

        if login_user is not None and login_password is not None:
            client.admin.authenticate(login_user, login_password, source=login_database)
        elif LooseVersion(PyMongoVersion) >= LooseVersion('3.0'):
            if db_name != "admin":
                module.fail_json(msg='The localhost login exception only allows the first admin account to be created')
            #else: this has to be the first admin user added

    except Exception:
        e = get_exception()
        module.fail_json(msg='unable to connect to database: %s' % str(e))

    try:
    	if action == 'insert':
    		try:
    			insert(module, client, db_name, db_object, data)
    		except Exception:
    			e = get_exception()
    			module.fail_json(msg='Unable to insert to database: $s' % str(e))

    	elif action == 'update':
    		try:
    			update(module, client, db_name, db_object, data)
    		except Exception:
    			e = get_exception()
    			module.fail_json(msg='Unable to update to database: $s' % str(e))
    	elif action == 'upsert':
    		try:
    			upsert(module, client, db_name, db_object, data)
    		except Exception:
    			e = get_exception()
    			module.fail_json(msg='Unable to upsert to database: $s' % str(e))

if __name__ == '__main__':
    main()
