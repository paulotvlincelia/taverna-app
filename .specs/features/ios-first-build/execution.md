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

## T1 concluída: núcleo local e cinco entradas de simulador

A realização nativa -05 terminou com exit 0 às 18:57:24 UTC de 2026-10-16, preservando fonte/receita/locks. O output by4ic9... foi conferido por path-info e store verify de conteúdo, exit 0; ultimate=true/signatures=[], narHash sha256-ZFKAmu/8pvBZFMK2I04JvtSd9A40L+qshJQmtOjscjs=. O ZIP local tem 70.599.757 bytes e SHA-256 18a6835191b226fc1b9a9961b9e3bd053aaa42c4e376261cf048c5d130a4fa66. Não é um binário do núcleo baixado de release.

O [manifesto de entradas](native-inputs.json), SHA-256 ae89d70ece47ce7e5f850a403b4fd1f74cd3fcf80c537369f3c8d77712cf1ce8, fixa o commit upstream 479548ee..., fonte Nix/NAR, receita, hashes e licenças. Os 290 arquivos filtrados pertinentes do fonte correspondem ao fork; a única diferença entre os 291 arquivos comparados é README.md. A configuração instalada declara AGPL-3.0-only. A inspeção das declarações Haskell no closure encontrou 150 registros, sem licença ausente; isso não é SBOM por objeto ou aprovação de distribuição. Foram preservados os textos de licença do GHC/runtime, OpenSSL 3.0.10, libffi, GMP e WebRTC.

A primeira conversão mac2ios -s falhou: 3.424 objetos continuaram LC_VERSION_MIN_IPHONEOS. Receipt BLOCKED/exit 1 e arquivos originais preservados em native-core-qualification-20261016. Os probes oficiais estão em native-legacy-platform-probe-20261016: ld recusou o objeto original, vtool converteu uma cópia preservando minos=11.0/sdk=0.0 e ld aceitou a cópia para simulador, exit 0. Não foi enfraquecida a checagem para aceitar tag de aparelho físico.

A nova tentativa native-core-qualification-20261016-02 usa vtool/libtool locais, com receipt exit 0 às 19:02:48 UTC. Conferiu todos os membros, inclusive nomes repetidos por ordinal: cinco arquivos, 4.187 objetos arm64/platform 7, payload e comandos fora da versão preservados. Código, dados, tabelas de símbolos e relocações permaneceram byte a byte idênticos; somente metadados de versão e o índice/empacotamento do arquivo mudaram. Nenhum arquivo da store foi alterado.

| Arquivo | Objetos | SHA-256 da cópia de simulador |
| --- | --- | --- |
| libHSsimplex-chat-7.0.0.12-4ehbYDRAXlKGgyS4p1jhJT-ghc9.6.3.a | 3.424 | 308563dc40b253a82183257c6b9d1641b0a39be5a7d1a27068fcc2fc97015c40 |
| libHSsimplex-chat-7.0.0.12-4ehbYDRAXlKGgyS4p1jhJT.a | 227 | e574e99a39f7c9d82dc6d544b293dd35ebc489a620ad8092e5f96e4ecab11999 |
| libffi.a | 8 | 8289154f2f75f63e3950ba997ba0e3a4b324fc05acb25f9803effb8ebe6c708a |
| libgmp.a | 516 | 2b8b504b45e943d4e1842bd446e2c466664ba58cb1e9dc8c76e484f7f39baf3b |
| libgmpxx.a | 12 | 99373f1e81e6702696a10b57c378939b002590e34d94cfc8787ca4a97c401d58 |

### Gate e adequação de T1

Full Native: realização fixada, inspeção completa, verificação de conteúdo, origem/licenças/hashes e python3.12 .build/check-native-inputs.py terminaram exit 0. Os 40 testes Python existentes passaram, incluindo os 28 Foundation originais; nenhum teste removido, alterado ou ignorado. Foundation/compileall/diff checks também aprovados. Fonte desconhecida, hash divergente e objeto de iPhone físico foram injetados somente em cópias de manifestos/bindings em native-input-negative-checks-20261016; todos foram recusados com exit 1 e motivo correto. Os artefatos reais permaneceram intactos.

