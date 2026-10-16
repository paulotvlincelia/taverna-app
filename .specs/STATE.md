# STATE

## Decisions

As decisões canônicas ficam em [docs/taverna/decisions](../docs/taverna/decisions/README.md). Este arquivo mantém somente o handoff. O primeiro build iOS foi integrado pelo PR #10; suas evidências e limitações permanecem nos artefatos da feature ios-first-build.

## Handoff

- Feature: invitation-only; spec aprovada no PR #11, issue #7. A prova AP-01..07 entrou pelo PR #14 em da9136c541dd4ca06da0269dfd12355a360e0d3b; issue #12 encerrada. Os 34 requisitos do produto seguem Pending.
- Método: TLC Spec Driven; retomada para desenho da integração, com spec/contexto preservados. O proprietário pediu continuar e preferiu solução simples. A rota A foi aprovada somente para o experimento; o novo desenho não inventa aprovação de arquitetura de produção.
- Estado: entry-design.md propõe adaptador SOCKS nativo sobre a ponte, admissão pequena com estado transacional e entrada visual depois do DESIGN.md. Código e fontes oficiais fundamentam a proposta; viabilidade do adaptador iOS/extensões permanece NOT RUN.
- Próximo passo: verificar e publicar este desenho documental; confirmar A1 e a interação administrativa proposta antes das tarefas formais/implementação. Primeiro gate técnico será transporte nativo real, incluindo falhas/fallback e os três targets; não reutilizar receipt offline do primeiro build como prova de rede.
- Ownership: Codex, harness e integrador; branch codex/invitation-entry-plan; worktree irmão taverna-app-worktrees/invitation-entry-plan. Escopo: entry-design.md, README, roadmap e este handoff. Verifier só escreve relatório independente.
- Recursos: somente pesquisa read-only e snapshots públicos em .build/invitation-entry, ignorados; nenhum estado de simulator, container ou provider alterado. Preservar worktrees/evidências e o preview existentes.
- Limites: não implementar telas antes do DESIGN.md aprovado; produção, DNS, ambientes administrativos externos, credenciais, app, CI, locks e licenças preservados. Nenhum token, chave ou URL de convite completa no Git.
