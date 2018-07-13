RESOURCE = "http://pythonwebapi.jastimso-dev"  # Add the resource you want the access token for
TENANT = "7A433BFC-2514-4697-B467-E0933190487F"  # Enter tenant name, e.g. contoso.onmicrosoft.com
AUTHORITY_HOST_URL = "https://co1-test7-dsts.dsts.core.azure-test.net"
CLIENT_ID = "9d855746-3b9b-4dd7-9517-e102cebeb285"  # copy the Application ID of your app from your Azure portal
RESPONCE_TYPE = "id_token code" #
RESPONCE_MODE = "form_post" # responce_mode is either form_post or query

DSTS_DOMAINS = [
        'dsts.core.windows.net',
        'dsts.core.chinacloudapi.cn',  
        'dsts.core.cloudapi.de', 
        'dsts.core.usgovcloudapi.net',  
        'dsts.core.azure-test.net',
        ]
# These settings are for the Microsoft Graph API Call
API_VERSION = 'v1.0'
