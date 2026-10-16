# Prontidão para o primeiro build iOS

## Estado atualizado em 2026-10-16

Primeiro build de base comprovado: duas reproduções limpas, CI e Verifier independente aprovados no commit 6ea482bd4a1912d8eef52904d930c7f6c57bf746. Perfil first-build com quatro métodos por execução, zero falhas/skips; 20/20 critérios verificados. Ver [relatório](validation.md).

| Parte | Estado atual | Evidência |
| --- | --- | --- |
| Núcleo | Realizado localmente do fonte fixado, com Nix; cinco arquivos e 4.187 objetos de simulador | T1/T8 em [execution.md](execution.md) e [manifesto](native-inputs.json). |
| App/framework/extensões | Build-for-testing aprovado, arm64 iOS Simulator e ad hoc | Duas provas limpas no SHA 6ea482bd4, quatro produtos e símbolos reais inspecionados em cada uma; hashes em execution.md. |
| Navegação inicial | Get started → Your profile aprovado, sem envio do formulário | Método real aprovado nas duas reproduções limpas, com limites de 30 s por tela e screenshots inspecionadas localmente. |
| Contenção | Prova antes do main no processo real do app | IPv4/IPv6 remotos negados e loopback permitido; dados/UDID próprios, conforme APP-004. |
| Ferramentas Python | 70 testes aprovados, zero falhas/skips | Autor, Verifier e CI; mantidos os 28 testes anteriores à feature. |
| Perfil first-build | Quatro métodos aprovados por reprodução, zero falhas/skips | Duas provas limpas com dados novos; nove eventos before-main e shutdown 0 em cada uma. |
| Matriz integral | Incompleta por timeout, sem PASS | Terceira tentativa: 60 min, 541 execuções positivas/zero falhas observadas; dados preservados e simulador desligado. |
| Decisão de gate | Aprovada pelo proprietário | Perfil first-build em inglês/portrait/light, quatro métodos/asserts e zero skips; matriz integral disponível e pendente. |
| Repetição/CI/Verifier | Aprovados | Mesmo SHA/manifesto/perfil em ambientes distintos; 20/20 critérios, sensor 6/6 e CI no SHA exato. Aparelho/push NOT RUN; distribuição BLOCKED. |

O texto abaixo preserva o levantamento inicial de planejamento. Seus estados de ausência e rotas candidatas são históricos; o estado atual e os limites do PASS estão registrados acima e em execution.md.

## Levantamento inicial, antes da implementação

Em 2026-10-16, o Xcode e os runtimes estão disponíveis. O primeiro build ainda não foi executado. O bloqueio de entrada mais importante é obter e qualificar as bibliotecas nativas do núcleo; os testes e o destino isolado também precisam de prova.

Este documento é um levantamento de planejamento. Não é o relatório de um Verifier e não declara a issue #6 concluída.

Atualização após aprovação: a [qualificação das bibliotecas](core-qualification.md) terminou BLOCKED; nenhuma entrada oficial iOS foi qualificada. O [Design da alternativa](design.md) detalha a compilação do núcleo via Nix e a exceção administrativa autorizada. Nix 2.34.9 foi instalado e validado; a receita está preparando suas ferramentas Haskell. As sete dependências SwiftPM foram resolvidas preservando integralmente Package.resolved. Não há build ou teste iOS executado.

## Base examinada

| Referência | Valor |
| --- | --- |
| Repositório | paulotvlincelia/taverna-app, público |
| Base Taverna | stable, 8b2ffa71dc414615236f3fd41cb3a11876be740c |
| Base upstream preservada | simplex-chat/simplex-chat, 479548ee53ffb73db73841e77acbeee5a78dbbd5 |
| Fundação anterior | PR #9 integrado; prova da fundação preservada em validation.md da feature foundation. |
| Sessão deste plano | codex/6-ios-first-build-plan; worktree ios-first-build-plan no diretório irmão taverna-app-worktrees. |
| Responsável/harness | Codex, sessão do planejamento; escopo limitado à especificação e ao handoff. |

## Já disponível e o que falta

