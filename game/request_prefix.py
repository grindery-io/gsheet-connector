import os

os.environ["CDS_NAME"] = "googleSheets"
REQUEST_PREFIX = os.path.expandvars(os.environ["CREDENTIAL_MANAGER_REQUEST_PREFIX"])