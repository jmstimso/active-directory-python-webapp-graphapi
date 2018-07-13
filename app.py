import flask
import uuid
import requests
import config
import json
import jwt
import base64
from cryptography.x509 import load_der_x509_certificate
from cryptography.hazmat.backends import default_backend

app = flask.Flask(__name__)
app.debug = True
app.secret_key = 'development'

PORT = 5000  # A flask app by default runs on PORT 5000
AUTHORITY_URL = config.AUTHORITY_HOST_URL + '/dstsv2/' + config.TENANT
REDIRECT_URI = 'http://localhost:{}/displaytoken'.format(PORT)
TEMPLATE_AUTHZ_URL = ('{}/dstsv2/{}/oauth2/authorize?' +
                      'response_type={}&client_id={}&redirect_uri={}&' +
                      'state={}&resource={}&response_mode={}&nonce={}')

def get_sign_cert(accessToken: str):
		endpoint = config.AUTHORITY_HOST_URL + '/dstsv2/common/discovery/keys'
		http_headers = {'User-Agent': 'adal-python-sample','Accept': 'application/json', 'Content-Type': 'application/json','client-request-id': str(uuid.uuid4())}
		sign_key = requests.get(endpoint, headers=http_headers, stream=False).json()
		certificate_text = ''
		for key in sign_key['keys']:
				if key['kid'] == jwt.get_unverified_header(accessToken)['kid']:
						certificate_text = base64.b64decode(key['x5c'][0])
						break
		if certificate_text == '' : return certificate_text
		certificate = load_der_x509_certificate(certificate_text, default_backend())
		return certificate.public_key()
		
def verify_iss(iss: str):
		for domain in config.DSTS_DOMAINS :
				if iss == domain :
						return True
		return False
		
@app.route("/")
def main():
    login_url = 'http://localhost:{}/login'.format(PORT)
    resp = flask.Response(status=307)
    resp.headers['location'] = login_url
    return resp


@app.route("/login")
def login():
    auth_state = str(uuid.uuid4())
    nonce = str(uuid.uuid4())
    flask.session['state'] = auth_state
    authorization_url = TEMPLATE_AUTHZ_URL.format(
    		config.AUTHORITY_HOST_URL,
    		config.TENANT,
        config.RESPONCE_TYPE,
        config.CLIENT_ID,
        REDIRECT_URI,
        auth_state,
        config.RESOURCE,
        config.RESPONCE_MODE,
        nonce)
    resp = flask.Response(status=307)
    resp.headers['location'] = authorization_url
    return resp


@app.route("/displaytoken", methods=['GET', 'POST'])
def main_logic():
		if flask.request.method == 'POST' :
				id_token = flask.request.form['id_token']
		else:
				id_token = flask.request.args['id_token']
		flask.session['id_token'] = id_token
		public_key = get_sign_cert(id_token)
		if public_key == '' : return 'Could not find certificate to validate token.', 500
		decoded_jwt = jwt.decode(id_token, public_key, audience=config.CLIENT_ID)
		iss = decoded_jwt['iss'].split('/')[2]
		if not verify_iss(iss): return 'Token not issued by a trusted authority.', 500
		return flask.render_template('display_token_info.html', id_token=json.dumps(decoded_jwt, indent=2)), 200

@app.route('/echo')
def echo_resp():
		access_token = flask.request.headers.get('Authorization')
		flask.session['access_token'] = access_token
		public_key = get_sign_cert(access_token)
		if public_key == '' : return 'Could not find certificate to validate token.', 500
		decoded_jwt = jwt.decode(access_token, public_key, audience=config.CLIENT_ID)
		iss = decoded_jwt['iss'].split('/')[2]
		if not verify_iss(iss): return 'Token not issued by a trusted authority.', 500
		return json.dumps(decoded_jwt, indent=2), 200


if __name__ == "__main__":
    app.run()
