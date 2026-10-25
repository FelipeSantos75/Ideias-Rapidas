# Apuração 2º turno 2026
**Status:** testando
**Página (GitHub Pages):** https://felipesantos75.github.io/Ideias-Rapidas/apuracao-2turno-2026/
**Link do artefato (versão painel):** https://claude.ai/artifact/YFR2EBqhuBtPuic8V62of7

## Ideia
Acompanhar pelo celular a apuração do 2º turno para presidente (25/10/2026): Lula (13) × Flávio Bolsonaro (22).
Mostra o placar nacional, % de seções apuradas, comparecimento/abstenção/brancos/nulos e o resultado por estado, com o 1º turno para comparar.

## Como funciona
- `index.html` é a versão autônoma: lê o TSE direto do navegador a cada 30 s (o TSE libera esse acesso). Usa `mapa_estados.json` e `primeiro_turno.json` da mesma pasta. Não depende do Claude.

Versão painel (artefato do Claude):
- `atualizar.py <cod_eleicao> <saida.json>` lê os arquivos oficiais do TSE (resultados.tse.jus.br) e gera linhas do Brasil + cada UF.
  - 2º turno = `6258`, 1º turno = `6257`.
- `vigiar.sh <saida.json>` roda o script a cada 2 min (Brasil sempre, 4 estados por vez em rodízio, porque o TSE limita pedidos) e avisa quando os votos mudam; o Claude então envia o arquivo novo para o painel.
- `gerar_mapa.py` transforma o GeoJSON dos estados em contornos SVG simplificados para o mapa.
- `pagina.html` é o código da página do painel (artefato do tipo Dashboard).

## Próximos passos
- ~~Mapa por estado~~ (feito: Lula em vermelho, Flávio em azul).
- Gráfico da evolução do placar ao longo da apuração.
