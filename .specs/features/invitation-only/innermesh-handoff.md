# Registro documental InnerMesh 0.5.2

Status: registro local verificado; exceção documental de CDN autorizada; publicação pendente. Data: 2026-10-18.

## Escopo e método

TLC Spec Driven, recorte documental de BRAND-01 de um plano existente. O pedido do proprietário e a seção “Leia antes de qualquer ação” do [HANDOFF](../../../docs/innermesh/design/HANDOFF.md) governam esta entrega. Não implementa produto nem encerra a feature invitation-only.

Etapa atômica: registrar o pacote conforme o mapa, aplicar a correção de capacidade autorizada, verificar contraste/links/escopo e fazer commit documental. Depois: Verifier independente no commit e publicação revisada em PR para stable. Nenhuma integração autorizada por este registro.

Responsável, harness e integrador: Codex. Branch exclusiva codex/identity-design-draft, worktree identity-design-draft. Escopo: DESIGN.md, GOVERNANCE.md, docs/innermesh/design, este registro, relatório independente e handoff de .specs/STATE.md; fixture test_foundation.py autorizada para incluir os novos destinos na cópia temporária. Ambientes e relatórios brutos em .build, sem compartilhar estado gravável.

## Critérios desta entrega

1. WHEN o pacote for registrado THEN os 51 arquivos SHALL ocupar os destinos do mapa, sem alterações além da correção de capacidade e da exceção documental de CDN autorizadas pelo proprietário.
2. WHEN a primeira versão indicar capacidade THEN a documentação SHALL preservar 20 convidados ativos além do anfitrião, 21 pessoas no total, exibindo “N de 21 membros”.
3. WHEN measure_contrast.py for executado THEN o JSON gerado SHALL ser idêntico ao do pacote e todos os 17 pares nos dois temas SHALL passar os limiares declarados.
4. WHEN os links dos três documentos forem conferidos THEN somente os dois destinos de assets previstos para a fase 6 SHALL permanecer pendentes; qualquer outro caminho ou âncora inválido SHALL falhar a verificação.
5. WHILE esta entrega registrar referências THEN apps, CI, docs/taverna e identificadores técnicos SHALL permanecer inalterados; tools admite somente a inclusão de GOVERNANCE.md e docs/innermesh na fixture de cópia autorizada pelo proprietário em relação ao início desta entrega; o gate de assets SHALL continuar BLOCKED, com lista aprovada vazia.
6. WHEN a entrega for publicada THEN o commit SHALL ter revisão independente, CI e pacote de publicação inspecionado; o PR SHALL apontar para stable, sem implementar ou integrar a UI.

## Resultado local

- Contraste: 17 pares, 34 medições, 34 PASS; JSON e bytes idênticos ao pacote. SHA-256: 51241208708f0ba50a7c806cc8b5519d930b2992fcbd183915b631d14901026e.
- Links Markdown: 17 ocorrências relativas; 14 resolvidas, três ocorrências esperadas para dois destinos em GOVERNANCE.md: `docs/innermesh/assets.md` e `docs/innermesh/asset-policy.json`. O anchor do contrato da spec resolve. HANDOFF.md usa caminhos em código, sem links Markdown relativos.
- Assets e protótipos permanecem referências documentais; nenhuma inclusão em catálogos do app.
- Contraste não comprova acessibilidade renderizada, implementação, aparelho ou distribuição.

A suíte Foundation teve 77/78 PASS antes da adequação: a fixture não copiava GOVERNANCE.md e docs/innermesh, embora o checker real resolvesse os links. O proprietário autorizou acrescentar somente esses dois destinos ao setUp. Nenhuma asserção foi modificada; o restante de tools permanece intacto.

## Ajustes e pendências

Os ajustes autorizados ao conteúdo recebido são: capacidade de 20 convidados mais anfitrião, 21 no total, em DESIGN.md e HANDOFF.md; exceção documental de CDN em GOVERNANCE.md. A spec aprovada permanece intacta. A proposta multicículos e limite configurável segue como referência futura, sem implementação. Protótipos e capturas foram preservados byte a byte; exemplos de limites configuráveis neles não alteram a primeira versão.

O pacote informa que a captura escura de Gestão → Membros foi retirada por ser duplicada. Sua reexportação segue pendente; a captura clara existe. A contagem de membros no cartão de convite continua decisão pendente. A seção “Arquivos” do HANDOFF cita DESIGN 0.5.1, embora os documentos entregues sejam 0.5.2; texto preservado por não afetar esta entrega.

O plano de remediação citado no pacote não foi localizado nos documentos locais consultados. Sua numeração não foi reconstruída nem alterada; o pré-requisito de prova efetiva da NSE antes de UI foi preservado, coerente com o gate técnico ainda aberto.

O publicador atual recusa binários sem adaptador de inspeção, incluindo as 25 capturas PNG recebidas. Esta entrega não modifica o publicador e não autoriza contornar esse controle. O bloqueio deve ser resolvido antes de qualquer publicação deste pacote completo.

