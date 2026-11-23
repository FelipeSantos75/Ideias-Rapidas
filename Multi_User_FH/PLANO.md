# Multi_User_FH — Plano do projeto

Thin clients em Raspberry Pi: cada aparelho liga direto no app Multi_User_FH, o usuário faz login e cai numa sessão remota (RDP) num servidor Windows compartilhado.

---

## 0. Antes de tudo: licenciamento do Windows (ponto crítico)

**Windows 10/11 Pro não aceita várias sessões ao mesmo tempo.** O Pro (e também o Enterprise comum) permite **uma** sessão interativa por vez. Se um segundo usuário entra por RDP, o primeiro é desconectado.

Para ter vários usuários simultâneos, as opções legais são:

| Opção | Sessões simultâneas | Custo | Observação |
|---|---|---|---|
| **Windows Server 2022/2025 + função RDS (Remote Desktop Services)** | Várias (limitadas pelo hardware) | Licença do Server + **1 RDS CAL por usuário ou por dispositivo** | **Recomendado.** É o caminho que a Microsoft prevê para isso. |
| Windows 11 Enterprise multi-session | Várias | Só roda no Azure Virtual Desktop (nuvem) | Não serve para servidor local. |
| Servidor Linux + xrdp | Várias | Grátis | Só serve se os usuários não precisarem de programas Windows. |
| ~~RDP Wrapper / patch do termsrv.dll no Win Pro~~ | Várias | — | **Viola a licença** e costuma quebrar a cada Windows Update. Não usar em produção. |

Dica de custo: com aparelhos fixos e vários turnos usando o mesmo Pi, a **CAL por dispositivo** sai mais barata. Se cada pessoa tem o seu aparelho, a **CAL por usuário** é melhor.

---

## 1. Arquitetura

```
 ┌──────────── Raspberry Pi (por posto) ────────────┐        ┌──────── Servidor ────────────────────┐
 │ Raspberry Pi OS Lite (64-bit)                    │        │ Windows Server + RDS Session Host     │
 │  └─ autologin → compositor kiosk (cage/Wayland)  │  RDP   │  ├─ Active Directory (ou contas locais)│
 │      └─ Multi_User_FH (tela de login)            │ ─────► │  ├─ GPO: limites de sessão/perfis      │
 │          └─ FreeRDP (motor da conexão)           │  3389  │  └─ (opcional) RD Gateway p/ internet  │
 │ root somente leitura (overlayfs) + watchdog      │        │                                       │
 └──────────────────────────────────────────────────┘        │ Multi_User_FH Manager (API + painel)  │
                     ▲  HTTPS (configuração, heartbeat)       │  ├─ cadastro dos aparelhos            │
                     └─────────────────────────────────────── │  ├─ sessões ativas / desconectadas    │
                                                              │  └─ logs, atualizações               │
                                                              └───────────────────────────────────────┘
```

Três peças de software:

1. **Cliente (no Pi)**: tela de login em tela cheia que chama o FreeRDP. Quando a sessão termina (logoff, queda de rede), volta para a tela de login.
2. **Imagem do Pi**: sistema mínimo e travado que só abre o cliente. O usuário não chega a um terminal nem a um desktop Linux.
3. **Manager (no servidor)**: API e painel web que registram os aparelhos, distribuem a configuração, mostram as sessões e permitem derrubar uma sessão ou reiniciar um aparelho.

### Como "salvar as sessões"
- **No Windows**: o RDS já mantém a sessão **desconectada** viva. Se o usuário sai sem fazer logoff (ou se a rede cai), ele faz login de novo, em qualquer Pi, e volta para onde estava. O tempo que uma sessão desconectada fica viva vem de uma GPO (ex.: 2 horas, depois logoff automático).
- **Perfis**: os perfis ficam no servidor (com perfis móveis ou FSLogix, se um dia houver mais de um servidor).
- **No Manager**: histórico de quem entrou, em qual aparelho, quando, e por quanto tempo.

---

## 2. Escolhas de tecnologia

