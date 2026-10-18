# Convite e entrada: desenho mínimo da integração

**Data:** 2026-10-16. **Status:** desenho técnico A1 aprovado em 2026-10-16; implementação ainda requer os gates abaixo.
**Spec canônica:** [spec.md](spec.md). **Contexto aprovado:** [context.md](context.md).
**Base:** PR #14 integrado em `da9136c541dd4ca06da0269dfd12355a360e0d3b`.
**Método:** TLC Spec Driven, porque a entrega conecta autorização durável, transporte nativo e três processos iOS. Este desenho continua a feature existente e preserva seus 34 critérios.

## Resultado e limite

Construir em ambiente fictício a fatia convite individual → confirmação → associação de um dispositivo → configuração automática → mensagens e arquivos nos relays autorizados → revogação. O proprietário emite convites; convidados não precisam cadastrar telefone ou e-mail. Repetir o piloto histórico do SimpleX não é o objetivo.

A [prova anterior](access-proof-validation.md) aprovou somente a fronteira local com clientes CLI. O adaptador iOS, os convites, a autoridade dos grupos e a operação continuam sem comprovação. Nenhum requisito do produto muda de `Pending` por causa deste documento.

Não criar painel web, login social, microserviços, Redis, filas ou um protocolo criptográfico. Não fazer deploy, DNS, mudança de conta Apple ou distribuição. O futuro ambiente de produção será qualificado separadamente no repositório privado. Os endereços e credenciais de administração não entram no fonte público.

## Architecture Overview

**Recomendação: continuar a rota A, usando o SOCKS já oferecido pelo núcleo.** Um adaptador local por processo iOS aceita somente SMP/XFTP previstos na configuração autenticada e encapsula seus bytes na ponte TLS por dispositivo. A implementação nativa ainda precisa passar a qualificação abaixo. Nenhuma API Apple consultada, isoladamente, prova essa composição.

| Alternativa | Como entrega a mesma fatia | Custo e risco |
| --- | --- | --- |
| A1: adaptador nativo local, recomendada | Núcleo usa SOCKS local obrigatório; adaptador valida destino e abre TLS externo autenticado; ponte só alcança os relays fixados | Reutiliza núcleo e binários qualificados; exige provar listener, credencial, suspensão e retomada em app/Share Extension/NSE |
| A2: transporte encapsulado no núcleo | O cliente Haskell recebe configuração de transporte externo por dispositivo e faz TLS sobre TLS antes do handshake SMP/XFTP | Dispensa listener local, mas exige patch mantido na dependência SimpleXMQ, reconstrução das bibliotecas e revisão do transporte; não altera a criptografia das mensagens |

A2 é alternativa caso A1 falhe, não um trabalho paralelo. Não modificar o núcleo ou trocar a arquitetura em silêncio para contornar um gate. A antiga rota de alterar os dois daemons foi descartada para este recorte pela preferência do proprietário por simplicidade.

Loopback não autentica o processo que conecta. O listener deve exigir credencial SOCKS efêmera e aleatória por processo, entregue ao núcleo em memória e nunca em logs/UserDefaults. O núcleo fixado oferece `SocksAuthUsername` em `Messaging/Client.hs:452`; `SocksIsolateByAuth` não é autenticação secreta de processo. Provar rejeição de cliente local sem essa credencial e impedir reuso entre processos/execuções. Porta efêmera sozinha não é controle de acesso.

### Componentes propostos

| Componente | Local proposto | Responsabilidade e reutilização |
| --- | --- | --- |
| Adaptador nativo | `apps/ios/SimpleXChat/Taverna/` | Network.framework; listener apenas em loopback, porta efêmera por processo, duas rotas exatas. Recebe credencial e configuração verificadas; não recebe backend arbitrário |
| Admissão | `services/admission/` | Serviço pequeno Python 3.12, SQLite e biblioteca X.509 qualificada. Emite/resgata/cancela convites, mantém associações e emite certificado para chave gerada no dispositivo |
| Ponte | Componente de runtime separado de `tools/taverna/access_proof` | Reutiliza o comportamento já provado de TLS, encaminhamento fixo e encerramento; consulta o mesmo estado autoritativo de associação. A fixture não se transforma em serviço por renomeação |
| Integração e entrada | App principal e pontos de startup das extensões | Aplica configuração antes de qualquer início/reativação do núcleo; a UI só entra após DESIGN.md aprovado. A configuração de rede não depende de ocultar menus |

