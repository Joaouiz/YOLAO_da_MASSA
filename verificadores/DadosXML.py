from dataclasses import dataclass


@dataclass
class DadosXML:
    nome_imagem: str

    width: int
    height: int
    depth: int

    tipo_defeito: str
    truncated: bool
    difficult: int
    xmin: int
    ymin: int
    xmax: int
    ymax: int