| Critério / AC | Evidência e asserção | Resultado exigido | Coberto |
| --- | --- | --- | --- |
| Origem/receita/locks e hashes; IOS-01/02/16 | .build/check-native-inputs.py:8: m['upstream_commit']=='479548ee53ffb73db73841e77acbeee5a78dbbd5'; linhas 11–15, 22–23 e 34–36 conferem conteúdo/locks/fonte | Fonte fixado e bytes correspondentes | Sim |
| Licença declarada; IOS-01 | .build/check-native-inputs.py:28: m['licenses']['simplex']['sha256']==sha(root/'LICENSE'); linha 29 exige zero ausência nos 150 registros declarados | Licença com evidência do fonte; sem aprovar distribuição | Sim |
| Todos os objetos; IOS-09 | .build/check-native-inputs.py:25: all(o['cpu']==16777228 and o['platforms']==[dict(kind='build',platform=7)] for o in actual['objects']) | arm64 e iOS Simulator em todos os objetos | Sim |
| Somente conversão de metadados; invariantes de AGENTS | .build/convert-core-vtool.py:58: before!=after bloqueia; linha 68 exige identity(data)==identity(outdata), linha 69 confere hash de cada objeto recomposto | Payload, offsets, símbolos, relocações e versões minos/sdk preservados | Sim |
| Local versus cache; IOS-19 | .build/check-native-inputs.py:31: actual_core['ultimate'] is True e NAR/derivação correspondentes; linha 32 exige receipt 0; linha 37 mantém WebRTC como artefato de fornecedor, não rebuild local | Estados separados | Sim |
| Rejeição; IOS-02 | native-input-negative-checks-20261016/results.json: unknown-source/wrong-hash/device-object com exit 1 e AssertionError correspondente | Zero falso PASS | Sim |

| Prova nova | Vínculo | Manter |
| --- | --- | --- |
| Fonte/locks/hashes e licenças acima | T1 Done when 1; IOS-01/02/16 | Sim |
| Objetos/payload e recusa da entrada de aparelho físico | T1 Done when 2; IOS-09 e invariantes de segurança | Sim |
| Realização local/receipts e WebRTC separado | T1 Done when 3; IOS-19 | Sim |
| Três entradas negativas | T1 Tests; IOS-02 | Sim |

Adequação: asserções de estado/conteúdo e resultados reais, sem mocks ou testes especulativos. As verificações operacionais desta tarefa estão no estado local; T4/T5 ainda devem publicar a checagem/procedimento reproduzível, conforme sua ordem aprovada. T1 concluída; isso não declara build do app, teste UI, reprodução ou Verifier aprovados.

## T3 em andamento: primeira incompatibilidade do SDK

As bibliotecas qualificadas foram copiadas, com hashes conferidos, para apps/ios/Libraries/sim. O preflight ios-app-live-preflight-20261016-01 confirmou novamente o UDID e guard. A primeira tentativa ios-app-build-20261016-01 iniciou às 19:14:08 UTC e terminou exit 65 às 19:15:03 UTC; xcresult/logs/receipt/diff preservados. Falhou na expansão @State @ObservedObject de ChatView, com _chat/$chat duplicados. Nenhum app lançado e nenhum teste executado.

O SDK instalado exporta macro State e o tipo property-wrapper State. Probes com swiftc -typecheck foram preservados em swift-state-composition-20261016: fonte original e especialização genérica falharam; alias interno do tipo State passou com tipos esperados de storage/projeção e inicializador. O ajuste mantém State<ObservedObject<Chat>> por meio de ChatViewState, sem mudar ownership, fonte nativo, protocolo ou dependências. Ainda falta a compilação e a suíte reais para concluir T3.

### Primeiro build e primeira execução real

A tentativa ios-app-build-20261016-02 terminou exit 0 às 19:19:46 UTC com TEST BUILD SUCCEEDED. A inspeção dos produtos SimpleX.app, SimpleXChat.framework, SimpleX NSE.appex e SimpleX SE.appex confirmou arm64/platform 7, assinatura ad hoc sem TeamIdentifier e codesign --verify --strict exit 0. O framework define chat_migrate_init_key, chat_send_cmd, chat_recv_msg_wait e hs_init; a prova usa o núcleo real qualificado. Produtos e hashes em products.json da tentativa.

O xctestrun real tem FormatVersion 1. Foi preservado e copiado para arquivo irmão no mesmo diretório Products, mantendo a resolução de __TESTROOT__. As únicas mudanças são ambiente do test host e do app: arquivos/guard/bindings da sessão. Nenhum Only/Skip foi inserido; ambiente e diagnósticos do SDK preservados.

Na sessão ios-app-ui-20261016-01, o teste Get started → Your profile passou em 10,091 segundos, com screenshots e prova antes do main. Os três métodos herdados foram executados; testLaunch repete em muitas configurações por sua regra original. Ao vencer a janela de 900 segundos havia 130 execuções aprovadas e zero falhas de asserção observadas, mas a suíte ainda não terminara. Não declarar PASS da suíte completa. O monitor interrompeu o Xcode; cleanup limitado pelo prazo esgotado retornou timeout e agregou exit 2. Receipt intacto, causa reconciliada separadamente, nenhum dispositivo clonado e antigo UDID confirmado Shutdown.

