# Multi_User_FH — Plano do projeto

Postos de trabalho baratos (Raspberry Pi, mini PC, celular reaproveitado…): o aparelho liga direto no app **Multi_User_FH**, o usuário faz login e usa **apenas os programas autorizados pela firma (RemoteApp)**, que rodam num servidor Windows compartilhado. O app e o Manager central cadastram os aparelhos, acompanham as sessões e guardam o histórico.

> **Princípio do projeto:** nada está escrito em pedra. O servidor e o Manager são únicos, e o **cliente pode rodar em vários tipos de hardware e sistema**, as "trilhas". Testamos cada trilha e escolhemos pelo custo, pela estabilidade e pela experiência do usuário.

---

## 1. Servidor: o que permite várias sessões

O número de sessões simultâneas é definido pelo **servidor**, não pelo aparelho do usuário.

| Opção | Sessões simultâneas | Custo | Observação |
|---|---|---|---|
| **Windows Server 2022/2025 + RDS (Remote Desktop Services)** | Várias (limitadas pelo hardware) | Licença do Server + **1 RDS CAL por usuário ou por dispositivo** | **Caminho principal.** |
| Windows 11 Enterprise multi-session | Várias | Só no Azure Virtual Desktop (nuvem) | Para uma versão hospedada na nuvem, no futuro. |
| Servidor Linux + xrdp | Várias | Grátis | Se os usuários não precisarem de programas Windows. |
| Windows 10/11 Pro | **Apenas 1** | — | O Pro não permite sessões simultâneas. Patches como o RDP Wrapper violam a licença e quebram com o Windows Update. |

Dica: com postos fixos e turnos compartilhando o aparelho, a **CAL por dispositivo** sai mais barata. Se cada pessoa tem o seu posto, a **CAL por usuário** é melhor.

### Configuração do servidor
- Função **RDS Session Host** e servidor de licenciamento RDS.
- **GPOs**: tempo de vida da sessão desconectada (ex.: 2 h), logoff de sessão ociosa, redirecionamentos permitidos (áudio, impressora, USB), certificado válido no RDP.
- **Perfis** no servidor (perfis móveis ou FSLogix quando houver mais de um Session Host).
- **Implantação RDS completa** (Gerenciador do Servidor): **Session Host + Connection Broker** (e, se quiser, **Web Access**). O Connection Broker é necessário para publicar os RemoteApps e permite crescer para vários servidores.
- Opcional: **RD Gateway** (ou VPN) para postos fora da rede local.

### Modo padrão: RemoteApp
O usuário **não recebe o desktop do Windows**. Ele vê só os **programas autorizados pela firma**, cada um numa janela, sem menu Iniciar, sem Explorer e sem desktop.

| Perfil | Modo |
|---|---|
| **Usuários comuns** | **RemoteApp** (padrão): só os apps publicados para o seu grupo |
| **Administradores / TI** | Desktop completo (permissão separada) |

**Configuração no servidor:**
- Criar uma **coleção de sessão** e **publicar os programas** (ERP, Excel, navegador, etc.).
- **Liberar cada RemoteApp por grupo do AD**. Exemplo: Financeiro vê ERP + Excel; Atendimento vê só o CRM.
- Todos os apps de um usuário rodam **na mesma sessão** no servidor: ele abre vários ao mesmo tempo, copia e cola entre eles e, ao reconectar, encontra tudo como deixou.
- Para testes rápidos sem Connection Broker, dá para publicar pelo registro (`TSAppAllowList`). Em produção, usar a coleção.

**Segurança (obrigatório junto com o RemoteApp):** o RemoteApp sozinho **não é uma barreira de segurança**. O usuário pode tentar abrir outros programas a partir dos liberados, por exemplo pela janela "Abrir arquivo", por links ou por macros. Por isso:
- **AppLocker** (ou **WDAC**) no servidor: só os executáveis autorizados rodam para os usuários comuns.
- **GPOs**: bloquear o prompt de comando, o PowerShell, o painel de controle, o regedit e o Gerenciador de Tarefas, esconder ou restringir os discos do servidor e desativar macros não assinadas.
- Pastas de trabalho em compartilhamento controlado, com permissões por grupo.

### Dimensionamento (uso de escritório)
| Usuários simultâneos | vCPU | RAM | Disco |
|---|---|---|---|
| até 10 | 8 | 32 GB | SSD 500 GB |
| 10–25 | 16 | 64 GB | SSD 1 TB |
| 25+ | 2+ servidores com Connection Broker | | |

Regra de bolso: de 2 a 4 GB de RAM por usuário e 1 vCPU para cada 2 ou 3 usuários.

