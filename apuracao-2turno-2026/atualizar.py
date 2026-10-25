"""Busca a apuração de presidente no TSE e gera um JSON de linhas (Brasil + UFs).

Uso: python3 atualizar.py <cod_eleicao> <saida.json>
2º turno 2026 = 6258 (1º turno = 6257).
"""
import json, sys, time, urllib.error, urllib.request

BASE = "https://resultados.tse.jus.br/oficial/ele2026/{e}/dados/{uf}/{uf}-c0001-e{e:06d}-u.json"
UFS = {"br": "Brasil", "ac": "Acre", "al": "Alagoas", "am": "Amazonas", "ap": "Amapá", "ba": "Bahia",
       "ce": "Ceará", "df": "Distrito Federal", "es": "Espírito Santo", "go": "Goiás", "ma": "Maranhão",
       "mg": "Minas Gerais", "ms": "Mato Grosso do Sul", "mt": "Mato Grosso", "pa": "Pará", "pb": "Paraíba",
       "pe": "Pernambuco", "pi": "Piauí", "pr": "Paraná", "rj": "Rio de Janeiro", "rn": "Rio Grande do Norte",
       "ro": "Rondônia", "rr": "Roraima", "rs": "Rio Grande do Sul", "sc": "Santa Catarina", "se": "Sergipe",
       "sp": "São Paulo", "to": "Tocantins", "zz": "Exterior"}
APELIDO = {"13": "lula", "22": "flavio"}


def num(x):
    return float(str(x).replace(",", ".")) if x not in (None, "") else 0.0


def baixar(e, uf):
    # Um pedido por vez, com pausa; se o TSE limitar (429), espera e tenta mais uma vez.
    for tentativa in range(2):
        try:
            with urllib.request.urlopen(BASE.format(e=e, uf=uf), timeout=30) as r:
                time.sleep(0.7)
                return json.load(r)
        except urllib.error.HTTPError as err:
            if err.code != 429 or tentativa:
                raise
            time.sleep(15)


def linha(uf, d):
    row = {"uf": uf.upper(), "nome": UFS[uf]}
    cands = [c for a in d["carg"][0]["agr"] for p in a["par"] for c in p["cand"]]
    for c in cands:
        k = APELIDO.get(c["n"])
        if k:
            row[k + "_votos"] = int(c["vap"])
            row[k + "_pct"] = round(num(c["pvapn"]) / 100, 6)
    s, el, v = d["s"], d["e"], d["v"]
    row.update({
        "secoes_pct": round(num(s["pstn"]) / 100, 6),
        "secoes_totalizadas": int(s["st"]),
        "secoes_total": int(s["ts"]),
        "eleitorado": int(el["te"]),
        "eleitorado_apurado": int(el["est"]),
        "comparecimento": int(el["c"]),
        "abstencao": int(el["a"]),
        "validos": int(v["vv"]),
        "brancos": int(v["vb"]),
        "nulos": int(v["tvn"]),
        "gerado_tse": f'{d["dg"]} {d["hg"]}',
        "totalizado_tse": f'{d["dt"]} {d["ht"]}'.strip(),
        "finalizado": d.get("tf") == "s",
    })
    return row


def main():
    e, out = int(sys.argv[1]), sys.argv[2]
    dados = {uf: baixar(e, uf) for uf in UFS}
    rows = [linha(uf, d) for uf, d in dados.items()]
    json.dump(rows, open(out, "w"), ensure_ascii=False)
    br = rows[0]
    print(f'{br["gerado_tse"]} secoes={br["secoes_pct"]:.4%} lula={br.get("lula_pct")} flavio={br.get("flavio_pct")}')


if __name__ == "__main__":
    main()