| Parte | Estado observado | Prova ou lacuna |
| --- | --- | --- |
| Xcode | Disponível: 27.1, build 27A9275 | xcodebuild -version retornou zero. |
| Runtime iOS 27.0 | Disponível: 24A434, arm64 | simctl list runtimes: isAvailable=true, 62 tipos de dispositivo, inclui iPhone 17. |
| Runtime iOS 27.1 | Disponível: 24A94425, arm64 | isAvailable=true; lista somente iPhone Duo. |
| Download antes relatado com falha | Nenhum runtime faltante nessa consulta | Os dois runtimes acima agora estão disponíveis. Isso não prova o build do app. |
| Fonte e projeto Xcode | Presentes | apps/ios/SimpleX.xcodeproj; scheme SimpleX (iOS). |
| Bibliotecas nativas | Ausentes | Nenhum dos diretórios apps/ios/Libraries/mac, ios ou sim existe na base examinada. |
| Origem imutável das bibliotecas | Não localizada/qualificada | O script de download recebe a URL de jobs e usa latest; isso não fixa artefato nem seu fonte correspondente. |
| ABI de simulador arm64 | Não comprovada | O upstream tem rotas diferentes para arm64 e x86_64, com transformação mac2ios. É necessário inspecionar plataforma e ligação, não só o nome do arquivo. |
| Nix e ferramentas Haskell | Nix 2.34.9 validado; auxiliares Haskell em construção pela receita | Não instalar GHC/Cabal/Stack globais para substituir o conjunto fixado. |
| Dependências SwiftPM | Sete pins resolvidos; Package.resolved byte a byte preservado | Resolver terminou com exit 0. Compilação dessas dependências no app ainda não executada; WebRTC inclui slice iOS Simulator arm64 segundo seu Info.plist. |
| Simulador da futura execução | Ainda não preparado | Provar que o executor de testes Xcode usa o UDID do device set do worktree. simctl --set sozinho não basta. |
| Assinatura para simulador | Estratégia ainda não testada | Projeto contém team IDs, bundle IDs e capabilities herdados; validar overrides sem autenticação Apple. |
| Contenção de saída de rede | Ainda não demonstrada | Definir mecanismo restrito à sessão e prová-lo antes de abrir o app; não desativar rede/VPN do host. |
| Teste observável do onboarding | Ainda não implementado | A suíte atual lança o app e captura screenshot/performance, sem asserções da tela esperada. |
| Build, ligação e execução | Não executados | Faltam produtos inspecionados e resultado de testes reais. |
| Repetição e Verifier | Pendentes da implementação | Exigem o último commit e outra sessão limpa. |

As versões acima são observações locais datadas, não garantia de compatibilidade. O procedimento deverá revalidá-las antes da execução.

## Rota recomendada e alternativa

**Recomendada, condicionada à origem comprovada:** compilar Swift e ligar bibliotecas oficiais do núcleo vinculadas ao fonte da base. Registrar URL imutável, evidência do vínculo, hashes e plataforma. Não basta calcular um hash depois de baixar um ZIP desconhecido. Se houver transformação mac2ios, registrar ferramenta, commit, entrada, comando e hashes antes/depois.

**Alternativa:** reconstruir o núcleo do fonte com o conjunto fixado pelo upstream. flake.nix seleciona ghc963, isto é, GHC 9.6.3; flake.lock fixa Haskell.nix, Nixpkgs e mobile-core-tools. O commit de mobile-core-tools é 4dcb77d5ea896d749381806dfab5358851b08951. A preparação e compatibilidade desse conjunto no macOS/Xcode atual ainda não foram testadas. Não instalar GHC mais recente como substituição presumida.

Se a rota recomendada não puder satisfazer a proveniência e a ABI, registrar o bloqueio e dimensionar a alternativa antes de executá-la. A especificação não promete que um artefato oficial compatível já está disponível.

## Organização local

Manter o clone taverna-app e seu diretório irmão taverna-app-worktrees na raiz Projects definida pelo proprietário. O plano atual usa somente arquivos textuais e não prepara recursos de execução.

Na futura implementação, cada sessão terá seu worktree e uma árvore de estado semelhante a:

```text
.build/
  session.json
  downloads/
  libraries/
  SourcePackages/
  package-cache/
  DerivedData/
  SimulatorDevices/
  attempts/<id>/
    logs/
    results/
    receipt.json
```

