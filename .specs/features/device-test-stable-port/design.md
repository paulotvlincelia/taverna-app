# Porte do ensaio SMP

A branch começa em stable. O ensaio usa as três fontes Swift do listener, as extensões da fixture local e o inicializador dedicado do núcleo. A projeção de build inclui o listener no framework do host técnico. O fluxo comum mantém os targets e a inicialização existentes.

| Opção | Consequência |
| --- | --- |
| Publicar a branch de revisão local | Arrastaria histórico de entregas distintas e documentos operacionais. |
| Reproduzir os commits de todos os laboratórios | Incluiria implementações e provas além do host técnico. |
| Portar as dependências do host e o patch de inicialização | Permite revisar o comportamento e a origem dos artefatos na base atual. |

O listener limita o destino ao relay fictício da fixture. A leitura técnica exige o handshake SMP com a identidade autorizada e o SOCKS autenticado em loopback. A prova exercita revogação, troca e histórico depois de reiniciar o núcleo. O recibo de build verifica a associação do pacote ao fonte. A execução usa dados fictícios e simulador isolado.
