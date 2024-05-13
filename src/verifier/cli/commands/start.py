# -*- encoding: utf-8 -*-
"""
Verifier command line interface
"""
import argparse
import logging

from keri import __version__
from keri import help
from keri.app import directing, habbing, keeping
from keri.app.cli.common import existing

from ... import verify

d = "Runs Cardano Ballot Keri verifier controller"
parser = argparse.ArgumentParser(description=d)
parser.set_defaults(handler=lambda args: launch(args))
parser.add_argument('-V', '--version',
                    action='version',
                    version=__version__,
                    help="Prints out version of script runner.")
parser.add_argument('-H', '--http',
                    action='store',
                    default=5631,
                    help="Local port number the HTTP server listens on. Default is 5666.")
parser.add_argument('-n', '--name',
                    action='store',
                    default="verifier",
                    help="Name of controller. Default is verifier.")
parser.add_argument('--base', '-b', help='additional optional prefix to file location of KERI keystore',
                    required=False, default="")
parser.add_argument('--alias', '-a', help='human readable alias for the new identifier prefix', required=True)
parser.add_argument('--passcode', '-p', help='22 character encryption passcode for keystore (is not saved)',
                    dest="bran", default=None)  # passcode => bran


def launch(args):
    help.ogler.level = logging.CRITICAL
    help.ogler.reopen(name=args.name, temp=True, clear=True)

    logger = help.ogler.getLogger()

    logger.info("\n******* Starting Verifier for %s listening: http/%s "
                ".******\n\n", args.name, args.http)

    runVerifier(name=args.name,
                base=args.base,
                alias=args.alias,
                bran=args.bran,
                http=int(args.http))

    logger.info("\n******* Ended Verifier for %s listening: http/%s "
                ".******\n\n", args.name, args.http)


def runVerifier(name="verifier", base="", alias="verifier", bran="", http=5666, expire=0.0):
    """
    Setup and run one verifier
    """

    ks = keeping.Keeper(name=name,
                        base=base,
                        temp=False,
                        reopen=True)

    aeid = ks.gbls.get('aeid')

    if aeid is None:
        hby = habbing.Habery(name=name, base=base, bran=bran)
    else:
        hby = existing.setupHby(name=name, base=base, bran=bran)

    hbyDoer = habbing.HaberyDoer(habery=hby)

    hab = hby.habByName(name=alias)
    if hab is None:
        hab = hby.makeHab(name=alias, transferable=False)

    doers = [hbyDoer]
    doers.extend(verify.setupVerifier(hby=hby,
                                         hab=hab,
                                         httpPort=http))

    directing.runController(doers=doers, expire=expire)
