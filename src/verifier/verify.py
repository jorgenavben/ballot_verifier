# -*- encoding: utf-8 -*-
"""
KERI
keri.app.verify module
"""

import falcon
import keri.app.oobiing
from hio.base import doing
from hio.core import http
from hio.core.tcp import serving
from hio.help import decking
from keri import help
from keri.app import directing, storing, httping, forwarding, oobiing
from keri.core import eventing, parsing, routing, indexing
from keri.db import basing
from keri.end import ending
from keri.peer import exchanging
from keri.vdr import verifying, viring
from keri.vdr.eventing import Tevery

logger = help.ogler.getLogger()


def setupVerifier(hby, alias="verifier", mbx=None, tcpPort=5631, httpPort=5632):
    cues = decking.Deck()
    doers = []

    # make hab
    hab = hby.habByName(name=alias)
    if hab is None:
        hab = hby.makeHab(name=alias, transferable=False)

    reger = viring.Reger(name=hab.name, db=hab.db, temp=False)
    verfer = verifying.Verifier(hby=hby, reger=reger)

    mbx = mbx if mbx is not None else storing.Mailboxer(name=alias, temp=hby.temp)
    forwarder = forwarding.ForwardHandler(hby=hby, mbx=mbx)
    exchanger = exchanging.Exchanger(db=hby.db, handlers=[forwarder])
    clienter = httping.Clienter()
    oobiery = keri.app.oobiing.Oobiery(hby=hby, clienter=clienter)

    app = falcon.App(cors_enable=True)
    ending.loadEnds(app=app, hby=hby, default=hab.pre)
    oobiRes = oobiing.loadEnds(app=app, hby=hby, prefix="/ext")
    rep = storing.Respondant(hby=hby, mbx=mbx)

    rvy = routing.Revery(db=hby.db, cues=cues)
    kvy = eventing.Kevery(db=hby.db,
                          lax=True,
                          local=False,
                          rvy=rvy,
                          cues=cues)
    kvy.registerReplyRoutes(router=rvy.rtr)

    tvy = Tevery(reger=verfer.reger,
                 db=hby.db,
                 local=False,
                 cues=cues)

    tvy.registerReplyRoutes(router=rvy.rtr)
    parser = parsing.Parser(framed=True,
                            kvy=kvy,
                            tvy=tvy,
                            exc=exchanger,
                            rvy=rvy)

    server = http.Server(port=httpPort, app=app)
    httpServerDoer = http.ServerDoer(server=server)

    # setup doers
    regDoer = basing.BaserDoer(baser=verfer.reger)

    server = serving.Server(host="", port=tcpPort)
    serverDoer = serving.ServerDoer(server=server)

    directant = directing.Directant(hab=hab, server=server, verifier=verfer)

    witStart = BackerStart(hab=hab, parser=parser, cues=cues,
                            kvy=kvy, tvy=tvy, rvy=rvy, exc=exchanger, replies=rep.reps,
                            responses=rep.cues)

    doers.extend(oobiRes)
    doers.extend([regDoer, exchanger, directant, serverDoer, httpServerDoer, rep, witStart, *oobiery.doers])

    return doers


