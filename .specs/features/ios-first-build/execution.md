# Execução do primeiro build iOS

Registro factual de 2026-10-16. O núcleo e o app ainda não foram compilados nesta etapa. Este arquivo não substitui o relatório independente de validação.

## Ambiente Nix validado

O proprietário concluiu a execução do instalador pelo Terminal gráfico. O helper registrou exit 0. A validação posterior encontrou Nix 2.34.9 e conexão funcional com o daemon.

| Prova | Resultado observado | Registro local ignorado |
| --- | --- | --- |
| Instalação gráfica | Exit 0 | .build/attempts/nix-bootstrap-20261016/gui-install.exit |
| Versão | nix (Nix) 2.34.9 | .build/attempts/nix-validation-20261016/environment.json |
| Conexão com daemon | Exit 0; version 2.34.9; trusted false | .build/attempts/nix-validation-20261016/daemon-ping.json |
| Store | /nix montado em APFS, global permissions habilitadas | environment.json e consulta diskutil da validação |

O cliente permanece sem privilégios de trusted user do Nix. A preparação dos inputs usa cache/configuração temporária sob .build/nix no worktree. Store e serviços do gerenciador seguem a exceção APP-002 já autorizada.

O erro inicial de vifs não foi tratado como instalação concluída. A tentativa com falha foi preservada, seguida da tentativa gráfica com exit 0. Não foi necessário desativar proteções do macOS.

## Fonte fixado e correspondência

A consulta flake metadata terminou com exit 0 usando o commit 479548ee53ffb73db73841e77acbeee5a78dbbd5 de simplex-chat/simplex-chat, com no-write-lock-file e no-update-lock-file.

Nar hash registrado pelo Nix: sha256-UnuHHuOg1GHTAHYLuht16IuLQvoQRK71MN2DYeGr3po=.

Os hashes SHA-256 de sete arquivos do fonte recuperado foram comparados com o fork:

- flake.nix e flake.lock;
- cabal.project e simplex-chat.cabal;
- LICENSE;
- apps/ios/SimpleXChat/SimpleX.h;
- Package.resolved do projeto iOS.

Todos os sete são idênticos. Os hashes individuais e o vínculo com o commit estão em .build/attempts/nix-core-evaluation-20261016/source-correspondence.json. Nenhuma biblioteca nativa foi qualificada por essa comparação: ela comprova as entradas examinadas, não um produto compilado.

## Avaliação da receita

O alvo selecionado é packages.aarch64-darwin com o atributo aarch64-darwin-ios:lib:simplex-chat. O primeiro probe desabilitou import-from-derivation e terminou com exit 1: a receita precisa realizar derivações auxiliares durante a avaliação.

A avaliação seguinte permite esse mecanismo da receita original, preservando o commit e os locks. Ela pode construir auxiliares usados para resolver o plano Haskell. Isso não equivale a compilar o app Swift ou a executar o mensageiro.

Registros locais: .build/attempts/nix-core-evaluation-20261016/drv-path-ifd.stdout, drv-path-ifd.stderr.log e drv-path-ifd-receipt.json, este último gravado ao término da tentativa. Nenhuma mudança do fonte é feita para silenciar erros da receita.

## Próximas provas

Ainda faltam resolver a derivação, obter as bibliotecas reais, conferir plataforma/arquitetura e fechar o executor de build e testes conforme a [especificação](spec.md). O destino isolado, a contenção de rede, o teste observável, a repetição limpa e o Verifier permanecem pendentes.

## Conferência do destino da navegação

O teste planejado passou a usar Your profile, o cabeçalho real da view CreateFirstProfile, aberta por Get started. A referência anterior à view CreateProfile foi corrigida antes de escrever o novo teste, conforme o contexto da feature. O código do app não foi alterado para acomodar o teste.

## Preparação SwiftPM independente

Enquanto a receita prepara seus auxiliares, as sete dependências Swift foram resolvidas com exit 0. Package.resolved permaneceu byte a byte idêntico, SHA-256 1b894975e60be2417dd202dce69b644f7d201560d98d4e661689e8df3cbb02ae. As revisões e o número de pins foram conferidos antes/depois.

O comando usou os flags documentados clonedSourcePackagesDirPath, packageCachePath, derivedDataPath, disableAutomaticPackageResolution, onlyUsePackageVersionsFromResolvedFile e skipPackageUpdates. O ambiente da ferramenta recebeu somente variáveis necessárias; HOME não foi reatribuído. Um probe Foundation confirmou home/Library Cocoa sob .build/xcode-user com CFFIXED_USER_HOME; temporários, configuração e module caches foram direcionados ao worktree.

O artefato WebRTC resolvido declara slice ios-x86_64_arm64-simulator. Essa observação de Info.plist não substitui a inspeção Mach-O dos produtos nem comprova o núcleo SimpleX. O manifesto fixado da dependência referencia WebRTC-M110.0.0.xcframework.zip com checksum 2598307f788ab668e0f42b2a1daef4306adbb9ec9c3959441064e8e84f7310ee. A resolução não manteve uma cópia ZIP nos diretórios examinados; não foi inventado um hash de arquivo baixado ausente.

