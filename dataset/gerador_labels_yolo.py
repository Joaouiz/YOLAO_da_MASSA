import json
import re
from pathlib import Path

from verificadores.DadosXML import DadosXML


def lerJson(caminho):
    with open(caminho, "r") as arquivo:
        dados = json.load(arquivo)

    lista = []
    for jpg in dados:
        lista.append(DadosXML(
                nome_imagem=jpg["nome_imagem"],
                width=jpg["width"],
                height=jpg["height"],
                depth=jpg["depth"],
                tipo_defeito=jpg["tipo_defeito"],
                truncated=jpg["truncated"],
                difficult=jpg["difficult"],
                xmin=jpg["xmin"],
                ymin=jpg["ymin"],
                xmax=jpg["xmax"],
                ymax=jpg["ymax"],
            )
        )

    return lista


def gerar_labels(pasta, class_id):
    pasta_images = Path(fr"C:\Users\joaol\PycharmProjects\PythonProject\dataset_yolo\images\{pasta}")

    for nome, objetos in dicionario.items():
        for i in range(len(objetos)):
            nome_arquivo = objetos[i].nome_imagem
            caminho_images = pasta_images / nome_arquivo

            if caminho_images.is_file():
                print("achei o arquivo")

                pasta_labels = Path(fr"C:\Users\joaol\PycharmProjects\PythonProject\dataset_yolo\labels\{pasta}")
                caminho_labels = pasta_labels / nome_arquivo
                caminho_labels = caminho_labels.with_suffix(".txt")

                with open(caminho_labels, "w") as arquivo:
                    for objeto in objetos:
                        W = objeto.width
                        H = objeto.height
                        xmin = objeto.xmin
                        ymin = objeto.ymin
                        xmax = objeto.xmax
                        ymax = objeto.ymax

                        xC = (xmin + xmax) / (2 * W)
                        yC = (ymin + ymax) / (2 * H)
                        width = (xmax - xmin) / W
                        height = (ymax - ymin) / H
                        arquivo.write(f"{class_id} {xC} {yC} {width} {height}\n")

            else:
                print("nao achei o arquivo")




lista = lerJson(r"C:\Users\joaol\PycharmProjects\PythonProject\dataset\seila.json")

dicionario = {}

for xml in lista:
    nome = xml.nome_imagem #defini qual chave usaremos
    nome = re.sub(r".jpg", "", nome) #tira o jpg do nome

    if nome not in dicionario:
        dicionario[nome] = []

    dicionario[nome].append(xml)

#print(dicionario)
#print(dicionario.get("01_missing_hole_01")[0].xmin)


gerar_labels("test", 0)
gerar_labels("train", 0)
gerar_labels("val", 0)