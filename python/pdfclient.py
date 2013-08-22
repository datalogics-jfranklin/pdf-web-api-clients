# Copyright (c) 2013, Datalogics, Inc. All rights reserved.

"Sample pdfprocess client module"

# This agreement is between Datalogics, Inc. 101 N. Wacker Drive, Suite 1800,
# Chicago, IL 60606 ("Datalogics") and you, an end user who downloads source
# code examples for integrating to the Datalogics (R) PDF Web API (TM)
# ("the Example Code"). By accepting this agreement you agree to be bound
# by the following terms of use for the Example Code.
#
# LICENSE
# -------
# Datalogics hereby grants you a royalty-free, non-exclusive license to
# download and use the Example Code for any lawful purpose. There is no charge
# for use of Example Code.
#
# OWNERSHIP
# ---------
# The Example Code and any related documentation and trademarks are and shall
# remain the sole and exclusive property of Datalogics and are protected by
# the laws of copyright in the U.S. and other countries.
#
# Datalogics and Datalogics PDF Web API are trademarks of Datalogics, Inc.
#
# TERM
# ----
# This license is effective until terminated. You may terminate it at any
# other time by destroying the Example Code.
#
# WARRANTY DISCLAIMER
# -------------------
# THE EXAMPLE CODE IS PROVIDED "AS IS" WITHOUT WARRANTY OF ANY KIND, EITHER
# EXPRESSED OR IMPLIED, INCLUDING, BUT NOT LIMITED TO THE IMPLIED WARRANTIES
# OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.
#
# DATALOGICS DISCLAIM ALL OTHER WARRANTIES, CONDITIONS, UNDERTAKINGS OR
# TERMS OF ANY KIND, EXPRESS OR IMPLIED, WRITTEN OR ORAL, BY OPERATION OF
# LAW, ARISING BY STATUTE, COURSE OF DEALING, USAGE OF TRADE OR OTHERWISE,
# INCLUDING, WARRANTIES OR CONDITIONS OF MERCHANTABILITY, FITNESS FOR A
# PARTICULAR PURPOSE, SATISFACTORY QUALITY, LACK OF VIRUSES, TITLE,
# NON-INFRINGEMENT, ACCURACY OR COMPLETENESS OF RESPONSES, RESULTS, AND/OR
# LACK OF WORKMANLIKE EFFORT. THE PROVISIONS OF THIS SECTION SET FORTH
# SUBLICENSEE'S SOLE REMEDY AND DATALOGICS'S SOLE LIABILITY WITH RESPECT
# TO THE WARRANTY SET FORTH HEREIN. NO REPRESENTATION OR OTHER AFFIRMATION
# OF FACT, INCLUDING STATEMENTS REGARDING PERFORMANCE OF THE EXAMPLE CODE,
# WHICH IS NOT CONTAINED IN THIS AGREEMENT, SHALL BE BINDING ON DATALOGICS.
# NEITHER DATALOGICS WARRANT AGAINST ANY BUG, ERROR, OMISSION, DEFECT,
# DEFICIENCY, OR NONCONFORMITY IN ANY EXAMPLE CODE.

import base64
import sys

import requests
import simplejson as json


class Application(object):
    BASE_URL = 'https://pdfprocess.datalogics-cloud.com'
    VERSION = 0

    ## @param id from [3scale](http://datalogics-cloud.3scale.net/)
    #  @param key from [3scale](http://datalogics-cloud.3scale.net/)
    def __init__(self, id, key):
        self._id, self._key = (id, key)
    def __str__(self):
        return json.dumps({'id': self.id, 'key': self.key})

    ## Request factory
    # @return a Request object
    # @param request_type e.g. 'image'
    def make_request(self, request_type, version=VERSION, base_url=BASE_URL):
        if request_type == 'image':
            return ImageRequest(self, version, base_url)

    @property
    ## ID property (string)
    def id(self): return self._id
    @property
    ## Key property (string)
    def key(self): return self._key