Registros ignorados: .build/attempts/swiftpm-preparation-20261016/resolve-receipt.json, resolve.log, directory-probe.json e binary-platform-metadata.json. Nenhum app foi lançado por essa preparação.

## Cache auxiliar Haskell

O cache indicado no flake.nix de Haskell.nix da revisão fixada, cache.iog.io, respondeu HTTP 403 ao identificador padrão do Python. Uma conferência posterior com User-Agent Nix/2.34.9 respondeu HTTP 200. A indisponibilidade inicialmente atribuída ao cache era uma conclusão incorreta; a restrição observada é específica ao cliente da consulta.

O cache contém o output rkapi2fhggp8axjb6ykh3ql8jsdnwhgi-ghc-8.10.7, correspondente à derivação auxiliar exata em compilação. nix store verify --store https://cache.iog.io --no-contents --sigs-needed 1, com a chave pública hydra.iohk.io publicada no Haskell.nix fixado, terminou com exit 0. Isso verifica a assinatura dos metadados; o conteúdo ainda não foi importado ou conferido localmente. Probes e proposta de configuração estão sob .build/attempts/nix-cache-configuration-20261016 e nix-core-evaluation-20261016-02/cache-probes.json.

Nenhuma configuração global de confiança de caches foi modificada até esse registro. O proprietário recebeu a proposta concreta de permitir somente esse cache e sua chave pública, mantendo verificação de assinatura e o usuário sem trusted-users. A compilação auxiliar continua enquanto a decisão está pendente. Versões auxiliares de bootstrap não são apresentadas como a versão do compilador selecionada para o núcleo, ghc963.

## Limite da primeira avaliação

A tentativa com import-from-derivation e limite inicial de 1.800 s terminou com exit 124. Ela ainda compilava GHC 8.10.7 como auxiliar; nenhum caminho da derivação final foi produzido. O timeout permanece registrado em drv-path-ifd-receipt.json e não é PASS.

A segunda tentativa iniciou em 2026-10-16 às 13:59:59 UTC, com limite de 5.400 s previsto para builds. Usa o mesmo commit, atributo e locks, com keep-failed. Registros próprios em .build/attempts/nix-core-evaluation-20261016-02. O receipt.json dessa tentativa só será emitido ao término; .build/active-native-core.json identifica o processo e a sessão em andamento. Os outputs já completos da store foram preservados. A compilação incompleta do compilador auxiliar reiniciou.

## Consulta das configurações Xcode

A consulta showBuildSettings terminou com exit 0, sem build ou lançamento. Para o alvo do app, confirmou SDK iphonesimulator27.1, plataforma iphonesimulator, arquitetura arm64 e produtos sob .build/DerivedData do worktree. Os overrides deixaram DEVELOPMENT_TEAM e CODE_SIGN_IDENTITY vazios e CODE_SIGNING_ALLOWED=NO; CODE_SIGNING_REQUIRED ainda aparece como YES na configuração consultada. Esses valores não comprovam instalação, assinatura ou execução de testes. A configuração efetiva do runner e dos demais produtos permanece por verificar na tarefa T3.

Comando completo, ambiente, saída JSON e resumo estão em .build/attempts/xcode-settings-20261016. O mesmo isolamento de cache/Library usado na resolução SwiftPM foi mantido.

## Ferramenta de transformação fixada

Os cinco arquivos necessários para inspecionar mac2ios foram recuperados do commit 4dcb77d5ea896d749381806dfab5358851b08951, com URLs imutáveis e hashes individuais sob .build/attempts/mac2ios-qualification-20261016. Não foram compilados ou executados nessa preparação. A árvore e os headers examinados não declaram licença da ferramenta; ela não foi incorporada aos arquivos públicos do fork nem autorizada para redistribuição.

A implementação trata LC_BUILD_VERSION com a plataforma escolhida por -s, mas trata o comando antigo LC_VERSION_MIN_MACOSX como iPhoneOS mesmo com essa opção. Portanto, executar mac2ios -s não basta como prova de compatibilidade: a inspeção dos objetos e dos produtos reais continua obrigatória.

## Cache autorizado e nova avaliação

O proprietário autorizou o cache assinado, conforme APP-003. A segunda avaliação foi interrompida com SIGINT enviado somente ao cliente registrado, em 2026-10-16 às 14:36:50 UTC; terminou com exit 1 e erro interrupted by the user. Não houve timeout dessa tentativa nem derivação final. Seus registros foram preservados.

O helper administrativo conferiu os hashes da configuração original e da proposta, recusou alterações concorrentes ou workers ativos e acrescentou somente extra-trusted-substituters e extra-trusted-public-keys. O proprietário autenticou no macOS. Aplicação e reinício do daemon Nix terminaram com exit 0 às 14:37:57 UTC. O arquivo anterior está preservado sob .build/attempts/nix-cache-configuration-20261016.

A validação confirmou require-sigs=true, trusted-users=root e cliente trusted=false. O cache não foi incluído como substituter padrão de todos os projetos: a terceira avaliação o seleciona explicitamente por extra-substituters. Receita, commit e locks permanecem os mesmos, com limite de 5.400 s e log de build habilitado. Registros próprios em .build/attempts/nix-core-evaluation-20261016-03; receipt.json será gravado ao término.

## Derivação resolvida e realização

