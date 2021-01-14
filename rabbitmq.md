## Overview
RabbitMQ is an open source message
queue designed for distributed software
architectures to solve application communication
over LAN/WAN. It uses the AMQP protocol for
communication (Using TCP as transport)

It has client libraries for the following languages:
 - Java
 - Ruby
 - Python
 - C#
 - PHP
 - Javascript


Built in Erlang

Defined as a MOM (Message-oriented Middleware) that 
allows for sending and receving of messages from
distributed systems. 

Application architectures no longer need a dependence
upon database write performance because the database
is decoupled from the application


 ## Example (C = Consumer/Listener)
```
                                      1.
 +=====+ Publish +==========+ Consume +===+       +====+
 | App | =====>  | RabbitMQ | =====>  | C | ====> | DB |
 +=====+         +==========+         +===+       +====+
                         \\  Consume 2.
                          \\ =====>  +===+ ===> +=======+
                                     | C |      | Cloud |
                                     +===+      |  Svc  |
                                               +=======+
```
Consumer 1 manages database writes for Application

Consumer 2 Can deliver the same data to a third-party

### Broker Terms:
- Exchange: The components of the message broker that
            routes messages
- Queue: A data structure on disk or in memory that stores
        messages (In mem vs persist to disk)
- Binding: A rule that tells the exchange which queue the
        message should be stored in

 ### Message format:

```
 +----------------------------------------------------------------+
 |  1  |  0  |  335  |            Frame Payload            | 0xce |
 +----------------------------------------------------------------+
  Type Channel  Frame             Variable Length            End of
        Number  Size                                         Frame
```

### Message types (Using Class.Method structure):

- Connection.open
- Connection.Close
- Channel.Close
- Exchange.Declare: Define Name of Exchange
- Exchange.Binding
- Queue.Declare
- Queue.Bind
- Queue.Delete
- Basic.Publish
    + Basic.Properties
        * content-types: How to interpret the message body
        * expiration
        * reply-to: Routing key for consumer when replying to a message
                    implementing RPC
        * content-encoding
        * delivery-mode: Writing to disk-backed or in-memory
        * headers: Key-value table in message properties
        * message-id
        * app-id: The publishing application
        * priority: Priority of the queue
        * correlation-id
        * user-id: User publishing the message
        * timestamp
        * type: Define contract with publishers and consumers


## Enable WebUI plugin
```Shell
rabbitmq-plugins enable rabbitmq_management
```