Escolher e fixar dependências HTTP/X.509/CSR na qualificação antes de executá-las. FastAPI e PyCA são candidatos documentados, não dependências instaladas ou versões aprovadas. Não escrever ASN.1, TLS ou assinatura próprios para evitar uma biblioteca. App, serviço e ponte mantêm contratos públicos; valores operacionais e custódia ficam privados.

## Code Reuse Analysis

| Código existente | Uso e cautela |
| --- | --- |
| `apps/ios/SimpleXChat/APITypes.swift:260` | `NetCfg` expõe SOCKS; a política Taverna deve fixá-lo e impedir remoção por importação/configuração. Campos públicos não provam aplicação obrigatória |
| `apps/ios/SimpleXChat/APITypes.swift:331` | O modo SMP proxy e seu fallback são controles distintos. Evitar salto para relays não autorizados; não confundir fallback SMP com disponibilidade do SOCKS |
| `apps/ios/Shared/Model/SimpleXAPI.swift:2262` | O app aplica rede antes de `apiStartChat`; cobrir também retomada e controlador temporário |
| `apps/ios/SimpleX NSE/NotificationService.swift:860` | A extensão inicia seu próprio controlador; precisa de adaptador/configuração antes de iniciar ou reativar, sem exigir que o app esteja aberto |
| `apps/ios/SimpleX SE/ShareModel.swift:174` | O caminho atual pode iniciar antes de aplicar rede; inverter essa precedência no recorte, com teste negativo de zero conexão externa |
| `apps/ios/SimpleXChat/KeyChain.swift:12` | Reutilizar padrão ThisDeviceOnly; o access group herdado exige identidade própria para aparelho. Não guardar chave ou token em UserDefaults |
| `apps/ios/Shared/SimpleXApp.swift:45` | O handler atual registra a URL. Interceptar convite antes do logger e do roteamento de links SimpleX para não registrar token |
| `src/Simplex/Chat.hs:157` e `src/Simplex/Chat/Library/Internal.hs:1561` | Presets/links curtos também podem fornecer destinos; configurar só o menu de servidores é insuficiente |
| `tools/taverna/access_proof/` | Reutilizar inputs fixados, controles SMP/XFTP reais, sentinela e testes de revogação; cada execução gera estado novo |

No SimpleXMQ fixado em `efaad8e73436d60f5052f07dda6b71151ad5039b`, `Messaging/Client.hs:441` configura SOCKS no transporte; `Transport/Client.hs:167` conecta por SOCKS antes do TLS interno. `FileTransfer/Client.hs:209` recebe configuração de transporte no HTTP/2. Isso fundamenta A1, mas não comprova execução iOS. O campo `clientCredentials` do TLS interno não substitui o encapsulamento externo: são duas conexões com papéis distintos.

## Interfaces e estado durável

Estes contratos são propostos para a implementação; nenhum endpoint está disponível agora.

| Interface | Autorização | Resultado previsto |
| --- | --- | --- |
| `GET /join` | Pública | Instrução estática para instalar/reabrir o link; não lê nem consome o token |
| `POST /v1/invites` | Proprietário autenticado | Convite com 32 bytes aleatórios, uma utilização, expiração em 72 horas; token retornado uma vez |
| `POST /v1/invites/{id}/cancel` | Proprietário autenticado | Cancela somente convite pendente; não altera uma associação já ativada |
| `POST /v1/enroll` | Token + CSR PKCS#10 com assinatura válida | Ativação transacional, certificado público para a chave do dispositivo e configuração autenticada; chave privada nunca sai do dispositivo |
| `GET /v1/members` | Proprietário autenticado | IDs opacos, estado e data da alteração; sem mensagens ou identidade civil obrigatória |
| `POST /v1/members/{id}/revoke` | Proprietário autenticado | Revogação durável; sessões da ponte fecham em até 60 segundos; repetição não reativa membro |

