#!/usr/bin/env python3
# run as `./gsfpy_read_test.py`
from gsfpy import open_gsf

def iter_mb_ping(gsf_file):
    from gsfpy import GsfException, RecordType
    i = 0
    while True:
        try:
            (_, r) = gsf_file.read(RecordType.GSF_RECORD_SWATH_BATHYMETRY_PING)
            yield i, r.mb_ping
            i += 1
        except GsfException:
            break

def read_many_gsf(ident):
    from datetime import datetime
    from time import sleep
    from datetime import datetime
    from shutil import copy
    import random
    import tempfile

    gsf_files = ["tests/gsfpy_test_data.gsf", "tests/0029_20160323_185603_EX1604_MB.gsf.mb121", "tests/0059_20181102_212138_EX1811_MB_EM302.gsf.mb121"]

    handles = []
    for i in range(4):
        try:
            handles.append(open_gsf(random.choice(gsf_files)))
            print(ident, "started", i, "at", datetime.now())
        except Exception as e:
            print(ident, "failed", i, "at", datetime.now())
            print(e)

    sleep(1)

    for h in handles:
        for j, mb_ping in iter_mb_ping(h):
            print(mb_ping.ping_number)

    for i, h in enumerate(handles):
        h.close()
        print(ident, "stopped", i, "at", datetime.now())


num_to_open = 2

def main():
    with open_gsf("tests/gsfpy_test_data.gsf") as f1:
        with open_gsf("tests/gsfpy_test_data.gsf") as f2:
            default()
            multiprocessing()
            subprocess()


def default():
    print("# default")
    for i in range(num_to_open):
        read_many_gsf(i)


def multiprocessing():
    print("# multiprocessing")
    from multiprocessing import Process, Pipe

    #pool = Pool(num_to_open)

    ps = []
    for i in range(num_to_open):
        p = Process(target=read_many_gsf, args=(i,))
        ps.append(p)

    for p in ps:
        p.start()

    for p in ps:
        p.join()


def subprocess():
    print("# subprocess")
    from subprocess import Popen


    sps = []
    for i in range(num_to_open):
        sp = Popen(["python3", __file__, "sample", str(i)])
        sps.append(sp)

    for sp in sps:
        sp.wait()


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        main()
    else:
        command = sys.argv[1]
        if command == "default":
            default()
        elif command == "multiprocessing":
            multiprocessing()
        elif command == "subprocess":
            subprocess()
        elif command == "sample":
            ident = sys.argv[2]
            read_many_gsf(ident)
