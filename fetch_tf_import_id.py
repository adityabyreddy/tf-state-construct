"""
Intro: Script fetches supported ID formats for the given terraform resource. This will be helpful while importing existing resource into a terraform state file.

Some of the providers resouces have different naming in the registry page compared to the one mentioned in the docs. Mainitaining a knowledge base to manage these mis-matches.
If you find any resources that has different namings, add an entry to the resource_name_alternatives dict in the following structure.


{
  <provider-name>: {
    <resource-name>: <alt-resource-name>,
    <resource-name>: <alt-resource-name>
  }
}

Usage: fetch_tf_import_id.py <provider-name> <provider-version> <resource-name>

Eg.

fetch_tf_import_id.py google 3.67.0 google_storage_bucket
fetch_tf_import_id.py google 3.67.0 google_service_account
fetch_tf_import_id.py google 3.67.0 google_storage_bucket_iam_member
"""

import sys
import urllib3
import json
import re

urllib3.disable_warnings()

HASHICORP_REGISTRY_URL="https://registry.terraform.io"

"""

"""
# Knowledge Base
resource_name_alternatives = {
  "google": {
    "google_storage_bucket": "storage_bucket",
    "google_storage_bucket_iam_member": "storage_bucket_iam"
  }
}

def alter_resource_name(provider_name, resource):
  if resource in resource_name_alternatives[provider_name].keys():
    return resource_name_alternatives[provider_name][resource]
  return resource

def get_provider_info(provider_name):
  return client.request("GET", HASHICORP_REGISTRY_URL+"/v2/providers?filter%5Bnamespace%5D=hashicorp&filter%5Bname%5D="+provider+"&filter%5Bmoved%5D=true&filter%5Bunlisted%5D=true&filter%5Bwithout-versions%5D=true").data

def get_provider_versions_info(provider_self_link):
  return client.request("GET", HASHICORP_REGISTRY_URL+provider_self_link+"?include=categories%2Cmoved-to%2Cpotential-fork-of%2Cprovider-versions%2Ctop-modules").data

def get_provider_version_id(provider_versions_info):
  return list(
    filter(
      lambda x: x['type']=="provider-versions" and x['attributes']['version']==provider_version, provider_versions_info['included']
    )
  )[0]['id']

def get_resource_doc_link(provider_version_id, resource_name):
  return json.loads(
    client.request("GET", HASHICORP_REGISTRY_URL+"/v2/provider-docs?filter%5Bprovider-version%5D="+provider_version_id+"&filter%5Bcategory%5D=resources&filter%5Bslug%5D="+resource_name+"&page%5Bsize%5D=1")
    .data
  )['data'][0]['links']['self']

def get_resource_doc(resource_doc_link):
  return json.loads(
    client.request("GET", HASHICORP_REGISTRY_URL+resource_doc_link)
    .data
  )

def get_resource_import_suggestions(resource_doc):
  return re.findall(r".*terraform import (.*)", resource_doc['data']['attributes']['content'])

if __name__ == "__main__":
  provider = sys.argv[1]
  provider_version = sys.argv[2]
  resource_name = sys.argv[3]

  resource_name = alter_resource_name(provider, resource_name)

  client = urllib3.PoolManager()

  try:
    # fetch provider id
    provider_info = json.loads(get_provider_info(provider))
    # fetch provider versions
    provider_versions_info = json.loads(get_provider_versions_info(provider_info['data'][0]['links']['self']))
    # filter provider version id from the versions list
    provider_version_id = get_provider_version_id(provider_versions_info)
    # get resource doc id
    resource_doc_link = get_resource_doc_link(provider_version_id, resource_name)
    # get resource doc
    resource_doc = get_resource_doc(resource_doc_link)
    # filter import docs
    resource_import_matches = get_resource_import_suggestions(resource_doc)
    print("Resource ID should be in the following formats,")
    for match in resource_import_matches:
      print("- "+match)
  except Exception as e:
    raise(e)

  
