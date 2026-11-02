import json
from dataclasses import asdict
from pathlib import Path
from PIL import Image
from DadosXML import DadosXML

import xml.etree.ElementTree as ET


caminhos_jpg_missingHole = Path(
    r"C:\Users\joaol\Pictures\SLM\trabAmarga\datasetPCB\PCB_DATASET\images\Missing_hole"
)

caminhos_xml_missingHole = Path(
    r"C:\Users\joaol\Pictures\SLM\trabAmarga\datasetPCB\PCB_DATASET\Annotations\Missing_hole"
)


CLASSES = {
    "missing_hole",
    "mouse_bite",
    "open_circuit",
    "short",
    "spur",
    "spurious_copper"
}


def verificar_nomes(caminho_jpg, caminho_xml):

    nomes_jpg = {
        arquivo.stem
        for arquivo in caminho_jpg.iterdir()
        if arquivo.is_file() and arquivo.suffix.lower() in {".jpg", ".jpeg"}
    }

    nomes_xml = {
        arquivo.stem
        for arquivo in caminho_xml.iterdir()
        if arquivo.is_file() and arquivo.suffix.lower() == ".xml"
    }

    jpg_sem_xml = nomes_jpg - nomes_xml
    xml_sem_jpg = nomes_xml - nomes_jpg

    if not jpg_sem_xml and not xml_sem_jpg:
        print("Todos os arquivos possuem correspondentes!")
    else:
        for nome in sorted(jpg_sem_xml):
            print(f"Imagem sem XML correspondente: {nome}")

        for nome in sorted(xml_sem_jpg):
            print(f"XML sem imagem correspondente: {nome}")

    return not jpg_sem_xml and not xml_sem_jpg


def verifica_xml(caminho_jpg, caminho_xml):

    dados_xml = []
    erros = []

    arquivos_xml = [
        arquivo
        for arquivo in caminho_xml.iterdir()
        if arquivo.is_file() and arquivo.suffix.lower() == ".xml"
    ]

    for arquivo_xml in arquivos_xml:

        nome_imagem = arquivo_xml.stem

        imagem = next(
            (
                caminho_jpg / f"{nome_imagem}{extensao}"
                for extensao in [".jpg", ".JPG", ".jpeg", ".JPEG"]
                if (caminho_jpg / f"{nome_imagem}{extensao}").is_file()
            ),
            None
        )

        if imagem is None:
            erros.append(f"{arquivo_xml.name}: imagem correspondente não encontrada.")
            continue

        # Leitura do XML
        try:
            arvore = ET.parse(arquivo_xml)
            raiz = arvore.getroot()

        except ET.ParseError:
            erros.append(f"{arquivo_xml.name}: XML malformado.")
            continue

        # Leitura das dimensões reais da imagem
        try:
            with Image.open(imagem) as img:
                largura_real, altura_real = img.size
                profundidade_real = len(img.getbands())

        except (OSError, ValueError) as erro:
            erros.append(f"{imagem.name}: não foi possível abrir a imagem: {erro}")
            continue

        # Extração das dimensões do XML
        try:
            largura = int(raiz.findtext("size/width"))
            altura = int(raiz.findtext("size/height"))
            profundidade = int(raiz.findtext("size/depth"))
            nome_imagem = raiz.findtext("filename")

        except (TypeError, ValueError):
            erros.append(f"{arquivo_xml.name}: dimensões ausentes ou inválidas.")
            continue

        # Validação das dimensões
        if largura <= 0 or altura <= 0 or profundidade <= 0:
            erros.append(f"{arquivo_xml.name}: dimensões devem ser positivas.")
            continue

        if largura != largura_real or altura != altura_real:
            erros.append(
                f"{arquivo_xml.name}: dimensões do XML ({largura}x{altura}) "
                f"diferem da imagem ({largura_real}x{altura_real})."
            )
            continue

        # Extração dos objetos
        objetos = raiz.findall("object")

        if not objetos:
            erros.append(f"{arquivo_xml.name}: nenhum objeto anotado.")
            continue

        # Validação individual de cada objeto
        for indice, objeto in enumerate(objetos, start=1):

            try:
                nome = objeto.findtext("name")

                truncated = int(objeto.findtext("truncated"))
                difficult = int(objeto.findtext("difficult"))

                xmin = int(objeto.findtext("bndbox/xmin"))
                ymin = int(objeto.findtext("bndbox/ymin"))
                xmax = int(objeto.findtext("bndbox/xmax"))
                ymax = int(objeto.findtext("bndbox/ymax"))

            except (TypeError, ValueError):
                erros.append(
                    f"{arquivo_xml.name}: objeto {indice} possui campos ausentes "
                    "ou valores inválidos."
                )
                continue

            if nome not in CLASSES:
                erros.append(
                    f"{arquivo_xml.name}: objeto {indice} possui classe desconhecida: {nome}."
                )
                continue

            if truncated not in (0, 1) or difficult not in (0, 1):
                erros.append(
                    f"{arquivo_xml.name}: objeto {indice} possui flags inválidas."
                )
                continue

            if not (0 <= xmin < xmax <= largura):
                erros.append(
                    f"{arquivo_xml.name}: objeto {indice} possui coordenadas X inválidas."
                )
                continue

            if not (0 <= ymin < ymax <= altura):
                erros.append(
                    f"{arquivo_xml.name}: objeto {indice} possui coordenadas Y inválidas."
                )
                continue

            # Armazenamento do objeto validado
            dados_xml.append(
                DadosXML(
                    nome_imagem=nome_imagem,
                    width=largura,
                    height=altura,
                    depth=profundidade,
                    tipo_defeito=nome,
                    truncated=bool(truncated),
                    difficult=difficult,
                    xmin=xmin,
                    ymin=ymin,
                    xmax=xmax,
                    ymax=ymax
                )
            )

    # Relatório final
    print("\n========== RELATÓRIO ==========")
    print(f"XMLs analisados: {len(arquivos_xml)}")
    print(f"Objetos válidos encontrados: {len(dados_xml)}")
    print(f"Problemas encontrados: {len(erros)}")

    for erro in erros:
        print("ERRO:", erro)

    return dados_xml, erros


verificar_nomes(caminhos_jpg_missingHole, caminhos_xml_missingHole)

dados, erros = verifica_xml(
    caminhos_jpg_missingHole,
    caminhos_xml_missingHole
)

print("\nPrimeiros objetos encontrados:")

for objeto in dados[:3]:
    print(objeto)

with open(r"../dataset/seila.json", "w") as arquivo:
    json.dump([asdict(c) for c in dados], arquivo, indent=4, ensure_ascii=False, default=str)