---

## 2. Arquitetura geral

```
          ┌──────────────── Clientes (qualquer trilha) ────────────────┐
          │  Trilha A: Linux (Pi / mini PC / thin client)              │
          │  Trilha B: Android quiosque (Galaxy S9/S10 + hub HDMI)     │
          │  Trilha C: Windows 11 ARM (Snapdragon / Pi com UEFI)       │
          │  Trilha D: Note 8 Pro com ponte DSI→HDMI (pesquisa)        │
          └─────────────┬──────────────────────────────┬───────────────┘
                        │ RDP (3389 / Gateway 443)     │ HTTPS (config, heartbeat)
                        ▼                              ▼
   ┌──────── Windows Server + RDS ────────┐   ┌──────── Multi_User_FH Manager ────────┐
   │ Sessões dos usuários                 │◄──┤ API + painel web                       │
   │ AD / contas, GPO, perfis             │   │ aparelhos, sessões, histórico, updates │
   │ Agente Multi_User_FH (PowerShell)    ├──►│                                       │
   └──────────────────────────────────────┘   └────────────────────────────────────────┘
```

### Contrato comum entre todos os clientes
Todas as trilhas fazem as mesmas coisas, cada uma com a sua tecnologia:

1. Iniciar direto no app em **modo quiosque**, sem desktop, sem atalhos e sem saída para o sistema.
2. Mostrar a **tela de login**: usuário e senha, nome do posto e status da rede e do servidor.
3. Depois do login, mostrar a **tela inicial do Multi_User_FH**, com a identidade visual da firma e **os ícones dos apps liberados para aquele usuário** (lista vinda do Manager). Ela tem ainda os botões **Sair** (logoff) e **Bloquear** (desconectar).
4. Ao clicar num ícone, abrir o programa como **RemoteApp** com NLA. As credenciais ficam só em memória e **nunca vão na linha de comando**. Os apps seguintes reaproveitam a mesma sessão no servidor.
5. **Administradores** podem abrir o **desktop completo** em tela cheia.
6. Quando o usuário sai (ou a sessão cai e não reconecta), **voltar para o login** e limpar tudo.
7. Falar com o **Manager**: registro do aparelho por serial ou MAC, download da configuração, heartbeat a cada 30 a 60 s e envio de logs.
8. **Atualizar-se** com pacotes assinados vindos do Manager.

### Sessões salvas
- O **RDS mantém viva a sessão desconectada**, com os RemoteApps abertos. O usuário entra de novo, em qualquer posto, e os programas voltam como estavam.
- O **Manager** registra quem entrou, onde, quando e por quanto tempo, e permite derrubar ou encerrar sessões.

---

## 3. As trilhas de cliente

### Trilha A — Linux leve (Raspberry Pi, mini PC N100, thin client)
| Item | Escolha |
|---|---|
| Hardware | **Raspberry Pi 5 / Pi 4 (4 GB)**, **mini PC Intel N100** (Beelink, GMKtec…) ou **thin client usado** (HP t620/t630, Dell Wyse 5070) |
| Sistema | Raspberry Pi OS Lite 64-bit (Pi) ou Debian netinst mínimo (x86) |
| Quiosque | **Xorg + Openbox mínimo** (sem painel, sem menu, atalhos desativados), autologin pelo systemd. O X11 é necessário porque o modo RemoteApp do FreeRDP (`/app`) funciona melhor no `xfreerdp3` |
| Motor RDP | **FreeRDP 3** (`xfreerdp3`), com credenciais via `/from-stdin`. RemoteApp por `/app`, desktop completo (admins) por `/f` |
| App | **Python 3 + PySide6 (Qt/QML)** |
| Proteção | root somente leitura (overlayfs), watchdog, troca de TTY desativada, SSH só por chave |
| Distribuição | imagem gerada com **pi-gen** (Pi) ou preseed/Ansible (x86) |

Exemplos de comando:
```bash
# RemoteApp (padrão)
xfreerdp3 /v:servidor.local /d:EMPRESA /u:joao /from-stdin \
  /app:program:"||ERP" /gfx /sound /microphone /auto-reconnect

# Desktop completo (administradores)
xfreerdp3 /v:servidor.local /d:EMPRESA /u:admin /from-stdin \
  /f /gfx /sound /dynamic-resolution /auto-reconnect
```

**Pontos fortes:** o hardware fica barato (principalmente o thin client usado), é estável e sem custo de licença no posto.
**A conferir:** o desempenho com vídeo pesado no Pi.

---

