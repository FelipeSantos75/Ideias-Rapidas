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

### Linha por série de Fourier
1. Toque numa cor da imagem (ou escolha no seletor de cor).
2. **Tolerância de cor:** quanto a cor pode variar e ainda contar (0% = só a cor exata).
3. **Intervalo de pontos:** distância, em pixels, entre os pontos tirados do contorno.
4. **Quantidade de pontos:** quanto dos pontos do contorno usar (100% = todos). O botão **Reduzir 20%** tira 20% a cada toque (1000 → 800 → 640…); os termos da série caem na mesma proporção, deixando a linha mais lisa. A linha final (e o SVG) tem exatamente essa quantidade de pontos.
5. **Termos da série:** quantas frequências usar (−N…N). Poucos termos = linha lisa; muitos = fiel ao contorno.
6. Escolha só a maior área ou todas, veja a área encontrada e os pontos, anime os círculos (epiciclos), baixe a linha em SVG ou copie os coeficientes em JSON.
7. **Furos:** áreas sem a cor totalmente cercadas pela área (o miolo de um "O", por exemplo) viram contornos internos, em laranja, com série de Fourier própria. No SVG ficam como subcaminhos do mesmo caminho (`fill-rule="evenodd"`).

## Arquivos
- `conteudo.html` — fonte da página (é o que vai para o artefato do Claude).
- `index.html` — página completa para o GitHub Pages, gerada com `python3 gerar_index.py`. Não edite à mão.
- Vetorização: [imagetracerjs 1.2.6](https://github.com/jankovicsandras/imagetracerjs) via CDN, com paleta inicial por k-means++ calculada na página.

## Próximos passos
- Fourier: escolher várias cores de uma vez; animar também os furos.
- Processar em segundo plano (Web Worker) para imagens grandes não travarem a tela.
- Editar a paleta (trocar ou juntar cores) antes de baixar.
- Exportar também em PDF ou PNG ampliado.
