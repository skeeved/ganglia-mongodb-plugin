#!/usr/bin/env python
"""
"""
import io
from os.path import expanduser
from subprocess import Popen, PIPE
import json
from bson import json_util
import re
from time import time
import logging
import logging.handlers
import socket

__author__ = 'Adam Lanier (skeeved@skeeved.org)'
__version__ = '0.0.1'
__copyright__ = 'Copyright 2017 Adam Lanier'

SERVER_STATUS_CMD = ['mongo', '--host', 'localhost', '--quiet', '--eval', 'printjson(db.serverStatus())']
REPL_STATUS_CMD = ['mongo', '--host', 'localhost', '--quiet', '--eval', 'printjson(rs.status())']
MAX_DATA_AGE = 5    # seconds

descriptors = None
last_data = None
logger = None

def get_response(cmd):
    data = None
    p = Popen(cmd,
        bufsize=16384,
        close_fds=True,
        cwd=expanduser('~'),
        stdout=PIPE,
        stderr=PIPE
        )
    (data, err) = p.communicate()
    if err:
        data = err
    else:
        # remove objects
        data = re.sub('(?:NumberLong|ISODate|ObjectId)\((.*)\)', r'\1', data)
        data = re.sub('(?:Timestamp)\((.*)\)', r'"(\1)"', data)
        data = json.loads(data, object_hook=json_util.object_hook)
    return data

def metric_init(params):
    """
    Skeleton metric descriptor:
    {
        'name': '',
        'call_back': '',
        'time_max': max_data_age,
        'value_type': '',
        'units': '',
        'slope': 'both',
        'format': '',
        'description': '',
        'groups': GROUPS
        }
    """
    TIME_MAX = 60
    GROUPS = 'mongodb'

    global descriptors, logger

    logger = logging.getLogger("gmond-mongo")
    logger.setLevel(logging.INFO)

    slh = logging.handlers.SysLogHandler(
        '/dev/log',
        facility=logging.handlers.SysLogHandler.LOG_SYSLOG,
        socktype=socket.SOCK_DGRAM
        )
    slh.setLevel(logging.INFO)
    short_format = logging.Formatter('%(name)s: %(message)s')
    slh.setFormatter(short_format)
    logger.addHandler(slh)
    logger.debug('metric_init called with arg: {}'.format(params))

    max_data_age = TIME_MAX
    try:
        if 'time_max' in params:
            max_data_age = params['time_max']
    except TypeError as e:
        logger.error("error: {}".format(e))

    try:

        descriptors = [
            {
                'name': 'mongodb_conn_current',
                'call_back': metric_handler,
                'time_max': max_data_age,
                'value_type': 'int',
                'units': 'Connections',
                'slope': 'both',
                'format': '%i',
                'description': 'Current Connections',
                'groups': GROUPS
            },
            {
                'name': 'mongodb_conn_available',
                'call_back': metric_handler,
                'time_max': max_data_age,
                'value_type': 'int',
                'units': 'Connections',
                'slope': 'both',
                'format': '%i',
                'description': 'Current Available Connections',
                'groups': GROUPS
            },
            {
                'name': 'mongodb_conn_total',
                'call_back': metric_handler,
                'time_max': max_data_age,
                'value_type': 'int',
                'units': 'Connections',
                'slope': 'both',
                'format': '%i',
                'description': 'Current Total Connections',
                'groups': GROUPS
            },
            {
                'name': 'mongodb_net_bytes_in',
                'call_back': metric_handler,
                'time_max': max_data_age,
                'value_type': 'int',
                'units': 'Bytes/Sec',
                'slope': 'positive',
                'format': '%i',
                'description': 'Bytes Received',
                'groups': GROUPS
            },
            {
                'name': 'mongodb_net_bytes_out',
                'call_back': metric_handler,
                'time_max': max_data_age,
                'value_type': 'int',
                'units': 'Bytes/Sec',
                'slope': 'positive',
                'format': '%i',
                'description': 'Bytes Sent',
                'groups': GROUPS
            },
            {
                'name': 'mongodb_op_count_insert',
                'call_back': metric_handler,
                'time_max': max_data_age,
                'value_type': 'int',
                'units': 'Operations',
                'slope': 'both',
                'format': '%i',
                'description': 'Oplog Inserts',
                'groups': GROUPS
            },
            {
                'name': 'mongodb_op_count_query',
                'call_back': metric_handler,
                'time_max': max_data_age,
                'value_type': 'int',
                'units': 'Operations',
                'slope': 'both',
                'format': '%i',
                'description': 'Oplog Queries',
                'groups': GROUPS
            },
            {
                'name': 'mongodb_op_count_update',
                'call_back': metric_handler,
                'time_max': max_data_age,
                'value_type': 'int',
                'units': 'Operations',
                'slope': 'both',
                'format': '%i',
                'description': 'Oplog Updates',
                'groups': GROUPS
            },
            {
                'name': 'mongodb_op_count_delete',
                'call_back': metric_handler,
                'time_max': max_data_age,
                'value_type': 'int',
                'units': 'Operations',
                'slope': 'both',
                'format': '%i',
                'description': 'Oplog Deletes',
                'groups': GROUPS
            },
            {
                'name': 'mongodb_op_count_getmore',
                'call_back': metric_handler,
                'time_max': max_data_age,
                'value_type': 'int',
                'units': 'Operations',
                'slope': 'both',
                'format': '%i',
                'description': 'Oplog Getmore',
                'groups': GROUPS
            },
            {
                'name': 'mongodb_op_count_command',
                'call_back': metric_handler,
                'time_max': max_data_age,
                'value_type': 'int',
                'units': 'Operations',
                'slope': 'both',
                'format': '%i',
                'description': 'Oplog Command',
                'groups': GROUPS
            },
            {
                'name': 'mongodb_mem_resident',
                'call_back': metric_handler,
                'time_max': max_data_age,
                'value_type': 'int',
                'units': 'KB',
                'slope': 'both',
                'format': '%i',
                'description': 'Memory Resident',
                'groups': GROUPS
            },
                    {
                'name': 'mongodb_mem_virtual',
                'call_back': metric_handler,
                'time_max': max_data_age,
                'value_type': 'int',
                'units': 'KB',
                'slope': 'both',
                'format': '%i',
                'description': 'Memory VIrtual',
                'groups': GROUPS
            },
                    {
                'name': 'mongodb_mem_mapped',
                'call_back': metric_handler,
                'time_max': max_data_age,
                'value_type': 'int',
                'units': 'KB',
                'slope': 'both',
                'format': '%i',
                'description': 'Memory Mapped',
                'groups': GROUPS
            },
                    {
                'name': 'mongodb_mem_mapped_with_journal',
                'call_back': metric_handler,
                'time_max': max_data_age,
                'value_type': 'int',
                'units': 'KB',
                'slope': 'both',
                'format': '%i',
                'description': 'Memory with Journal',
                'groups': GROUPS
            },
        ]

        return descriptors
    except Exception as e:
        logger.exception("metric_init exception: {}".format(e))

