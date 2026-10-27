# Vetorizador de Bitmap
**Status:** testando
**Link do artefato:** https://claude.ai/artifact/4MdgwYSKMnEgTE8mPSbDuo
**Página (GitHub Pages):** https://felipesantos75.github.io/Ideias-Rapidas/vetorizador/

## Ideia
Transformar imagens bitmap (PNG, JPG, WebP, GIF, BMP) em SVG direto no navegador, sem enviar a imagem para servidor nenhum.

## Como usar
1. Escolha, arraste ou cole (Ctrl+V) uma imagem. Abre com uma imagem de exemplo.
2. Escolha o tipo: Logo / ícone, Ilustração, Foto, Preto e branco ou Bem detalhado.
3. Ajuste cores, detalhe, manchas, suavização e tamanho. Dá para remover o fundo e realçar cantos retos.
4. Compare arrastando a linha (original × vetor) ou veja só o vetor ou só os contornos.
5. Baixe o SVG ou copie o código.

## Arquivos
- `conteudo.html` — fonte da página (é o que vai para o artefato do Claude).
- `index.html` — página completa para o GitHub Pages, gerada com `python3 gerar_index.py`. Não edite à mão.
- Vetorização: [imagetracerjs 1.2.6](https://github.com/jankovicsandras/imagetracerjs) via CDN, com paleta inicial por k-means++ calculada na página.

## Próximos passos
- Processar em segundo plano (Web Worker) para imagens grandes não travarem a tela.
- Editar a paleta (trocar ou juntar cores) antes de baixar.
- Exportar também em PDF ou PNG ampliado.
