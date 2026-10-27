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
4. Compare arrastando a linha (original × vetor) ou veja só o vetor, só o preenchimento (formas coloridas com o contorno sem cor; o SVG baixado/copiado nesse modo sai com `stroke="none"`) ou só os contornos.
5. Baixe o SVG ou copie o código.

### Linha por série de Fourier
1. Toque numa cor da imagem (ou escolha no seletor de cor).
2. **Tolerância de cor:** quanto a cor pode variar e ainda contar (0% = só a cor exata).
   - **Suavizar ruído antes:** desfoque leve (0–6 px) antes de procurar a cor; tira textura de papel e ruído de JPG. Em imagens escaneadas, use 2 px e baixe a tolerância para ~10%.
3. **Intervalo de pontos:** distância, em pixels, entre os pontos tirados do contorno.
4. **Quantidade de pontos:** quanto dos pontos do contorno usar (100% = todos). O botão **Reduzir 20%** tira 20% a cada toque (1000 → 800 → 640…); os termos da série caem na mesma proporção, deixando a linha mais lisa. A linha final (e o SVG) tem exatamente essa quantidade de pontos.
   - **Densidade por região:** escolha "Pintar: mais pontos" (verde) ou "Pintar: menos pontos" (laranja) e passe o dedo na imagem. Na parte pintada, a linha ganha ou perde pontos na proporção da **Intensidade** (×1,5 a ×10). "Apagar pintura" e "Limpar pintura" desfazem. Os pontos são espaçados pelo comprimento do contorno ponderado pela pintura, e como a série usa passos iguais de t, as partes com mais pontos também ganham mais detalhe.
5. **Termos da série:** quantas frequências usar (−N…N). Poucos termos = linha lisa; muitos = fiel ao contorno.
6. Escolha só a maior área ou todas, veja a área encontrada e os pontos, anime os círculos (epiciclos), baixe a linha em SVG ou copie os coeficientes em JSON.
7. **Curvas Bézier:** cada trecho entre dois pontos (de A até B) é uma curva cúbica de Bézier, não uma reta. As alças vêm da derivada da própria série, z'(t) = Σ 2πi·n·cₙ·e^(2πi·n·t): P1 = A + z'(t₀)·Δt/3 e P2 = B − z'(t₁)·Δt/3. Assim as curvas emendam sem quina e ficam fiéis à série mesmo com poucos pontos. Dá para ver as alças e desligar (volta a retas). O SVG usa comandos `C`.
8. **Furos:** áreas sem a cor totalmente cercadas pela área (o miolo de um "O", por exemplo) viram contornos internos, em laranja, com série de Fourier própria. No SVG ficam como subcaminhos do mesmo caminho (`fill-rule="evenodd"`).

### Juntar degradês
Com o interruptor **Juntar degradês**, cada objeto com degradê (um círculo do vermelho claro ao escuro, por exemplo) vira **uma forma só, em cor chapada** (a cor média do objeto), em vez de dezenas de faixas. A opção **Preencher com o degradê** (desligada por padrão) troca a cor chapada por um `linearGradient`.
1. A imagem é dividida em regiões que crescem pixel a pixel: o vizinho entra se a cor mudar pouco em relação a ele (**Tolerância do degradê**, padrão 6) e não se afastar demais da cor média da região.
2. Manchas pequenas e tiras finas (bordas serrilhadas) são absorvidas pela região vizinha.
3. Com "Preencher com o degradê" ligado, o degradê vem das cores reais: direção pela regressão cor = a + b·x + c·y e 5 paradas pela média de cor ao longo dessa direção. Regiões sem variação ficam com cor sólida.
4. O contorno é simplificado (Douglas-Peucker) e suavizado em curvas Bézier, mantendo cantos; regiões vazadas ganham furos (`evenodd`).
Teste: círculo + retângulo em degradê passaram de 48 caminhos (16 cores) para 3 formas (2 em degradê), e o SVG de 17,5 KB para 2,4 KB.

## Visual
Segue o design system **Liquid Glass** da conta (https://claude.ai/artifact/4MXM3vL7iBhfxCU9weAxkW): cartões opacos para o conteúdo, vidro translúcido só no que flutua sobre a imagem (etiquetas, puxador, avisos), botões e escolhas em cápsula, interruptores, fonte do sistema e temas claro e escuro pelos tokens.

## Arquivos
- `conteudo.html` — fonte da página (é o que vai para o artefato do Claude).
- `index.html` — página completa para o GitHub Pages, gerada com `python3 gerar_index.py`. Não edite à mão.
- Vetorização: [imagetracerjs 1.2.6](https://github.com/jankovicsandras/imagetracerjs) via CDN, com paleta inicial por k-means++ calculada na página.

## Próximos passos
- Fourier: escolher várias cores de uma vez; animar também os furos.
- Processar em segundo plano (Web Worker) para imagens grandes não travarem a tela.
- Editar a paleta (trocar ou juntar cores) antes de baixar.
- Exportar também em PDF ou PNG ampliado.
