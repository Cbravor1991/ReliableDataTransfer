import argparse
from enum import Enum
import logging

DEFAULT_HOST = "localhost"
DEFAULT_PORT = 12000
DEST = "./"
SRC = "./texto.txt"
VERBOSITY = {1: logging.DEBUG, 2: logging.INFO, 3: logging.ERROR}

class protocol_type(Enum):
    SW = "stop&wait"
    SP = "selectiveRepeact"

    def __str__(self):
        return self.value


def parse_arguments():
    parser = argparse.ArgumentParser(description= '<command description>')
    parser.add_argument(
        "-P",
        "--protocol",
        help="protocol to use",
        dest="protocol",
        type= protocol_type,
        choices= list(protocol_type),
        default=protocol_type.SW,
    )

    
    
    parser.add_argument(
        "-v",
        "--verbose",
        help="increase output verbosity",
        action="store_true"
    )

    parser.add_argument(
        "-q", "--quiet", help="decrease output verbosity", action="store_true"
    ) 

    parser.add_argument(
        "-H", "--host", help="server IP address", dest="host", type=str, action="store",
         default = DEFAULT_HOST
    )

    parser.add_argument(
        "-p",
        "--port",
        help="server port",
        dest="port",
        type=int,
        action="store",
        default= DEFAULT_PORT,
    )

    
    return parser


def parse_client_upload():
    parser = parse_arguments()
    parser.add_argument (
        "-s",
        "--src",
        help="source file path",
        dest="src",
        type=str,
        action="store",
        required=False,
        default= SRC,
    )
    
    parser.add_argument(
        "-n",
        "--name",
        help="file name",
        dest="filename",
        type=str,
        action="store",
        required=False,
        default="unknown",
    )

    return validate_parse(parser.parse_args())


def parse_client_download():
    parser = parse_arguments()
    parser.add_argument(
        "-d",
        "--dst",
        help="Destination file path",
        dest="dst",
        type=str,
        action="store",
        required=False,
        default="./",
    )
    parser.add_argument(
        "-n", "--name", 
        help="filename",
        dest="filename",
        type=str,
        action="store",
        default='unknown'
    )
    return  validate_parse(parser.parse_args())

def parse_server_start():
    parser = parse_arguments()
    parser.add_argument(
        "-s",
        "--storage",
        help="storage dir path",
        dest="dest",
        type=str,
        action="store",
        required=False,
        default=DEST,
    )
    return validate_parse( parser.parse_args())

#implementado para manejar verbosity mas que nada que utiliza la libretia loggin
def validate_parse(args):
    if args.verbose:
        logging.basicConfig(level=VERBOSITY[1])
    else:
        logging.basicConfig(level=VERBOSITY[2])
    if args.quiet:
        logging.disable(level=logging.CRITICAL + 1)
    if not args.host or not args.host.replace(".", "").isdigit():
        args.host = DEFAULT_HOST
    if args.port:
        if args.port < 1024 or args.port > 65535:
            args.port = DEFAULT_PORT
    return args