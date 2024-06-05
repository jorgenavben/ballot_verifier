# -*- encoding: utf-8 -*-
"""
KERI
keri.app.verify module
"""

import falcon
from hio.core import http
from keri import help, kering
from keri.app import oobiing
from keri.core import coring
from keri.db import basing
from keri.help import helping

logger = help.ogler.getLogger()

def setupVerifier(hby, hab, httpPort=5632):
    doers = []

    oobiery = oobiing.Oobiery(hby=hby)
    app = falcon.App(cors_enable=True)

    oobiEnd = OOBIEnd(hby=hby)
    app.add_route("/oobi", oobiEnd)
    verificationEnd = VerificationEnd(hab=hab)
    app.add_route("/verify", verificationEnd)

    server = http.Server(port=httpPort, app=app)
    httpServerDoer = http.ServerDoer(server=server)

    doers.extend([httpServerDoer, *oobiery.doers])

    return app, doers


class OOBIEnd:
    def __init__(self, hby):
        self.hby = hby

    def on_get(self, req, resp):
        oobi = getRequiredParam(req.get_media(), 'oobi')

        result = self.hby.db.roobi.get(keys=(oobi))
        if result:
            resp.status = falcon.HTTP_200
            resp.text = result.cid
        else:
            resp.status = falcon.HTTP_404

    def on_post(self, req, resp):
        oobi = getRequiredParam(req.get_media(), 'oobi')
        obr = basing.OobiRecord(date=helping.nowIso8601())
        self.hby.db.oobis.put(keys=(oobi,), val=obr)
        resp.status = falcon.HTTP_202


class VerificationEnd:
    def __init__(self, hab):
        self.hab = hab

    def on_post(self, req, resp):
        body = req.get_media()
        aid = getRequiredParam(body, 'aid')
        signature = getRequiredParam(body, 'signature')
        payload = getRequiredParam(body, 'payload')

        try:
            kever = self.hab.kevers[aid]
        except KeyError as e:
            resp.status = falcon.HTTP_404
            resp.text = f"Unknown AID {aid}, please ensure corresponding OOBI has been resolved"
            return
        verfers = kever.verfers

        try:
            cigar = coring.Cigar(qb64=signature)
        except (ValueError, kering.ShortageError) as e:
            resp.status = falcon.HTTP_400
            resp.text = f"Invalid signature format (single sig only supported) - error: {e}"
            return

        # Single sig support
        cigar.verfer = verfers[0]
        if cigar.verfer.verify(cigar.raw, str.encode(payload)):
            resp.status = falcon.HTTP_200
            resp.text = "Verification successful"
        else:
            resp.status = falcon.HTTP_400
            resp.text = f"Signature is invalid"


def getRequiredParam(body, name):
    param = body.get(name)
    if param is None:
        raise falcon.HTTPBadRequest(description=f"required field '{name}' missing from request")

    return param
