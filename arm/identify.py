#!/usr/bin/python3

import os
import sys # noqa # pylint: disable=unused-import
import logging
import classes # noqa # pylint: disable=unused-import
import getmovietitle
import getvideotype
import utils

from config import cfg


def identify(disc, logfile):
    """Identify disc attributes"""

    logging.debug("Identification starting: " + str(disc))

    # If UDF CHeck is on
    # if cfg['ARM_CHECK_UDF']:

    logging.info("Mounting disc to: " + str(disc.mountpoint))

    if not os.path.exists(str(disc.mountpoint)):
        os.makedirs(str(disc.mountpoint))

    os.system("mount " + disc.devpath)
    # Check to make sure it's not a data disc
    if disc.disctype == "music":
        logging.debug("Disc is music.  Skipping identification")
    elif os.path.isdir(disc.mountpoint + "/VIDEO_TS"):
        logging.debug("Found: " + disc.mountpoint + "/VIDEO_TS")
        disc.disctype = "dvd"
    elif os.path.isdir(disc.mountpoint + "/video_ts"):
        logging.debug("Found: " + disc.mountpoint + "/video_ts")
        disc.disctype = "dvd"
    elif os.path.isdir(disc.mountpoint + "/BDMV"):
        logging.debug("Found: " + disc.mountpoint + "/BDMV")
        disc.disctype = "bluray"
    elif os.path.isdir(disc.mountpoint + "/HVDVD_TS"):
        logging.debug("Found: " + disc.mountpoint + "/HVDVD_TS")
        # do something here
    elif utils.find_file("HVDVD_TS", disc.mountpoint):
        logging.debug("Found file: HVDVD_TS")
        # do something here too
    else:
        discSet = False
        for file in os.listdir(disc.mountpoint):
            if file.endswith(".mp3") or file.endswith(".m3u"):
                disc.disctype = "mp3CD"
                discSet=True
        if not discSet:
            logging.debug("Did not find valid dvd/bd files. Changing disctype to 'data'")
            disc.disctype = "data"

    if disc.disctype in ["dvd", "bluray"]:

        logging.info("Disc identified as video")

        if cfg["GET_VIDEO_TITLE"]:

            logging.info("Getting movie title...")
            disc.videotitle, disc.videoyear = getmovietitle.main(disc)

            if disc.hasnicetitle:
                logging.info("Getting video type...")
                disc.videotype, disc.videoyear = getvideotype.main(disc)
            else:
                logging.info("Disc does not have a nice title.  Skipping video type identification and setting title=title_unkonwn")
                disc.videotitle = "title_unknown"

            if not cfg['VIDEOTYPE'].lower() == "auto":
                logging.debug("Overriding videotype with value in VIDEOTYPE config parameter: " + cfg['VIDEOTYPE'].lower())
                disc.videotype = cfg['VIDEOTYPE'].lower()

            logging.info("Disc title: " + str(disc.videotitle) + " : " + str(disc.videoyear) + " : " + str(disc.videotype))
            logging.debug("Identification complete: " + str(disc))

    if not disc.disctype == "mp3CD":
        os.system("umount " + disc.devpath)
