# ganglia-mongodb-plugin
Ganglia plugin for monitoring mongodb clusters

This plugin has been tested on Centos 7 with ganglia 3.7.2 and mongodb 3.4.6.

Note that the EPEL RPM packages use `/var/lib/ganglia` as the home directory
for the `ganglia` user but they don't create that directory. You'll need to
create that directory if it doesn't exist.

## Statistics

This plugin currently collects the following statistics:

* mongodb_conn_current
* mongodb_conn_available
* mongodb_conn_total
* mongodb_net_bytes_in
* mongodb_net_bytes_out
* mongodb_op_count_insert
* mongodb_op_count_query
* mongodb_op_count_update
* mongodb_op_count_delete
* mongodb_op_count_getmore
* mongodb_op_count_command
* mongodb_mem_resident
* mongodb_mem_virtual
* mongodb_mem_mapped
* mongodb_mem_mapped_with_journal

## Installation

* Copy mongodb.py to /usr/lib64/ganglia/python_modules
* Copy mongodb.pyconf to /etc/ganglia/conf.d

## AUTHOR

Adam Lanier <skeeved@skeeved.org>
