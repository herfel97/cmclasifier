"""
    C&M - Clasificador
    ========================
    Gestor del Clasificador de tweets | zero-shot-classification
    :autor @cmorocho
"""
import re
from cleantext import clean
from transformers import pipeline

# REGEX TO DELETE NOICE
REGEX_1 = r'[(http(s)?):\/\/(www\.)?a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}\b([-a-zA-Z0-9@:%_\+.~#?&//=]*)'  # Urls
#REGEX_2 = r'([@#]\w+)+'  # Hastasg, Menciones
REGEX_2 = r"(([@#]\w+)(\s+|$)){2,}"
#REGEX_3 = r"[^\w\s]+"  # Signos de putuacion
REGEX_3 = r"(\s*[^\w\s]+\s*){2,}|[@#&!+/*~=]"
REGEX_4 = r'[\n\t\r\f\s]+'  # Caracteres Especiales


class ClasificationModel(object):

    def __init__(self):
        # self.model = fasttext.load_model("C:/Users/Usuario/Documents/Tesis/cm_clasificador/data_entrenamiento/QuejasCuenca.bin")
        # self.model = pipeline("zero-shot-classification", model="dccuchile/bert-base-spanish-wwm-cased")
        # self.model = pipeline("zero-shot-classification", model="Recognai/bert-base-spanish-wwm-cased-xnli")
        # self.model = pipeline("zero-shot-classification", model="Recognai/zeroshot_selectra_medium")
        self.model = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

    @staticmethod
    def normalizar(texto):
        texto = clean(texto, no_emoji=True, lower=False)
        texto = re.sub(REGEX_1, " ", texto)
        texto = re.sub(REGEX_2, " ", texto)
        texto = re.sub(REGEX_3, " ", texto)
        texto = re.sub(REGEX_4, " ", texto)
        texto = texto.strip()
        return texto if len(texto.split(" ")) > 2 else ''

    def clasificar(self, texto, clases):
        """
        Clasifica el texto segun las clases
        :param texto:
        :param clases:
        :return:
        """
        labels = {c['nombre']: {**c} for c in clases}
        resultado = self.model(texto, candidate_labels=list(labels.keys()),  # multi_label=True)
                               hypothesis_template="Este ejemplo trata de {}.", multi_label=True)
        prediccion = dict(zip(resultado['labels'], resultado['scores']))
        clasificacion = []
        for clase in prediccion:
            # Obtiene el score prediction
            score = float('{:.2%}'.format(prediccion[clase]).replace("%", ""))
            # Compara con los scores min y max
            if score >= labels[clase]['min_score']:
                is_selected = score >= labels[clase]['max_score']
                clasificacion.append({'clase': labels[clase], 'score': score, 'is_selected': is_selected})
        # Retorna la clasificacion
        return clasificacion
