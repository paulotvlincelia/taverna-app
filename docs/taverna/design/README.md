# Referências da identidade

Proposta visual 0.1.0, em revisão pelo proprietário. [DESIGN.md](../../../DESIGN.md) é a autoridade da proposta. O app ainda não usa esta identidade.

- [Prancha](reference.svg): Confirmar convite, Conversas e Conversa em claro/escuro, com conteúdo fictício. O símbolo de porta é um estudo.
- [Tokens](tokens.json): cores semânticas sRGB, sem uso automático em runtime.
- [Contraste medido](contrast.json): 46 pares opacos; não certifica acessibilidade do app.
- [Calculador](measure_contrast.py): Python 3.12/biblioteca padrão; saída JSON e exit 1 se algum par declarado não atingir o mínimo.

A prancha não cobre interação, VoiceOver, texto ampliado ou execução no iOS. Essas provas permanecem exigidas na implementação. O gate de assets de distribuição continua bloqueado.

A prancha SVG e os dados desta proposta são originais do projeto Taverna, produzidos com assistência de Codex, e ficam sob [Creative Commons Attribution 4.0 International](https://creativecommons.org/licenses/by/4.0/), com atribuição a Taverna. Não incluem imagens ou fontes copiadas do SimpleX/Apple. O SVG usa texto com fontes do sistema de quem o visualizar. O ícone final precisa de exportação e inventário próprios; estes arquivos são referências documentais.