| Item | Escolha | Por quê |
|---|---|---|
| Hardware | **Raspberry Pi 5 (4 GB)** ou Pi 4 (4 GB) | O Pi 5 decodifica o fluxo gráfico do RDP por software com folga. O Pi 4 tem decodificador H.264 por hardware, mas a CPU é mais fraca. Testar os dois no PoC. |
| Armazenamento | SSD por USB ou NVMe (Pi 5) > cartão SD de boa qualidade | Cartão SD se desgasta. O root somente leitura ajuda muito. |
| SO | Raspberry Pi OS Lite 64-bit (Debian) | Leve, bem suportado, tem FreeRDP 3 nos repositórios. |
| Kiosk | **cage** (compositor Wayland de um app só) | Abre apenas o nosso app e não tem barra de tarefas nem desktop. |
| Motor RDP | **FreeRDP 3** (`sdl-freerdp3` / `xfreerdp3`) | Open source e maduro. Tem NLA, áudio, microfone, USB, impressora, RemoteFX/GFX e multi-monitor. Não vale escrever um protocolo RDP do zero. |
| App cliente | **Python 3 + PySide6 (Qt/QML)** | Rápido de desenvolver, roda bem no Pi e permite uma interface bonita em tela cheia. (Alternativa: Rust + Slint, se quiser um binário único e mais leve.) |
| Manager | **Python FastAPI + SQLite/PostgreSQL** + painel web simples | Pode rodar no próprio Windows Server ou numa VM ou container à parte. |
| Provisionamento | **pi-gen** (imagem customizada) ou script + Ansible | Grava a mesma imagem em todos os Pis. A identidade do aparelho vem do serial ou MAC. |

---

## 3. Fluxo do usuário

1. O usuário liga o Pi. O boot leva cerca de 15 s e abre a tela do Multi_User_FH com logo, campos de usuário e senha, status da rede e o nome do posto.
2. Ele digita usuário e senha e dá Enter.
3. O app inicia o FreeRDP em tela cheia, passando as credenciais por **stdin** (`/from-stdin`) e nunca na linha de comando, para não aparecerem no `ps`.
4. Com NLA, o próprio Windows valida a senha. Se ela estiver errada, o app mostra uma mensagem amigável traduzida a partir do código de saída do FreeRDP.
5. O usuário trabalha no Windows.
6. Quando ele faz logoff, desconecta ou a rede cai, o FreeRDP encerra e o app volta à tela de login, limpando os campos.
7. Opcional: um botão "Desligar" ou "Reiniciar" na tela de login.

Exemplo de comando que o app vai montar:
```bash
sdl-freerdp3 /v:servidor.local /d:EMPRESA /u:joao /from-stdin \
  /f /gfx /sound /microphone /dynamic-resolution \
  /cert:tofu /auto-reconnect /auto-reconnect-max-retries:5
```

---

## 4. Fases

### Fase 0 — Prova de conceito (1 a 2 semanas)
- [ ] Montar o servidor de teste: Windows Server 2022/2025 com período de avaliação de 180 dias, função RDS Session Host e licenciamento RDS em modo de avaliação (120 dias).
- [ ] Criar 3 ou 4 usuários de teste.
- [ ] Instalar o Raspberry Pi OS Lite e o FreeRDP 3 no Pi e conectar pela linha de comando.
- [ ] Medir CPU, fluidez de vídeo e rolagem, áudio e latência no Pi 4 e no Pi 5.
- [ ] Testar 3 Pis conectados ao mesmo tempo no mesmo servidor.
- **Entregável**: decisão de hardware e confirmação de que a experiência é aceitável.

### Fase 1 — App cliente MVP (2 a 3 semanas)
- [ ] Tela de login em PySide6/QML, em tela cheia e navegável só pelo teclado.
- [ ] Módulo `rdp_runner`: monta os argumentos, abre o FreeRDP, envia as credenciais pelo stdin, monitora o processo e traduz os códigos de erro.
- [ ] Arquivo de configuração local (`/etc/multi_user_fh/config.toml`) com servidor, domínio, opções de áudio/USB/impressora e nome do posto.
- [ ] Volta automática para a tela de login, com limpeza de memória e dos campos.
- [ ] Indicador de rede (IP, se o servidor está alcançável).
- [ ] Logs locais em arquivo rotativo.
- **Entregável**: app rodando no Pi com sessões abrindo e fechando em ciclo.

### Fase 2 — Imagem kiosk do Pi (1 a 2 semanas)
- [ ] Autologin de um usuário sem privilégios (`kiosk`) e cage abrindo o app pelo systemd.
- [ ] Se o app cair, o systemd o reinicia (`Restart=always`).
- [ ] Desativar a troca de TTY (Ctrl+Alt+F1…), o console no HDMI e o SSH por senha (deixar só por chave, para manutenção).
- [ ] Root somente leitura com overlayfs e uma partição separada para configuração e logs.
- [ ] Watchdog de hardware, NTP e firewall (só a saída para o servidor).
- [ ] Gerar a imagem com o pi-gen: gravar e usar.
- **Entregável**: `multi_user_fh-vX.img`.

