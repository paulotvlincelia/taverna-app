# Design do primeiro build iOS

**Spec:** [spec.md](spec.md), aprovada em 2026-10-16.
**Status:** núcleo realizado do fonte e entradas locais qualificadas em 2026-10-16. T1 concluída; build do app/onboarding comprovados em tentativa local, suíte completa/reprodução pendentes.

## Architecture Overview

O plano aprovado selecionou bibliotecas oficiais pré-compiladas, condicionadas à origem comprovada. O [levantamento](core-qualification.md) não localizou uma entrada qualificada. O proprietário escolheu Nix e autorizou a exceção administrativa descrita abaixo. As alternativas permanecem registradas como contexto da escolha.

| Abordagem | Benefício | Custo e condição |
| --- | --- | --- |
| **Nix/Haskell.nix fixado, recomendada** | Reutiliza a receita do upstream, seus locks e GHC 9.6.3. | Nix ainda não instalado; instalação macOS cria store /nix e serviços/arquivos de sistema. Exige exceção explícita. Compatibilidade com o macOS/Xcode instalado ainda precisa de prova. |
| GHC/Cabal instalados localmente sob Projects | Mantém toolchain e estado do projeto na árvore aprovada, sem daemon Nix. | Exige traduzir a derivação, preparar dependências C, flags e empacotamento, e comprovar equivalência. Essa adaptação não foi implementada nem qualificada como atalho. |

Ambas miram o mesmo resultado do plano: app com núcleo real em simulador arm64, teste observável e repetição independente. As bibliotecas do núcleo passariam a ser construídas do fonte; esse estado precisa aparecer nas evidências, sem alegar reprodução bit a bit.

## Rota Nix proposta

1. Instalar o pacote oficial Nix fixado e revisado, com confirmação administrativa pessoal quando exigida pelo macOS. Preservar os checkouts e manter os arquivos de preparação sob Projects. Não aceitar contratos de terceiros ou consultar contas Apple.
2. Avaliar a derivação do fonte fixado sem atualizar flake.lock. Selecionar packages.aarch64-darwin com o atributo aarch64-darwin-ios:lib:simplex-chat. A sintaxe do comando final será validada pela ferramenta instalada; nenhum comando de compilação é apresentado aqui como já executado.
3. Registrar o plano de dependências e construir a biblioteca, incluindo flags swift/client_library, CommonCrypto e demais opções da receita original. Não substituir o conjunto por GHC/Cabal mais recentes.
4. Copiar os produtos da store imutável para o estado próprio do worktree. Preservar entrada original e registrar cada transformação mac2ios -s aplicada às cópias para simulador.
5. Inspecionar objetos e plataforma final, fixar hashes, licenças e entradas em manifesto. Só então avançar para SwiftPM/Xcode, seleção do simulador e contenção de rede.

O desenho restante do executor Xcode será fechado com as entradas conhecidas. Uma alteração de flake, flags ou locks para resolver erro é uma mudança revisável, não uma atualização automática.

## Exceção administrativa autorizada

