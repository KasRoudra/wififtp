# -*- coding: UTF-8 -*-
# ToolName   : WiFiFTP
# Author     : KasRoudra
# License    : MIT
# Copyright  : KasRoudra (2021-2023)
# Github     : https://github.com/KasRoudra
# Contact    : https://t.me/KasRoudra
# Description: Share files between devices connected to same wlan/wifi/hotspot/router""
# Tags       : ftp, wififtp, share-files
# 1st Commit : 18/08/2021
# Language   : Python
# Portable file/script
# If you copy open source code, consider giving credit
# Env        : #!/usr/bin/env python

"""
MIT License

Copyright (c) 2021-2023 KasRoudra

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from argparse import ArgumentParser
from os import (
    name,
    getcwd,
    getenv
)
from os.path import (
    isfile,
    isdir,
    dirname
)
from socket import (
    socket,
    error,
    AF_INET,
    SOCK_DGRAM,
    SOCK_STREAM
)
from subprocess import (
    run,
    DEVNULL,
    PIPE,
    Popen
)
from sys import (
    executable,
    stdout
)
from time import sleep
from re import escape


# Color snippets
black = "\033[0;30m"
red = "\033[0;31m"
bred = "\033[1;31m"
green = "\033[0;32m"
bgreen = "\033[1;32m"
yellow = "\033[0;33m"
byellow = "\033[1;33m"
blue = "\033[0;34m"
bblue = "\033[1;34m"
purple = "\033[0;35m"
bpurple = "\033[1;35m"
cyan = "\033[0;36m"
bcyan = "\033[1;36m"
white = "\033[0;37m"
nc = "\033[00m"

version = "0.1.1"

# Major Minor version ignoring patch
mm_ver = version[:3]

# Regular Snippets
ask = f"{green}[{white}?{green}] {yellow}"
success = f"{yellow}[{white}√{yellow}] {green}"
error = f"{blue}[{white}!{blue}] {red}"
info = f"{yellow}[{white}+{yellow}] {cyan}"
info2 = f"{green}[{white}•{green}] {purple}"

default_dir = getcwd()
default_port = 2121

banner = f"""
{red}__        ___ _____ _  _____ _____ ____  
{blue}\ \      / (_)  ___(_)|  ___|_   _|  _ \  
{green} \ \ /\ / /| | |_  | || |_    | | | |_) |
{cyan}  \ V  V / | |  _| | ||  _|   | | |  __/ 
{purple}   \_/\_/  |_|_|   |_||_|     |_| |_| 
{blue}{" "*31}[{green}v{cyan}{mm_ver}{blue}]   
{cyan}{" "*23}[{blue}By {green}KasRoudra{cyan}]{nc}
"""

argparser = ArgumentParser()

argparser.add_argument("-p", "--port", type=int, help=f"WiFiFTP's server port [Default: {default_port}]")
argparser.add_argument("-d", "--directory", help=f"Directory where server will start [Default: {default_dir}]")
argparser.add_argument("-u", "--username", help=f"FTP Username [Default: None]")
argparser.add_argument("-k", "--password", help=f"FTP Password [Default: None]")
argparser.add_argument("-v", "--version", help=f"Prints version of WiFiFTP", action="store_true")

args = argparser.parse_args()

arg_port = args.port
arg_directory = args.directory
arg_username = args.username
arg_password = args.password
arg_version = args.version


# Check if a package is installed
def is_installed(package):
    return shell(f"command -v {package}", True).returncode == 0

# Print lines slowly
def sprint(text, second=0.05):
    for line in text + '\n':
        stdout.write(line)
        stdout.flush()
        sleep(second)

# Prints colorful texts
def lolcat(text, slow=True, second=0.05):
    if is_installed("lolcat"):
        run(["lolcat"], input=text, text=True)
    else:
        if slow:
            sprint(text, second)
        else:
            print(text)


def show_banner():
    shell(["clear", "cls"][name == "nt"])
    lolcat(banner, second=0.01)


# Run shell commands in python
def shell(command, capture_output=False):
    return run(command, shell=True, capture_output=capture_output)

# Install pip requirements if not found
def inst_deps():
    retry = 3
    shell("stty -echoctl")
    while retry:
        try:
            import pyftpdlib
            break
        except ImportError:
            shell(f"{executable} -m pip install pyftpdlib --break-system-packages")
        except Exception as e:
            print(f"{error}{str(e)}")
        if retry == 1:
            print(f"{error}Install pyftpdlib manually!{nc}")
            exit(1)
        retry -= 1

# Swap bettween ~ and /home/user
def pretty_path(path, rel=True):
    new_path = path
    home = getenv("HOME")
    if path.startswith("\\"):
        new_path = path[1:]
    if "~" in path:
        new_path = new_path.replace("~", home)
    if home in path and rel:
        new_path = new_path.replace(home, "~")
    return new_path

# Check if a port is being used
def is_available_port(port):
    with socket(AF_INET, SOCK_STREAM) as connection:
        return connection.connect_ex(("localhost", int(port))) != 0

# Get user ip address
def get_ip():
    with socket(AF_INET, SOCK_DGRAM) as connection:
        connection.settimeout(10)
        try:
            connection.connect(("8.8.8.8", 80))
            return connection.getsockname()[0]
        except error:
            print(f"{error}No internet")
            exit()
        except Exception as e:
            print(f"{error}{str(e)}")
            exit()


# Check if local ip
def check_local():
    ip = get_ip()
    if not ip.startswith("192") and not ip.startswith("172"):
        print(
            f"{error}You are not using any local network!\nPlease connect to a hotspot or router/Wi-Fi!{nc}"
        )
        exit()

def check_args():
    if arg_version:
        print(f"{info2}WiFiFTP version: {green}{version}")
        exit()

# Use current directory as ftp path if no path is specified by user
def get_path():
    while True:
        if arg_directory is None:
            path = pretty_path(
                escape(
                    input(
                        f"{ask}Enter path (Default: {green}{default_dir}{yellow})\n->{green} "
                    )
                ),
                rel=False
            )
        else:
            path = arg_directory
        if isfile(path):
            path = dirname(path)
            break
        elif isdir(path):
            break
        elif path == "":
            path = default_dir
            break
        else:
            print(f"{error}Invalid path: {path}!{nc}")
    print(f"{info}Choosing directory {pretty_path(path)}{nc}")
    return path

# Use 2121 as ftp port if no port is specified by user
def get_port():
    while True:
        if arg_port is None:
            port = input(
            f"{ask}Enter port (Default: {green}{default_port}{yellow})\n->{green} ")
        else:
            port = str(arg_port)
        if port.isdigit() and int(port) > 1023 and int(port) < 65536 and is_available_port(port):
            break
        elif port == "" and is_available_port(default_port):
            port = default_port
            break
        else:
            print(f"{error}Invalid port: {port}!{nc}")
    print(f"{info}Choosing port {port}{nc}")
    return port

# https://github.com/giampaolo/pyftpdlib#quick-start
def ftp(path, port):
    from pyftpdlib.authorizers import DummyAuthorizer
    from pyftpdlib.handlers import FTPHandler
    from pyftpdlib.servers import FTPServer
    authorizer = DummyAuthorizer()
    if arg_username is not None and arg_password is not None:
        authorizer.add_user(arg_username, arg_password, path, perm="elradfmw")
    else:
        authorizer.add_anonymous(path, perm="elradfmw")

    handler = FTPHandler
    handler.authorizer = authorizer

    server = FTPServer(("0.0.0.0", port), handler)
    server.serve_forever()

# Print ftp address and start ftp by taking inputs
def start_ftp():
    ip = get_ip()
    path = get_path()
    port = get_port()
    lolcat(f"{info2}Your FTP link is: {green}ftp://{ip}:{port}\n{nc}")
    ftp(path, port)

# StartPoint of script
def main():
    try:
        check_args()
        inst_deps()
        show_banner()
        check_local()
        start_ftp()
    except KeyboardInterrupt:
        print(f"\n{info}Closing script....{nc}")
    except Exception as e:
        print(f"{error}{str(e)}")


if __name__ == "__main__":
    main()