Ferramentas de gestão usam os endpoints autenticados. A custódia e o bootstrap são definidos no repositório privado; o resgate de um convite nunca concede papel de proprietário.

Identidade administrativa exige mTLS validado no terminador TLS do próprio serviço e papel consultado no estado autoritativo. Não aceitar certificado, papel ou cabeçalho de identidade enviado pelo corpo HTTP; não confiar em headers injetáveis por um proxy. Qualificar a passagem segura da identidade TLS para o runtime HTTP antes de adotar um framework. A associação referencia o certificado emitido, além da chave pública, para que outro certificado da mesma CA não herde permissão.

### Modelos e transações

- Convite: ID opaco, SHA-256 do token aleatório, emissão/expiração UTC, estado pendente/cancelado/resgatado e associação vencedora. Não persistir token em claro.
- Associação: ID opaco, papel proprietário/convidado, hash da chave pública, certificado emitido, estado ativo/revogado e datas. Papel vem do servidor, nunca de extensões pedidas no CSR.
- Configuração: versão, ID da instância, origem HTTPS fixa, lista exata de destinos/portas SMP e XFTP, fingerprints dos relays e confiança pública da ponte. É obtida somente da origem autenticada do app; o convite não escolhe uma API ou CA arbitrária.
- Resgate: `BEGIN IMMEDIATE`; validar estado/expiração, verificar limite, emitir e persistir certificado/associação e marcar convite consumido antes do commit. Só responder sucesso depois do commit. Falha na emissão/persistência não consome convite nem vaga.
- Concorrência: dois resgates por chaves diferentes produzem exatamente um vencedor; repetição pelo mesmo par de chaves retorna a mesma associação/certificado sem nova vaga. A chave precisa sobreviver à perda da resposta. Um membro revogado nunca é reativado por essa repetição.
- Repetição depois do primeiro sucesso não é uma nova ativação: pode recuperar a mesma associação ativa mesmo após as 72 horas do convite original. Perder a chave exige novo convite do proprietário; não há recuperação por telefone/e-mail.
- Capacidade: 20 convidados ativos, além do proprietário. Verificar na mesma transação do resgate. Cancelamento, expiração ou capacidade esgotada não apagam o convite nem consomem vaga.

Token em fragmento do link, com origem/caminho fixos: HTTPS no domínio Taverna, `/join`, fragmento contendo o token. O fragmento evita enviar o segredo no GET; app/browser não o registram nem carregam analytics. Não publicar um convite completo, mesmo como exemplo. Prévia por GET/HEAD nunca ativa. Universal Links dependem de AASA, entitlement e assinatura próprios; simular abertura de URL não satisfaz a prova em aparelho de INV-07.

A origem de bootstrap e sua confiança pública são entradas do build, nunca segredos compartilhados. Validar HTTPS/hostname e a confiança qualificada dessa origem antes de aceitar configuração; persistir a configuração verificada em armazenamento protegido. Uma resposta de uma origem escolhida pelo convite não pode substituir essa confiança. Qualificar falhas de TLS, troca de instância e configuração adulterada antes de marcar NET-04.

CSR e resposta têm limites explícitos antes de parse/alocação: URL 8192 bytes conforme spec; proposta de corpo de resgate 16 KiB e CSR 8 KiB. Resposta: estados estáveis `invalid_invite`, `capacity_reached`, `retry_later`, `unavailable`. CSR inválido não ativa; expiração é inválida inclusive na igualdade do timestamp. Cinco falhas de resgate/minuto por origem; sexta recebe HTTP 429 e Retry-After 60. Cabeçalhos de origem enviados pelo cliente não são confiáveis. A fronteira de proxy autorizada precisa de qualificação antes do deploy.

### Associação na ponte

Não usar cópia de JSON que continue autorizando indefinidamente após a admissão parar. Admissão e ponte compartilham uma única autoridade SQLite na mesma instância administrativa; a ponte consulta estado com prazo limitado e falha fechada. Não criar um serviço de autorização remoto adicional nesta etapa. A forma de execução conjunta será qualificada junto do runtime HTTP/TLS, sem cache de autorização positivo sem prazo.

