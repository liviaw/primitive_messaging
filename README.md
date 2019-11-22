# Primitive Messaging Application

Instant messaging applications such as WhatsApp, WeChat, Facebook Messenger, etc. are widely
used with millions of subscribers participating in them globally. Through this program, I implemented a simple instant messaging application. This application consist of two model of messaging:
  1. A client server model consisting of one server and multiple messaging clients - The clients communicate with the server using TCP
  2. Peer-to-Peer messaging - clients can send peerto-peer messages to each other that bypass the server.

## Commands supported by the client
| Command | Description|
|-----|-----|
|message \<user\> \<message>|Send \<message> to \<user> through the server. If the user is online then deliver the message immediately, else store the message for offline delivery. If \<user> has blocked A, then a message to that effect should be displayed for A. If the \<user> is not present in the credentials file (i.e. invalid user) or is self (A) then an appropriate error message should be displayed. The \<message> used in our tests will be a few words at most.|
|broadcast \<message>|Send \<message> to all online users except A and those users who have blocked A. Inform A that message could not be sent to some recipients.|
|whoelse|This should display the names of all users that are currently online excluding A. Users can be displayed in any order.|
|whoelsesince \<time> | This should display the names of all users who were logged in at any time within the past \<time> seconds excluding A. |
|block \<user> | block a user from messaging you and includes presences notification|
|unblock \<user>|unblock previously blocked user|
|logout|logs user out|
