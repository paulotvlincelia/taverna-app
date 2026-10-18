# Qualificação do ambiente NSE

**Estado em 2026-10-18: BLOCKED_ENVIRONMENT.** A retomada preserva NP-07: execução do processo efetivo e política de transporte aplicada antes de iniciar ou reativar o núcleo. Build, notificação exibida ou chamada manual de `NotificationService` dentro do app não comprovam esse critério.

## Aprovação visual

O proprietário aprovou a direção visual InnerMesh do [PR #20](https://github.com/paulotvlincelia/taverna-app/pull/20), HEAD `67aed65c7789167db11c3a5e047b28565d3d2d0a`, em 2026-10-18. A aprovação encerra a pausa para análise visual. Nenhum merge foi autorizado. Assets de distribuição continuam BLOCKED; este registro não implementa identidade, telas ou renomeação.

## Evidência disponível

O build limpo `share-final-clean`, no commit `4e0051008da46e3fdf9a1c3d3918f554d41e832f`, contém os quatro produtos de simulador, incluindo `SimpleX NSE.appex`. Os hashes continuam iguais ao recibo. A assinatura do host é ad hoc, com bundle ID herdado `chat.simplex.app`; o artefato inspecionado não declara `aps-environment`, `application-identifier` ou identificador de equipe. O inventário local não qualifica assinatura, provisionamento nem entrega remota APNs.

A extensão declara `com.apple.usernotifications.service` e `NotificationService` como classe principal. O código NSE de início/reativação ainda não aplica `TavernaCoreTransport`; sua integração e prova pertencem a T4. O recorte app/Share não qualifica a NSE por equivalência.

## Caminho documentado pela Apple

As [notas do Xcode 14](https://developer.apple.com/documentation/xcode-release-notes/xcode-14-release-notes) descrevem APNs Sandbox no simulador compatível e distinguem recursos de push remoto, incluindo NSE, das notificações simuladas por arquivo ou `simctl push`. As [notas do Xcode 11.4](https://developer.apple.com/documentation/xcode-release-notes/xcode-11_4-release-notes) registram que `mutable-content` não é honrado na simulação local. A [documentação de NSE](https://developer.apple.com/documentation/usernotifications/modifying-content-in-newly-delivered-notifications) exige alerta e `mutable-content: 1` no payload remoto. Exibir um alerta não prova que `didReceive` executou.

O [Push Notification Console](https://developer.apple.com/documentation/usernotifications/testing-notifications-using-the-push-notification-console) é uma opção oficial para enviar a notificação de teste, com topic e token próprios. A identidade de teste e a entrega remota ainda precisam ser qualificadas. Nenhuma chamada APNs foi feita nesta retomada.

## Preparação proposta para desbloquear

1. A prova exige uma identidade de desenvolvimento apta a APNs Sandbox; este documento não qualifica condições administrativas.
2. APNs Sandbox, provisionamento e credenciais ficam fora do escopo atual de [native-proof.md](native-proof.md) e exigem um gate separado.
3. Usar identidade de desenvolvimento e host de qualificação isolados. Não usar o topic do upstream nem alterar os identificadores do produto, App Group, keychain ou entitlements. Fontes, produtos, dados e evidências pertencem ao worktree; a entrega remota é uma dependência externa explícita.
4. Qualificar primeiro uma entrega remota com payload fictício, sem mensagens ou participantes reais e sem som. Capturar a chamada efetiva de `didReceive`, PID e vínculo com o binário/commit da extensão. Um controle mínimo de ativação é somente prova de ambiente, sem PASS de transporte.
5. Implementar e provar na extensão compilada das fontes do produto, instalada no host de teste e acionada pelo sistema, a mesma política gerenciada. Uma classe instanciada dentro do host ou a extensão mínima de controle não substitui essa execução. Exigir: ausência/stop negam start e resume; configuração anterior ao comando real; SMP/XFTP da fixture autorizada, sentinela e nenhum fallback direto. Identidade, CA e dados da fixture são novos por rodada. O processo precisa de contenção comprovada antes do main; os serviços iOS do sistema permanecem fora dessa contenção e devem ser discriminados no relatório.
6. Repetir build e gates aplicáveis, executar Verifier independente e sensor. T4, T6 e NP-01..08 só podem ser concluídos quando suas obrigações agregadas forem atendidas. CI e revisão de publicação continuam exigidas; merge permanece proibido.

Este documento não prova APNs, NSE efetiva, aparelho, distribuição ou uso sensível. As tarefas pendentes continuam abertas.
