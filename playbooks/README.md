# Playbooks

## load_gdrive_identities.yml
This playbook is used to retrieve identities from google sheets and insert/update users and groups into an identity manager (IPA)

Example run:

```

>>ansible-playbook -i  load_gdrive_identities.yml -e google_doc_file_id=1qcp8yI -e google_doc_file_name=sample.csv -e gdrive_command_tool=gdrive -e google_service_account=labs-sa.json -e ipa_admin_user=admin -e ipa_admin_password=admin

```


**Notes**
 1. The user needs to have idm rights to add/remove/modify users and groups