A próxima tentativa tem janela agregada de 1.200 segundos registrada no spec; tempos funcionais continuam em 30 segundos. Os argumentos de idioma foram movidos da factory para o novo teste, preservando os argumentos/configurações de lançamento dos métodos herdados. A sessão antiga/dados/índices foram preservados em owned-session.json, sem limpeza forçada. Novo dispositivo criado por ios_session.create: UDID 2775E39A-9AC2-47F0-9025-70E606449968, mesmo runtime/modelo aprovado, dados/logs físicos no worktree. Nenhum app foi lançado nesse novo UDID ainda.

### Segunda sessão real vinculada ao build atual

Após restringir o idioma somente ao onboarding, ios-app-build-20261016-03 recompilou os testes com exit 0 entre 19:40:45 e 19:40:48 UTC. Uma tentativa de despacho que ainda vinculava o build -02 foi corretamente recusada pela comparação do patch iOS antes de inicializar/lançar o app; registro preservado em ui-dispatch-build-binding-check-20261016. O despacho corrigido vincula hashes dos dois fontes de teste e o diff exato ao build -03.

A sessão ios-app-ui-20261016-02 iniciou às 19:42:51 UTC no novo UDID, com prazo 20:02:51 UTC. Configuração xctestrun preserva métodos, configuração de UI, ambiente/diagnósticos do SDK; somente acrescenta os caminhos/guard necessários. Os quatro produtos do build -03 foram reinspecionados: hashes idênticos aos de -02, arm64/platform 7, assinaturas ad hoc válidas e símbolos Haskell presentes. A suíte segue ativa; seu receipt e xcresult final ainda são necessários para fechar T3.

### Limite de -02 e enumeração dos métodos

A sessão -02 terminou às 20:02:51 UTC com test_exit_code=124/test_timed_out=true; agregado também 124, shutdown 0 e new_device_ids vazio. Havia 177 casos aprovados e zero falhas de asserção observadas, mas a suíte permanecia incompleta. Nenhum PASS de suíte. A enumeração ui-enumeration-20261016 terminou exit 0 às 20:03:44 UTC, descobrindo os três métodos herdados e o onboarding; não informa o total de configurações geradas no runtime. A enumeração inicializou apenas o test runner no UDID próprio; não executou testes ou abriu o app. O shutdown adicional retornou 149 porque o Xcode já havia desligado o dispositivo; snapshot posterior confirmou Shutdown, com reconciliação separada e resultado original preservado. A próxima tentativa usa 3.600 segundos agregados conforme revisão registrada antes do despacho, mantendo todos os testes e seus limites funcionais.

## T8 concluída: preparação nativa reproduzível

Premissas: usar somente o ZIP Nix qualificado e as ferramentas Apple cujos hashes constam do manifesto; nada de download implícito, instalação ou alteração das bibliotecas usadas pela suíte ativa. Arquivos: tools/taverna/ios_native.py e tools/taverna/tests/test_ios_native.py. Sucesso: preparar os cinco hashes fixados em tentativa exclusiva, preservar todos os membros/payloads e rejeitar entradas inválidas com exit não zero. T8 depende apenas de T1; o código iOS de T3 permaneceu fixo durante esta validação automática.

A CLI foi executada com --bundle apontando para o ZIP local da derivação by4ic9... e --attempt public-native-preparation-20261016-02. Terminou exit 0 entre 20:08:14 e 20:08:48 UTC. O receipt vincula o fonte do preparador pelo SHA-256 ccc4cb74a79dc63b16f2a48f644df5304c0fdf7fe3c5e1a8291ea59bfcec8e8b e o manifesto ae89d70e.... Cinco arquivos/4.187 objetos reproduziram exatamente os hashes qualificados em T1, com plataforma 7 e preservação de código, dados, versões, offsets e comandos que não são de versão. Não houve cópia para os produtos ativos ou escrita na store. A primeira prova anterior da CLI permanece separada em -01.

A CLI registra active/receipt e prazo agregado de 5.400 s; cada ferramenta respeita o tempo restante. Fonte/locks/licença, conjunto do ZIP, SHA recebido e originais são conferidos antes da conversão. Extração não usa extractall; membros duplicados do arquivo recebem diretórios por ordinal. A CLI recusou ZIP inválido e tentativa existente com exit 2; hash do receipt anterior permaneceu idêntico, em public-native-negative-20261016/results.json. Os 51 testes Python passaram, preservando os 40 anteriores e os 28 Foundation, sem skips. Foundation/compileall/diff e validadores TLC aprovados.