O Design deve verificar todos os caminhos efetivamente graváveis, inclusive caches de ferramentas, antes de prometer isolamento. O compilador e os runtimes instalados são compartilhados; produtos e estado das sessões são separados. As bibliotecas podem exigir ajustes de search paths do projeto; não criar dependência de Downloads nem copiar arquivos para outro checkout.

Não executar automaticamente scripts/ios/download-libs.sh, prepare.sh ou prepare-x86_64.sh: a versão examinada usa Downloads compartilhado e remove diretórios Libraries. A adaptação futura deve preservar a base e confinar as entradas.

## Prova de aceitação

O registro por tentativa reunirá identificação do fonte e das entradas, versões, comandos, saídas por etapa, produtos e contagem de testes. A evidência bruta fica no estado ignorado; o relatório versionado contém apenas dados técnicos sanitizados.

A execução deve confirmar Get started visível/habilitado, tocar no botão e encontrar Your profile. Não enviar o formulário, criar identidade nem convidar pessoas. Essa prova confirma o início da interface e a ligação do app ao núcleo real; não comprova funções do protocolo nem mensagens ponta a ponta.

A segunda sessão parte do mesmo commit e manifesto, sem produtos/caches da primeira. O Verifier verifica os critérios e testa que as checagens rejeitam, pelo menos, hash adulterado, plataforma errada, ausência de produto apesar de saída de sucesso e execução sem o teste obrigatório. Falhas são injetadas em cópias isoladas, preservando o worktree real.

CI Foundation continua comprovando a fundação. Os novos checks automatizáveis precisam de CI própria ou extensão delimitada da existente. Uma suíte Python verde não será apresentada como compilação iOS feita pelo GitHub. A prova do build neste marco será a execução local no MacBook.

## Ordem de conclusão

| Resultado | Dependência para avançar |
| --- | --- |
| Plano revisado | Especificação e contexto com escolhas explícitas. |
| Entradas qualificadas | Origem, revisões, hashes, licença e ABI verificados. |
| Sessão apta a executar | Destino isolado, política de assinatura e contenção de rede demonstrados. |
| Primeira prova | Produtos reais do scheme e testes iOS com asserções passando. |
| Prova repetida | Segunda execução limpa do mesmo commit/manifesto. |
| Entrega concluída | CI e Verifier aprovados no commit final; documentação com alcance e limites. |

O proprietário não precisa encontrar senha da VPS ou credencial Apple para esta proposta de simulador. Se surgir uma necessidade real de privilégio, contrato ou conta, o relatório identificará a causa antes de qualquer ação correspondente.

## Fontes e consultas

- [Proveniência da base](../../../docs/taverna/provenance.md) e [ambientes](../../../docs/taverna/environments.md).
- [Guia iOS upstream no fork](../../../apps/ios/README.md), [projeto Xcode](../../../apps/ios/SimpleX.xcodeproj/project.pbxproj) e [Package.resolved](../../../apps/ios/SimpleX.xcodeproj/project.xcworkspace/xcshareddata/swiftpm/Package.resolved).
- [flake.nix](../../../flake.nix), [flake.lock](../../../flake.lock), [download-libs.sh](../../../scripts/ios/download-libs.sh), [prepare.sh](../../../scripts/ios/prepare.sh) e [prepare-x86_64.sh](../../../scripts/ios/prepare-x86_64.sh).
- [Testes existentes](../../../apps/ios/Tests%20iOS/Tests_iOS.swift) e [teste de lançamento](../../../apps/ios/Tests%20iOS/Tests_iOSLaunchTests.swift).
- [Tela inicial](../../../apps/ios/Shared/Views/Onboarding/SimpleXInfo.swift), [criação de perfil](../../../apps/ios/Shared/Views/Onboarding/CreateProfile.swift) e [inicialização do app](../../../apps/ios/Shared/SimpleXApp.swift).
- [Apple TN2339: xcodebuild e testes por linha de comando](https://developer.apple.com/library/archive/technotes/tn2339/_index.html). A nota documenta a ferramenta; não prova compatibilidade deste fork com Xcode 27.1.
- Consultas locais: xcodebuild -version; xcodebuild -help; xcrun simctl help; xcrun simctl list runtimes --json; detecção de toolchains pelo PATH e inspeção dos diretórios Libraries. Nenhuma compilação ou download de biblioteca foi feito nesta etapa.
