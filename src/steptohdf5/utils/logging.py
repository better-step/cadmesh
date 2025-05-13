from __future__ import annotations

import logging
import glob
from tqdm.auto import tqdm
import datetime
import os
import time
# import matplotlib.pyplot as plt
import numpy as np


def setup_logger(
    name: str,
    log_file: str,
    formatter: logging.Formatter | None = None,
    level: int = logging.INFO,
    reset: bool = True,
) -> logging.Logger:
    """
    Create (or reset) and return a named Logger that writes to `log_file`.

    Parameters
    ----------
    name
        Name of the logger (appears in log records).
    log_file
        Path to the file where logs are written.
    formatter
        logging.Formatter instance to format log messages.
        If None, a default '%(asctime)s %(levelname)s %(message)s' formatter is used.
    level
        Logging level (e.g. logging.INFO).
    reset
        If True and the log file already exists, it will be deleted,
        and any existing handlers on the logger will be removed.

    Returns
    -------
    logging.Logger
    """
    # Remove old log file if desired
    if reset and os.path.exists(log_file):
        try:
            os.remove(log_file)
        except OSError:
            pass

    # Use default formatter if none provided
    if formatter is None:
        formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")

    # Configure file handler
    handler = logging.FileHandler(log_file)
    handler.setFormatter(formatter)

    # Get or create the logger
    logger = logging.getLogger(name)
    logger.setLevel(level)

    if reset:
        # Remove any existing handlers to avoid duplicate logs
        for h in list(logger.handlers):
            logger.removeHandler(h)

    logger.addHandler(handler)
    return logger


# def analyse_log_files(path="data/log_abc/*.log"):
#     logs = sorted(glob.glob(path))
#     #print(len(logs))

#     times = []
#     parts = []
#     errors = []
#     elogs = []
#     n_errors = []
#     n_elogs = []
#     success = []

#     pbar = tqdm(range(len(logs)))
#     for i in pbar:
#         #pbar.set_description("Processing %s"%logs[i])
#         log = logs[i]
#         with open(log, "r") as fi:
#             lines = fi.readlines()

#         if len(lines) < 2:
#             errors.append(i)
#             elogs.append("%i: %s"%(i, "Lines missing"))
#             continue
#         time_start = " ".join(lines[0].split(" ")[:2])[:-4]
#         time_end = " ".join(lines[-1].split(" ")[:2])[:-4]
#         #for line in lines:
#         t_s = datetime.datetime.strptime(time_start, '%Y-%m-%d %H:%M:%S')
#         t_e = datetime.datetime.strptime(time_end, '%Y-%m-%d %H:%M:%S')
#         times.append((t_e - t_s).total_seconds())

#         try:
#             parts.append(int(lines[1].split(" ")[5]))
#         except:
#             parts.append(0)
#             errors.append(i)
#             elogs.append("%i: %s"%(i, "Translation problem"))

#         for line in lines:
#             if "ERROR" in line and "Nurbs conversion error" in line:
#                 n_errors.append(i)
#                 n_elogs.append("%i: %s"%(i, line))
#             elif "ERROR" in line and not "Nurbs conversion error" in line:
#                 errors.append(i)
#                 elogs.append("%i: %s"%(i, line))

#             if "Stat dict: Done" in line:
#                 success.append(i)



#     plt.hist(parts, bins=np.linspace(0, 100, 20))
#     plt.show()

#     plt.hist(times, bins=np.linspace(0, 250, 25))
#     plt.show()

#     print("Parts: Avg: %0.2f"%(sum(parts)/len(parts)))
#     print("Times: Avg: %0.2f"%(sum(times)/len(times)))

#     print("Errors occurred: %i(total)/%i(single)"%(len(errors), len(list(set(errors)))))
#     print("Conversion errors occurred: %i(total)/%i(single)"%(len(n_errors), len(list(set(n_errors)))))
#     print("Success: %i/%i"%(len(success), len(logs)))

#     for elog in elogs:
#         print(elog.strip())