| Critério / requisito | file:line e asserção | Resultado exigido | Coberto |
| --- | --- | --- | --- |
| Conjunto e origem fixados; IOS-01/02 | tools/taverna/tests/test_ios_native.py:138, assertRaises(ValueError) para upstream/locks divergentes; ios_native.py:233, validate_manifest(root, manifest) antes da extração | Fonte/pins/licença conferidos | Sim |
| Extração íntegra/confinada; IOS-07/15 | test_ios_native.py:111, assertEqual(bytes extraídos, data); :112, assertRaises(FileExistsError); :126 e :130, assertRaises(ValueError) para escape/link/duplicatas/limite | Nenhum arquivo fora do destino ou tentativa sobrescrita | Sim |
| Hash e plataforma reais; IOS-02/09 | test_ios_native.py:64 e :66, assertRaisesRegex(..., arm64.*Simulator); :150 e :153, rejeição de hash/contagem/plataforma | Arm64 físico/macOS não aceito como simulador | Sim |
| Preservação da transformação; IOS-09 | test_ios_native.py:74, assertEqual(invariant(before), invariant(after)); :77/:81/:89, assertRaisesRegex(..., payload) | Alteração de payload/versões/cabeçalho/comando é rejeitada | Sim |
| Todos os membros; IOS-09 | test_ios_native.py:52–54, assertEqual nomes, bytes e contagem; :59/:94, assertRaises(ValueError) para truncamento | Nenhum nome repetido sobrescrito; estrutura válida | Sim |
| Timeout; IOS-14 | test_ios_native.py:142, assertRaisesRegex(ValueError, timeout); ios_native.py:202/211, timeout=remaining(deadline, cap) | Prazo esgotado impede a chamada da ferramenta | Sim |
| Repetição real; IOS-16 | public-native-preparation-20261016-02/receipt.json, exit_code=0 e cinco hashes; ios_native.py:219/221, hash individual e validate_library | 4.187 objetos e cinco hashes idênticos | Sim |

| Prova nova / asserções | Vínculo | Manter |
| --- | --- | --- |
| Dez casos de formato/extração/hash/origem/payload e uma prova de prazo | T8 Done when 1/2; IOS-01/02/07/09/14/15 | Sim |
| CLI negativa e recusa de sobrescrita | T8 Done when 2/3; IOS-02/15 | Sim |
| Conversão real com cinco hashes | T8 Done when 3; IOS-09/16 | Sim |

Adequação: todas asserções novas têm vínculo com os critérios, inclusive resultados negativos e bytes reais; nenhuma substitui a suíte iOS. Estilo unittest e gate de CONTRIBUTING preservados. Nenhuma conclusão T3/T4–T6 ou de distribuição.

## T4 preparada, gate positivo pendente

Escopo de arquivos: ios_proof.py e seus testes co-localizados. Premissas: JSON observado do xcresulttool 0.4.0, produtos reais e fonte/patch identificados; nenhum sucesso de comando isolado substitui todos os métodos ou as duas reproduções finais. A implementação lê binários, valida fonte/hashes/destino/guard, registra códigos de build/teste e timeout com preservação dos erros, e compara dois resultados limpos. Não muda código iOS nem produtos da suíte ativa.

O probe parcial -01 foi recusado exit 70 por usar o módulo como target; nenhum teste executado. O probe -02 usou o target correto Tests iOS/Tests_iOS/testExample e terminou exit 0 às 20:11:46 UTC, com um caso aprovado e destino antigo próprio desligado. Ele fornece formato real e uma prova deliberadamente incompleta, sem representar a suíte inteira. A CLI em proof-partial-rejection-20261016 recusou os três métodos ausentes, exit 2. O parser leu os quatro executáveis reais arm64/platform 7/ad hoc. Os 68 testes Python passaram; T4 permanece sem seu gate positivo até o resultado integral de T3. As funções de registro usam os comandos Xcode já executados em T3; suas reproduções finais serão verificadas em ambientes novos.

O registro público também contabiliza cada Test Case do console, pois o summary do SDK pode agrupar configurações sob métodos. Contagens, métodos e eventos before-main serão comparados; falha, interrupção ou ausência de método impede sucesso.

A reavaliação via referência GitHub imutável e flags no-write/no-update-lock retornou novamente a derivação c27zzp98..., exit 0. A realização subsequente reaproveitou by4ic9..., exit 0; não é uma segunda compilação do fonte. Curl 8.7.1 recusou fixtures HTTP locais por tamanho (63) e tempo (28), sem usar destinos de produto. O novo download HTTPS limitado do WebRTC recebeu 34.279.775 bytes, SHA 2598307f..., 406 entradas sem escape. Outputs locais próprios, sem publicar URLs temporárias de redirect ou binários.

