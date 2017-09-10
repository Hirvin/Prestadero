#! /usr/bin/env python

from bs4 import BeautifulSoup as soup
import pandas as pd
import sys
import os.path as path
import re
from unidecode import unidecode



_PATH            = "Misprestamos/BuscarPrestamosRealizados.html"
_PATH_OUT        = "ListaUsuarios/"
_LIBERADO        = "LIBERADO (NORMAL)"
_PAGO_EN_PROCESO = 'Pago en proceso'
_USER            = "Usuario"
_MONTO           = "Monto"
_ESTATUS         = "Estatus"
_SUB_ESTATUS     = "SubEstatus"
_TASA            = "Tasa"
_PLAZO           = "Plazo"
_DIAS_PROX_PAGO  = "Dias Prox. Pago"
_PRINCIPAL       = "Principal"
_INTERESES       = "Intereses"
_IMPUESTOS       = "Impuestos"
_POR_PAGAR       = " Por Pagar"
_COLUMNS         = [_USER, _MONTO, _PRINCIPAL, _INTERESES, _IMPUESTOS,_DIAS_PROX_PAGO,_TASA, _PLAZO, _POR_PAGAR, _ESTATUS, _SUB_ESTATUS]


def remove_u(input_string):
    words = input_string.split()
    words_u = [(word.encode('unicode-escape')).decode("utf-8", "strict") for word in words]
    words_u = [word_u.split('\\u')[1] if r'\u' in word_u else word_u for word_u in words_u]
    return ' '.join(words_u)


def userStatus():
	if path.exists(_PATH):
		datos     = open (_PATH, "r");
		datosHtml = datos.read();
		datos.close();
	else:
		print " El archivo " + _PATH + " no exite. Finalizado la ejecusion"
		return False

	users_soup   = soup(datosHtml, "html.parser");
	misPrestamos = users_soup.findAll("div", {"id":"MisPrestamos"})

	# obtiene la lista de todos los usuarios 
	userList = misPrestamos[0].table.tbody.findAll('tr')
	i = 0

	userDf = pd.DataFrame(columns = _COLUMNS);


	for user in userList:

		userElements = user.findAll("td")

		# Estatus
		statusElement = userElements[0].findAll("span")
		estado        = statusElement[0].text
		alCorriente   = statusElement[1].text
		if (alCorriente == '' and estado == _LIBERADO):
			subestatus = "en Mora"
		else: 
			subestatus = alCorriente

		userDf.loc[i, _ESTATUS]     = estado
		userDf.loc[i, _SUB_ESTATUS] = subestatus

		# Calificacion
		calificacion = userElements[1].span.text
		userDf.loc[i, _TASA]  = float(calificacion.split('%')[0])
		userDf.loc[i, _PLAZO] = int(calificacion.split('%')[1].split(' ')[0])

		# User

		name = unidecode(userElements[2].span.text)
		name = name.encode("ascii")
		userDf.loc[i, _USER] = name[:11]

		# dias para el proximo pago
		diaProxPago = userElements[3].span.text
		if diaProxPago != _PAGO_EN_PROCESO:
			diaProxPago = int(diaProxPago)
		else:
			diaProxPago = -1

		userDf.loc[i, _DIAS_PROX_PAGO] = diaProxPago

		# monto prestado
		userDf.loc[i, _MONTO] = float(userElements[4].span.text.replace('$',''))

		# pagado: principal, interese, impuestos
		pagado    = userElements[5].div.text.replace('\t','').replace(" ","")
		pagado    = re.sub("[a-zA-Z\:\$]","",pagado).split("\n")

		userDf.loc[i, _PRINCIPAL] = float(pagado[1])
		userDf.loc[i, _INTERESES] = float(pagado[2])
		userDf.loc[i, _IMPUESTOS] = float(pagado[3])

		# por pagar
		userDf.loc[i, _POR_PAGAR] = float(userElements[6].span.text.replace('$',''))

		# agregar nuevo indice
		i = i + 1

	userDf.to_csv(_PATH_OUT + "Usuarios.csv", index = True, index_label = "Index")


userStatus()