### Trilha B — Android em modo quiosque (Galaxy S9 / S10)
| Item | Escolha |
|---|---|
| Hardware | **Samsung Galaxy S9 / S10 / Note 9 / Note 10** usados (Exynos no Brasil) |
| Vídeo | **HDMI nativo pelo USB-C** (o mesmo recurso do DeX) |
| Periféricos | **Hub USB-C com HDMI, USB e carga (PD passthrough)**: tela, teclado, mouse e carga num cabo só |
| Sistema | Android original sem os apps desnecessários. Opcional: ROM leve (LineageOS) a ser testada |
| Quiosque | **Device Owner** (`adb shell dpm set-device-owner …`) com **Lock Task Mode** |
| Motor RDP | biblioteca **FreeRDP para Android** (base do aFreeRDP, licença Apache 2.0) embutida no app |
| RemoteApp | **a conferir**: o suporte do FreeRDP para Android a janelas RemoteApp é limitado. Alternativas: abrir cada RemoteApp em tela cheia (um app por vez, alternando pela tela inicial) ou uma sessão restrita que já começa direto num programa |
| App | **Kotlin** (Jetpack Compose) |
| Bateria | ativar **"Proteger bateria"** (limite de 85 %), disponível no S10. No S9, conferir se existe |

**Pontos fortes:** reaproveita aparelhos baratos, é compacto e não exige abrir o celular.
**A conferir:** se o hub carrega e usa USB ao mesmo tempo, se a bateria aguenta muito tempo na tomada e se o HDMI continua funcionando numa ROM leve.
**Variações:** Linux puro (postmarketOS) costuma perder o HDMI e a aceleração de vídeo. Fica como pesquisa, não como caminho principal.

---

### Trilha C — Windows 11 ARM
**Requisitos:** processador **Qualcomm Snapdragon**, para o qual existem drivers de Windows (ou um Raspberry Pi com UEFI da comunidade), **bootloader desbloqueável** e **firmware UEFI** para o aparelho.

| Aparelho candidato | Chip | Situação na comunidade |
|---|---|---|
| **OnePlus 6 / 6T** | Snapdragon 845 | Port maduro (Renegade / WOA) |
| **Xiaomi Poco F1** | Snapdragon 845 | Bom suporte e barato usado |
| **Xiaomi Pad 5** | Snapdragon 860 | Muito popular para Windows ARM |
| **Microsoft Surface Duo** | Snapdragon 855 | Projeto dedicado e ativo |
| **Raspberry Pi 4 / 5** | Broadcom + UEFI da comunidade (projeto WoR) | Pi 4 funcional, ainda sem aceleração de vídeo; Pi 5 em evolução |
| Notebooks e mini PCs Snapdragon X | Snapdragon X | Windows ARM oficial, mas mais caros |

| Item | Escolha |
|---|---|
| Motor RDP | **cliente RDP nativo do Windows** (controle ActiveX/COM do `mstsc`, ou `mstsc` com arquivo `.rdp`). **RemoteApp nativo**, com `remoteapplicationmode:i:1` no `.rdp`: é a trilha com o melhor suporte a RemoteApp |
| App | **C# / .NET 8 (WPF ou WinUI 3) para ARM64** |
| Quiosque | **Shell Launcher / Assigned Access**: o app substitui o Explorer |
| Licença | 1 licença de Windows 11 por aparelho |

**Pontos fortes:** RDP nativo da Microsoft, com a melhor compatibilidade (áudio, impressora, multi-monitor, RemoteFX).
**A conferir primeiro:** a **saída de vídeo pelo USB-C no Windows** em cada port, os drivers de USB, Wi-Fi e rede, e a estabilidade em uso contínuo.

---

### Trilha D — Pesquisa: Note 8 Pro com ponte DSI → HDMI
Reaproveitar a placa do Redmi Note 8 Pro (MediaTek Helio G90T), ligando o conector da tela numa ponte de vídeo.

| Etapa | Detalhe |
|---|---|
| Ponte de vídeo | chip **Lontium LT8912B** (MIPI-DSI → HDMI/LVDS) ou **ICN6211** (DSI → RGB); para VGA, um conversor HDMI → VGA depois dela |
| PCB | placa própria com o conector board-to-board do celular (cerca de 0,35 mm entre pinos) e trilhas DSI com impedância controlada |
| Kernel | desbloquear o bootloader, compilar o kernel *begonia* (código-fonte publicado pela Xiaomi) e trocar o driver do painel pelo da ponte, a 1920×1080. Pode ser preciso ajustar também o bootloader LK da MediaTek |
| Energia | sem bateria: fonte de cerca de 4 V nos terminais e simulação dos pinos NTC/ID da bateria |
| Teclado e mouse | hub USB OTG (já funciona no Android) |
| App | o mesmo da trilha B |

