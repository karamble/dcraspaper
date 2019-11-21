#!/usr/bin/python
# -*- coding:utf-8 -*-
import sys
import os
import urllib2
import json
import datetime

picdir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'pic')
libdir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'lib')
if os.path.exists(libdir):
    sys.path.append(libdir)

import logging
from waveshare_epd import epd2in13_V2
import time
from PIL import Image,ImageDraw,ImageFont
import traceback

from ascii_graph import Pyasciigraph

logging.basicConfig(level=logging.INFO)

try:
    logging.info(str(datetime.datetime.now()) + " - Decred Raspberry Pi e-Paper Dashboard")

    epd = epd2in13_V2.EPD()
    epd.init(epd.FULL_UPDATE)
    epd.Clear(0xFF)

    # Fonts to drraw on the image
    font10 = ImageFont.truetype(os.path.join(picdir, 'SourceSansPro-Regular.ttf'), 10)
    font12 = ImageFont.truetype(os.path.join(picdir, 'SourceSansPro-Regular.ttf'), 12)
    font15 = ImageFont.truetype(os.path.join(picdir, 'SourceSansPro-Regular.ttf'), 15)
    font24 = ImageFont.truetype(os.path.join(picdir, 'SourceSansPro-Regular.ttf'), 24)
    fontgraph10 = ImageFont.truetype(os.path.join(picdir, 'SourceCodePro-Regular.ttf'), 10)
    fontgraph12 = ImageFont.truetype(os.path.join(picdir, 'SourceCodePro-Regular.ttf'), 12)

    # read logo bmp file 
    logging.info(str(datetime.datetime.now()) + " - Show Decred Logo")
    image = Image.open(os.path.join(picdir, '2in13-v2-logo.bmp'))
    epd.display(epd.getbuffer(image))

    logging.info(str(datetime.datetime.now()) + " - Show Stakey Image")
    initlog_image = Image.open(os.path.join(picdir, '2in13-v2-stakeyloader.bmp'))
    initlog_draw = ImageDraw.Draw(initlog_image)

    epd.init(epd.FULL_UPDATE)
    epd.displayPartBaseImage(epd.getbuffer(initlog_image))

    while True:
       logging.info(str(datetime.datetime.now()) + " - Connecting dcrdata")
       blockheight_url = 'https://dcrdata.decred.org/api/block/best/height'
       response = urllib2.urlopen(blockheight_url)
       blockheight = response.read()

       stakeinfo_url = urllib2.urlopen('https://dcrdata.decred.org/api/block/best/pos')
       stakeinfo_json = json.loads(stakeinfo_url.read())
       stakediff = stakeinfo_json['stakediff'] 
       stakediff_2decimals = "{:3.2f}".format(stakediff)

       exchange_url = urllib2.urlopen('https://dcrdata.decred.org/api/exchanges')
       exchange_json = json.loads(exchange_url.read())
       usd_price = exchange_json['price']
       usd_price_2decimals = "{:3.2f}".format(usd_price)

       stakereward_url = urllib2.urlopen('https://dcrdata.decred.org/api/block/best/subsidy')
       stakereward_json = json.loads(stakereward_url.read())
       stakereward = float(stakereward_json['stake_reward'])/100000000
       stakereward_2decimals = "{:1.3f}".format(stakereward)

       txcount_url = urllib2.urlopen('https://dcrdata.decred.org/api/block/best/tx/count')
       txcount_json = json.loads(txcount_url.read())
       txcount = txcount_json['tx']
       stxcount = txcount_json['stx']

       # partitial display update
       logging.info(str(datetime.datetime.now()) + " - Show dcrdata infos")
       epd.init(epd.PART_UPDATE)
       initlog_draw.rectangle((150, 0, 250, 122), fill = 255)
       initlog_draw.text((150, 0),  'Block: ' + str(blockheight) + '\n tx: ' + str(txcount) + ' / stx: ' + str(stxcount) + '\n Ticket: ' + str(stakediff_2decimals) + '\n Reward: ' + str(stakereward_2decimals) + '\n Price $: ' + str(usd_price_2decimals), font = font15, fill = 1)
       epd.displayPartial(epd.getbuffer(initlog_image))
       time.sleep(5)

       logging.info(str(datetime.datetime.now()) + " - Connecting politeia")
       politeiactivevote_url = urllib2.urlopen('https://proposals.decred.org/api/v1/proposals/activevote')
       # politeiactivevote_url = urllib2.urlopen('http://dev.urbandigital.de/result.json')

       politeiactivevote_json = json.loads(politeiactivevote_url.read())
       activevote_sum = len(politeiactivevote_json['votes'])
       if activevote_sum > 0:
           logging.info(str(datetime.datetime.now()) + " - " + str(activevote_sum) + " Active votes found. Show politeia dashboard")
           politeia_image = Image.open(os.path.join(picdir, '2in13-v2-politeia.bmp'))
           politeia_draw = ImageDraw.Draw(politeia_image)

           epd.init(epd.FULL_UPDATE)
           epd.displayPartBaseImage(epd.getbuffer(politeia_image))
           for proposals in politeiactivevote_json['votes']:
		for proposal,v1 in proposals.iteritems():
                    if proposal == 'proposal':
                       proposal_name =  v1['name']
                       proposal_token = v1['censorshiprecord']['token']
                       proposal_url = urllib2.urlopen('https://proposals.decred.org/api/v1/proposals/'+proposal_token+'/votestatus')
                       # proposal_url = urllib2.urlopen('http://dev.urbandigital.de/prop.json')
                       logging.info(str(datetime.datetime.now()) + " - Requesting votestatus for proposal "+proposal_name)
                       proposalstatus_json = json.loads(proposal_url.read())
                       proposal_totalvotes = proposalstatus_json['totalvotes']
                       voteresults = []
                       for options in proposalstatus_json['optionsresult']:
                           option_description = options['option']['id']
                           option_votesreceived =  options['votesreceived']
                           voteresults.append(tuple((option_description,option_votesreceived)))
                       # graph generation here
                       graph = Pyasciigraph(
                           line_length=40,
                           graphsymbol='*',
                           separator_length=2,
                           min_graph_length=15,
                           )
                       graphtext = ""
                       for line in graph.graph(proposal_name, voteresults):
                           graphtext = graphtext + line + "\n"
                       epd.init(epd.PART_UPDATE)
                       politeia_draw.rectangle((0, 40, 250, 122), fill = 255)
                       politeia_draw.text((0, 40), graphtext, font = fontgraph10, fill = 1)
                       epd.displayPartial(epd.getbuffer(politeia_image))
                       time.sleep(10)
       else:
           logging.info(str(datetime.datetime.now()) + " - Sleep for 5 minutes")
           time.sleep(300)

    logging.info(str(datetime.datetime.now()) + " - Clear...")
    epd.init(epd.FULL_UPDATE)
    epd.Clear(0xFF)

    logging.info(str(datetime.datetime.now()) + " - Goto Sleep...")
    epd.sleep()

except IOError as e:
    logging.info(e)

except KeyboardInterrupt:
    logging.info(str(datetime.datetime.now()) + " - ctrl + c:")
    epd.init(epd.FULL_UPDATE)
    epd.Clear(0xFF)
    epd2in13_V2.epdconfig.module_exit()
