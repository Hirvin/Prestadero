#! /usr/bin/env python

from bs4 import BeautifulSoup as soup
import pandas as pd
import sys
import re
import os.path as path
from unidecode import unidecode
import os
from colorama import Fore, init

_PATH = "test_todos_usuarios.csv"
_PATH_OUT = "test_2.csv"
_FECHA         = "Fecha"

Df = pd.read_csv(_PATH, index_col = "Index")

for i,data in enumerate(Df.Fecha):
    date = Df.Fecha[i]
    date = date.replace("pm","")
    date = date.replace("am", "")
    year = date.split(" ")[0].split("/")[2]
    month = date.split(" ")[0].split("/")[1]
    if len(month) == 1:
        month = "0" + month
    day = date.split(" ")[0].split("/")[0]
    if len(day) == 1:
        day = "0" + day

    hora = date.split(" ")[1].split(":")[0]
    min = date.split(" ")[1].split(":")[1]
    seg = "00"
    
    datefinal = year + "-" + month + "-" + day + " " + hora + ":" + min + ":" + seg
    print datefinal
    Df.loc[i, _FECHA] = datefinal


Df.to_csv(_PATH_OUT, index = True, index_label = "Index")
print Df