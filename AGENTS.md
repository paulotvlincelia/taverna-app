# Desenvolvimento da Taverna

Autoridade comum para Codex, Claude e outros agentes. Leia README.md, CONTRIBUTING.md e docs/taverna/provenance.md. O GitHub contém as instruções necessárias.

Antes de planejar ou implementar, carregue efetivamente a skill TLC e suas referências da etapa: .agents/skills/tlc-spec-lean/SKILL.md para escopo delimitado sem checklist anterior; .agents/skills/tlc-spec-driven/SKILL.md para múltiplas dependências ou tarefas existentes. Registre a escolha. Lean usa profile standard. Preservar critérios aprovados e realizar verificação independente após o último commit. Artefatos por feature em .specs/features; decisões públicas em docs/taverna/decisions.

Uma branch e um worktree exclusivos por sessão, Git nativo. Registre responsável, harness, escopo de arquivos e integrador na issue/PR; ambientes e simuladores isolados conforme docs/taverna/environments.md. Não reverta mudanças de outros agentes. Integrador único para CI, AGENTS, licenças, locks e handoff. Conflito ou arquivos não integrados impedem remoção; sem limpeza forçada.

Nunca publicar chaves, convites reais, participantes, conversas, endereços administrativos ou histórico operacional. Fixtures fictícias. Código de terceiros preserva licença e atribuição. Assets restritos permanecem bloqueados para distribuição customizada até inventário/permissão aprovados. Não alterar criptografia/protocolos como efeito de branding.

CI sem segredos e sem mutações live. Credenciais Apple/APNs, release, gastos, produção e contas exigem autorização específica. Plano aprovado autoriza commits locais; push/merge dependem da autorização correspondente, CI e Verifier no último commit. Nenhum PASS local significa ambiente iOS ou operação prontos.

Commits atômicos Conventional Commits. Execute os checks de CONTRIBUTING.md, preserve testes e asserções, registre comando/commit/resultado/limites. As instruções e ferramentas necessárias ao desenvolvimento devem estar versionadas ou documentadas neste repositório.

Antes de qualquer push ou escrita de título/corpo/comentário/review/descrição/Project, usar o fluxo de publicação atribuído ao mantenedor: conferir repo canônico, ID, visibilidade, todos os commits enviados e classificação do conteúdo. Revisão independente deve corresponder ao digest exato. Classificação desconhecida bloqueia publicação. Não copiar inventários, restrições de máquinas/serviços externos ou narrativas administrativas para exemplos, planos, descrições e relatórios públicos. A CI detecta padrões genéricos depois de envio e não substitui o gate anterior à publicação.

Após uma limpeza de histórico, branches antigas precisam de reconciliação antes de publicar. Não mesclar ancestrais substituídos para contornar a reescrita; preservar trabalho local e seguir o mapa de reconciliação fornecido pelo mantenedor.