## Bloqueio do gate integral, em 2026-10-16

A tentativa ios-app-ui-20261016-03 terminou às 21:04:39 UTC por timeout (test_exit_code e agregado 124). Havia 541 execuções aprovadas e zero falhas de asserção observadas; a suíte não encerrou. Shutdown do UDID 4C162668... retornou 0, nenhum dispositivo novo foi criado e os processos terminaram. O build/onboarding reais não substituem esse gate; T3 permanece incompleta.

Scheme e xctestrun não declaram repetições extras; o teste herdado mantém runsForEachTargetApplicationUIConfiguration=true. A enumeração mostra quatro métodos lógicos, não o total das configurações expandidas. Logs de configuração e descritores abertos do runner não informaram esse total. Após três tentativas incompletas, nenhuma quarta foi iniciada automaticamente.

Foi apresentada ao proprietário a proposta local ui-matrix-gate-proposal.md: um perfil explícito first-build, quatro métodos/asserts preservados e zero skips, mantendo a matriz integral disponível/pendente. A revisão mudaria o gate IOS-13 e depende de aprovação; o plano atual não foi substituído. Duas provas limpas, CI e Verifier continuam necessárias. O probe separado onboarding-evidence-probe-20261016 usa novo UDID e somente o método de onboarding para produzir imagens reais; não serve à aprovação da suíte integral.

### Imagens reais do onboarding, sem aprovação da suíte inteira

O preflight do novo UDID 22C3C673... terminou exit 0. onboarding-evidence-probe-20261016 executou somente Tests_iOS/testFirstBuildOnboarding e terminou exit 0 às 21:07:51 UTC. O caso passou em 12,912 s, com zero falhas/skips; não é execução integral. As duas screenshots e o JSON before-main foram exportados com xcresulttool e inspecionados. Get started aparece habilitado; Your profile mostra formulário vazio e Create profile desabilitado. Nenhum perfil criado. A prova de negação IPv4/IPv6 e loopback foi revalidada, e o simulador foi desligado.

Os arquivos exportados permanecem ignorados em onboarding-evidence-probe-20261016/attachments; git check-ignore confirmou os dois PNGs. visual-evidence.json registra hashes e escopo onboarding-only. Nenhuma screenshot, binário ou bundle será publicado. A decisão de gate continua pendente do proprietário.


## T3 concluída: perfil aprovado do primeiro build

O proprietário aprovou explicitamente o perfil first-build em 2026-10-16; context/spec/design/tasks registram a revisão. Os quatro métodos/asserts permanecem e a matriz integral é o default da classe herdada quando o perfil first-build não é explícito. Perfis desconhecidos falham antes de abrir o app. O executor fixa light no UDID próprio; a factory confere portrait e usa inglês. Nenhum filtro Only/Skip foi aplicado.

A tentativa first-build-profile-build recompilou as fontes modificadas com exit 0 às 21:13:58 UTC, usando o recorder preparado de T4 com allow-dirty somente nesta exploração. App, framework, NSE e Share Extension continuam arm64/platform 7, ad hoc/TeamIdentifier ausente, símbolos Haskell reais definidos e os sete pins preservados. O patch iOS e os hashes de teste estão ligados aos receipts.

first-build-profile-tests terminou exit 0 às 21:16:27 UTC. XCTest executou os quatro métodos em 85,065 s, zero falhas/skips: testExample, testFirstBuildOnboarding (13,334 s), testLaunchPerformance (medições herdadas) e testLaunch (screenshot). Não houve destino novo; shutdown próprio retornou 0. A validação first-build-profile-proof terminou exit 0: quatro métodos/casos expandidos, nove eventos válidos before-main, full_matrix=PENDING. As screenshots exportadas foram inspecionadas: Get started habilitado; Your profile em light/portrait, nome vazio e Create profile desabilitado. Nenhum perfil/conversa criado. PNGs/xcresult continuam somente no estado ignorado.

Esta prova fecha T3, mas não as duas reproduções limpas, CI ou Verifier. O fonte da exploração identifica HEAD 23f14dba8 e patch iOS; as provas finais usarão um único commit limpo posterior.

### Adequação T3