Revogação só responde concluída depois de persistir. Conexões novas e já abertas revalidam associação; estado ilegível, indisponível ou verificação que exceda seu prazo fecha acesso. Testar explicitamente arquivo grande durante revogação e falha da base, além dos fluxos de controle já provados. Nenhuma autorização de grupo é inferida do texto cifrado.

## Qualificação antes da implementação completa

| Entrega | Prova exigida para avançar | O que não libera |
| --- | --- | --- |
| 1. Transporte nativo | App real e cada extensão usam o adaptador; dois clientes fictícios trocam mensagem SMP e bytes XFTP; credencial ausente/revogada, listener indisponível e destino sentinela não permitem bypass; TLS interno continua validando fingerprint | Não libera convites, UI ou produção; se A1 não passar, revisar A2 antes de escrever o onboarding |
| 2. Admissão ligada à ponte | Emissão autorizada, GET inofensivo, resgate único/concorrente, repetição após perda de resposta, expiração/cancelamento/limite, reinício e revogação afetam efetivamente os dois protocolos reais | Não libera aparelho, push, distribuição ou grupos |
| 3. Entrada visual | DESIGN.md da raiz aprovado e assets qualificados; tela confirma convite, mostra erros e inicia rede somente após associação/configuração verificadas | Não libera piloto sem gates privados e prova em dois iPhones |

Grupos e aceite mútuo continuam na spec; este desenho não declara CHAT-01..06 implementados nem descarta esses requisitos. Os relays não leem o conteúdo E2EE, e a autoridade dos grupos precisa de uma entrega própria. Não iniciar esse trabalho no mesmo PR da entrada.

As tarefas formais com testes e comandos serão produzidas depois de confirmar este desenho, conforme a skill. Não marcar tarefas inexistentes como aprovadas ou reutilizar o PASS da fixture como gate nativo. Não mudar locks, bibliotecas ou o mecanismo de contenção do primeiro build sem qualificação específica.

## Testes e gates propostos

Manter os 70 testes Foundation e os 12 do experimento. Para o novo recorte, derivar asserts dos INV-01..09, MEM-01..06 e NET-01..05 aplicáveis; o relatório distingue prova parcial e requisito completo.

| Camada | Casos necessários |
| --- | --- |
| Admissão/SQLite | Corrida do mesmo convite; mesma chave após resposta perdida; reinício após commit; rollback na emissão; limite 20+proprietário; relógio na expiração; cancelado/usado; papel forjado; CSR inválido; limite por origem; zero token/chave em logs |
| Adaptador | Somente loopback; porta e credencial efêmera exclusivas por processo; cliente local sem credencial/reuso entre processos recusados; rejeição antes de DNS/conexão para host/porta fora da lista; frames SOCKS parciais/malformados; backpressure; cancelamento; limite de conexões; TLS externo não confiável e fingerprint interno incorreto |
| App/extensões | Inicialização e retomada fechadas sem associação/configuração/Keychain; Share Extension configura antes de iniciar; NSE independente; importação, link curto, contato e edição de rede não escapam da política |
| Ponta a ponta | Dois clientes reais, SMP e XFTP; arquivo grande em andamento; revogação e base indisponível cortam em até 60 s; sentinela alcançável no controle positivo e zero tentativas durante casos proibidos |

Comandos já disponíveis de regressão: `python3.12 -m unittest discover -s tools/taverna/tests -q`, `python3.12 tools/taverna/check_foundation.py`, `python3.12 -m compileall -q tools/taverna` e `git diff --check`. A fixture tem comandos no [guia](../../../docs/taverna/access-proof.md). O [guia iOS](../../../docs/taverna/ios-build.md) prova o primeiro build sob contenção antiga; seus comandos não comprovam a nova integração de rede.

A nova prova de rede requer contenção que permita somente seus destinos fictícios e uma sentinela observável. Revisar explicitamente esse mecanismo antes de habilitar tráfego no app; não retirar o bloqueio atual e reutilizar o receipt antigo. CI sem segredos; testes novos apropriados à camada entram na sua entrega. Verifier independente no último commit, sensor de autorização/fallback com pelo menos cinco mutações e CI verde precedem integração.

## Risks & Concerns

