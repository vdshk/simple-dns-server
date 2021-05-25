import copy
import socket

import dns.resolver

PORT = 53
IP = "127.0.0.1"

client_socket = dns.query._make_socket(
    socket.AF_INET,
    socket.SOCK_DGRAM,
    (IP, PORT),
)

resolver = dns.resolver.Resolver(configure=False)
resolver.nameservers = [
    "8.8.8.8",
    "8.8.4.4",
]

cache = dict()

while True:
    request, received_time, from_address = dns.query.receive_udp(client_socket)

    query = str(request.question[0]).split()[0]

    response = copy.deepcopy(request)

    if query in cache:
        result = cache[query]
    else:
        result = resolver.resolve(
            query,
            rdtype=dns.rdatatype.A,
            rdclass=dns.rdataclass.IN,
            search=True,
            raise_on_no_answer=False,
        )
        cache[query] = result

    response.answer = result.response.answer
    response.flags |= dns.flags.QR

    dns.query.send_udp(client_socket, response, from_address)