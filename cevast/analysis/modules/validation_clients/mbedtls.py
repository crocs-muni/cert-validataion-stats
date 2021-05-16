#!/usr/bin/python3

"""
This module contains an implementation of a certificate chain validation client for command-line MbedTLS.

The validation client can be both imported and used externally (as a standalone module) through the provided
command-line interface.

..Important::
  The validation client must be set up correctly before use. It is necessary to ensure, that MbedTLS is installed
  correctly, "libfaketime.so.1" binary (used for setting reference time) is present, and that `TRUST_STORE_FILE` is
  set to the path to the local trust store.

  When using the validation client externally, these prerequisites are always checked before validation is performed.
  When the validation client is imported, it is necessary to do these checks manually (i.e., using the method `is_setup_correctly()`).
"""

import argparse
import datetime
import os
import subprocess
import tempfile


# noinspection PyBroadException
class MbedTLS:
    """
    A class for certificate chain validation client utilizing command-line MbedTLS.

    Special error messages:

    "Error": any error / exception not related to the certificate chain validation (algorithm) itself

    "Unknown": validation result is unknown
    """

    TRUST_STORE_FILE = "/etc/pki/tls/cert.pem"

    @staticmethod
    def verify(chain, reference_time=None, crl=None, **kwargs):
        """
        Validates a certificate chain.

        `chain` is a list of paths to certificates forming a chain.
        `reference_time` is a reference time of validation in seconds since the epoch.
        `crl` is a path to CRL.
        `kwargs` are other, unexpected arguments.

        The returned result is a list of a set of error messages returned by command-line MbedTLS.
        """

        chain = list(chain)

        try:
            with tempfile.NamedTemporaryFile() as chain_file:
                for i in range(len(chain)):
                    with open(chain[i]) as input_file:
                        chain[i] = input_file.read()

                    chain_file.write(chain[i].encode())

                chain_file.flush()

                command = []

                if reference_time:
                    command += MbedTLS.__get_faketime_command(reference_time)

                command += ["mbedtls_cert_app", "mode=file", "filename={0}".format(chain_file.name), "ca_file={0}".format(MbedTLS.TRUST_STORE_FILE)]

                if crl:
                    command += ["crl_file={0}".format(crl)]

                command_output_lines = [line.strip() for line in subprocess.check_output([" ".join(command)], shell=True).decode(errors="ignore").strip().split("\n")]

                result = ["Unknown"]

                if command_output_lines[-1] == "ok":
                    result = ["Verified"]
                elif command_output_lines[-1][0] == "!":
                    messages = []

                    for i, line in enumerate(command_output_lines):
                        if line == "failed":
                            for message_line in command_output_lines[i + 1:]:
                                if message_line[0] == "!":
                                    messages.append("".join([word.capitalize() for word in message_line[1:].split()]))

                            break

                    if len(messages) > 0:
                        result = sorted(set(messages))
        except Exception:
            result = ["Error"]

        return result

    @staticmethod
    def is_setup_correctly():
        """
        Verifies that the validation client is set up correctly. (MbedTLS is installed, reference time works,
        and trust store exists)
        """

        is_setup_correctly = True

        try:
            subprocess.check_output(" ".join(["type", "mbedtls_cert_app"]), stderr=subprocess.DEVNULL, shell=True)
        except Exception:
            is_setup_correctly = False

        if is_setup_correctly:
            try:
                command_output = subprocess.check_output(" ".join(MbedTLS.__get_faketime_command(0) + ["date", "-u"]), stderr=subprocess.DEVNULL, shell=True)

                if command_output.decode().strip() != "Thu  1 Jan 01:00:00 CET 1970":
                    is_setup_correctly = False
            except Exception:
                is_setup_correctly = False

        if is_setup_correctly:
            if not os.path.isfile(MbedTLS.TRUST_STORE_FILE):
                is_setup_correctly = False

        return is_setup_correctly

    @staticmethod
    def __get_faketime_command(reference_time):
        return ["LD_PRELOAD={0}".format(os.path.join(os.path.dirname(os.path.realpath(__file__)), "libfaketime.so.1")),
                "FAKETIME=\"{0}\"".format(datetime.datetime.fromtimestamp(reference_time).strftime("%Y-%m-%d %H:%M:%S"))]


if __name__ == "__main__":
    argument_parser = argparse.ArgumentParser(description="chain format: ENDPOINT [INTERMEDIATE ...] [CA]")

    argument_parser.add_argument("-r", type=lambda s: int(datetime.datetime.strptime(s, "%Y-%m-%d").timestamp()),
                                 required=False, dest="reference_date_as_time", metavar="DATE",
                                 help="reference date in format YYYY-MM-DD (at 00:00:00)")
    argument_parser.add_argument("-t", type=int, required=False, dest="reference_time", metavar="N",
                                 help="reference time in seconds since the epoch (surpassing reference date)")
    argument_parser.add_argument("--crl", type=str, required=False, dest="crl", metavar="FILE",
                                 help="certificate revocation list")
    argument_parser.add_argument("CERTIFICATE", type=str, nargs="+")

    if MbedTLS.is_setup_correctly():
        args = argument_parser.parse_args()
        print(MbedTLS.verify(args.CERTIFICATE, reference_time=args.reference_time if args.reference_time is not None else args.reference_date_as_time, crl=args.crl))
    else:
        print("Client is not set up correctly")
