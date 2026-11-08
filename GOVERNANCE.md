# Governança de design

**Acompanha [DESIGN.md](DESIGN.md). Versão 0.5.2 · 2026-10-18.**

Produto: **InnerMesh**. Prefixo de tokens e recursos no código: `InnerMesh/`. Documentação de design em `docs/innermesh/`. Arquivos novos de design entram já em `docs/innermesh/design/`; os herdados (`assets.md`, `asset-policy.json`) continuam em `docs/taverna/` até a fase 6 do plano de remediação, e os links abaixo para eles só resolvem depois dela.

Este arquivo reúne o que não é decisão visual: aprovação, licenças, assets, distribuição e provas. O DESIGN.md define a aparência e o comportamento; este define como a identidade pode entrar no app.

## Aprovação

A aprovação do anfitrião (`owner` nas specs) autoriza a **direção visual**. Implementação, acessibilidade em execução, licença de cada asset e distribuição têm gates próprios. O app ainda usa a interface herdada; nenhuma tela da proposta está implementada.

**Antes de implementar:** o anfitrião aprova direção, símbolo e navegação; o recorte de transporte exigido passa (fase 5 do plano de remediação: prova da NSE); existe spec TLC para o fluxo; a primeira versão tem um único círculo; tarefas apontam para seções e tokens do DESIGN.md. Aprovar a proposta não aprova distribuição nem produção.

**Evidências revisadas:** [decisões do proprietário](.specs/features/invitation-only/context.md), [README](README.md), [inventário de assets](docs/innermesh/assets.md), [política de distribuição](docs/innermesh/asset-policy.json), `apps/ios/Shared/Theme/Theme.swift`, `apps/ios/SimpleXChat/Theme/ThemeTypes.swift`, catálogos de assets e pontos de entrada do app, Share Extension e NSE. Temas e componentes upstream são reutilizáveis como código; isso não aprova imagens ou aparência licenciadas separadamente.

## Assets e licenças

O [gate de assets](docs/innermesh/asset-policy.json) continua **BLOCKED**, com a lista de assets de distribuição aprovados vazia.

- Referências originais da proposta: documentação, CC BY 4.0, atribuição a InnerMesh. Não são assets finais.
- Código mantém sua licença. Não inferir licença de imagem a partir da AGPL do código.
- Fontes Apple: usadas só via APIs do sistema. Não embutir arquivos San Francisco em exports públicos. Documentação web usa `system-ui`; exports vetoriais finais precisam de autorização ou letras originais.
- SF Symbols: via API, verificando disponibilidade e termos no SDK suportado. Nunca exportar o catálogo para o repositório.
- Ilustrações futuras: origem e licença por arquivo.
- Fotos e avatares de participantes: dados locais, nunca fixtures nem assets da marca. Exemplos usam só iniciais fictícias.
- Sem downloads automáticos de imagens, analytics, fontes ou CDN. Referências visuais são locais.

**Exceção documental aprovada pelo proprietário em 2026-10-18:** o protótipo recebido em `docs/innermesh/design/prototype/` é preservado como referência, sem execução nesta entrega. Seu `support.js` carrega React, ReactDOM e Babel de `unpkg.com`; portanto, ele não é autocontido nem tem operação offline comprovada. Esta exceção permite somente registrar os arquivos recebidos e não autoriza executar o protótipo, baixar dependências ou usar CDN no app. A regra acima permanece válida para a implementação.

**Pacote final do símbolo:** SVG mestre com caminhos, PDF vetorial para os catálogos, PNGs de referência, exportação para o Xcode/Icon Composer adotado. Registrar autor, licença, versão e SHA-256 por arquivo no inventário.

| Superfície herdada | Ação |
| --- | --- |
| AppIcon, ícones e nomes do app, Share e notificações | Substituir por exportações InnerMesh aprovadas; testar tamanhos e localização |
| `apps/ios/Shared/Assets.xcassets`, `SimpleXAssets.xcassets` | Inventariar cada imagem usada; substituir ou comprovar permissão |
| Onboarding, links, ajuda, exemplos | Ajustar nome e texto; remover promoção upstream; preservar atribuição em informações legais |
| Ícones de dependências e mídia em docs | Registrar origem, licença, uso e substituição |

## Restrições de implementação

- Reutilizar SwiftUI e UIKit necessários. Share Extension segue a mesma linguagem sem duplicar recursos pesados; NSE não tem interface própria.
- Não alterar bundle IDs, grupos de Keychain, entitlements ou criptografia como efeito da aprovação visual.
- `tokens.json` é referência de design, não um carregador de tema.
- Definir migração de preferências de tema e revisar o efeito nos três targets antes de substituir o sistema upstream.
- Não habilitar temas ou importações que eliminem legibilidade ou estados.

## Contraste

O script [measure_contrast.py](docs/innermesh/design/measure_contrast.py) recalcula os pares declarados:

```bash
python3.12 docs/innermesh/design/measure_contrast.py
```

Pares de texto ≥ 4,5:1; bordas e foco ≥ 3:1. O [relatório](docs/innermesh/design/contrast.json) registra os valores medidos, sem arredondar na comparação com o limiar. A v0.5 registra 17 pares medidos (DESIGN 5.1), incluindo `text/outgoing`, `textSecondary/surfaceMuted` e `border/canvas`. A paleta alternativa bordô (DESIGN 5.1.2) precisa de medição completa, inclusive contra `danger`, antes de qualquer adoção. Os números cobrem cores opacas; transparência, imagens, materiais do sistema e interface renderizada precisam de revisão própria. Isto não é certificação de acessibilidade.

## Provas após implementação

- **Revisão visual obrigatória:** Confirmar convite (antes e depois da entrada no círculo), Seletor de círculo, Conversas e Conversa × claro/escuro × escala padrão/maior escala de acessibilidade (≥ 12 combinações). Incluir offline, convite inválido, acesso retirado (com e sem outros círculos), papéis anfitrião e membro, Reduce Motion na entrada no círculo, e Share Extension com escolha de círculo.
- **Capturas** com dados fictícios, versão, SHA e target registrados.
- **Contraste** dos pares renderizados; VoiceOver, foco, toque e texto ampliado em iPhone.
- **Zero** tokens, convites ou conteúdo real em logs.
- Nenhum critério aprovado só por screenshot. Testes de autorização verificam efeitos reais.
- CI e Verifier independente no último commit antes da integração. BRAND-02 e distribuição seguem pendentes até implementação e prova.

## Rastreabilidade

Contrato completo em [BRAND-01..03 e Contrato do DESIGN.md](.specs/features/invitation-only/spec.md#contrato-do-designmd). Referências de plataforma: [Apple Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility), [Apple App icons](https://developer.apple.com/design/human-interface-guidelines/app-icons), [W3C contraste mínimo](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html). As regras são propostas do InnerMesh, sem alegar endosso Apple ou SimpleX.
