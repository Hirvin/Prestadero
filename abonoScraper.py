#! /usr/bin/env python

from bs4 import BeautifulSoup as soup
import pandas as pd
import sys
import re
import os.path as path
from unidecode import unidecode
import os
from colorama import Fore, init

init()

_CSV_NAME      = "Movimientos.csv"
_PATH_CSV      = "ListaMovimientos/"
_PATH          = "Abonos/Historial de Movimientos.html"
_AUTORIZACION  = "Autorizacion"
_USUARIO       = "Usuario"
_FECHA         = "Fecha"
_IMPORTE       = "Importe"
_PRINCIPAL     = "Principal"
_INTERES       = "Interes"
_IMPUESTO      = "Impuesto Interes"
_MORATORIO     = "Moratorio"
_IMP_MORATORIO = "Impuesto Moratorio"
_TIPO          = "Tipo"
_MOVIMIENTO    = "Moimiento"
_RASTREO       = "Rastreo"
_WEEK          = "Week" 
_MONTH         = "Month"
_QUARTER       = "Quarter"
_YEAR          = "Year"
_COLUMNS       = [_AUTORIZACION, _USUARIO, _FECHA, _IMPORTE, _PRINCIPAL, _INTERES, _IMPUESTO, _MORATORIO, _IMP_MORATORIO, _TIPO, _MOVIMIENTO, _RASTREO, _WEEK, _MONTH, _QUARTER, _YEAR]


######################################################33
# df.Fecha = pd.to_datetime(df.Fecha)

def getMovimientos():
    print Fore.BLUE + "\n* leyendo datos de: " + Fore.GREEN + _PATH
    rewrite = False;

    if path.exists(_PATH):
        datos     = open (_PATH, "r");
        datosHtml = datos.read();
        datos.close();
    else:
        print " el Archvio: " + _PATH + " no se pudo leer";
        return False
    
    movimientosDf = pd.DataFrame(columns = _COLUMNS);



    abonos_soup   = soup(datosHtml, "html.parser");

    misAbonos = abonos_soup.findAll("tbody",  {"data-expanded":"true"})
    abonos_list = misAbonos[0].findAll('tr')
    

    for abono in abonos_list:
        abonoElements                        = abono.findAll("td")

        i = len(movimientosDf)
        movimientosDf.loc[i, _AUTORIZACION]  = int(abonoElements[0].text)
        movimientosDf.loc[i, _FECHA]         = abonoElements[1].text
        movimientosDf.loc[i, _TIPO]          = abonoElements[2].text
        movimientosDf.loc[i, _MOVIMIENTO]    = abonoElements[3].text
        movimientosDf.loc[i, _RASTREO]       = abonoElements[4].text
        movimientosDf.loc[i, _IMPORTE]       = float(abonoElements[5].text.replace('$',''))

        name                                 = unidecode(abonoElements[6].text.split(': ')[1])
        name = name.encode("ascii")
        movimientosDf.loc[i, _USUARIO]       = name


        text                                 = re.sub("[a-zA-Z\n\s\t]","",abonoElements[7].text).split(':')
        movimientosDf.loc[i, _PRINCIPAL]     = float(text[1])
        movimientosDf.loc[i, _INTERES]       = float(text[2])
        movimientosDf.loc[i, _IMPUESTO]      = float(text[3])
        movimientosDf.loc[i, _MORATORIO]     = float(text[4].replace("-","e-"))
        movimientosDf.loc[i, _IMP_MORATORIO] = float(text[5])

    return movimientosDf

def actualizarFechas(orig):
    print Fore.BLUE + "\n* Actualizando Fechas."
    orig.Fecha = pd.to_datetime(orig.Fecha)

    for i,data in enumerate(orig.Fecha):
        orig.loc[i, _WEEK]    = orig.Fecha[i].week
        orig.loc[i, _QUARTER] = orig.Fecha[i].quarter
        orig.loc[i, _YEAR]    = orig.Fecha[i].year
        orig.loc[i, _MONTH]   = orig.Fecha[i].strftime("%b")

    orig[_YEAR] = orig[_YEAR].astype(int)

    return orig


def getRepositories(orig):
    print Fore.BLUE + "\n* Generando estructura de directorios."
    for i,year in enumerate(orig[_YEAR]):
        dir = _PATH_CSV + str(year) + '/'
        if path.exists(dir) == False:
            print Fore.MAGENTA + "  creando directorio: " + Fore.GREEN + dir
            os.mkdir(dir)

    for i,month in enumerate(orig[_MONTH]):
        year = str(orig[_YEAR][i])
        dir = _PATH_CSV + year + "/" + month + "/"
        if path.exists(dir) == False:
            print Fore.MAGENTA + "  creando directorio: " + Fore.GREEN + dir
            os.mkdir(dir)

def updateCSV(orig):
    print Fore.BLUE + "\n* Actualizando los archivos csv"
    for i,year in enumerate(orig[_YEAR].drop_duplicates()):
        for j,month in enumerate(orig[orig[_YEAR] == year][_MONTH].drop_duplicates()):
            print Fore.MAGENTA + "  Verficando directorios del: " + Fore.CYAN + month + " " + str(year)
            dirName = "movimiento_" + month + "_" + str(year) + ".csv"
            dir = _PATH_CSV + str(year) + '/' + month + '/' + dirName
            
            df = orig[(orig[_YEAR] == year) & (orig[_MONTH] == month)]
            if path.exists(dir) == False:
                if df.empty == False:
                    print Fore.YELLOW + "    No se encontro referencia, creando : " + Fore.GREEN + dir
                    df.reset_index(inplace = True)
                    df.to_csv(dir, index = True, index_label = "Index")
            else:
                if df.empty == False:
                    print Fore.YELLOW + "    resolviendo coincidencias de: " + Fore.GREEN + dir
                    
                    # leyendo directorio guardado previamente
                    print Fore.WHITE + "      Leyendo Directorio: " + Fore.GREEN + " " + dir
                    baseDf = pd.read_csv(dir, index_col = "Index")
                    baseNumAut = baseDf.Autorizacion.count()
                    print Fore.WHITE + "      El numero de autorizaciones base es : " + Fore.GREEN +str(baseNumAut)

                    # junstando ambos Df
                    auxDf = pd.concat([baseDf, df])

                    # eliminando repretidos
                    auxDf.drop_duplicates([_AUTORIZACION], keep ='first', inplace = True)
                    auxDf.reset_index(inplace = True)
                    finalNumAut = auxDf.Autorizacion.count()

                    # Actualizando nueva tabla
                    if finalNumAut <= baseNumAut:
                        print Fore.WHITE + "      No hay abonos nuevo : " + Fore.RED + "No es necesario actualizar el archivo " + dirName
                    else:
                        print Fore.WHITE + "      hay " + Fore.YELLOW + str(finalNumAut - baseNumAut) + "nuevo abonos, actualizando : " + Fore.GREEN + dirName
                        auxDf.to_csv(dir, index = True, index_label = "Index")
                    print " "

movDf = getMovimientos()
movDf = actualizarFechas(movDf)
getRepositories(movDf)
updateCSV(movDf)