| Concern | Local/evidência | Impacto | Mitigação |
| --- | --- | --- | --- |
| Ponte CLI confundida com integração | access-proof-validation.md | UI aparenta proteção inexistente no núcleo | Transporte nativo é o primeiro gate, antes de admissão/onboarding |
| Núcleo inicia antes da rede na extensão | ShareModel.swift:174–195 | Janela de conexão com configuração herdada | Configurar e autorizar antes de início/reativação em cada processo; sentinela observa tentativa, não só sucesso |
| Proxy SMP ou resolução de link curto | APITypes.swift:267; Library/Internal.hs:1561 | Relay autorizado encaminha para outro destino | Bloquear caminhos não autorizados e provar proxy interno; filtro de socket sozinho não satisfaz NET-02 |
| Política espelhada fica antiga | gateway.py:17 | Revogação ou falha de admissão sem efeito | Uma autoridade durável, consulta limitada/fail-closed e prova com base indisponível |
| Listener/credencial em extensão | Network.framework e KeyChain.swift:12–13 | Falha em suspensão, processo separado ou aparelho | Gate em cada target; credencial ThisDeviceOnly e entitlement próprio antes de aparelho |
| Listener acessível a outro processo local | Messaging/Client.hs:452 | Uso indevido da credencial de dispositivo pela ponte local | Exigir autenticação SOCKS aleatória por processo em memória; recusar cliente local sem credencial; não tratar SocksIsolateByAuth como segredo |
| URL completa no logger herdado | SimpleXApp.swift:46 | Token individual em diagnóstico | Interceptar e sanitizar antes do handler; teste de ausência de token em logs |
| CSR nativo ainda não qualificado | SwiftPM não tem biblioteca X.509/CSR | Emissão funciona só no driver | Qualificar biblioteca padrão de CSR e seu uso com chave do dispositivo; sem encoder/criptografia próprios |
| Assets ainda bloqueados | docs/taverna/asset-policy.json | Distribuição customizada sem licença | DESIGN.md e inventário antes das telas; preservar gate de distribuição |

## Fontes e limites da pesquisa

Código fixado do app em `da9136c54`; dependência SimpleXMQ em `efaad8e73436d60f5052f07dda6b71151ad5039b`. Reutilizamos o clone de pesquisa existente somente para leitura; nenhum novo fork ou patch foi publicado. Context7 não está disponível nesta sessão; a consulta seguiu código, docs do projeto e fontes oficiais.

- [Transporte SOCKS/TLS do núcleo fixado](https://github.com/simplex-chat/simplexmq/blob/efaad8e73436d60f5052f07dda6b71151ad5039b/src/Simplex/Messaging/Transport/Client.hs).
- [Configuração XFTP fixada](https://github.com/simplex-chat/simplexmq/blob/efaad8e73436d60f5052f07dda6b71151ad5039b/src/Simplex/FileTransfer/Client.hs).
- [Apple NWListener](https://developer.apple.com/documentation/network/nwlistener) e [NWConnection](https://developer.apple.com/documentation/network/nwconnection): primitivas candidatas, composição ainda não provada.
- [Apple Keychain](https://developer.apple.com/documentation/security/keychain-services): armazenamento de chave/certificado; aparelho exige qualificação da identidade própria.
- [Apple Associated Domains](https://developer.apple.com/documentation/xcode/supporting-associated-domains): associação depende de AASA/entitlement e da identidade do app; não é uma mudança apenas no parser de URL.
- [PyCA: CSR e certificados X.509](https://cryptography.io/en/latest/x509/tutorial/): emissão padronizada a qualificar, sem enviar a chave privada.
- [FastAPI](https://fastapi.tiangolo.com/): candidato de runtime HTTP, ainda sem adoção/versão fixada.
- [SQLite: transações](https://www.sqlite.org/lang_transaction.html): exclusão de escritores por BEGIN IMMEDIATE não substitui testes de concorrência e falha.

Responsável/harness/integrador: Codex. Branch `codex/invitation-entry-plan`, worktree irmão `taverna-app-worktrees/invitation-entry-plan`. Escopo desta entrega documental: desenho, README, roadmap e handoff. App, dependências, credenciais, simuladores e produção preservados.