### Fase 3 — Manager central (3 a 4 semanas)
- [ ] API: cadastro e aprovação de aparelhos (o Pi se registra pelo serial), configuração por aparelho ou grupo e heartbeat.
- [ ] Coleta de sessões no Windows: um pequeno agente PowerShell ou serviço que lê `qwinsta`/`Get-RDUserSession` e envia para a API.
- [ ] Painel web: aparelhos online/offline, quem está logado e onde, sessões desconectadas, botões de "derrubar sessão", "logoff" e "reiniciar Pi", e histórico.
- [ ] Atualização do app: o Pi verifica se há uma versão nova e baixa um pacote `.deb` assinado.
- [ ] Autenticação do painel (admin) e HTTPS.
- **Entregável**: painel controlando todos os postos.

### Fase 4 — Servidor de produção e piloto (2 semanas)
- [ ] Dimensionar o servidor (veja a seção 5), comprar o Windows Server e as RDS CALs e ativar o servidor de licenças RDS.
- [ ] GPOs: limite de sessão desconectada, logoff de sessão ociosa, redirecionamentos permitidos (impressora, USB, áudio), bloqueios.
- [ ] Certificado válido no RDP, para evitar o aviso de certificado.
- [ ] Backup dos perfis e do servidor.
- [ ] Piloto com 3 a 5 usuários reais durante 1 a 2 semanas, recolhendo feedback.

### Fase 5 — Implantação e operação
- [ ] Rollout gradual dos postos.
- [ ] Documentação: manual do usuário (1 página) e manual do administrador.
- [ ] Monitoramento: alerta se o servidor passar de 80 % de RAM ou CPU e se um Pi ficar offline.

---

## 5. Dimensionamento aproximado do servidor

Para uso de escritório (navegador, Office, sistema de gestão):

| Usuários simultâneos | vCPU | RAM | Disco |
|---|---|---|---|
| até 10 | 8 | 32 GB | SSD 500 GB |
| 10–25 | 16 | 64 GB | SSD 1 TB |
| 25+ | considerar 2 servidores + Connection Broker | | |

Regra de bolso: de 2 a 4 GB de RAM por usuário e 1 vCPU para cada 2 ou 3 usuários. Navegadores pesados aumentam muito essa conta.

Rede: cabo de **1 Gbps** nos Pis sempre que possível. Wi-Fi funciona, mas oscila.

---

## 6. Estrutura sugerida do repositório

```
Multi_User_FH/
├── PLANO.md
├── client/                 # App do Pi (Python + PySide6)
│   ├── multi_user_fh/
│   │   ├── main.py
│   │   ├── ui/            # QML
│   │   ├── rdp_runner.py
│   │   ├── config.py
│   │   └── manager_api.py
│   ├── tests/
│   └── pyproject.toml
├── image/                  # pi-gen stage customizado, units systemd, overlayfs
├── manager/                # API FastAPI + painel web
├── server-agent/           # Script/serviço PowerShell no Windows Server
└── docs/                   # Manuais usuário/admin, GPOs
```

---

## 7. Riscos e cuidados

| Risco | Mitigação |
|---|---|
| Licença errada (Win Pro com patch) | Usar Windows Server + RDS CALs desde o início (seção 0). |
| Desempenho com vídeo (YouTube, Teams) | Testar no PoC. Usar `/gfx` com H.264 e, se for crítico, considerar o Pi 5. |
| Cartão SD corromper | Root somente leitura, SSD e watchdog. |
| Senha exposta | Credenciais só via stdin e só em memória, NLA obrigatório, TLS e certificado válido. |
| Servidor único é ponto de falha | Backup e snapshot. Na fase 2, um segundo Session Host com Connection Broker. |
| Periféricos (impressora, leitor, USB) | Levantar cedo e testar o redirecionamento do FreeRDP no PoC. |

---

## 8. Perguntas em aberto (definem detalhes do plano)

1. Quantos postos e quantos usuários simultâneos?
2. Quais programas os usuários vão usar? Precisam mesmo de Windows?
3. Os Pis ficam na mesma rede local do servidor ou acessam pela internet (isso exige RD Gateway ou VPN)?
4. Já existe Active Directory/domínio, ou vamos usar contas locais no servidor?
5. Que periféricos são necessários: impressora, leitor de código de barras, webcam, áudio?
6. O servidor será físico, uma VM local ou ficará na nuvem?

---

## 9. Próximo passo imediato

Montar a **Fase 0**: instalar o Windows Server em avaliação numa máquina ou VM, ativar o RDS e conectar 2 ou 3 Pis usando só o FreeRDP pela linha de comando. Se a experiência for boa, começar a escrever o app cliente (Fase 1).
