#! /usr/bin/env python

import os
from os import path, listdir
import re
import sys

from rich import print
from rich.panel import Panel
from rich.align import Align
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich.progress import Progress

from tkinter import filedialog
from tkinter import *

from skimage import io
from copy import deepcopy, copy

min_t = None
# modify this offset to sync with other camera views if necessary
offset = 0


def sync_timestamp(path):
    """ Sync all timestamp string recorded as the name of a frame"""
    global min_t
    timestamp_list = [int(filename[:-4]) for filename in os.listdir(path)
                      if re.match('-*[0-9]+(?=\.jpg)', filename)]
    min_t = min(timestamp_list)
    print("Minimal timestamp: ", min_t)
    y = Prompt.ask("Proceed?", choices=["y", "n"])
    if (y == 'Y' or y == 'y'):
        pass
    else:
        sys.exit("Renaming cancelled")
    with Progress() as progress:
      task = progress.add_task(f"[green]Processing ", total=len(timestamp_list))
      for i, filename in enumerate(sorted(os.listdir(path))):
          m = re.search('-*[0-9]+(?=\.jpg)', filename)
          if m is not None:
              t = int(m.group(0))
              # print(f"Renamed {filename} to {t - min_t + offset:08}.jpg")
              os.rename(path+'/'+filename, path+'/' +
                        f'{t - min_t + offset:08}.jpg')
              progress.update(task, advance=1)

    os.system(f"touch {path + '/'}.synced")


def color_correction(path):
    total_frames = len(os.listdir(path))
    with Progress() as progress:
        print(f"Running color correction in {path}")
        task = progress.add_task(f"[green]Processing ", total=total_frames)
        for i, filename in enumerate(sorted(os.listdir(path))):
            m = re.search('-*[0-9]+(?=\.jpg)', filename)
            if m is not None:
                abs_file = path + "/" + filename
                frame = io.imread(abs_file)
                tmp = deepcopy(frame[:, :, 0])
                frame[:, :, 0] = deepcopy(frame[:, :, 2])
                frame[:, :, 2] = copy(tmp)
                io.imsave(abs_file, frame)
                progress.update(task, advance=1)


if __name__ == "__main__":
    table = Table(expand=True, leading=2)
    table.add_column("Fish cutting data preprocess toolset",
                     justify="center", style="green")
    table.add_row("[1] Sync timestamp")
    table.add_row("[2] Frame color correction")
    print(table)
    mode = Prompt.ask(
        "Please choose the tool you would like to proceed", choices=["1", "2"])
    if mode == "1":
        print("[red]Choose the directory of the frame data[/red]")
        Tk().withdraw()
        dir = filedialog.askdirectory()
        sync_timestamp(dir)
    elif mode == "2":
        print("[red]Choose the directory of the frame data[/red]")
        Tk().withdraw()
        dir = filedialog.askdirectory()
        color_correction(dir)

    # sync_timestamp()