A terceira avaliação terminou com exit 0. Produziu /nix/store/c27zzp98xz7brkfbs4cgkp6gy4cfxix6-simplex-chat-lib-simplex-chat-7.0.0.12.drv; o output out esperado é by4ic9kf94n9vnz7hcnpqi2lmldvpr6v-simplex-chat-lib-simplex-chat-7.0.0.12. O formato JSON observado por derivation show é versão 4, com inputs.drvs e paths relativos à store. O comando não aceita json-format; o probe rejeitado foi preservado e o consumidor foi corrigido sem modificar a receita.

O dry-run terminou com exit 0, mas também listou paths data que não sabia construir. Esse resultado não foi tratado como gate nativo aprovado. A realização real iniciou às 14:42:34 UTC de 2026-10-16, limitada a 5.400 s, com no-link, keep-failed e o cache explícito. Logs e receipts ficam em .build/attempts/nix-core-realization-20261016. Nenhum produto do núcleo foi qualificado até aqui.

## Probes independentes da sessão

O preparo de T2 foi separado de T1 porque os controles de ambiente não dependem das bibliotecas. T3 continua dependendo dos dois gates, e nenhum teste do mensageiro foi iniciado. Todos os programas abaixo são controles sintéticos locais, fora dos arquivos versionados do app; seu sucesso não comprova o build iOS da Taverna.

Um iPhone 17 com runtime 27.0 foi criado no device set do worktree. O registro .build/session.json contém UDID, responsável, branch e caminhos. Só esse dispositivo foi inicializado ou encerrado. Nenhum simulador alheio foi apagado ou resetado.

| Probe | Resultado | Evidência ignorada sob .build/attempts |
| --- | --- | --- |
| Sandbox pela API de dentro do runtime | FAIL: biblioteca libsandbox.1.dylib ausente; boot interrompido antes do sistema do simulador | simulator-isolation-20261016 |
| Assinatura ad hoc com App Sandbox | FAIL: assinatura aceita, mas conexão externa continuou permitida | simulator-isolation-20261016-02 |
| sandbox-exec macOS via trampoline iOS | Execução host possível; perfil inicial recusado; perfil corrigido perdeu DYLD_ROOT_PATH ao voltar ao simulador | simulator-isolation-20261016-03 |
| Helper macOS próprio, com restauração explícita do ambiente | Controle externo bloqueado com EPERM, exit 0; controles sem restrição no host e no simulador tiveram conexão bem-sucedida | simulator-isolation-20261016-04 e -02 |
| Aplicar o helper ao launchd_sim | Perfil aplicado e conexão negada, mas boot falhou ao se vincular à sessão; permitir IPC Unix não resolveu | simulator-isolation-20261016-05 e -06 |
| Controle positivo do mesmo exec, sem sandbox | Boot exit 0; resultado não é contenção | simulator-isolation-20261016-07-positive-exec |
| Negar somente IP remoto, permitindo localhost | Controle externo EPERM; boot ainda falhou | simulator-isolation-20261016-08 |
| Controle positivo com sandbox allow default | Boot também falhou, embora o exec sem sandbox funcione. A falha não depende apenas das regras de rede; causa interna do vínculo ainda não comprovada | simulator-isolation-20261016-09-positive-policy |
| Roteamento de device set no Xcode inspirado no idb | showdestinations exit 0, mas UDID próprio ausente: probe exit 2. xcodebuild usa library-validation; não desativada | xcode-device-set-20261016 |
| Destino explícito sem instrumentação | showBuildSettings recusou o UDID do set exclusivo, exit 64. Nenhum destino alheio foi escolhido como substituto | xcode-device-set-20261016-02 |