class Request(object):
    def __init__(self, application, request_type, version, base_url):
        self._application = {'application': str(application)}
        self._url = '%s/api/%s/actions/%s' % (base_url, version, request_type)
        self.reset()

    ## Post request
    #  @return a requests.Response object
    #  @param input request document file object
    #  @param options e.g. {'pages': '1', 'printPreview': True}
    def post(self, input, **options):
        if input.name: self.data['inputName'] = input.name
        if options: self.data['options'] = json.dumps(options)
        return requests.post(self.url, data=self.data, files={'input': input})

    ## Reset #data
    def reset(self):
        self._data = self._application.copy()

    @property
    ## %Request data property (dict), set by #post
    def data(self): return self._data
    @property
    ## %Request URL property (string)
    def url(self): return self._url


class ImageRequest(Request):
    def __init__(self, client, version, base_url):
        Request.__init__(self, client, 'image', version, base_url)

    ## Post request
    #  @return an ImageResponse object
    #  @param input request document file object
    #  @param options e.g. {'outputForm': 'jpg', 'printPreview': True}
    #  * [colorModel](https://datalogics-cloud.3scale.net/docs#colorModel)
    #  * [compression](https://datalogics-cloud.3scale.net/docs#compression)
    #  * [disableColorManagement](https://datalogics-cloud.3scale.net/docs#disableColorManagement)
    #  * [disableThinLineEnhancement](https://datalogics-cloud.3scale.net/docs#disableThinLineEnhancement)
    #  * [OPP](https://datalogics-cloud.3scale.net/docs#OPP)
    #  * [outputForm](https://datalogics-cloud.3scale.net/docs#outputForm)
    #  * [pages](https://datalogics-cloud.3scale.net/docs#pages)
    #  * [password](https://datalogics-cloud.3scale.net/docs#password)
    #  * [pdfRegion](https://datalogics-cloud.3scale.net/docs#pdfRegion)
    #  * [printPreview](https://datalogics-cloud.3scale.net/docs#printPreview)
    #  * [resolution](https://datalogics-cloud.3scale.net/docs#resolution)
    #  * [smoothing](https://datalogics-cloud.3scale.net/docs#smoothing)
    #  * [suppressAnnotations](https://datalogics-cloud.3scale.net/docs#suppressAnnotations)
    def post(self, input, **options):
        self.reset()
        return ImageResponse(Request.post(self, input, **options))


## Returned by Request.post
class Response(object):
    def __init__(self, request_response):
        self._status_code = request_response.status_code
        try: self._json = request_response.json()
        except ValueError: self._json = {}
    def __str__(self):
        return '%s: %s' % (response.process_code, response.output)
    def __bool__(self):
        return self.process_code == 0
    __nonzero__ = __bool__
    def __getitem__(self, key):
        return json.dumps(self._json[key])
    @property
    ## API status code (int)
    def process_code(self):
        if 'processCode' in self._json: return int(self['processCode'])

    @property
    ## Base64-encoded data (string) if request was successful, otherwise None
    def output(self):
        if 'output' in self._json and self: return self['output']

    @property
    ## None if successful, otherwise information (string) about process_code
    def exc_info(self):
        if 'output' in self._json and not self: return self['output']

    @property
    ## HTTP status code (int)
    def status_code(self): return self._status_code


## Returned by ImageRequest.post
class ImageResponse(Response):
    def _image(self):
        if sys.version_info.major < 3:
            return self['output'].decode('base64')
        else:
            return base64.b64decode(self['output'])
    @property
    ## Image data (bytes) if request was successful, otherwise None
    def output(self):
        if self: return self._image()


## Values returned by Response.process_code
class ProcessCode:
    OK = 0
    AuthorizationError = 1
    InvalidSyntax = 2
    InvalidInput = 3
    InvalidPassword = 4
    MissingPassword = 5
    AdeptDRM = 6
    InvalidOutputType = 7
    InvalidPage = 8
    RequestTooLarge = 9
    UsageLimitExceeded = 10
    UnknownError = 20

## Values returned by ImageResponse.process_code
class ImageProcessCode(ProcessCode):
    InvalidColorModel = 21
    InvalidCompression = 22
    InvalidRegion = 23
    InvalidResolution = 24

