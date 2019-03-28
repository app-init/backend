from flask import Response

class HttpResponse(Response):
   default_status = 200
   content_type = "application/json"

   # @classmethod
   # def force_type(cls, rv, environ=None):
   #    if isinstance(rv, dict):
   #       rv = jsonify(convert(rv))
   #    return super(HttpResponse, cls).force_type(rv, environ)


class HttpResponseForbidden(Response):
   default_status = 403
   # @classmethod
   # def force_type(cls, rv, environ=None):
   #    if isinstance(rv, dict):
   #       rv.status_code = 403
   #    return super(HttpResponseForbidden, cls).force_type(rv, environ)


class HttpResponseUnauthorized(Response):
   default_status = 401

class HttpResponseBadRequest(Response):
   default_status = 400

class HttpResponseUnprocessableEntity(Response):
   default_status = 422
   content_type = "application/json"
   # @classmethod
   # def force_type(cls, rv, environ=None):
   #    if isinstance(rv, dict):
   #       rv.status_code = 403
   #    return super(HttpResponseBadRequest, cls).force_type(rv, environ)

class HttpResponseInternalServerError(Response):
   default_status = 500
   content_type = "application/json"
