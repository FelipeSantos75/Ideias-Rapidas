# Ideias Rápidas — Memória principal

## O que é este repositório
Caixa de entrada de ideias simples que o dono tem **longe do PC** (geralmente pelo celular).
Cada ideia vira um protótipo pequeno, quase sempre um **artefato** (página HTML) para usar e testar rápido.

## Regras
- **Uma pasta por ideia**, na raiz do repositório.
  - Nome em `kebab-case`, curto e descritivo (ex.: `lista-de-compras`, `timer-pomodoro`).
- Cada pasta tem no mínimo:
  - `README.md` — a ideia em 2–5 linhas, como usar e o status.
  - `index.html` — o artefato, autocontido (HTML + CSS + JS no mesmo arquivo sempre que possível).
    - Painéis com dados (tipo Dashboard) guardam o código da página em `pagina.html` e os scripts que buscam os dados ao lado.
- O repositório é publicado no GitHub Pages: `index.html` da raiz lista as ideias (adicionar um link a cada ideia nova) e cada pasta abre em `https://felipesantos75.github.io/Ideias-Rapidas/<pasta>/`.
- Manter simples: sem build, sem dependências locais. Bibliotecas externas só via CDN com versão fixa.
- Funcionar bem no celular (layout responsivo, toque).
- Ao criar uma ideia nova, adicionar uma linha no índice abaixo.
- Idioma: português do Brasil (textos, READMEs, commits).

## Modelo de README da ideia
```md
# Nome da ideia
**Status:** rascunho | testando | pronto | arquivado
**Link do artefato:** (se publicado)

## Ideia
O que é e por que.

## Como usar
Passos curtos.

## Próximos passos
- ...
```

## Índice de ideias
| Pasta | Ideia | Status |
|-------|-------|--------|
| [`apuracao-2turno-2026`](apuracao-2turno-2026/) | Apuração ao vivo do 2º turno para presidente | testando |
| [`vetorizador`](vetorizador/) | Vetorizar imagens bitmap (PNG/JPG) em SVG no navegador | testando |