**Pontos fortes:** domínio total do hardware e reaproveitamento de placas.
**A conferir:** o tempo de desenvolvimento (de semanas a meses) e o trabalho manual de montar cada posto.

---

## 4. Fases do projeto

### Fase 0 — Base de testes (1 a 2 semanas)
- [ ] Servidor de teste: **Windows Server em avaliação (180 dias)** com RDS Session Host e licenciamento RDS em avaliação.
- [ ] Implantação RDS com **Connection Broker** e uma **coleção RemoteApp** com 2 ou 3 programas publicados.
- [ ] 2 grupos de teste com apps diferentes (ex.: "Financeiro" e "Atendimento") e 1 administrador com desktop completo.
- [ ] **AppLocker** e GPOs de bloqueio básicas.
- [ ] 3 ou 4 usuários de teste.
- [ ] Definir o **roteiro de teste padrão**, que todas as trilhas seguem (seção 5).

### Fase 1 — Testes das trilhas (2 a 4 semanas, em paralelo)
Cada trilha começa com **um aparelho** e, sempre que existir, um cliente RDP pronto antes de escrever código.

| Trilha | Comprar ou separar | Primeiro teste |
|---|---|---|
| A | 1 Pi 5 (ou 1 thin client usado) | FreeRDP pela linha de comando |
| B | 1 Galaxy S10 Exynos + 1 hub USB-C com HDMI, USB e PD | aFreeRDP ou Windows App da loja |
| C | 1 OnePlus 6T, Poco F1 ou Pad 5 (ou um Pi 4 com WoR) | instalar Windows ARM, confirmar o vídeo externo e testar o `mstsc` |
| D | 1 Note 8 Pro + kit de desenvolvimento LT8912B | levantar a pinagem do DSI e compilar o kernel (sem prazo fixo) |

**Entregável:** uma tabela comparativa (seção 5) e a escolha da trilha principal e da secundária.

### Fase 2 — Manager central (3 a 4 semanas)
- [ ] **API** (Python FastAPI + PostgreSQL ou SQLite): cadastro e aprovação de aparelhos, configuração por posto ou grupo, heartbeat, logs e versões do app.
- [ ] **Agente no Windows Server** (PowerShell ou serviço): lê as sessões (`Get-RDUserSession` / `qwinsta`), envia para a API e executa logoff ou desconexão sob comando.
- [ ] **Catálogo de apps**: o agente lê os RemoteApps publicados e os grupos permitidos (`Get-RDRemoteApp`) e os ícones. O Manager monta a **lista de apps de cada usuário** e o cliente desenha a tela inicial. App novo publicado no servidor aparece nos postos sozinho.
- [ ] **Painel web**: postos online/offline, quem está logado e onde, **quais apps estão abertos**, sessões desconectadas, ações (derrubar sessão, logoff, reiniciar posto) e histórico.
- [ ] **Protocolo do cliente documentado** (OpenAPI), para todas as trilhas usarem o mesmo.

### Fase 3 — App cliente da trilha principal (3 a 4 semanas)
- [ ] Tela de login, **tela inicial com os ícones dos apps**, abertura de RemoteApps, desktop completo para admins e volta automática para o login.
- [ ] Integração com o Manager (registro, configuração e heartbeat).
- [ ] Modo quiosque travado e atualização automática.
- [ ] Imagem ou instalador para replicar os postos.

### Fase 4 — App da trilha secundária (2 a 4 semanas)
- [ ] Porta do mesmo contrato para a segunda plataforma, reaproveitando o Manager sem mudanças.

### Fase 5 — Produção e piloto (2 semanas)
- [ ] Comprar o Windows Server e as RDS CALs e ativar o licenciamento.
- [ ] GPOs finais, certificado válido e backup.
- [ ] Piloto com 3 a 5 usuários reais durante 1 a 2 semanas.

### Fase 6 — Implantação e operação
- [ ] Rollout gradual.
- [ ] Manual do usuário (1 página) e manual do administrador.
- [ ] Alertas: servidor acima de 80 % de RAM ou CPU e posto offline.

### Em paralelo — Trilha D (pesquisa)
- [ ] Levantar a pinagem do conector da tela, prototipar a ponte LT8912B e portar o kernel.
- [ ] Sem prazo fixo: ela entra no projeto se e quando o protótipo funcionar.

---

## 5. Roteiro de teste padrão (vale para todas as trilhas)

