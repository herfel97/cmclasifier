"""
    C&M - Gestor Reportes
    =====================
    Logica para la gestion de reportes
    :autor @cmorocho
"""
from cm_gestores import gestor_tweets
import requests
import base64
from os.path import abspath, join
from relatorio import Report
from settings import BASEDIR
import subprocess
import matplotlib.pyplot as plt
import io

ODT_MIME = 'application/vnd.oasis.opendocument.text'


def get_values(data):
    if isinstance(data, list):
        return data
    else:
        return [data]


def generar_accion_reporte(id_cuenta, accion, cuenta, usuario):
    """
    Genera el reporte segun la configuracion
    :param id_cuenta:
    :param accion:
    :param cuenta:
    :param usuario:
    :return:
    """
    filtros = accion.get("filtros", {})
    reporte = accion.get("reporte", {})
    # Obtiene las metricas
    metricas = cuenta['metricas']
    cuenta.update({'TT': metricas['tweets'], 'S1': metricas['followers'], 'S2': metricas['following']})
    # Obtiene la imagen de la cuenta
    url_profile = cuenta['url_profile'].replace("_normal.", "_400x400.")
    result = requests.get(url_profile, stream=True).content
    imagen = base64.b64encode(result).decode()
    # Obtiene los campos
    titles = []
    con_autores = len(reporte.get("camposAutor", [])) > 0
    con_clases = len(reporte.get("camposClasificacion", [])) > 0
    # Obtiene el template
    if con_autores and con_clases:
        template_name = 'reporte_tweets2'
    elif con_autores or con_clases:
        template_name = 'reporte_tweets1'
    else:
        template_name = 'reporte_tweets0'
    # Obtiene los campos
    if con_autores:
        titles.append({
            'key': 'usuario',
            'label': "AUTOR",
            'labels': reporte["camposAutor"]
        })
    if con_clases:
        titles.append({
            'key': 'clasificaciones',
            'label': "CLASIFICACION",
            'labels': reporte["camposClasificacion"]
        })
    # Obtiene el titulo
    titulo = "REPORTE DE TWEETS POR FECHA"
    if reporte.get("conTitulo") and reporte.get("titulo"):
        titulo = reporte["titulo"]
    # Obtiene las graficas
    graficas = generar_graficas_estadisticas(id_cuenta, filtros, reporte)
    # Obtiene los tweets
    con_totales = reporte.get("totalTipo", True)
    consulta = gestor_tweets.obtener_tweets_reporte(id_cuenta, filtros, con_clases, con_autores, con_totales)
    # Arma el contexto
    contexto = {
        'titulo': titulo,
        'cuenta': cuenta,
        "usuario": usuario,
        'get_values': get_values,
        'titles': titles,
        'grafica': graficas,
        **consulta
    }
    # Agrega la imagen
    dtemp = join(BASEDIR, 'cm_templates/')
    path_file = join(dtemp, f"{template_name}.fodt")
    content = open(path_file, "r").read().replace("[IMAGEN]", imagen).encode()
    path_file_in = join(dtemp, f'in_{template_name}.fodt')
    open(path_file_in, 'wb').write(content)
    # Genera el reporte
    reporte = Report(abspath(path_file_in), ODT_MIME)
    content = reporte(**contexto).render().getvalue()
    path_file_out = join(dtemp, f'out_{template_name}.fodt')
    open(path_file_out, 'wb').write(content)
    cmd = ['soffice', '--headless', '--nolockcheck', '--nodefault', '--norestore',
           '--convert-to', 'pdf', '--outdir', dtemp, path_file_out]
    file_out = join(dtemp, f'out_{template_name}.pdf')
    subprocess.check_call(cmd)
    return file_out


def generar_graficas_estadisticas(id_cuenta, filtros, reporte):
    """
    Genera las graficas Bar / LInea
    :param id_cuenta:
    :param filtros:
    :param reporte:
    :return:
    """
    if reporte.get("graficaBar", False):
        resultado = gestor_tweets.obtener_todas_clasificaciones(id_cuenta, "TB", filtros)
        # Genera el grafico
        tweets = [item['total'] for item in resultado.get('items', [])]
        clases = [item['nombre'] for item in resultado.get('items', [])]
        # Creamos la Gráfica
        pic_reporte_iobytes = io.BytesIO()
        plt.bar(clases, tweets)
        plt.ylabel('Total de Tweets')
        plt.xlabel('Clases')
        plt.grid(True)
        plt.savefig(pic_reporte_iobytes, format='png')
        pic_reporte_iobytes.seek(0)
        plt.close()
        # Creamos el objeto grafico
        return {
            'titulo': "GRAFICA DE BARRAS ( CLASIFICACION )",
            'items': resultado['items'],
            'imagen': pic_reporte_iobytes.read()
        }
    if reporte.get("graficaLinea", False):
        resultado_tb = gestor_tweets.obtener_todas_clasificaciones(id_cuenta, "TB", filtros)
        resultado_tl = gestor_tweets.obtener_todas_clasificaciones(id_cuenta, "TL", filtros)
        items = resultado_tl['items']
        fechas = list(items.keys())
        # Creamos la Gráfica
        pic_reporte_iobytes = io.BytesIO()
        plt.ylabel('Total de Tweets')
        plt.xlabel('Fechas')
        plt.grid(True)
        for clase in items['0'].keys():
            tweets = []
            for fecha in fechas:
                tweets.append(items[fecha][clase]['total'])
            plt.plot(fechas, tweets)
        plt.savefig(pic_reporte_iobytes, format='png')
        pic_reporte_iobytes.seek(0)
        plt.close()
        return {
            'titulo': "GRAFICA DE LINEAS ( CLASIFICACION )",
            'items': resultado_tb['items'],
            'imagen': pic_reporte_iobytes.read()
        }