| Critério | Evidência e asserção | Resultado exigido |
| --- | --- | --- |
| IOS-11, Get started em 30 s | apps/ios/Tests iOS/Tests_iOS.swift:57, XCTAssertTrue(getStarted.waitForExistence(...)); :58 isHittable; :59 isEnabled; :60 XCTAssertLessThanOrEqual(..., 30) | Visível/habilitado dentro do limite; método real aprovado. |
| IOS-12, Your profile sem envio | apps/ios/Tests iOS/Tests_iOS.swift:69, waitForExistence; :74 XCTAssertTrue(profile.isHittable); :75 limite 30 | Navegação real aprovada; método termina após screenshot, sem entrada/envio. |
| IOS-10, cada lançamento | apps/ios/Tests iOS/Tests_iOS.swift:190, event.pid > 0, executable == SimpleX, phase == before_main, errno EPERM/EACCES para IPv4/IPv6 e loopback | Ausência/divergência lança erro, inclusive dentro da medição; nove eventos reais conferidos. |
| IOS-13, perfil e testes herdados | apps/ios/Tests iOS/Tests_iOS.swift:111, XCTAssertEqual(...orientation, .portrait); :40 measure(metrics: [XCTApplicationLaunchMetric()]); Tests_iOSLaunchTests.swift:29 screenshot keepAlways | Quatro métodos reais aprovados; todos asserts preservados; full-matrix disponível/pendente. |
| IOS-03/06/08/09 | Settings/build/produtos reais dos receipts first-build-profile-build e proof; Package.resolved hash fixado | Sete pins, quatro produtos e signing ad hoc efetivamente inspecionados; nenhum provisionamento. |

| Asserção / prova | Necessidade | Manter |
| --- | --- | --- |
| waits/isHittable/isEnabled/limites de 30 s | IOS-11/12 | Sim |
| checks de paths/hashes e novo evento before-main a cada launch | IOS-04/05/10/14 | Sim |
| portrait/performance/screenshot e quatro métodos | IOS-13 aprovado | Sim |
| Build real, assinaturas/símbolos/plataformas e probe State<ObservedObject> | IOS-03/06/08/09 e compatibilidade pontual | Sim |

Adequação: resultados observáveis, sem teste especulativo, sem excluir/skipping/assert enfraquecido. CONTRIBUTING.md e matriz de testes aplicados. A compatibilidade SwiftUI preserva State<ObservedObject<Chat>> e seus bindings; não altera protocolos/criptografia. O gate Full iOS passou no perfil autorizado; matriz integral continua sem PASS.


## T4 concluída: recorder e validador da prova

O componente tools/taverna/ios_proof.py registra settings/build/test com comandos, tempo, códigos separados, versão, commit/patch, hashes de fontes/entradas/produtos e guard. Verifica bytes Mach-O, assinaturas ad hoc, símbolos Haskell, todas as bibliotecas ligadas ao manifesto e os quatro métodos reais no xcresult/console. O estado da matriz integral fica PENDING no perfil first-build. O comparador exige fonte limpa, mesmo SHA/manifesto/perfil e caminhos físicos/caches/UDIDs distintos. O procedimento falha fechado se falta qualquer parte; --allow-dirty não satisfaz reprodução final.

Gate: 70 testes Python aprovados (28 Foundation originais preservados, 12 sessão, 11 nativo, 19 prova), Foundation/compileall/diff aprovados. first-build-profile-build/tests foram registrados pelo componente, não por um logger fictício; first-build-profile-proof lê os artefatos reais e aprova quatro produtos, quatro métodos, zero falhas/skips e nove eventos before-main. Como a exploração tinha fonte sujo, clean_source=false e não substitui T6.

Negativo real: actual-partial-outcome-negative aplica validate_results ao xcresult original de uma sessão que executou somente testExample com exit 0. Retorna 2 e identifica os três métodos ausentes. Uma tentativa de revalidar o receipt histórico completo pelo recorder atual foi antes recusada pela mudança legítima da fonte iOS após aquele build; prova-partial-rejection-current preserva essa recusa, sem reinterpretá-la como outro teste. Unit tests também executam um processo exit 65 e timeout 124 e rejeitam cleanup que tenta ocultar falha. Nenhum artefato anterior foi sobrescrito.

### Adequação T4