| # | Teste | Critério |
|---|---|---|
| 1 | Tempo de boot até a tela de login | < 30 s |
| 2 | Vídeo no monitor externo (HDMI/VGA) a 1920×1080 | estável, sem piscar |
| 3 | Teclado e mouse pelo hub | sem atraso perceptível |
| 4 | Carga ou alimentação durante o uso | o aparelho não descarrega em 8 h |
| 5 | Login RDP com NLA | < 10 s até o desktop |
| 6 | Office e navegador (rolagem e digitação) | fluido |
| 6a | **RemoteApp**: abrir 2 ou 3 apps, alternar entre as janelas, copiar e colar entre eles | janelas corretas, sem bordas quebradas |
| 6b | **RemoteApp**: reconectar em outro posto | apps voltam como estavam |
| 6c | **Fuga do RemoteApp**: tentar abrir o cmd ou o Explorer pela janela "Abrir arquivo" | bloqueado pelo AppLocker |
| 7 | Vídeo (YouTube a 720p) | assistível |
| 8 | Áudio (saída e microfone) | funciona |
| 9 | Impressora e USB redirecionados (se precisar) | funciona |
| 10 | Queda de rede de 30 s | reconecta ou volta ao login sem travar |
| 11 | Uso contínuo de 5 dias | sem travar, sem aquecer demais, sem bateria inchando |
| 12 | Custo total do posto | registrar |
| 13 | Tempo para preparar um posto novo | registrar |

---

## 6. Estrutura do repositório

```
Multi_User_FH/
├── PLANO.md
├── docs/                    # manuais, GPOs, resultados dos testes
├── manager/                 # API (FastAPI) + painel web
├── server-agent/            # agente PowerShell no Windows Server
├── protocol/                # contrato cliente ↔ Manager (OpenAPI)
├── client-linux/            # Trilha A: Python + PySide6 + FreeRDP
│   └── image/               # pi-gen / preseed, systemd, overlayfs
├── client-android/          # Trilhas B e D: Kotlin + FreeRDP
├── client-windows-arm/      # Trilha C: C#/.NET + RDP nativo
└── hardware/                # Trilha D: esquemas e PCB da ponte DSI→HDMI
```

---

## 7. Riscos e cuidados

| Risco | Mitigação |
|---|---|
| Licença errada no servidor | Windows Server + RDS CALs desde o início. |
| Desempenho com vídeo | Medir no roteiro de teste; usar `/gfx` com H.264 no FreeRDP. |
| Bateria inchando (trilhas B e D) | "Proteger bateria" (85 %), ou alimentação direta sem bateria na trilha D; boa ventilação. |
| Port de Windows ARM sem driver de vídeo externo (trilha C) | Testar o vídeo antes de qualquer outra coisa e escolher o aparelho pelo resultado. |
| Cartão SD corromper (trilha A) | Root somente leitura, SSD e watchdog. |
| Usuário escapar do RemoteApp e abrir outros programas | AppLocker/WDAC + GPOs de bloqueio, testados no roteiro (6c). |
| Cliente sem bom suporte a RemoteApp (trilha B) | Usar RemoteApp em tela cheia (um por vez) ou sessão que começa direto num programa. |
| Senha exposta | Credenciais só em memória, NLA obrigatório, TLS e certificado válido. |
| Servidor único é ponto de falha | Backup e snapshot; depois, um segundo Session Host com Connection Broker. |
| Vários tipos de hardware para manter | Contrato comum com o Manager, e só 1 ou 2 trilhas em produção. |

---

## 8. Perguntas em aberto

1. Quantos postos e quantos usuários simultâneos?
2. Quais programas os usuários vão usar?
3. Os postos ficam na rede local do servidor ou acessam pela internet (Gateway ou VPN)?
4. Já existe Active Directory, ou vamos usar contas locais?
5. Que periféricos são necessários: impressora, leitor de código de barras, webcam, áudio?
6. O servidor será físico, uma VM local ou ficará na nuvem?
7. Quais aparelhos você já tem disponíveis para os testes da Fase 1?
8. Quais programas serão publicados como RemoteApp, e para quais grupos?

---

## 9. Próximo passo imediato

1. Montar o **servidor de teste com a coleção RemoteApp** (Fase 0).
2. Conseguir **um aparelho de cada trilha** que for testar primeiro. Sugestão: **Galaxy S10 + hub** (B) e **Pi 5 ou thin client** (A). A trilha C entra assim que houver um Snapdragon compatível.
3. Rodar o **roteiro de teste** e preencher a tabela comparativa.
