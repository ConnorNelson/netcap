#!/usr/bin/env python3

import os
import pathlib
import collections

import pyshark
import inotify.adapters


TCPDUMP_FILTER = 'port 8080'
TCPDUMP_INTERFACE = 'any'
TCPDUMP_ROTATE = 10


def main():
    persist_dir = pathlib.Path('/persist')
    assert persist_dir.exists(), "Could not find persist directory"

    pcap_dir = (persist_dir / 'pcaps').resolve()
    pcap_dir.mkdir(exist_ok=True)

    conversation_dir = (persist_dir / 'conversations').resolve()
    conversation_dir.mkdir(exist_ok=True)

    server_pid = os.fork()
    if server_pid == 0:
        os.execv('/app/server.py', ['server.py'])

    tcpdump_pid = os.fork()
    if tcpdump_pid == 0:
        os.execv('/usr/sbin/tcpdump',
                 ['tcpdump',
                  '-i', TCPDUMP_INTERFACE,
                  '-w', f"{pcap_dir}/%T.pcap",
                  '-G', str(TCPDUMP_ROTATE),
                  TCPDUMP_FILTER])

    i = inotify.adapters.Inotify()
    i.add_watch(str(pcap_dir))
    for _, event_types, path, filename in i.event_gen(yield_nones=False):
        if filename and 'IN_CLOSE_WRITE' in event_types:
            time = filename.split('.', 2)[0]
            cap = pyshark.FileCapture(str(pcap_dir / filename))
            conversations = collections.defaultdict(list)
            for pkt in cap:
                if not hasattr(pkt, 'tcp'):
                    continue
                if not hasattr(pkt.tcp, 'payload'):
                    continue
                src = int(pkt.tcp.srcport)
                dst = int(pkt.tcp.dstport)
                payload = bytes.fromhex(pkt.tcp.payload.replace(':', ''))
                conversation_id = tuple(sorted((src, dst)))
                conversations[conversation_id].append((src, dst, payload))
            for conversation_id, conversation in conversations.items():
                a, b = conversation_id
                with open(conversation_dir / f'{time}-{a}-{b}', 'w') as f:
                    f.write(repr(conversation))


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
