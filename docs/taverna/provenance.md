# Proveniência e alterações

Base adotada em 2026-10-16: [simplex-chat/simplex-chat](https://github.com/simplex-chat/simplex-chat), branch stable, commit `479548ee53ffb73db73841e77acbeee5a78dbbd5`. Este repositório é um fork público independente.

A fundação altera README, documentação/contribuição, entradas de agentes, CI e ferramentas de preflight. Preserva LICENSE, a licença dos assets e o fonte do app/núcleo. O README original está em README.upstream.md. As skills TLC têm suas atribuições nos NOTICE.md e, quando presente, ORIGIN.json de cada skill; não fazem parte da autoria original SimpleX.

Workflows build.yml, cla.yml, reproduce-schedule.yml e web.yml foram preservados como referência fora de .github/workflows. Não habilitar publicação, assinatura ou deploy herdados sem revisão própria. A CI Foundation usa fixtures e não contém credenciais.

Atualizações upstream entram por PR, registrando SHA anterior/novo, mudanças relevantes, licenças, dependências e provas. Antes de um binário Taverna ser distribuído, o release precisa registrar exatamente seu fonte correspondente, instruções e modificações, mantendo os avisos AGPL exigidos. A fundação não distribui um binário.
