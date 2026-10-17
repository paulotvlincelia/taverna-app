# Proveniência e alterações

Base adotada em 2026-10-16: [simplex-chat/simplex-chat](https://github.com/simplex-chat/simplex-chat), branch stable, commit `479548ee53ffb73db73841e77acbeee5a78dbbd5`. Este repositório é um fork público independente.

A fundação altera README, documentação/contribuição, entradas de agentes, CI e ferramentas de preflight. Preserva LICENSE, a licença dos assets e o fonte do app/núcleo. O README original está em README.upstream.md. As skills TLC têm suas atribuições nos NOTICE.md e, quando presente, ORIGIN.json de cada skill; não fazem parte da autoria original SimpleX.

Workflows build.yml, cla.yml, reproduce-schedule.yml e web.yml foram preservados como referência fora de .github/workflows. Não habilitar publicação, assinatura ou deploy herdados sem revisão própria. A CI Foundation usa fixtures e não contém credenciais.

Atualizações upstream entram por PR, registrando SHA anterior/novo, mudanças relevantes, licenças, dependências e provas. Antes de um binário Taverna ser distribuído, o release precisa registrar exatamente seu fonte correspondente, instruções e modificações, mantendo os avisos AGPL exigidos. A fundação não distribui um binário.


O primeiro build iOS acrescenta ferramentas locais de preparo/sessão/prova, manifesto fixado e teste do onboarding. A única correção de compatibilidade no código do app é um alias do tipo SwiftUI.State em ChatView, preservando a composição State<ObservedObject<Chat>> diante do macro do SDK 27.1. Os testes herdados continuam disponíveis; o perfil first-build aprovado não expande a matriz integral e executa todos os quatro métodos/asserts. Não há alteração de protocolo, criptografia, locks ou fluxo de mensagens. O [guia](ios-build.md) registra os comandos, e a [execução](../../.specs/features/ios-first-build/execution.md) identifica provas e limites. Os artefatos permanecem locais; essa prova não autoriza distribuir os assets herdados.

## Referências após a reconciliação documental

Em 2026-10-16, o histórico próprio posterior à base upstream foi reconciliado para generalizar a documentação. A base upstream mantém o mesmo SHA. Todos os blobs não documentais de cada commit mapeado foram preservados; a reescrita muda SHAs e invalida assinaturas dos commits afetados.

A implementação que as duas reproduções iOS aprovaram originalmente em `6ea482bd4a1912d8eef52904d930c7f6c57bf746` corresponde agora ao commit `65dd2bc8afe0eedc58d99c779bd831c5b880065a` no histórico limpo. Esse é o ponto correspondente para consultar ou reproduzir o código técnico daquela prova. Os relatórios anteriores conservam o SHA original como proveniência. A comparação dos blobs comprova preservação do fonte; nenhuma nova execução iOS é alegada pela reconciliação.

Use uma base remota atualizada para novas entregas. Preserve seu delta local e reconcilie-o em um worktree novo antes de publicar; mesclar uma base anterior pode reintroduzir o histórico substituído.