A [documentação oficial do Nix](https://nix.dev/manual/nix/2.34/installation/installing-binary.html) e os scripts do pacote revisado descrevem instalação multiusuário no macOS. O instalador 2.34.9 rejeita --no-daemon no Darwin.

| Superfície | Efeito esperado do instalador oficial |
| --- | --- |
| /nix | Store e estado do gerenciador; volume APFS de suporte no macOS. |
| /etc/synthetic.conf e /etc/fstab | Montagem do volume, preservando entradas existentes. |
| /Library/LaunchDaemons | Serviço de montagem e daemon do Nix. |
| Usuários/grupo de build | Contas técnicas e grupo nixbld para a compilação. |
| /etc/nix/nix.conf | Configuração do gerenciador. |
| Perfis de shell de sistema | Inicialização do ambiente Nix e backups gerados pelo instalador. |
| Keychain do sistema | Se o volume for criptografado, credencial gerada para sua montagem; não é consulta a senhas existentes do projeto. |

Repos, worktrees, produtos do app, evidências, bancos e simuladores continuam sob Projects. O gerenciador e sua store de dependências seriam a exceção explícita, comparável a uma ferramenta instalada no sistema, e não um novo checkout do projeto. Não mover repositórios para /nix.

A preparação para revisão já baixou o pacote fixado dentro do worktree e conferiu o hash publicado pelo instalador. Nenhum script foi executado. Não prometer que --no-modify-profile evita alterações no modo daemon: a flag é tratada de forma diferente nos scripts examinados. Não instalar automaticamente canais móveis; a receita do app vem de flake.lock.

## Code Reuse Analysis

| Componente | Local | Uso previsto |
| --- | --- | --- |
| Receita do núcleo | flake.nix e flake.lock | GHC e dependências fixados; empacotamento de arquivos .a. |
| Dependências Haskell | cabal.project | Commits das fontes e index-state preservados. |
| Conversão de plataforma | mobile-core-tools, commit 4dcb77d5ea896d749381806dfab5358851b08951 | Ferramenta mac2ios da receita, com prova dos hashes antes/depois. |
| Projeto e scheme | apps/ios/SimpleX.xcodeproj | App, framework, extensões e suíte iOS existentes. |
| Ferramentas da fundação | tools/taverna | Checks preservados; não equivalem a prova iOS. |

## Components

- **Manifesto do núcleo:** identifica fonte, receita, ferramentas, hashes, licença e plataforma das bibliotecas reais. A qualificação atual tem estado BLOCKED e não fornece um manifesto de biblioteca aprovada.
- **Preparo da sessão:** mantém estado do projeto no worktree; registra responsável, caminhos e UDID exclusivo. Nix requer a exceção de sistema acima.
- **Executor de build/testes:** só será implementado após resolver a entrada do núcleo e demonstrar destino e rede isolados. Registra produtos reais, códigos de saída e testes obrigatórios.
- **Relatório final:** distingue build Swift, núcleo construído do fonte, assinatura em aparelho e distribuição; depende de duas execuções e do Verifier.

## Data Models

Nenhuma mudança de dados da aplicação. O registro local da qualificação contém schema, horário, commit fonte, status, exit_code, consultas e seus resultados, qualified_artifacts, downloaded_core_binaries, hashes dos arquivos de entrada e estados build/ios_tests/verifier. A ausência de uma biblioteca qualificada impede PASS.

## Error Handling Strategy

| Erro | Tratamento |
| --- | --- |
| Ausência de biblioteca qualificada | BLOCKED, exit 2; nenhum download ou build do núcleo presumido. |
| API indisponível ou sem JSON | INCONCLUSIVE para essa consulta; preservar a resposta e não convertê-la em ausência de artefatos. |
| Hash de ferramenta divergente | Não abrir o arquivo nem executar o instalador. |
| Conflito de instalação no Mac | Interromper; preservar os recursos existentes e pedir reconciliação, sem limpeza forçada. |
| Falha ao avaliar/buildar a receita fixada | Preservar logs e registrar o erro exato; não atualizar o lock para silenciá-lo. |

## Risks & Concerns

| Risco | Local | Impacto | Mitigação |
| --- | --- | --- | --- |
| Endpoint móvel e diretórios compartilhados | scripts/ios/download-libs.sh:36 e scripts/ios/prepare.sh:6 | Origem sem vínculo e interferência entre sessões. | Não executar esses scripts; entradas fixadas e cópias próprias. |
| Receita antiga com toolchain Apple atual | flake.nix:33, flake.lock | A instalação do Nix não garante que o núcleo compilará. | Avaliar/buildar o lock preservado e relatar incompatibilidades. |
| Conversão de plataforma altera arquivos | scripts/ios/prepare.sh:13 e mac2ios.c da revisão fixada | Arm64 sozinho não prova ABI de simulador. | Preservar original, inspecionar objetos e registrar hashes antes/depois. |
| Testes de lançamento sem asserção da tela | apps/ios/Tests iOS/Tests_iOS.swift:25 | Sucesso da suíte não prova navegação. | Acrescentar teste observável, preservando os existentes. |
| Biblioteca desktop confundida com iOS | Releases simplex-chat-libs | Link inválido ou falsa prova de compatibilidade. | Não substituir bibliotecas iOS por arquivos macOS sem a receita e a prova exigidas. |
| Efeitos administrativos fora de Projects | Instalador Nix 2.34.9 | Extrapolar a organização autorizada do Mac. | Exceção explícita antes de executar; pacote já preparado para revisão. |

## Tech Decisions

O proprietário autorizou Nix 2.34.9 no MacBook, com store e serviços fora de Projects, mantendo os projetos e suas evidências na árvore aprovada. A rota pré-compilada permanece bloqueada; a alternativa GHC/Cabal local não foi adotada. A instalação é um pré-requisito administrativo; o restante do executor será detalhado em tarefas antes de alterar código.

## Andamento da instalação

A primeira tentativa autenticou no macOS, criou o ponto /nix e um volume APFS vazio, mas terminou com exit 1 em vifs: error creating /etc/fstab. Não houve instalação do binário ou daemon até essa etapa. Evidência local: .build/attempts/nix-bootstrap-20261016/install.log.

O [relato no repositório Nix](https://github.com/NixOS/nix/issues/13723#issuecomment-3251454726) apresenta o mesmo erro e informa sucesso ao executar pela sessão gráfica. Isso indica um caminho de investigação; a causa neste MacBook ainda não foi comprovada. Não desativar SIP ou alterar permissões globais como atalho.

O controle automatizado do Terminal foi recusado pela ferramenta de UI por segurança. Foi preparado um helper local interativo, com verificação de hash e logs próprios, para execução manual pelo proprietário. Nenhum instalador foi reiniciado automaticamente após a falha, e o volume vazio foi preservado. Depois da execução manual, validar versão, conexão com o daemon e montagem antes de iniciar a avaliação da receita.

## Ambiente após a execução gráfica

O proprietário concluiu o helper com exit 0. A validação confirmou Nix 2.34.9, conexão com o daemon e /nix montado. Os registros posteriores estão em [execution.md](execution.md). A avaliação usa o commit upstream fixado, com locks preservados e cache/configuração do cliente no worktree; não depende de um PATH configurado por um harness específico.

## Isolamento aprovado para o SDK 27.1

**Aprovado pelo proprietário em 2026-10-16.** Aplicar a revisão de IOS-05 e IOS-10 e a precisão de armazenamento de IOS-04, registrada em APP-004. A aprovação autoriza implementar esta alternativa; T2 ainda exige suas provas e gate.

O SDK recusou o UDID criado apenas no set privado. A tentativa de roteamento por biblioteca não encontrou esse destino; não remover a validação de bibliotecas do Xcode para contornar isso. O sandbox aplicado ao launchd_sim impediu a inicialização, inclusive com allow default. O controle do mesmo exec sem sandbox inicializou normalmente. A causa interna da recusa de vínculo ainda não foi determinada.

Dois controles concretos permitem uma alternativa local:

- Um dispositivo novo, exclusivo do Codex, foi registrado pela API padrão simctl. Antes de inicializar, seu armazenamento foi movido para o worktree, com um alias por UDID no índice do SDK. Xcode showBuildSettings aceitou o destino com exit 0 e TARGET_DEVICE_IDENTIFIER igual ao UDID solicitado. O set privado não lista esse registro: o índice é o padrão do SDK, e o armazenamento físico é exclusivo da sessão. Evidências em .build/attempts/xcode-native-registration-20261016.
- Um app UIKit sintético foi compilado e assinado ad hoc, sem conta Apple. Um helper próprio aplicou sandbox no macOS e retornou ao mesmo processo iOS antes do main. O processo confirmou EPERM na conexão externa e chegou ao callback de criação da interface. Registros de PID, perfil, conexão e UIKIT_CONTROL_READY em .build/attempts/uikit-process-containment-20261016. Esse app de controle não contém código, perfil ou mensagens da Taverna e não prova o build do mensageiro.

| Critério | Forma aprovada | Limite preservado |
| --- | --- | --- |
| IOS-04 e IOS-05 | Usar UDID exclusivo registrado no índice padrão do SDK; preflight compara o destino efetivo e o caminho físico dos dados com a sessão/worktree. Estado do app, caches e logs permanecem no worktree; índices por UDID do SDK podem ser aliases. | Nenhum dispositivo de outra sessão pode ser selecionado, resetado ou removido. Registro existente com outro destino físico exige reconciliação. |
| IOS-10 | Aplicar e comprovar contenção de IP remoto no processo do app sob teste antes de sua inicialização, com controle externo negado e comunicação local permitida. | Não alterar firewall/VPN global, não criar perfil nem enviar mensagens. Processos do sistema operacional simulado ficam fora dessa contenção; não afirmar que toda a sessão iOS está offline. |

O procedimento aprovado ainda precisa ser implementado e testado na Taverna real. O preflight deve rejeitar entradas sem origem, helper ausente ou divergente, destino estranho e ausência de prova de contenção. O resultado final precisa manter estados separados: build do app, teste UI, origem do núcleo e distribuição. A prova sintética não substitui os testes herdados, as novas asserções, a segunda execução ou o Verifier.

A alternativa preserva Git/worktrees nativos e evita instalar outro gerenciador de ambientes. Usa uma API de sandbox marcada como deprecated; a compatibilidade precisa ser requalificada a cada mudança de SDK/macOS. Manter os critérios originais exigirá outra abordagem de isolamento ainda não qualificada, possivelmente um ambiente macOS separado. Não instalar VM ou alterar proteções como consequência automática desta proposta.


## Conversão dos metadados legados do núcleo

Refinamento de T1, sem alterar critérios, fonte, locks ou flags: a derivação produziu o núcleo, mas mac2ios -s manteve LC_VERSION_MIN_IPHONEOS nos 3.424 objetos da biblioteca agregada. A tentativa foi bloqueada e preservada. O vtool do Xcode 27.1 instalado aceitou um objeto de amostra e o linker oficial recusou a entrada original/aceitou a convertida para iOS Simulator. O manual instalado ainda afirma não suportar objetos; o resultado aqui vem dos probes reais dessa versão, sem generalizar para outros Xcodes.

A cópia final usa vtool por membro, preservando os números minos/sdk originais, e libtool -static -D para recompor cada arquivo. Nomes repetidos recebem diretórios por ordinal; nunca extrair sobrescrevendo basenames. Conferir igualdade do cabeçalho fora do tamanho dos comandos, comandos que não são de versão, offsets, bytes de payload, relocações e símbolos. A plataforma final precisa ser LC_BUILD_VERSION 7 em todos os objetos. Qualquer divergência bloqueia. Não há edição de instruções, criptografia, protocolo ou fonte do núcleo.

Foram conferidos 4.187 objetos em cinco arquivos. O [manifesto](native-inputs.json) fixa origem, licenças declaradas, receita e hashes, com estado do núcleo distinto do app. Os comandos e provas estão em [execution.md](execution.md); o procedimento reproduzível de T5 ainda está pendente.


## Compatibilidade SwiftUI observada em T3

O primeiro build-for-testing terminou exit 65 em 2026-10-16: o novo macro State do SDK 27.1 gerou _chat/$chat duplicados na composição @State @ObservedObject de ChatView. O probe swift-state-composition-20261016 reproduziu a falha; explicitar argumentos genéricos ainda escolheu o macro. Um typealias interno do tipo SwiftUI.State compilou com asserções estáticas dos tipos originais State<ObservedObject<ProbeChat>>, Binding<ObservedObject<ProbeChat>> e do inicializador memberwise. Um alias privado impediria o acesso atual da propriedade e foi recusado no probe.

Aplicar somente o alias interno ChatViewState ao atributo composto de ChatView. Não substituir por StateObject, migrar o modelo de observação ou alterar os bindings dos chamadores. A compilação real completa e a suíte continuam sendo o gate de T3; a prova isolada de tipos não prova conversas ou navegação do app.


## Janela total da suíte e preservação das configurações

A primeira sessão real atingiu 900 segundos com 130 execuções aprovadas, zero falhas de asserção observadas e configurações herdadas ainda pendentes. O monitor encerrou o teste; o cleanup tinha somente um segundo restante e sobrescreveu o código agregado com 2. O receipt original foi preservado; reconciliation.json distingue timeout do teste, erro de cleanup e sucesso do build/onboarding. O dispositivo antigo foi confirmado Shutdown, sem apagar dados.

A próxima sessão usa 1.200 segundos agregados, conforme a regra de revisão registrada dos limites. Nenhuma espera funcional de 30 segundos foi alterada. O cleanup recebe prazo próprio para desligar somente o dispositivo pertencente à sessão, sem converter uma falha de teste em sucesso ou ocultar seu código.

A revisão do código de teste também restringiu os argumentos de idioma ao novo método de onboarding. Os lançamentos herdados conservam seus argumentos/configurações do SDK, inclusive runsForEachTargetApplicationUIConfiguration=true. Usar novo UDID registrado no índice padrão, com dados/logs no worktree, para garantir dados novos sem apagar a sessão anterior.

### Preparo nativo versionado

A conversão comprovada em T1 será encapsulada no componente ios_native.py (T8), com testes co-localizados e repetição real antes de fechar seu gate. O manifesto continua sendo a referência fixada; o preparo não consulta latest, não escreve na store Nix e não apaga tentativas. O validador T4 reutiliza o leitor de Mach-O/arquivos para conferir bytes reais, e o guia T5 usa somente comandos versionados. Isso fecha a reprodução prevista, sem alterar os critérios.

A segunda sessão real também venceu o limite agregado: 177 execuções aprovadas e zero falhas de asserção observadas, exit 124, shutdown 0, nenhum clone criado. A enumeração suportada do Xcode retornou exit 0 e quatro métodos lógicos; ela não inclui a expansão das configurações de UI. A revisão registrada para a tentativa -03 aumenta somente a janela agregada para 3.600 segundos. O dispositivo anterior foi confirmado Shutdown após enumeração e seu registro foi arquivado na própria tentativa; nova sessão mantém dados novos sem apagar as anteriores.

## Perfil do primeiro build aprovado em 2026-10-16

Após três tentativas integrais incompletas, o proprietário aprovou limitar o gate do marco ao perfil first-build, em inglês/portrait/light. TAVERNA_UI_PROFILE é uma seleção explícita do test host, não um filtro Only/Skip. Os quatro métodos e suas asserções permanecem. O teste herdado de screenshot mantém runsForEachTargetApplicationUIConfiguration=true quando o perfil não é first-build; full-matrix continua disponível e não aprovado. Perfis desconhecidos são recusados antes de abrir o app. O executor fixa a aparência apenas no UDID próprio, e os testes fixam portrait no perfil. Receipts, validador e comparação identificam o perfil; duas reproduções precisam usar o mesmo perfil. Guard, assinaturas, fonte, limites de tela e gates finais permanecem.
