import re
import time
import discord
import asyncio
import calendar
import logging
import logging.config
from datetime import date, timedelta, datetime
from decimal import Decimal
from dataclasses import dataclass

@dataclass
class mSettings():
    sweeps_channel: str = 'sweeps'
    signature_channel: str = 'signature'
    blocks_channel: str = 'blocks'
    test_channel: str = 'test'
    TradeValue: int = 200000
    SweepsRegex: str = r^(?P<here>@\w+)\s*(?P<ticker>\[\w+\])\s*(?P<optional>\w* OPTION ALERT:)*\s*(?P<month>\w+)\s*((?P<date>\d+,*\s*\d*))*\s*\$(?P<strike>\d+\.*\d*)\s*(?P<type>\w+).*\s*(?P<ask>ASK!*:)\s*(?P<quantity>\d+)\s*@\s*\$\s*(?P<price>\d+\.*\d*)\s*.*(?P<ref>REF=\$\d+\.*\d*).*'	
    # Get your discord token from the discord web client.  Instructions here: https://discordhelp.net/discord-token
    Discord_Token: str = 'YourDscordToken'

# Create logger.
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)
# Create filehandler with desired filename.
fh = logging.FileHandler('sweepPPTWBot_{}.log'.format(datetime.now().strftime('%Y_%m_%d')))
fh.setLevel(logging.DEBUG)
log_formatter = logging.Formatter('%(asctime)s | %(levelname)-8s | %(lineno)04d | %(message)s')
fh.setFormatter(log_formatter)
# Add filehandler to logger.
LOGGER.addHandler(fh)
# LOGGER.addHandler(logging.StreamHandler())

sfile='sweepfile.txt'.format(datetime.now().strftime('%Y_%m_%d'))
sweepfile=open(sfile,'a')

client = discord.Client()

@client.event
async def on_ready():
    LOGGER.info('Logged in as')
    LOGGER.info(client.user.name)
    LOGGER.info(client.user.id)
    LOGGER.info('------')
    for server in client.servers:
        if server.name == 'Profit Planet Pro':
            LOGGER.info ('{0} Server ID: {1}'.format(server.name, server.id))
            for channel in server.channels:
                if channel.name == mSettings.signature_channel:	
                    LOGGER.info ('Signature Channel Name: {0} ID: {1}'.format(channel.name, channel.id))
                if channel.name == mSettings.test_channel:
                    LOGGER.info ('Test Channel Name: {0} ID: {1}'.format(channel.name, channel.id))
                if channel.name == mSettings.blocks_channel:
                    LOGGER.info ('Blocks Channel Name: {0} ID: {1}'.format(channel.name, channel.id))
                if channel.name == mSettings.sweeps_channel:
                    LOGGER.info ('Options sweeps Channel Name: {0} ID: {1}'.format(channel.name, channel.id))
					
@client.event
async def on_message(message):
	if message.channel.name == mSettings.sweeps_channel:
		LOGGER.info ('Sweeps signal received: {}'.format(message.content))
		message_ucase = message.content.upper()
		Sweep = re.search(mSettings.SweepsRegex, message_ucase)
		if Sweep:
			await ProcessSweepSignal(Sweep,message.channel.name)
	elif message.channel.name == mSettings.blocks_channel:
		LOGGER.info ('Blocks signal received: {}'.format(message.content))
		message_ucase = message.content.upper()
		Block = re.search(mSettings.SweepsRegex, message_ucase)
		if Block:
			await ProcessSweepSignal(Block,message.channel.name)
	elif message.channel.name == mSettings.signature_channel:
		LOGGER.info ('Signature signal received: {}'.format(message.content))
		message_ucase = message.content.upper()
		Signature = re.search(mSettings.SweepsRegex, message_ucase)
		if Signature:
			await ProcessSweepSignal(Signature,message.channel.name)


async def ProcessSweepSignal(Sweep,channelname):
	Ticker = Sweep.group('ticker').upper()
	Month = Sweep.group('month').upper()
	if Sweep.group('date'):
		Date = Sweep.group('date')
	else:
		Date = '***'
	Strike = Decimal(Sweep.group('strike'))
	Type = Sweep.group('type').upper()
	Ask = Sweep.group('ask').upper()
	Price = Decimal(Sweep.group('price'))
	Quantity = Decimal(Sweep.group('quantity'))
	TotalValue = Price * Quantity * 100
	if TotalValue > mSettings.TradeValue:
		LOGGER.info ('{}: Total Value of {} {} {} {} ${} strike {}@{} is ${}'.format(channelname,Ticker,Type,Month,Date,Strike,Quantity,Price,TotalValue))
		print ('\n{}: Total Value of {} {} {} {} ${} strike {}@{} is ${}'.format(channelname,Ticker,Type,Month,Date,Strike,Quantity,Price,TotalValue))
		sweepfile.write('{}: {} Total Value of {} {} {} {} ${} strike {}@{} is ${}'.format(channelname,datetime.now().strftime('%A_%m_%d %I:%M%p'),Ticker,Type,Month,Date,Strike,Quantity,Price,TotalValue))
		sweepfile.write("\n")
	elif Month == 'FRI':
		print ('\nFRIDAY: {}: Total Value of {} {} {} {} ${} strike {}@{} is ${}'.format(channelname,Ticker,Type,Month,Date,Strike,Quantity,Price,TotalValue))

		
print('started!')
loop = asyncio.get_event_loop()

try:
    task1 = loop.create_task(client.start(mSettings.Discord_Token, bot=False))
    loop.run_until_complete(asyncio.gather(task1))
except KeyboardInterrupt:
    pass
except Exception as ex:
    LOGGER.error('An unexpected error occurred in the main loop: {}'.format(ex.message))
    sweepfile.close()
    LOGGER.fatal(ex, exc_info=True)
finally:
    loop.run_until_complete(client.logout())
    loop.run_until_complete(client.close())
    time.sleep(3)
    sweepfile.close()
    loop.close()
