#!/usr/bin/env python3

"""
generate_setup_files.py
Creates a personalized Docker Compose setup for a TCP echo demo.

- Prompts for a username (or use --username).
- Sanitizes it for Docker names.
- Chooses a random, currently-available host port and a random container port.
- Writes: docker-compose.yml

Usage:
        python generate_setup_files.py
        python generate_setup_files.py --username alice
"""

import os
import re
import sys
import random
import socket
import argparse

from pathlib import Path
from textwrap import dedent

RANDOM_PORT_RANGE = (20000, 39999)  # range used to pick a free host port
CONTAINER_PORT_RANGE = (8000, 9000)  # range to pick a random inside-container port


def sanitize_username(u: str) -> str:
    """
    Convert to a Docker-friendly slug:
    - lowercase
    - keep a-z0-9 and -_. only
    - ensure starts with alphanumeric; if not, prefix 'u-'
    - collapse repeats
    """
    u = u.strip().lower()
    u = re.sub(r'[^a-z0-9._-]', '-', u)
    u = re.sub(r'[-._]+', lambda m: m.group(0)[0], u)  # compress repeats per char
    if not re.match(r'^[a-z0-9]', u):
        u = f"u-{u}"
    return u[:48]  # keep it short-ish for names

def port_is_free(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            s.bind(("0.0.0.0", port))
            return True
        except OSError:
            return False


def pick_random_free_port() -> int:
    low, high = RANDOM_PORT_RANGE
    # Try random samples first, then fall back to linear scan if needed
    for _ in range(64):
                    p = random.randint(low, high)
                    if port_is_free(p):
                                    return p
    # Fallback scan
    for p in range(low, high + 1):
                    if port_is_free(p):
                                    return p
    raise RuntimeError("No free port found in the given range.")


def pick_random_container_port() -> int:
    """Pick a random port number for use inside the container.

    Container ports don't need to be free on the host, so we simply pick
    a random port in CONTAINER_PORT_RANGE and return it.
    """
    low, high = CONTAINER_PORT_RANGE
    return random.randint(low, min(high, 65535))


def write_file(path: Path, contents: str, overwrite=False):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and not overwrite:
                    return
    path.write_text(contents, encoding="utf-8")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--username", "-u", help="Student username to embed")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing files")
    args = parser.parse_args()

    username = args.username or input("Enter username: ").strip()
    if not username:
        print("Username is required.", file=sys.stderr)
        sys.exit(1)

    user_slug = sanitize_username(username)

    # Random available host port (for host -> container mapping)
    host_port = pick_random_free_port()
    # Random container-side port so each user gets a different internal port
    container_port = pick_random_container_port()

    # Names/paths
    project_net = f"csci-net-{user_slug}"
    server_name = f"csci-server-{user_slug}"
    client_name = f"csci-client-{user_slug}"
    server_dir = Path(f"server-{user_slug}")
    client_dir = Path(f"client-{user_slug}")

    # Compose file
    compose = dedent(f""" 
    version: "3.9" 
    services:
      server:
        image: python:3.11-slim
        container_name: {server_name}
        working_dir: /app
        volumes:
                - ./{server_dir.name}:/app
        environment:
                - STUDENT_USERNAME={username}
                - APP_PORT={container_port}
        command: bash
        tty: true
        stdin_open: true
        networks: [ {project_net} ]
        ports:
                - "{host_port}:{container_port}"
        

      client:
        image: python:3.11-slim
        container_name: {client_name}
        working_dir: /app
        volumes:
                - ./{client_dir.name}:/app
        environment:
                - STUDENT_USERNAME={username}
                - SERVER_HOST={server_name}
                - SERVER_PORT={container_port}
        command: bash
        tty: true
        stdin_open: true
        networks: [ {project_net} ]
        

    networks:
            {project_net}:
                    driver: bridge
    """).strip() + "\n"

    write_file(Path("docker-compose.yml"), compose, overwrite=args.overwrite)

    os.makedirs(server_dir, exist_ok=True)
    os.makedirs(client_dir, exist_ok=True)

    print(f"\n✅ Generated docker-compose.yml\nHost port: {host_port}\nContainer port: {container_port}\nProject network: {project_net}\nServer container name: {server_name}\nClient container name: {client_name}")


if __name__ == "__main__":
    main()