| Critério | file:line e asserção | Resultado definido |
| --- | --- | --- |
| IOS-13/14, quatro métodos/zero skips | tools/taverna/tests/test_ios_proof.py:61, assertEqual(executed, 4); :62/:63 zero; :71/:81/:88 assertRaises para parcial/skip/falha; :206/:208 contagens expandidas | Ausência de método/falha/skip não pode aprovar; prova real positiva e parcial negativa. |
| IOS-13/16, perfil explícito | tools/taverna/tests/test_ios_proof.py:42, assertEqual(validate_profile(...), first-build); :46/:49/:52 assertRaises para configuração/runner divergente/filtro | Inglês/portrait/light e quatro métodos sem filtro; full-matrix preservado. |
| IOS-02/09/14, produto/hash/plataforma | tools/taverna/tests/test_ios_proof.py:115 assertEqual(artifact(...), path); :116/:119/:122 assertRaises; :131 arm64/platform 7; :133 rejeição | Artefato ausente/adulterado/externo ou não Simulator não aprova. |
| IOS-10, rede antes do main | tools/taverna/tests/test_ios_proof.py:142/:144, assertRaises para cada campo inválido/ausência | PID/executável/fase/IPv4/IPv6/loopback conferidos em valor, não contagem de spy. |
| IOS-14/16, etapas e timeout | tools/taverna/tests/test_ios_proof.py:103/:109 assertRaises; :159 exit 65; :163 exit 124; :164 timed_out true; :172 exit 2 e :174 steps vazio | Falha/ausência impede avançar e não inicializa simulador após build falho. |
| IOS-17, duas provas independentes | tools/taverna/tests/test_ios_proof.py:183/:184 SHA/manifesto iguais; :185 duas execuções; :188/:195 rejeição | Fonte limpa, roots físicos/UDIDs/cache distintos e mesmo perfil. T6 fará duas provas reais. |
| IOS-19/20, estados e evidências | tools/taverna/tests/test_ios_proof.py:150/:151 exit 2/NOT PROVEN; :152 NOT CHECKED; :153 NOT RUN; :154 BLOCKED | Falha não promove outros estados. git ls-files .build vazio; PNGs/xcresult ignorados. |

| Asserções | AC / necessidade | Manter |
| --- | --- | --- |
| Todos os 19 métodos em test_ios_proof.py:38–226 | IOS-02/09/10/13/14/16/17/19; cada caso está mapeado na tabela acima | Sim |
| package_args recusa alias externo (:215/:218) e clean gate (:223/:225) | IOS-04/17, sem compartilhar estado gravável ou admitir reprodução suja | Sim |
| Resultado real e parcial negativa | IOS-08/13/14, fixtures isoladas não provam integração com Xcode | Sim |

Adequação A–D aprovada: valores/estados explícitos, testes derivados dos critérios, nenhum skip/exclusão/assert enfraquecido e padrão unittest/stdlib de CONTRIBUTING. A verificação independente ainda fará sensor; T4 não declara a feature concluída.


## T5 concluída: guia de reprodução e ambiente corrigido

Publicado docs/taverna/ios-build.md com os comandos versionados de avaliação/realização Nix, preparo dos cinco arquivos, download limitado do WebRTC, resolução dos sete pins, sessão/guard/controle, build/test/prova e comparação. As etapas constituintes têm execuções reais registradas em T1–T4/T8; seis blocos bash/Python passaram a checagem de sintaxe. O procedimento integral em dois worktrees limpos será executado em T6, sem antecipar esse gate.

O escopo documental de T5 inclui environments.md: suas instruções antigas ainda apontavam para set privado, recusado pelo Xcode instalado. O guia de entrada agora aplica APP-004 (índice padrão/aliases/dados físicos próprios), preservando o preflight F0 como inventário histórico, sem alterar código/testes da fundação. A ampliação corrige o caminho de leitura necessário para IOS-05/16, não introduz uma nova funcionalidade.

O primeiro gate unitário detectou que a cópia de teste da fundação não incluía os destinos dos novos links para a feature. O check no repositório real passou, mas o teste corretamente recusou a cópia incompleta. Um commit local foi criado antes de corrigir essa falha; ele foi corrigido por amend somente após repetir os gates com sucesso. A fixture agora copia também a feature ios-first-build real; todas as asserções e os 70 testes permanecem. Gate Build final aprovado: 70 testes, Foundation/links, compileall e diff. Documentação não exige testes artificiais; sua adequação vem dos comandos reais de T1–T4 e da reprodução final obrigatória. Não publicar screenshots/binários, não compartilhar caches graváveis e não apagar worktree pendente são instruções explícitas. Git/store imutável não dependem de harness ou chat anterior.


## T6: fonte final de implementação preparada

README, CONTRIBUTING e proveniência agora descrevem o build local comprovado e seus limites, com caminhos para o guia e estados atuais. Gates estáticos aprovados antes do commit. T6 permanece aberta: as duas provas precisam executar o SHA resultante deste commit, depois CI e Verifier independente. Esse SHA não pode ser conhecido dentro de seu próprio conteúdo; status/evidências de fechamento entrarão somente como relatório posterior, sem alterar o código testado. O último commit de implementação será identificado explicitamente nos dois receipts e na validação independente. Nenhum gate foi removido por essa ordem.


## T6 concluída: duas reproduções limpas e verificação independente

