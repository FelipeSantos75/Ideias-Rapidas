"""Gera index.html (página completa, para o GitHub Pages) a partir de conteudo.html (fonte do artefato)."""
import pathlib
aqui = pathlib.Path(__file__).parent
c = (aqui / "conteudo.html").read_text()
cab, _, resto = c.partition("<style>")
html = ('<!doctype html>\n<html lang="pt-BR">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
        + cab + "<style>" + resto.split("</style>", 1)[0] + "</style>\n</head>\n<body>\n"
        + resto.split("</style>", 1)[1].lstrip() + "</body>\n</html>\n")
(aqui / "index.html").write_text(html)
print("index.html gerado")
