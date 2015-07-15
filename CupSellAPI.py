#
# PYTHON CupSell API
#
# Coded by RayZor.pl
#
import time, json, hmac, hashlib, urllib, pycurl, StringIO, sys

reload(sys)
sys.setdefaultencoding('utf8')

class CupSellAPI:

	target = 'http://cupsell.pl/api/'

	def __init__(self, config):
		self.config = config

	def request(self, data, val = None, data_only = False, debug = False):
		if isinstance(val, dict):
			get = val['get'] if 'get' in val else None
			post = val['post'] if 'post' in val else None
			if get == None and post == None: post = val
		else:
			sid = val
			get = None
			post = None

		target = self.target + data + ('/' + str(sid) if 'sid' in locals() and sid is not None else '') + "?"
		excluded_params = ('signature', 'pages_count', 'page')
		params = {
			'api_key' : self.config['api_key'],
			'timestamp' : int(time.time()),
			'signature' : None
		}

		if 'sid' in locals() and sid is not None: params['id'] = sid
		if get: params.update(get)
		params['signature'] = self.toHash(params, self.config['private_key'], excluded_params, post)
		response = self.sendRequest(params, target, post)

		if debug: print "DEBUG START \n" + response + "\n DEBUG END \n"

		jd = json.loads(response)
		return jd['response']['details']['data'] if data_only else jd['response']

	def test(self):
		ret = self.request('api-test')
		return True if ret['status'] == 200 else False

	def toHash(self, params, private_key, excluded_params, post):
		string = ''
		if post: params.update(post)

		for key in sorted(params):
			if not key in excluded_params and params[key]:
				string = string + str(key) + '=' + str(params[key]) + '#'
		return hmac.new(private_key, string, hashlib.sha256).hexdigest()

	def sendRequest(self, params, target, post):
		for key, val in enumerate(params):
			if val == None:
				del params[key]

		buf = StringIO.StringIO()

		target += urllib.urlencode(params)
		c = pycurl.Curl()
		c.setopt(pycurl.URL, target)
		c.setopt(pycurl.WRITEFUNCTION, buf.write)

		if post:
			c.setopt(pycurl.POST, 1)
			c.setopt(pycurl.POSTFIELDS, urllib.urlencode(post))

		c.perform()
		c.close()
		return buf.getvalue()