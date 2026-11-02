import json
from dataclasses import asdict
from pathlib import Path
from PIL import Image

import xml.etree.ElementTree as ET

from DadosXML import DadosXML

caminhos_jpg_missingHole = Path(r"C:\Users\joaol\Pictures\SLM\trabAmarga\datasetPCB\PCB_DATASET\images\Missing_hole")
caminhos_xml_missingHole = Path(r"C:\Users\joaol\Pictures\SLM\trabAmarga\datasetPCB\PCB_DATASET\Annotations\Missing_hole")

def verificar_nomes(caminho_jpg, caminho_xml):

    nomes_jpg = []
    for arquivo in caminho_jpg.iterdir():
        if arquivo.is_file():
            if arquivo.suffix == ".jpg" or arquivo.suffix == ".JPG":
                nomes_jpg.append(arquivo.stem)

    nomes_xml = []
    for arquivo in caminho_xml.iterdir():
        if arquivo.is_file():
            if arquivo.suffix == ".xml" or arquivo.suffix == ".XML":
                nomes_xml.append(arquivo.stem)

    erros = 0
    if len(nomes_jpg) == len(nomes_xml):
        for i in range(len(nomes_jpg)):
            if nomes_jpg[i] not in nomes_xml:
                print("Este caramarada ", nomes_jpg[i], " nao tem correspondente em nomes_xml")
                erros += 1

        for i in range(len(nomes_xml)):
            if nomes_xml[i] not in nomes_jpg:
                print("Este caramarada ", nomes_xml[i], " nao tem correspondente em nomes_jpg")
                erros += 1
    else:
        print("A quantidade de jpg nao bate com a de xml, arrume ai!")
        return

    if erros == 0:
        print("Nenhum erro, todos os jpg tem um xml correspondente, e vice versa!")
    else:
        print("Foram encontrados erros durante a verificacao dos arquivos, no total foram: ", erros, "erros!")


def verifica_xml(caminho_xml):
    dados_xml = []

    nomes_xml = []
    for arquivo in caminho_xml.iterdir():
        if arquivo.is_file():
            if arquivo.suffix == ".xml" or arquivo.suffix == ".XML":
                nomes_xml.append(arquivo.name)

    erros = 0
    for i in range(len(nomes_xml)):
        try:
            xml_safado = ET.parse(caminho_xml / nomes_xml[i])
            dados = xml_safado.getroot()

            #print(dados.find("folder").text)
        except ET.ParseError:
            print("Nao foi possivel acessar um XML!")
            return

        #verifica se as tags obrigatorias existem e pega os dados delas
        if dados.find("size/width") is not None:
            width = int(dados.find("size/width").text)
        else:
            erros += 1
            print("Erro: A tag 'size/width' não foi encontrada.")

        if dados.find("size/height") is not None:
            height = int(dados.find("size/height").text)
        else:
            erros += 1
            print("Erro: A tag 'size/height' não foi encontrada.")

        if dados.find("size/depth") is not None:
            depth = int(dados.find("size/depth").text)  # Corrigido: adicionei .text aqui
        else:
            erros += 1
            print("Erro: A tag 'size/depth' não foi encontrada.")

        if dados.find("object/name") is not None:
            tipo_defeito = dados.find("object/name").text
        else:
            erros += 1
            print("Erro: A tag 'object/name' (tipo do defeito) não foi encontrada.")

        if dados.find("object/truncated") is not None:
            truncated = bool(dados.find("object/truncated").text)
        else:
            erros += 1
            print("Erro: A tag 'object/truncated' não foi encontrada.")

        if dados.find("object/difficult") is not None:
            difficult = int(dados.find("object/difficult").text)
        else:
            erros += 1
            print("Erro: A tag 'object/difficult' não foi encontrada.")

        if dados.find("object/bndbox/xmin") is not None:
            xmin = int(dados.find("object/bndbox/xmin").text)
        else:
            erros += 1
            print("Erro: A tag 'object/bndbox/xmin' não foi encontrada.")

        if dados.find("object/bndbox/ymin") is not None:
            ymin = int(dados.find("object/bndbox/ymin").text)
        else:
            erros += 1
            print("Erro: A tag 'object/bndbox/ymin' não foi encontrada.")

        if dados.find("object/bndbox/xmax") is not None:
            xmax = int(dados.find("object/bndbox/xmax").text)
        else:
            erros += 1
            print("Erro: A tag 'object/bndbox/xmax' não foi encontrada.")

        if dados.find("object/bndbox/ymax") is not None:
            ymax = int(dados.find("object/bndbox/ymax").text)
        else:
            erros += 1
            print("Erro: A tag 'object/bndbox/ymax' não foi encontrada.")


        imagem = Image.open(r"C:\Users\joaol\Pictures\SLM\trabAmarga\datasetPCB\PCB_DATASET\images\Missing_hole\01_missing_hole_01.jpg")
        larguraI, alturaI = imagem.size
        if width == larguraI and height == alturaI:
            if 0 <= xmin and xmin < xmax and xmax <= width:
                if 0 <= ymin and ymin < ymax and ymax <= height:
                    dados_xml.append(DadosXML(width, height, depth, tipo_defeito, truncated, difficult, xmin, ymin, xmax, ymax))
                else:
                    print("alguma coisa deu pau, boa sorte pra acha ai, to morrendo de preguica")
                    erros += 1

    if erros > 0:
        print("Erro ao ler os dados.")
    else:
        print(dados_xml)
        return dados_xml
    #print(width)
    #print(dados.find("size"))


#verificar_nomes(caminhos_jpg_missingHole, caminhos_xml_missingHole)
lista = verifica_xml(caminhos_xml_missingHole)

with open(r"../dataset/seila.json", "w") as arquivo:
    json.dump([asdict(c) for c in lista], arquivo, indent=4, ensure_ascii=False, default=str)