O Verifier independente examinou o commit 21b58fecf88ac7e53edbc3dddf1e7790799208cb: critérios locais 1–5 PASS, 78/78 testes, três mutantes detectados; publicação NOT READY. O conflito de CDN recebeu decisão explícita do proprietário em 2026-10-18: preservar o protótipo byte a byte e registrar a exceção, sem executá-lo. GOVERNANCE.md agora explicita as três dependências externas e não afirma que o protótipo funciona offline. Esta correção documental exige nova revisão no commit que a contém. A autorização para suporte restrito a PNG no publicador ainda está pendente; nenhum push ou CI novo foi executado.

## Comandos

```sh
python3 docs/innermesh/design/measure_contrast.py
python3.12 -m unittest discover -s tools/taverna/tests -q
python3.12 tools/taverna/check_foundation.py
python3.12 -m compileall -q tools/taverna
git diff --check
```

A comparação do JSON usa o contrast.json original do arquivo recebido, antes da execução do script. A verificação complementar local em .build/innermesh-handoff/verify_handoff.py compara arquivos com o ZIP, aplica somente as substituições autorizadas para o valor esperado, valida links e o gate BLOCKED. Seus relatórios são locais. O Verifier confere os mesmos resultados independentemente.

## Arquivos recebidos e destinos

- `docs/innermesh/design/tokens.json`
- `docs/innermesh/design/contrast.json`
- `docs/innermesh/design/assets/symbol/innermesh-symbol-medium-dark.svg`
- `docs/innermesh/design/assets/symbol/innermesh-symbol-mono-onprimary.svg`
- `docs/innermesh/design/assets/symbol/innermesh-symbol-medium-light.svg`
- `docs/innermesh/design/assets/symbol/innermesh-symbol-invite-light.svg`
- `docs/innermesh/design/assets/symbol/innermesh-symbol-outside-dark.svg`
- `docs/innermesh/design/assets/symbol/innermesh-symbol-small-light.svg`
- `docs/innermesh/design/assets/symbol/innermesh-symbol.js`
- `docs/innermesh/design/assets/symbol/innermesh-symbol-mono-ink.svg`
- `docs/innermesh/design/assets/symbol/innermesh-symbol-outside-light.svg`
- `docs/innermesh/design/assets/symbol/innermesh-symbol-large-dark.svg`
- `docs/innermesh/design/assets/symbol/innermesh-symbol-invite-dark.svg`
- `docs/innermesh/design/assets/symbol/innermesh-symbol-small-dark.svg`
- `docs/innermesh/design/assets/symbol/innermesh-symbol-large-light.svg`
- `docs/innermesh/design/assets/app-icon/AppIcon-dark-1024.svg`
- `docs/innermesh/design/assets/app-icon/AppIcon-tinted-1024.svg`
- `docs/innermesh/design/assets/app-icon/AppIcon-light-1024.svg`
- `docs/innermesh/design/prototype/innermesh-symbol.js`
- `docs/innermesh/design/prototype/InnerMesh App.dc.html`
- `docs/innermesh/design/prototype/InnerMesh Exploracoes.dc.html`
- `docs/innermesh/design/prototype/support.js`
- `docs/innermesh/design/HANDOFF.md`
- `GOVERNANCE.md`
- `docs/innermesh/design/screenshots/escuro/08-conversa-grupo.png`
- `docs/innermesh/design/screenshots/escuro/03-convite-confirmado.png`
- `docs/innermesh/design/screenshots/escuro/10-ajustes.png`
- `docs/innermesh/design/screenshots/escuro/09-informacoes-grupo.png`
- `docs/innermesh/design/screenshots/escuro/01-entrada.png`
- `docs/innermesh/design/screenshots/escuro/02-convite.png`
- `docs/innermesh/design/screenshots/escuro/04-convite-indisponivel.png`
- `docs/innermesh/design/screenshots/escuro/11-gestao-convites.png`
- `docs/innermesh/design/screenshots/escuro/06-conversas.png`
- `docs/innermesh/design/screenshots/escuro/13-acesso-retirado.png`
- `docs/innermesh/design/screenshots/escuro/05-perfil.png`
- `docs/innermesh/design/screenshots/escuro/07-seletor-de-circulo.png`
- `docs/innermesh/design/screenshots/claro/08-conversa-grupo.png`
- `docs/innermesh/design/screenshots/claro/03-convite-confirmado.png`
- `docs/innermesh/design/screenshots/claro/10-ajustes.png`
- `docs/innermesh/design/screenshots/claro/09-informacoes-grupo.png`
- `docs/innermesh/design/screenshots/claro/01-entrada.png`
- `docs/innermesh/design/screenshots/claro/02-convite.png`
- `docs/innermesh/design/screenshots/claro/04-convite-indisponivel.png`
- `docs/innermesh/design/screenshots/claro/11-gestao-convites.png`
- `docs/innermesh/design/screenshots/claro/06-conversas.png`
- `docs/innermesh/design/screenshots/claro/13-acesso-retirado.png`
- `docs/innermesh/design/screenshots/claro/05-perfil.png`
- `docs/innermesh/design/screenshots/claro/07-seletor-de-circulo.png`
- `docs/innermesh/design/screenshots/claro/12-gestao-membros.png`
- `DESIGN.md`
- `docs/innermesh/design/measure_contrast.py`
