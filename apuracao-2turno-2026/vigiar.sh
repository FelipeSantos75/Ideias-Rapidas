#!/bin/bash
# Consulta o TSE a cada 2 min; quando os votos mudam, grava $OUT e imprime uma linha.
DIR=$(cd "$(dirname "$0")" && pwd)
OUT=${1:?saida}; TMP=$OUT.tmp; LAST=$OUT.hash
while true; do
  if msg=$(python3 "$DIR/atualizar.py" 6258 "$TMP" 2>&1); then
    h=$(python3 -c "import json,sys,hashlib;r=json.load(open(sys.argv[1]));print(hashlib.md5(json.dumps([{k:v for k,v in x.items() if k not in('gerado_tse','consultado_em','proxima_em')} for x in r]).encode()).hexdigest())" "$TMP")
    if [ "$h" != "$(cat "$LAST" 2>/dev/null)" ]; then
      mv "$TMP" "$OUT"; echo "$h" > "$LAST"; echo "NOVO $msg"
      grep -q '"finalizado": true' <(python3 -c "import json;print(json.dumps(json.load(open('$OUT'))[0]))") && { echo "FINALIZADO"; exit 0; }
    fi
  else
    echo "ERRO $(echo "$msg" | tail -1)"
    sleep 300  # TSE limitou (429) ou falhou: espera mais antes de tentar de novo
  fi
  sleep 120
done
