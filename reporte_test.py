from os.path import abspath, join, dirname
import requests
import base64
from relatorio import Report, reporting

from settings import BASEDIR

ODT_MIME = 'application/vnd.oasis.opendocument.text'
import subprocess


def get_values(data):
    if isinstance(data, list):
        return data
    else:
        return [data]


if __name__ == '__main__':
    # ODT
    print("reporte tweets ")
    titles = [
        # {
        #     'key': 'autor',
        #     'label': "AUTOR",
        #     'labels': [{'key': 'codigo', 'label': "CODIGO"},
        #                {'key': 'nombre', 'label': "NOMBRE"},
        #                {'key': 'usuario', 'label': "USUARIO"}]
        # },
        {
            'key': 'entidades',
            'label': "ENTIDADES",
            'labels': [{'key': 'tipo', 'label': "TIPO"},]
                     #  {'key': 'valor', 'label': "VALOR"}],
        },
        {
            'key': 'clasificacion',
            'label': "CLASIFICACION",
            'labels': [{'key': 'codigo', 'label': "CODIGO"},
                       {'key': 'score', 'label': "SCORE"}]
        },
    ]
    tweets = [
        {
            'codigo': '123345',
            'fecha': '2022-01-01',
            'tipo': 'Mension',
            'texto': 'Esto es una  sdzf asdfasdf assad fas prueba3',
            'autor': {'codigo': '25463', 'nombre': "cmorocho", "usuario": "dsffasa"},
            'clasificacion': [{'codigo': '25463', 'score': 10},
                              {'codigo': '25463', 'score': 30}],
            'entidades': [{'tipo': '25463', 'valor': 10},
                          {'tipo': '25463', 'valor': 30}]
        },
        {
            'codigo': '123345',
            'fecha': '2022-01-01',
            'tipo': 'Mension',
            'texto': 'Esto es una  sdzf asdfasdf assad fas prueba3',
            'autor': {'codigo': '25463', 'nombre': "cmorocho", "usuario": "dss52ffasa"},
            'clasificacion': [{'codigo': '25463', 'score': 10},
                              {'codigo': '25463', 'score': 30}],
            'entidades': [{'tipo': '25463', 'valor': 10},
                          {'tipo': '25463', 'valor': 30}]
        },
        {
            'codigo': '123345',
            'fecha': '2022-01-01',
            'tipo': 'Mension',
            'texto': 'Esto es una  sdzf asdfasdf assad fas prueba3',
            'autor': {'codigo': '25463', 'nombre': "cmorocho", "usuario": "ds203s"},
            'clasificacion': [{'codigo': '25463', 'score': 10},
                              {'codigo': '25463', 'score': 30}],
            'entidades': [{'tipo': '25463', 'valor': 10},
                          {'tipo': '25463', 'valor': 30}]
        },
        {
            'codigo': '123345',
            'fecha': '2022-01-01',
            'tipo': 'Mension',
            'texto': 'Esto es una  sdzf asdfasdf assad fas prueba3',
            'autor': {'codigo': '25463', 'nombre': "cmorocho", "usuario": "d03ss"},
            'clasificacion': [{'codigo': '25463', 'score': 10},
                              {'codigo': '25463', 'score': 30}],
            'entidades': [{'tipo': '25463', 'valor': 10},
                          {'tipo': '25463', 'valor': 30}]
        },
        {
            'codigo': '123345',
            'fecha': '2022-01-01',
            'tipo': 'Mension',
            'texto': 'Esto es una  sdzf asdfasdf assad fas prueba3',
            'autor': {'codigo': '25463', 'nombre': "cmorocho", "usuario": "dsffasa0"},
            'clasificacion': [{'codigo': '25463', 'score': 10},
                              {'codigo': '25463', 'score': 30}],
            'entidades': [{'tipo': '25463', 'valor': 10},
                          {'tipo': '25463', 'valor': 30}]
        },
    ]
    totales = {
        'M': '20', 'R': '600', 'QT': '70', 'RT': '1K'
    }
    cuenta = {
        'nombre': "Carlos Morocho",
        'usuario': "@cmorocho4",
        'verificado': True,
        'TT': '20 k',
        'S1': '30 k',
        'S2': '24 k'
    }
    usuario = {
        'nombre': "Carlos Morocho",
        'fecha': "2022-04-12",
        'hora': "12:30 PM",
    }
    ulr_img = "https://pbs.twimg.com/profile_images/1521501534865043462/9Maxnqvt_400x400.jpg"
    result = requests.get(ulr_img, stream=True).content
    imagen = base64.b64encode(result).decode()
    grafica = {
        'titulo': "Grfica de barras ",
        'items': [{
            'nombre': 'carlos'
        }],
        'imagen': result
    }
    atributos = {
        'titulo': 'REPORTE DE TWEETS', 'fecha_desde': '2022-06-17', 'fecha_hasta': '2022-06-17',
        'titles': titles, 'tweets': tweets, 'totales': {}, 'cuenta': cuenta,
        'get_values': get_values, "usuario": usuario, 'grafica': {}
    }
    dtemp = join(BASEDIR, 'cm_templates/')
    path = join(dtemp, 'reporte_tweets0.fodt')
    template = open(path, "r").read()
    template = template.replace("[IMAGEN]", imagen)
    in_path = join(dtemp, 'in_reporte_tweets.fodt')
    open(in_path, 'wb').write(template.encode())
    report = Report(abspath(in_path), ODT_MIME, loader=reporting.MIMETemplateLoader())
    content = report(**atributos).render().getvalue()
    out_path = join(dtemp, 'out_reporte_tweets.odt')
    open(out_path, 'wb').write(content)
    cmd = ['soffice',
           '--headless', '--nolockcheck', '--nodefault', '--norestore',
           '--convert-to', 'pdf', '--outdir', dtemp, out_path]
    subprocess.check_call(cmd)
    print("done")
