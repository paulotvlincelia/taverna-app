# Porte do ensaio SMP

O trabalho usa `tlc-spec-driven` porque a revisão cruza o núcleo iOS, o host Swift e a fixture de rede. A branch parte de `stable`. O projeto Xcode gerado para o ensaio inclui as três fontes Swift do listener e ativa `TAVERNA_DEVICE_TEST` no framework. O fluxo comum mantém os targets e a inicialização existentes.

O núcleo técnico confirma a rota única com um handshake SMP pelo SOCKS autenticado em loopback. O host só inicia o chat depois de verificar a configuração efetiva e a autorização da fixture. Os bancos e o item do Keychain do ensaio têm nomes próprios.

## Provas locais

- Rodar `python3.12 -m unittest discover -s tools/taverna/tests -v` e `python3.12 tools/taverna/check_foundation.py`.
- Compilar o alvo Nix `aarch64-darwin-ios:lib:simplex-chat` e conferir a fonte imutável da derivação contra os arquivos do checkout. O ZIP gerado contém as cinco bibliotecas arm64. A prova registra os hashes dos arquivos originais e, para o simulador, a preservação dos objetos na conversão de plataforma.
- Com um simulador arm64 do checkout, rodar `tools/taverna/native_access_tests/device_test_core.py` sobre as bibliotecas convertidas e `device_test_delivery.py` sobre a sonda compilada. As duas provas usam a fixture fictícia em loopback.
- Rodar `tools/taverna/device_build.py --technical` com o ZIP imutável, a derivação, o mapa de hashes da fonte e das bibliotecas, os pacotes Swift fixados e os insumos privados de identidade. O recibo associa a projeção de fonte ao pacote sem assinatura.
