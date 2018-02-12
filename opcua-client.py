import sys
sys.path.insert(0, "..")
import logging
import time

# example objects with variables created at opcua-server.py
MY_OBJECTS = ["Device0001", "MyCoolObject"]
MY_VARIABLES = ["MyStringVariable"]

try:
    from IPython import embed
except ImportError:
    import code

    def embed():
        vars = globals()
        vars.update(locals())
        shell = code.InteractiveConsole(vars)
        shell.interact()


from opcua import Client
from opcua import ua


class SubHandler(object):

    """
    Subscription Handler. To receive events from server for a subscription
    data_change and event methods are called directly from receiving thread.
    Do not do expensive, slow or network operation there. Create another
    thread if you need to do such a thing
    """

    def datachange_notification(self, node, val, data):
        print("Python: New data change event", node, val)        

    def event_notification(self, event):
        print("Python: New event", event)


if __name__ == "__main__":
    logging.basicConfig(level=logging.WARN)
    #logger = logging.getLogger("KeepAlive")
    #logger.setLevel(logging.DEBUG)

    client = Client("opc.tcp://localhost:4840/freeopcua/server/")
    # client = Client("opc.tcp://admin@localhost:4840/freeopcua/server/") #connect using a user
    try:
        client.connect()
        print "--->Connected to freeopcuaServer"

        # Client has a few methods to get proxy to UA nodes that should always be in address space such as Root or Objects
        root = client.get_root_node()
        #print("Root node is: ", root)
        objects = client.get_objects_node()
        #print("Objects node is: ", objects)

        # Node objects have methods to read and write node attributes as well as browse or populate address space
        #print("Children of root are: ", root.get_children())

        # get a specific node knowing its node id
        #var = client.get_node(ua.NodeId(1002, 2))
        #var = client.get_node("ns=3;i=2002")
        #var = client.get_node(85)
        #print(var)
        #var.get_data_value() # get value of node as a DataValue object
        #var.get_value() # get value of node as a python builtin
        #var.set_value(ua.Variant([23], ua.VariantType.Int64)) #set node value using explicit data type
        #var.set_value(3.9) # set node value using implicit data type

        # Now getting a variable node using its browse path
        #myvar = root.get_child(["0:Objects", "2:MyObject", "2:MyVariable"])
        #obj = root.get_child(["0:Objects", "2:MyObject"])

        # Exposing all objects at the Server
        print "--->Exposing Children of objects defined in the MY_OBJECTS list"
        obj_children = objects.get_children()
        d = {} # for storing relevant paths for MY_OBJECTS
        for idx,o in enumerate(obj_children):
            p = o.get_path(max_length=20, as_string=True)
            print "%s-Path: %s" % (idx, p)
            for w in p: # checking if it is in MY_OBJECTS
                (k,v) = w.split(":")
                if v in MY_OBJECTS:
                    children = o.get_children()
                    print "\t***CHILDREN:"
                    for c in children:
                        # only showing objects from MY_OBJECTS
                        (i, attribute) = c.get_browse_name().to_string().split(":")
                        print "\t-%s" % attribute
                        p2 = c.get_path(max_length=20, as_string=True)
                        print "\t\t-PATH: %s" % p2

        ####
        #uncharted territory
        ####

        # Now getting a variable node using its browse path
        myvar = root.get_child(['0:Objects', '1:Device0001', '0:controller'])

        # subscribing to a variable node
        handler = SubHandler()
        sub = client.create_subscription(500, handler)
        handle = sub.subscribe_data_change(myvar.get_children()[0])
        time.sleep(0.1)

        # we can also subscribe to events from server
        sub.subscribe_events()
        # sub.unsubscribe(handle)
        # sub.delete()

        """
        # calling a method on server
        res = obj.call_method("2:multiply", 3, "klk")
        print("method result is: ", res)
        """
        embed()
    finally:
        client.disconnect()
