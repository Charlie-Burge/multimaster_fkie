#!/usr/bin/env python
# Original code from https://github.com/jhu-lcsr-forks/fkie_multimaster/tree/param-sync
# adapt to change only local ROS Parameter Server

import rospy

from fkie_master_discovery.common import masteruri_from_master
from fkie_multimaster_msgs.msg import MasterState

def master_changed(msg, cb_args):
    master_proxies, param_cache, __add_ns = cb_args
    master_proxies[msg.master.name] = rospy.MasterProxy(msg.master.uri)

    for name_from, master_from in master_proxies.items():
        for name_to, master_to in master_proxies.items():
            if name_to != name_from:
                rospy.logdebug("Getting params from...".format(name_from))
                params_from = master_from['/']
                rospy.logdebug("Got {} params.".format(len(params_from)))
                if name_to in params_from:
                    del params_from[name_to]
                if '/'+name_to in params_from:
                    del params_from['/'+name_to]
                rospy.logdebug("Syncing params from {} to {}...".format(name_from, name_to))
                if __add_ns:
                    _ns = name_from
                else:
                    _ns = ''
                if param_cache.get(_ns, None) != params_from:
                    param_cache[_ns] = params_from
                    master_to['/'+_ns] = params_from
                    rospy.logdebug("Done syncing params from {} to {}.".format(name_from, name_to))
                else:
                    rospy.logdebug("Params have not changed from {} to {}.".format(name_from, name_to))


def main():
    rospy.init_node('param_sync')

    master_proxies = dict()
    param_cache = dict()

    __add_ns = rospy.get_param('~add_ns', False)
    sub = rospy.Subscriber(
        'master_discovery/changes', 
        MasterState, 
        master_changed, 
        callback_args=(master_proxies, param_cache, __add_ns)
    )

    rospy.spin()

if __name__ == '__main__':
    main()