class BackerStart(doing.DoDoer):
    """ Doer to print backer prefix after initialization

    """

    def __init__(self, hab, parser, kvy, tvy, rvy, exc, cues=None, replies=None, responses=None, queries=None, **opts):
        self.hab = hab
        self.parser = parser
        self.kvy = kvy
        self.tvy = tvy
        self.rvy = rvy
        self.exc = exc
        self.queries = queries if queries is not None else decking.Deck()
        self.replies = replies if replies is not None else decking.Deck()
        self.responses = responses if responses is not None else decking.Deck()
        self.cues = cues if cues is not None else decking.Deck()

        doers = [doing.doify(self.start), doing.doify(self.msgDo),
                 doing.doify(self.exchangerDo), doing.doify(self.escrowDo), doing.doify(self.cueDo)]
        super().__init__(doers=doers, **opts)

    def start(self, tymth=None, tock=0.0):
        """ Prints backer name and prefix

        Parameters:
            tymth (function): injected function wrapper closure returned by .tymen() of
                Tymist instance. Calling tymth() returns associated Tymist .tyme.
            tock (float): injected initial tock value

        """
        self.wind(tymth)
        self.tock = tock
        _ = (yield self.tock)

        while not self.hab.inited:
            yield self.tock

        print("Backer", self.hab.name, "ready", self.hab.pre)

    def msgDo(self, tymth=None, tock=0.0):
        """
        Returns doifiable Doist compatibile generator method (doer dog) to process
            incoming message stream of .kevery

        Parameters:
            tymth (function): injected function wrapper closure returned by .tymen() of
                Tymist instance. Calling tymth() returns associated Tymist .tyme.
            tock (float): injected initial tock value

        Usage:
            add result of doify on this method to doers list
        """
        self.wind(tymth)
        self.tock = tock
        _ = (yield self.tock)

        if self.parser.ims:
            logger.info("Client %s received:\n%s\n...\n", self.kvy, self.parser.ims[:1024])
        done = yield from self.parser.parsator()  # process messages continuously
        return done  # should nover get here except forced close

    def escrowDo(self, tymth=None, tock=0.0):
        """
         Returns doifiable Doist compatibile generator method (doer dog) to process
            .kevery and .tevery escrows.

        Parameters:
            tymth (function): injected function wrapper closure returned by .tymen() of
                Tymist instance. Calling tymth() returns associated Tymist .tyme.
            tock (float): injected initial tock value

        Usage:
            add result of doify on this method to doers list
        """
        self.wind(tymth)
        self.tock = tock
        _ = (yield self.tock)

        while True:
            self.kvy.processEscrows()
            self.rvy.processEscrowReply()
            if self.tvy is not None:
                self.tvy.processEscrows()
            self.exc.processEscrow()

            yield

    def cueDo(self, tymth=None, tock=0.0):
        """
         Returns doifiable Doist compatibile generator method (doer dog) to process
            .kevery.cues deque

        Doist Injected Attributes:
            g.tock = tock  # default tock attributes
            g.done = None  # default done state
            g.opts

        Parameters:
            tymth is injected function wrapper closure returned by .tymen() of
                Tymist instance. Calling tymth() returns associated Tymist .tyme.
            tock is injected initial tock value

        Usage:
            add result of doify on this method to doers list
        """
        self.wind(tymth)
        self.tock = tock
        _ = (yield self.tock)

        while True:
            while self.cues:
                cue = self.cues.popleft()
                cueKin = cue["kin"]
                if cueKin == "stream":
                    self.queries.append(cue)
                else:
                    self.responses.append(cue)
                yield self.tock
            yield self.tock

    def exchangerDo(self, tymth=None, tock=0.0):
        """
        Returns doifiable Doist compatibile generator method (doer dog) to process
            .exc responses and pass them on to the HTTPRespondant

        Parameters:
            tymth (function): injected function wrapper closure returned by .tymen() of
                Tymist instance. Calling tymth() returns associated Tymist .tyme.
            tock (float): injected initial tock value

        Usage:
            add result of doify on this method to doers list
        """
        self.wind(tymth)
        self.tock = tock
        _ = (yield self.tock)

        while True:
            for rep in self.exc.processResponseIter():
                self.replies.append(rep)
                yield  # throttle just do one cue at a time
            yield


class ResolveOOBIEnd:

    def __init__(self, hby):
        self.hby = hby

    def on_post(self, req, resp):
        try:
            oobiUrl = req.media.get('oobiUrl', None)
        except Exception as e:
            resp.status = falcon.HTTP_400
            resp.text = f"Error: {e}"
            return

        if not oobiUrl:
            resp.status = falcon.HTTP_400
            resp.text = "Missing required parameters"
            return

        result = self.hby.db.eoobi.get(keys=(oobiUrl,))

        if result is not None:
            resp.status = falcon.HTTP_200
            resp.text = f"OOBI resolved successfully: {result}"
        else:
            resp.status = falcon.HTTP_404
            resp.text = f"OOBI resolution failed for given url: {oobiUrl}"


class VerificationEnd:
    def __init__(self, hab):
        self.hab = hab

    def on_post(self, req, resp):
        try:
            oobi = req.media.get('oobi', None)
            signature = req.media.get('signature', None)
        except Exception as e:
            resp.status = falcon.HTTP_400
            resp.text = f"Error: {e}"
            return

        if not all([oobi, signature]):
            resp.status = falcon.HTTP_400
            resp.text = "Missing required parameters"
            return

        kever = self.hab.kevers[oobi]
        verfers = kever.verfers

        siger = indexing.Siger(qb64=signature)

        if siger.index >= len(verfers):
            resp.status = falcon.HTTP_400
            resp.text = f"Index = {siger.index} too large for keys."
            return

        siger.verfer = verfers[siger.index]

        if siger.verfer.verify(siger.raw, signature):
            resp.status = falcon.HTTP_200
            resp.text = "Verification successful"
        else:
            resp.status = falcon.HTTP_400
            resp.text = f"Signature {siger.index + 1} is invalid."