Último commit de implementação: 6ea482bd4a1912d8eef52904d930c7f6c57bf746. Este registro e os demais ajustes de estado são somente relatório; não alteram fontes, testes, ferramentas ou comandos comprovados. As duas sessões partiram desse SHA limpo e seguiram o guia em worktrees/caches/UDIDs próprios. A store Nix imutável foi reaproveitada; isso não representa uma segunda reconstrução do núcleo. Cada sessão repetiu a conversão nativa e os cinco hashes qualificados.

| Prova | Build e suíte | Resultado |
| --- | --- | --- |
| ios-proof-author | Build 2026-10-16T21:22:14.815463+00:00 → 2026-10-16T21:29:56.792485+00:00; sessão UI terminou 2026-10-16T21:34:42.437507+00:00 | Exit 0 no build/test/prova strict; fonte limpa; 4 métodos, 0 falhas/skips; 9 eventos before-main; shutdown 0, nenhum destino novo. |
| ios-proof-verifier | Build 2026-10-16T21:23:25.344184+00:00 → 2026-10-16T21:29:50.510248+00:00; sessão UI terminou 2026-10-16T21:34:46.724538+00:00 | Exit 0 no build/test/prova strict; fonte limpa; 4 métodos, 0 falhas/skips; 9 eventos before-main; shutdown 0, nenhum destino novo. |

Manifesto idêntico nas duas sessões: ae89d70ece47ce7e5f850a403b4fd1f74cd3fcf80c537369f3c8d77712cf1ce8. Xcode 27.1 (27A9275), SDK 27.1 e runtime 27.0/iPhone 17. Perfil first-build inglês/portrait/light. O comparador versionado do autor e a comparação independente do Verifier retornaram exit 0, com roots físicos, caches e UDIDs distintos. Os oito métodos executados nas duas sessões não são a matriz integral; full_matrix permanece PENDING.

| Produto arm64 iOS Simulator, ad hoc | SHA-256 autor | SHA-256 Verifier |
| --- | --- | --- |
| SimpleX.app | a2424d54b03fe3d0417fb6493760380ed926d009538e4ec2408462bd59b85c86 | e4975fe6a04103a6cc145f93463fbfc407bad4bbc4855c326001723741785c82 |
| SimpleXChat.framework | 418431a852d3537daa0e83a8862c83b95a265cd379e0b1be8ac44a3fd37b262b | 2cb5c86a3002132afce7ebee2a8664f1f0eb22c37696004ab1e0b44cba8ebea1 |
| SimpleX NSE.appex | 90b0cd54e7a8eb81808557c0743b9a2f83d8457909f3d2c36166f39786e6d506 | e91bdfd47fc1bd26d7d89eb2a30e76e1a6f413c784e488e72cbbcc18cad5bfee |
| SimpleX SE.appex | f8be7adf0df22491ae9957bf8eabdff1edff4c0a6c5dc1d0bd940517018ea17b | e6eceae242dde5d3305a4f9293f4cd40f668f27b353d457ae958627aed6c54e1 |

Hashes de binários de sessões distintas não precisam ser iguais; cada conjunto foi validado contra suas próprias fontes/entradas e produtos reais. Os símbolos Haskell exigidos foram encontrados nos dois frameworks. Os nomes/configurações herdados são os da base, não identidade de distribuição Taverna.

O Verifier independente aprovou 20/20 critérios e matou 6/6 falhas em cópias isoladas: plataforma, payload, hash de bundle, destino estrangeiro, aparência e skips. Porcelain real vazio antes/depois. Autor/Verifier: 70 testes Python, Foundation, compileall, diff e gates TLC aprovados. [CI push](https://github.com/paulotvlincelia/taverna-app/actions/runs/38968716168) e [CI PR](https://github.com/paulotvlincelia/taverna-app/actions/runs/38968724419) aprovaram o SHA de implementação exato. A CI verifica ferramentas/documentação; as provas de iOS são locais.

As screenshots reais de A e B foram exportadas e inspecionadas localmente: Get started habilitado e Your profile vazio/Create profile desabilitado, em light/portrait. Binários, PNGs, xcresult, dados e receipts continuam ignorados em cada worktree. Nenhum perfil/conversa foi criado. rede administrativa/ambiente externo/serviço externo/produção e contas Apple não foram alterados.

Adequação final: [validation.md](validation.md), 20 critérios com file:line/asserção/resultado, sensor e gates independentes. O PASS é de build Debug no simulador, núcleo realizado do fonte e perfil inicial aprovado. Matriz integral PENDING; assinatura/push em aparelho NOT RUN; identidade/assets/distribuição mantêm gates próprios. Não há pendência que bloqueie o marco aprovado.