def metric_cleanup():
    global logger

    logger.debug("metric_cleanup called")

def metric_handler(name):
    global last_data, logger

    now = time()
    data = 0
    try:
        if not last_data or last_data['timestamp'] < (now - MAX_DATA_AGE):
            server_status = get_response(SERVER_STATUS_CMD)
            #repl_status = get_response(REPL_STATUS_CMD)
            last_data = {
                'timestamp': now,
                'status': {
                    'server': server_status,
                    #'repl': repl_status
                }
            }
        else:
            # using cached data
            server_status = last_data['status']['server']
            #repl_status = last_data['status']['repl']

        if name == 'mongodb_conn_current':
            data = server_status['connections']['current']
        elif name == 'mongodb_conn_available':
            data = server_status['connections']['available']
        elif name == 'mongodb_conn_total':
            data = server_status['connections']['totalCreated']
        elif name == 'mongodb_net_bytes_in':
            data = server_status['network']['bytesIn']
        elif name == 'mongodb_net_bytes_out':
            data = server_status['network']['bytesOut']
        elif name == 'mongodb_op_count_insert':
            data = server_status['opcounters']['insert']
        elif name == 'mongodb_op_count_query':
            data = server_status['opcounters']['query']
        elif name == 'mongodb_op_count_update':
            data = server_status['opcounters']['update']
        elif name == 'mongodb_op_count_delete':
            data = server_status['opcounters']['delete']
        elif name == 'mongodb_op_count_getmore':
            data = server_status['opcounters']['getmore']
        elif name == 'mongodb_op_count_command':
            data = server_status['opcounters']['command']
        elif name == 'mongodb_mem_resident':
            data = server_status['mem']['resident']
        elif name == 'mongodb_mem_virtual':
            data = server_status['mem']['virtual']
        elif name == 'mongodb_mem_mapped':
            data = server_status['mem']['mapped']
        elif name == 'mongodb_mem_mapped_with_journal':
            data = server_status['mem']['mappedWithJournal']

        logger.debug("metric_handler returning: name={} val={}".format(
            name,
            data))
        return data
    except Exception as e:
        logger.exception("metric_handler exception: {}".format(e))
        return 0

if __name__ == '__main__':
    from time import sleep
    from datetime import datetime
    metric_init({'time_max': '60'})
    while True:
        print "--- {}".format(datetime.ctime(datetime.utcnow()))
        print "Conn Current: {}".format(metric_handler('mongodb_conn_current'))
        print "OP Insert:    {}".format(metric_handler('mongodb_op_count_insert'))
        print "OP Query:     {}".format(metric_handler('mongodb_op_count_query'))
        print "OP Update:    {}".format(metric_handler('mongodb_op_count_update'))
        print "MEM Resident: {}".format(metric_handler('mongodb_mem_resident'))
        print "MEM Virtual:  {}".format(metric_handler('mongodb_mem_virtual'))
        sleep(1)
