# versio de windows

from bs4 import BeautifulSoup as soup
import pandas as pd
import sys
import re
import os.path as path

_CSV_NAME      = "Movimientos.csv"
_PATH_CSV      = "ListaMovimientos//"
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
_COLUMNS       = [_AUTORIZACION, _USUARIO, _FECHA, _IMPORTE, _PRINCIPAL, _INTERES, _IMPUESTO, _MORATORIO, _IMP_MORATORIO, _TIPO, _MOVIMIENTO, _RASTREO]


######################################################33
# df.Fecha = pd.to_datetime(df.Fecha)

def remove_u(input_string):
    words = input_string.split()
    words_u = [(word.encode('unicode-escape')).decode("utf-8", "strict") for word in words]
    words_u = [word_u.split('\\u')[1] if r'\u' in word_u else word_u for word_u in words_u]
    return ' '.join(words_u)

def getMovimientos(Update = True):
	rewrite = False;

	datos     = open (_PATH, "r");
	datosHtml = datos.read();
	datos.close();

	if path.exists(_PATH_CSV + _CSV_NAME):
		print " la tabla ya exite"
		rewrite = True
		movimientosDf = pd.read_csv(_PATH_CSV + _CSV_NAME, index_col = "Index")
	else:
		print "creando una nueva tabla"
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
		name                                 = abonoElements[6].text.split(': ')[1]
		movimientosDf.loc[i, _USUARIO]       = remove_u(name)
		text                                 = re.sub("[a-zA-Z\n\s\t]","",abonoElements[7].text).split(':')
		movimientosDf.loc[i, _PRINCIPAL]     = float(text[1])
		movimientosDf.loc[i, _INTERES]       = float(text[2])
		movimientosDf.loc[i, _IMPUESTO]      = float(text[3])
		movimientosDf.loc[i, _MORATORIO]     = float(text[4].replace("-","e-"))
		movimientosDf.loc[i, _IMP_MORATORIO] = float(text[5])

		#print name
#		print "\n"

	if Update:
		print "Eliminando Duplicados"
		#numero_dupli =  movimientosDf.duplicated()
		#dupli = len(numero_dupli[numero_dupli == True])
		movimientosDf.drop_duplicates([_AUTORIZACION], keep = 'first', inplace = True)
		print "Guardando tabla"
		num_autorizaciones = movimientosDf.Autorizacion.count()
		#movimientosDf.reset_index(inplace=True)
		movimientosDf.to_csv(_PATH_CSV + _CSV_NAME, index = True, index_label = "Index")
		
		#print "El numeor de duplicados es: " + str(dupli)
		print "El numero de autorizaciones es: " + str(num_autorizaciones)
		#print "El numero de autorizaciones es duplicados : " + str(duplicados.Autorizacion.count())





getMovimientos(True)