O padrão investigado para roteamento vem do código público de [XcodeBuildOperation](https://github.com/facebook/idb/blob/main/FBXCTestCore/Utility/XcodeBuildOperation.swift) e do [shim do idb](https://github.com/facebook/idb/blob/main/Shims/Shimulator/TestReporterShim/XCTestReporterShim.m). O protótipo local não altera resultados XCTest; não foi incorporado ao projeto nem apresentado como compatível com Xcode 27.1. Não remover assinatura ou validação de bibliotecas do Xcode para fazê-lo funcionar.

CFFIXED_USER_HOME muda o logPath informado pelo cliente simctl, mas o runtime ainda gravava sob Library/Logs do usuário. Essa diferença foi medida, sem tratar o caminho informado como prova física. Após encerrar somente o dispositivo próprio, seus logs foram movidos integralmente para .build/SimulatorLogs, preservando nove arquivos. O índice por UDID criado pelo CoreSimulator ficou como symlink para esse armazenamento. Caminhos e realpath estão em session.json e simulator-isolation-20261016-04/log-relocation.json; reconciliar esse índice antes de qualquer remoção futura do worktree.

Situação de T2: controles parciais obtidos; contenção da sessão e destino efetivo do executor ainda não aprovados. O mensageiro permanece sem instalação ou lançamento. Nenhuma alteração de firewall global, VPN, rede administrativa ou proteção do macOS foi feita.

O probe de destino explícito gerou um bundle de erro no temporário do macOS, apesar de TMPDIR local. Esse bundle específico foi preservado em xcode-device-set-20261016-02/error.xcresult; sua movimentação consta do receipt. Os próximos comandos precisam de resultBundlePath explícito, sem presumir que TMPDIR controla todos os caminhos do Xcode.

Um teste adicional verificou aliases de índice: um segundo set dentro do worktree reconheceu um alias para o dispositivo próprio. O índice padrão já carregado pelo CoreSimulator não reconheceu a mesma forma de registro. Só o alias desse UDID foi criado no índice padrão e removido após o teste, preservando o dispositivo original e todos os outros IDs. Não houve reinício do serviço CoreSimulator ou mudança de seu índice compartilhado para forçar recarga. Registros em simulator-index-alias-20261016 e xcode-device-index-20261016.

## Agendamento da realização nativa

O Nix usava max-jobs=1. Um segundo cliente da mesma realização foi iniciado com max-jobs=3 e cores=2 para antecipar dependências independentes, coordenadas pelos locks nativos da store. O cliente original não foi interrompido. Ambos têm o mesmo prazo absoluto, 16:12:34 UTC; o novo agendador não estende o limite da tentativa. Seus registros estão em nix-core-realization-20261016/scheduler-02 e parallel-scheduler.json. Isso não é a segunda execução independente exigida pela feature.

## Alternativa de isolamento comprovada somente em controles

O registro nativo de um dispositivo novo seguido da relocação de seu armazenamento permitiu que Xcode showBuildSettings selecionasse exatamente seu UDID, com exit 0. O SDK o mantém no índice padrão; o set privado não o lista. Os dados físicos estão em .build/SimulatorDevices e o índice do SDK aponta para essa localização. O registro desse controle, separado do primeiro dispositivo, está em .build/attempts/xcode-native-registration-20261016/registration.json. Nenhum outro registro de dispositivo foi movido ou removido.

Foi compilado um app UIKit fictício de controle, separado do fonte Taverna. Ele foi instalado somente nesse novo simulador. Seu processo retornou do helper macOS com o mesmo PID, confirmou connect_errno=1/EPERM e chegou a UIKIT_CONTROL_READY. A contenção cobre esse processo; não cobre todos os daemons do simulador. Recibos e código do controle estão em .build/attempts/uikit-process-containment-20261016. Build e lançamento da Taverna continuam NOT RUN.

O [Design](design.md) propõe revisar os critérios de isolamento para essa alternativa. A proposta depende da resposta do proprietário; os critérios originais ainda não foram substituídos, e T2 continua sem aprovação de seu gate.

A captura local do app de controle confirmou visualmente a tela Isolation control. A imagem e seu hash permanecem ignorados. Um controle adicional removeu a instrumentação: o mesmo app recebeu connect_errno=36/EINPROGRESS e recusou avançar para a interface, conforme sua asserção de rede. Isso distingue o efeito do sandbox de uma restrição já imposta pelo ambiente. Registros em screenshot-receipt.json e negative-control-no-guard.json do mesmo diretório. Após os controles, somente esse simulador foi encerrado, preservando instalação e evidências. Os dois dispositivos desta sessão estão Shutdown; nenhum teste da Taverna foi executado.


## T2: sessão aprovada e ferramentas reproduzíveis, em 2026-10-16

APP-004 registra a revisão aprovada pelo proprietário. Método mantido: TLC Spec Driven, seis tarefas e execução inline. T1 continua independente; este gate de T2 qualifica o ambiente com um controle próprio, sem afirmar execução da Taverna.

**Antes da implementação:** assumir somente o SDK/runtime já identificados; API sandbox deprecated exige prova real, não apenas compilação. Escopo: tools/taverna/ios_session.py, tools/taverna/ios, tools/taverna/tests/test_ios_session.py e este registro, além dos artefatos de aprovação/status. Sucesso: destino próprio confirmado pelo Xcode, caminhos físicos locais, bloqueio externo antes do main com loopback permitido, controle negativo discriminante e tentativas anteriores preservadas.

Ferramentas versionadas:

- create registra pela API padrão do SDK, salva a posse antes de mover o dispositivo desligado e cria somente aliases por UDID para dados/logs físicos no worktree. Conflitos exigem reconciliação; não há comando de erase/delete/limpeza forçada.
- check e preflight conferem posse, device.plist, aliases, índice padrão e destino efetivo do Xcode. guard compila os dois auxiliares e registra hashes de fontes/binários locais. Uma entrada ausente ou divergente termina com exit 2.
- control compila um app UIKit próprio de teste, sem código de mensageria. O guard aplica a política por exec no mesmo PID, comprova negação IPv4/IPv6 e conexão local antes do main. O controle também se recusa a abrir a interface se a contenção faltar. Serviços do sistema iOS ficam fora da política.

Comandos comprovados neste worktree:

```bash
python3.12 tools/taverna/ios_session.py guard --attempt session-guard-20261016-02
python3.12 tools/taverna/ios_session.py control --attempt session-control-versioned-20261016 --guard-manifest .build/attempts/session-guard-20261016-02/guard-manifest.json
python3.12 tools/taverna/ios_session.py preflight --attempt session-preflight-final-20261016 --guard-manifest .build/attempts/session-guard-20261016-02/guard-manifest.json
python3.12 -m unittest discover -s tools/taverna/tests
python3.12 tools/taverna/check_foundation.py
python3.12 -m compileall -q tools/taverna
git diff --check
```

**Resultado:** controles e preflight exit 0; 39 testes Python, zero falhas/skips, incluindo os 28 Foundation preservados. Xcode aceitou exatamente o UDID próprio e a plataforma iphonesimulator. No controle versionado, o PID 44714 registrou ipv4_errno=1, ipv6_errno=1 e loopback=true antes do main; UIKit emitiu UIKIT_CONTROL_READY. Sem instrumentação, o controle recebeu EINPROGRESS (36) e não abriu a interface. O dispositivo foi desligado pelo próprio executor; nenhum outro UDID foi alterado.

Registros locais ignorados: .build/ios-session.json; .build/attempts/session-control-versioned-20261016/{preflight.json,steps.json,guard.jsonl,receipt.json}; .build/attempts/session-preflight-final-20261016. O primeiro ensaio versionado falhou na verificação local por não aguardar a conexão; failure.json e os logs permanecem em session-control-20261016. A correção aguardou o socket com poll; nenhuma asserção foi removida ou enfraquecida. A segunda tentativa e a ferramenta versionada passaram.

**Revisão da adequação, suficiente e necessária:**

| Obrigação | Asserção localizada | Resultado definido / vínculo reverso |
| --- | --- | --- |
| IOS-04, IOS-05: dados/logs físicos locais, índice e identidade | tools/taverna/tests/test_ios_session.py:41 — assertEqual(index.resolve(), storage); :51/:60/:69/:74/:79 — assertRaisesRegex(ValueError, ...) | Aceitar a sessão própria; rejeitar escape, redirecionamento, índice privado e identidade divergente. Todos necessários para IOS-04/05. |
| IOS-05: destino alheio | tools/taverna/tests/test_ios_session.py:44 — assertRaisesRegex(ValueError, 'destination'); tools/taverna/ios_session.py:200 — validate_session(... TARGET_DEVICE_IDENTIFIER) na integração real | Destino deve ser o UDID registrado da sessão. |
| IOS-10: auxiliar ausente/adulterado | tools/taverna/tests/test_ios_session.py:88/:91 — assertRaisesRegex(ValueError, 'hash'/'missing') | Bloquear preflight antes do mensageiro. |
| IOS-10: negação externa e conexão local no PID do app antes do main | tools/taverna/tests/test_ios_session.py:113–118 — assertEqual(pid/executable/phase/errno) e assertIs(loopback, True); :122 — assertRaisesRegex(ValueError, 'containment') | Rejeitar conexão externa permitida, ausência de loopback ou PID alheio; não aceitar mero timeout como negação. |
| IOS-10: prova real e sensor | tools/taverna/ios_session.py:268–270 — guard_proof(...) e ausência de UIKIT_CONTROL_READY causa ValueError; :282–283 — controle sem guard exige EINPROGRESS e recusa da interface | A política real muda o resultado observado, no app sintético identificado, sem atribuí-lo à Taverna. |
| IOS-15: preservação/retomada | tools/taverna/tests/test_ios_session.py:97 — assertRaises(FileExistsError); :100–101 — assertNotEqual(attempt, second), assertEqual(evidence, 'keep'); :104 — assertRaisesRegex(ValueError, 'attempt') | Nova tentativa não apaga nem sobrescreve a anterior, nem escapa de seu diretório. |

Cada teste novo corresponde a IOS-04/05/10/15; sem casos especulativos ou testes de framework. O payload de prova é conferido campo a campo. Padrões: CONTRIBUTING.md e unittest da fundação. Sem desvios do ajuste aprovado. **T2 concluída como gate de ambiente.** IOS-10 na Taverna real ainda depende da integração em T3; F1, build, testes iOS e verificação final continuam pendentes.


## T7: correção dos caches efetivos do Xcode

A consulta de ajustes de todos os targets encontrou CACHE_ROOT global, apesar de CFFIXED_USER_HOME e dos caches de módulos locais. T2 comprovou destino e contenção; a lacuna de caches exige esta correção adicional antes de T3. Não houve build real do mensageiro usando esse cache. IOS-04 e APP-004 permanecem com a mesma obrigação; nenhuma revisão de critério foi necessária.

**Escopo:** tools/taverna/ios_session.py, seu teste de sessão e este registro. **Hipótese comprovada:** overrides de build para CACHE_ROOT, SHARED_PRECOMPS_DIR, SDK_STAT_CACHE_DIR e COMPILATION_CACHE_CAS_PATH relocam esses campos; ambiente Cocoa sozinho não basta. **Resultado requerido:** todos os campos efetivos dentro do worktree, com rejeição de valor externo/ausente ou symlink de escape e controle de rede preservado.

A implementação acrescenta os quatro ajustes explícitos ao preflight e valida os caminhos efetivos devolvidos pelo Xcode, incluindo produtos/intermediários quando presentes. Caminhos futuros são resolvidos pelos ancestrais existentes; o check não exige que um cache já tenha sido criado para validar seu destino.

A primeira consulta -alltargets com -derivedDataPath foi recusada com exit 64; o SDK exige scheme nessa combinação. A consulta seguinte usou SYMROOT/OBJROOT explícitos, sem mudar preferências globais. A terceira consulta confirmou todos os targets com caches locais e assinatura manual ad hoc, Team/perfil vazios. Esses ajustes não comprovam assinatura em aparelho nem build. Registros preservados nas três tentativas xcode-all-target-settings-20261016, -02 e -03.

**Gate:** 40 testes Python passaram, zero falhas/skips; os 28 anteriores permanecem. Foundation, compileall e diff-check passaram. O controle real em session-cache-correction-20261016 terminou exit 0: PID 91824, negação IPv4/IPv6 EPERM, loopback=true antes do main, UIKIT_CONTROL_READY; sem guard recebeu EINPROGRESS e recusou a interface. O próprio dispositivo foi desligado. O preflight final com os quatro campos obrigatórios passou em session-cache-final-preflight-20261016.

```bash
python3.12 tools/taverna/ios_session.py control --attempt session-cache-correction-20261016 --guard-manifest .build/attempts/session-guard-20261016-02/guard-manifest.json
python3.12 tools/taverna/ios_session.py preflight --attempt session-cache-final-preflight-20261016 --guard-manifest .build/attempts/session-guard-20261016-02/guard-manifest.json
python3.12 -m unittest discover -s tools/taverna/tests
python3.12 tools/taverna/check_foundation.py
python3.12 -m compileall -q tools/taverna
git diff --check
```

**Adequação suficiente e necessária:**

| Obrigação / resultado | Asserção localizada | Vínculo reverso |
| --- | --- | --- |
| IOS-04: caches efetivos locais, rejeição de valores externos | tools/taverna/tests/test_ios_session.py:129 — validate_build_paths(root, settings); :132 — assertRaisesRegex(ValueError, key) para cada campo externo | Reproduz o defeito real de CACHE_ROOT e verifica também os demais caches/produtos presentes. |
| IOS-04: campo obrigatório ausente | tools/taverna/tests/test_ios_session.py:137 — assertRaisesRegex(ValueError, key) para os quatro campos removidos individualmente | Falta de dado não pode equivaler a isolamento provado. |
| IOS-04: alias aponta para fora | tools/taverna/tests/test_ios_session.py:142 — assertRaisesRegex(ValueError, 'CACHE_ROOT') | Verificar o caminho físico, não somente o prefixo textual. |
| IOS-05/10/15: preservar destino, contenção e evidências | Asserções existentes de T2, sem alteração; integração real do controle e preflight citada acima | Nenhum teste herdado removido/relaxado. Nova tentativa com nome distinto preserva a falha anterior. |

Todos os casos novos se vinculam ao defeito observado em IOS-04. Padrão unittest/CONTRIBUTING preservado; sem testes de framework. T7 concluída, sem declarar build ou teste UI da Taverna. T1 e T3–T6 continuam pendentes.


## T1: inspeção antecipada dos auxiliares, em 2026-10-16

A realização principal segue ativa; esta inspeção não fecha T1 e não declara a biblioteca SimpleX produzida. Em .build/attempts/native-platform-qualification-20261016 foram preservados derivations, registros de fontes/licenças, logs de build locais e inspeção dos arquivos .a. Os três auxiliares libffi 3.4.4, GMP 6.3.0 e mac2ios têm logs de realização local/ultimate no Nix; a conferência adicional da store verificou o conteúdo local, sem mudar a política de assinaturas de importação. Não atribuir esses produtos ao cache.

Os cinco arquivos do fonte mac2ios na derivação realizada coincidem com os hashes da revisão 4dcb77d5ea896d749381806dfab5358851b08951 previamente consultada. A ferramenta da store, não uma cópia modificada, foi usada com -s sobre cópias próprias. Original e transformação permanecem separados. A licença da ferramenta continua sem identificação no fonte consultado; ela não será vendorizada/distribuída. Código de inspeção operacional próprio e resultados em inspect_archives.py/archive-inspection.json, no diretório local acima.

| Biblioteca auxiliar | Objetos inspecionados | Original | Cópia de simulador |
| --- | --- | --- | --- |
| libffi.a | 8 | arm64, LC_BUILD_VERSION platform 1 | arm64, platform 7 |
| libgmp.a | 516 | arm64, LC_BUILD_VERSION platform 1 | arm64, platform 7 |
| libgmpxx.a | 12 | arm64, LC_BUILD_VERSION platform 1 | arm64, platform 7 |

Todos os 536 objetos dessas cópias têm a plataforma esperada. Não há objeto legacy sem plataforma nesse conjunto inspecionado. Isso não qualifica automaticamente a biblioteca Haskell ainda ausente. SHA-256 de fontes, originais e transformações em summary.json/support-provenance.json; arquivos COPYING.LESSERv3 e LICENSE foram lidos diretamente das fontes tar correspondentes, sem extrair caminhos arbitrários. Hashes das fontes coincidem com os fixed-output hashes das respectivas derivações Nix.

O filtro do núcleo contém 291 arquivos: 290 coincidem byte a byte com o fork; a diferença é README.md, que a fundação substituiu. Não há diferença do código/receita do núcleo entre o upstream fixado e o fork atual. Relatório por arquivo: filtered-core-source-correspondence.json. Nenhum arquivo de runtime foi alterado por essa conferência.

### WebRTC fixado pelo SwiftPM

O [release M110](https://github.com/simplex-chat/WebRTC/releases/tag/110.0.0) declara o fonte WebRTC 218b56e516386cd57c7513197528c3124bcd7ef3 e o SHA-256 2598307f788ab668e0f42b2a1daef4306adbb9ec9c3959441064e8e84f7310ee. O objeto de commit foi confirmado no endpoint público Googlesource. O pacote da base permanece em 34bedc50f9c58dccf4967ea59c7e6a47d620803b; sua receita e patch estão preservados, sem atualizar revisão ou reconstruir esse binário.

O ZIP de 34.279.775 bytes foi recebido sob o limite de 5 GiB/30 minutos e bate com esse SHA. API do asset identificada pelo ID 97488736. Inspeção de todos os caminhos e symlinks do ZIP não encontrou escape; a fatia efetivamente resolvida pelo SwiftPM coincide byte a byte com o arquivo no ZIP. Seu SHA-256 é 1318935eb67b5443a52a0ea7a48fba163a88dd0e2afd5eea153dff28f1ad5249. A inspeção otool da arquitetura arm64 confirma LC_BUILD_VERSION platform 7, minos 14.0, SDK 16.2. A licença do artefato foi preservada localmente.

Evidências locais ignoradas em .build/attempts/webrtc-qualification-20261016: release.json, download-receipt.json, source-commit.json, manifest.json, artifact-LICENSE.txt e comandos de arquitetura/plataforma. Este é um WebRTC pré-compilado já fixado pela base; não é a biblioteca Haskell nem uma reconstrução local. App e testes iOS continuam NOT RUN.


Precisão adicional de proveniência WebRTC: o tag 110.0.0 aponta para 28dd8570a3482d46b90ce4e924e8ff1d17614e78, anterior ao patch; ele não deve ser tratado como a receita completa do binário consumido. O pacote fixado 34bedc50 inclui o patch de frame encryption e a mudança de origem/checksum de stasel para simplex-chat. O commit e493ce51785bbadb286fe68fa2f5929293db6821 registra a atualização do release M110; os símbolos RTCFrameEncryptor/RTCFrameDecryptor estão exportados no binário recebido. Manifesto local explicita a garantia: metadados do fornecedor + checksum/receita fixados + API modificada observada, sem atestação de build nem reconstrução local. Preservar essa precisão no relatório; não afirmar fonte upstream puro ou que o tag antigo sozinho reproduz o artefato. Comparação de commits, diff do pacote e símbolos permanecem em webrtc-qualification-20261016.


## T1: limite da realização e nova tentativa, em 2026-10-16

A primeira realização nativa atingiu seu limite absoluto em 16:12:35 UTC. Ambos os clientes encerraram com exit 124, ainda em módulos GHC 9.6.3 Stage1. O texto interrupted by the user veio do sinal emitido pelos monitores ao vencer o prazo; não indica cancelamento pelo proprietário. Nenhuma biblioteca Haskell final foi produzida; build/testes da Taverna permanecem NOT RUN.

Preservados build.stdout, build.stderr.log e receipt.json dos dois clientes sob nix-core-realization-20261016, incluindo scheduler-02. A nova execução só foi iniciada depois de conferir ambos os receipts. Ela usa a mesma derivação c27zzp98xz7brkfbs4cgkp6gy4cfxix6-simplex-chat-lib-simplex-chat-7.0.0.12.drv, sem alterar receita, flags compiladas, fontes ou locks. O ajuste operacional é max-jobs=2/cores=5, para distribuir os dez núcleos disponíveis entre os builds. Não atribuir uma aceleração medida antes de observar o resultado.

A nova tentativa começou às 16:12:41 UTC, com novo limite de 5.400 s, até 17:42:41 UTC. Não é extensão da tentativa anterior nem uma segunda reprodução do app. Estado/receipts próprios em .build/attempts/nix-core-realization-20261016-02; comando e PIDs em .build/active-native-core-retry.json. O runner local .build/native-core-retry.py recusa iniciar se os clientes anteriores estiverem ativos ou se a falha não for exclusivamente timeout. Nenhum limite de download ou testes foi aumentado.


Observação da repetição: cores=5 é um parâmetro de paralelismo fornecido à receita pelo Nix, não um limite rígido de CPU. Os dois processos Hadrian observados usam -j sem número explícito. O registro parallelism-observation.json guarda essa informação; resource-observation.json registra a amostra dos processos próprios e memória. Não declarar cinco threads exatos nem aceleração comprovada somente por ter mudado a opção. A origem do worker foi identificada no log desta realização; nenhuma configuração do daemon foi alterada.

### Retomada após atualização do Codex

Em 2026-10-16, às 17:07 UTC, a reconciliação encontrou a tentativa nix-core-realization-20261016-02 sem receipt final, monitor, cliente, worker ou processo GHC/Hadrian ativo. O log parou às 17:04:43 UTC em GHC Stage1; nem o núcleo nem os dois compiladores finais estavam na store. O retorno original é desconhecido. A atualização/interrupção da sessão coincide com esse encerramento; não há prova da causa exata. O registro interruption.json preserva estado INTERRUPTED e exit_code null, sem inventar timeout ou falha de compilação.

Os dois outputs GHC exatos retornaram HTTP 404 no cache autorizado, usando User-Agent Nix/2.34.9; consultas preservadas em update-recovery-20261016/cache-probes.json. Nenhuma fonte, receita, flag de compilação ou lock foi alterado.

A preparação foi retomada às 17:08:30 UTC em uma dependência por vez, começando pela derivação 700zdsaz65dn4war5jzc6pwj20dbssfl-ghc-9.6.3.drv, já pertencente ao grafo aprovado. Agendamento max-jobs=1/cores=10; cores continua sendo uma indicação, não quota rígida. Limite de 5.400 segundos preservado, até 18:38:30 UTC. Logs, metadados e receipt próprio em .build/attempts/nix-ghc-small-20261016-03; sessão exec 57073. Isso prepara somente um compilador, não realiza o núcleo nem comprova o app. Não há compilação concorrente da tentativa anterior.

T2/T7 permanecem concluídas; T1 continua sem seu gate final e T3–T6 pendentes. Todos os arquivos existentes e as evidências anteriores foram preservados. Nenhuma mudança no rede administrativa, ambiente externo, serviço externo ou produção.

### Primeiro GHC exato realizado

A tentativa nix-ghc-small-20261016-03 terminou às 17:52:05 UTC com exit 0, dentro de seu limite de 90 minutos. O output 6mrz4w4nri6wq4nzys2grfzml9mk2m97-ghc-9.6.3 pertence à derivação 700zdsaz65dn4war5jzc6pwj20dbssfl-ghc-9.6.3.drv; path-info confirma ultimate=true, signatures=[] e narHash sha256-SE4TuL4yg4YKecGZ2DuJY69gKxC+okJFKRZE2rJWTzA=. O executável ghc --numeric-version retornou 9.6.3, exit 0. Trata-se de realização local de uma ferramenta do host, não de biblioteca iOS nem de build do app. Receipt, logs, path-info e qualification.json preservados no diretório da tentativa.

O segundo compilador exato do grafo, derivação 7r81jvdqpz36bf6aba0j4yfiin2g8xp6-ghc-9.6.3.drv, iniciou às 17:52:10 UTC em nix-ghc-normal-20261016-04, depois do receipt 0 do primeiro. Agendamento max-jobs=1/cores=10; mesma receita/locks, limite de 5.400 segundos até 19:22:10 UTC. Sessão exec 67142, monitor 32420 e cliente 32428; conferir active.json e receipt.json antes de qualquer retomada. Nenhuma biblioteca final ou app foi declarada concluída.

### Dependências do núcleo em paralelo com o segundo compilador

O dry-run de nix-core-ready-graph-20261016 terminou exit 0 e identificou 164 derivações pendentes, incluindo somente o segundo GHC exato como compilador final ainda não realizado. A realização do núcleo c27zzp98... foi iniciada às 17:53:16 UTC em nix-core-realization-20261016-05, com max-jobs=1/cores=5 e limite próprio de 5.400 segundos até 19:23:16 UTC. Sessão exec 87662, monitor 41199, cliente 41207. A segunda realização GHC permanece na sua tentativa e limite originais; os locks da store coordenam os clientes. Não modificar ou substituir outputs em compilação.

O log confirmou uso do GHC 9.6.3 já concluído na derivação w27xkfk29hf3h6x3pghzgf7ww8bvhzb6-ghc-9.6.3-deps.drv. Isso permite antecipar dependências sem duplicar o segundo compilador. Não é reprodução independente nem resultado do núcleo; ambos os receipts precisam de inspeção antes de qualquer retomada.

### Dois compiladores do host concluídos

A tentativa nix-ghc-normal-20261016-04 terminou às 18:42:05 UTC com exit 0. O output pmyvxihh7msvbgkjdgk0bz49ni0xpwbv-ghc-9.6.3 corresponde à derivação 7r81jvdqpz36bf6aba0j4yfiin2g8xp6-ghc-9.6.3.drv, ultimate=true/signatures=[], narHash sha256-pkrTa4anD/ogU1fr2BQHlnlZuMWqvPjtaJFFkLX/Poc=. ghc --numeric-version confirmou 9.6.3, exit 0. A primeira consulta path-info omitiu --json e retornou texto apesar de --json-format=1; essa saída foi preservada como formato inválido. A nova consulta explicitou ambas as opções, validou o JSON e a derivação antes de registrar metadados.

O conteúdo dos dois outputs GHC foi revalidado com nix store verify --no-trust, exit 0, em nix-compilers-content-check-20261016. --no-trust aplica-se à conferência de conteúdo de produtos locais; não modifica require-sigs, chaves ou importação de cache. Os compiladores foram realizados localmente, sem atribuí-los ao cache.

O núcleo continua ativo na tentativa -05, prazo original 19:23:16 UTC; o log iniciou 134 derivações até 18:42 UTC. Falta realizar e qualificar a biblioteca final; não há build do app nem teste UI da Taverna. A consulta ao manual xcodebuild.xctestrun instalado foi preservada em xctest-execution-research-20261016: documenta build-for-testing/test-without-building e distingue EnvironmentVariables do test host de UITargetAppEnvironmentVariables. Isso orienta a próxima tarefa, sem afirmar propagação real ao app ou editar testes antes do gate T1.
