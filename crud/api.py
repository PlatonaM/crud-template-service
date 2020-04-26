"""
   Copyright 2020 Yann Dumont

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""

__all__ = ("Collection", "Resource")


from .logger import getLogger
from .configuration import crud_conf
import snorkels
import falcon
import json
import uuid


logger = getLogger(__name__.split(".", 1)[-1])


def reqDebugLog(req):
    logger.debug("method='{}' path='{}' content_type='{}'".format(req.method, req.path, req.content_type))


def reqErrorLog(req, ex):
    logger.error("method='{}' path='{}' - {}".format(req.method, req.path, ex))


class Collection:
    def __init__(self, kvs: snorkels.KeyValueStore):
        self.__kvs = kvs

    def on_get(self, req: falcon.request.Request, resp: falcon.response.Response):
        reqDebugLog(req)
        try:
            if crud_conf.Endpoint.full_collection:
                data = dict()
                for key in self.__kvs.keys():
                    data[key.decode()] = self.__kvs.get(key).decode()
            else:
                data = [key.decode() for key in self.__kvs.keys()]
            resp.status = falcon.HTTP_200
            resp.content_type = falcon.MEDIA_JSON
            resp.body = json.dumps(data)
        except Exception as ex:
            resp.status = falcon.HTTP_500
            reqErrorLog(req, ex)

    def on_post(self, req: falcon.request.Request, resp: falcon.response.Response):
        reqDebugLog(req)
        if not crud_conf.Endpoint.allow_post:
            resp.status = falcon.HTTP_405
            reqErrorLog(req, "method disabled in configuration")
        else:
            if not req.content_type == crud_conf.Endpoint.content_type:
                resp.status = falcon.HTTP_415
                reqErrorLog(req, "wrong content type - '{}'".format(req.content_type))
            else:
                try:
                    data = req.bounded_stream.read()
                    r_id = str(uuid.uuid4())
                    self.__kvs.set(r_id, data)
                    resp.content_type = falcon.MEDIA_JSON
                    resp.body = json.dumps({"resource": r_id})
                    resp.status = falcon.HTTP_200
                except Exception as ex:
                    resp.status = falcon.HTTP_500
                    reqErrorLog(req, ex)


class Resource:
    def __init__(self, kvs: snorkels.KeyValueStore):
        self.__kvs = kvs

    def on_get(self, req: falcon.request.Request, resp: falcon.response.Response, resource):
        reqDebugLog(req)
        try:
            data = self.__kvs.get(resource)
            resp.status = falcon.HTTP_200
            resp.content_type = crud_conf.Endpoint.content_type
            resp.body = data.decode()
        except snorkels.GetError as ex:
            resp.status = falcon.HTTP_404
            reqErrorLog(req, ex)
        except Exception as ex:
            resp.status = falcon.HTTP_500
            reqErrorLog(req, ex)

    def on_put(self, req: falcon.request.Request, resp: falcon.response.Response, resource):
        reqDebugLog(req)
        if not req.content_type == crud_conf.Endpoint.content_type:
            resp.status = falcon.HTTP_415
            reqErrorLog(req, "wrong content type - '{}'".format(req.content_type))
        else:
            try:
                data = req.bounded_stream.read()
                self.__kvs.set(resource, data)
                resp.status = falcon.HTTP_200
            except Exception as ex:
                resp.status = falcon.HTTP_500
                reqErrorLog(req, ex)

    def on_delete(self, req: falcon.request.Request, resp: falcon.response.Response, resource):
        reqDebugLog(req)
        try:
            self.__kvs.delete(resource)
            resp.status = falcon.HTTP_200
        except snorkels.DeleteError as ex:
            resp.status = falcon.HTTP_404
            reqErrorLog(req, ex)
        except Exception as ex:
            resp.status = falcon.HTTP_500
            reqErrorLog(req, ex)
