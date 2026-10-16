# Prova local da fronteira de acesso

Experimento da [issue #12](https://github.com/paulotvlincelia/taverna-app/issues/12), derivado do [plano aprovado](../../.specs/features/invitation-only/spec.md). O proprietário escolheu a alternativa mais simples: reutilizar relays oficiais e provar uma camada de acesso separada, sem alterar o protocolo nem repetir o piloto inteiro do SimpleX.

A ponte em `tools/taverna/access_proof` é uma fixture experimental. Não é um serviço de produção, não emite convites e ainda não está integrada ao app iOS. Os [resultados locais](../../.specs/features/invitation-only/access-execution.md) separam os controles testados das obrigações que continuam pendentes.

## O que foi exercitado

Doze testes de integração usam relays reais: mensagens SMP nos dois sentidos e arquivo XFTP comparado byte a byte; credencial ausente ou desconhecida; revogação; conexões existentes; política indisponível/inválida; tentativa de alcançar os backends diretamente; tentativa de usar a ponte como proxy para um destino sentinela e isolamento dos logs por execução. Isso qualifica essa fronteira local, não todos os caminhos de rede do app.

Relays v7.0.0.6 vêm da release oficial v7.0.0, no mesmo commit SimpleXMQ fixado no núcleo do fork. O cliente CLI oficial v7.0.0.11 é de interoperabilidade e tem fonte distinto do build iOS. O XFTP CLI oficial usado como ferramenta de prova é experimental/deprecated; não foi adotado como componente do app. [Entradas e hashes](../../tools/taverna/access_proof/inputs.json).

Duas redes Docker internas separam os clientes da rede dos relays. Somente a ponte participa das duas. Não há portas publicadas no host, modo privilegiado, acesso à VPS ou mudanças na configuração do Docker ou de redes administrativas existentes. Estado da aplicação, chaves fictícias e logs ficam em `.build/access-qualification`. Imagens usam o cache do Docker Desktop já instalado; nenhum ambiente de outro projeto é reutilizado ou removido.

## Reproduzir no MacBook

Use um worktree exclusivo sob Projects, Python 3.12, GitHub CLI e Docker Desktop já disponíveis. A preparação baixa somente assets públicos fixados e confere seus hashes antes de executar. O Dockerfile fixa a imagem Ubuntu por digest; pacotes auxiliares vêm do repositório da distribuição, não representam um build bit a bit reproduzível do sistema operacional. Registrar o ID da imagem usada com a execução.

```bash
mkdir -p .build/access-qualification/bin
python3.12 - <<'PY'
from pathlib import Path
import hashlib, json, urllib.request
root = Path('.build/access-qualification/bin')
manifest = json.loads(Path('tools/taverna/access_proof/inputs.json').read_text())
for asset in manifest['assets']:
    target = root / asset['name']
    if not target.exists():
        with urllib.request.urlopen(asset['url'], timeout=60) as response:
            target.write_bytes(response.read())
    if hashlib.sha256(target.read_bytes()).hexdigest() != asset['sha256']:
        raise SystemExit('STOP: hash mismatch: ' + asset['name'])
    target.chmod(0o755)
PY

TAVERNA_DOCKER=/Applications/Docker.app/Contents/Resources/bin/docker
"$TAVERNA_DOCKER" build -t taverna-access-proof:20261016 tools/taverna/access_proof
"$TAVERNA_DOCKER" image inspect taverna-access-proof:20261016 --format '{{.Id}}'

export TAVERNA_PROOF_RUN=example1
python3.12 tools/taverna/access_proof/fixture.py init
python3.12 tools/taverna/access_proof/fixture.py start
python3.12 tools/taverna/access_proof/fixture.py clients
python3.12 tools/taverna/access_proof/test_boundary.py
python3.12 tools/taverna/access_proof/fixture.py stop
```

Execute em sequência, interrompendo no primeiro erro. `init` recusa um diretório de execução existente; escolha outro nome e preserve a tentativa anterior. `start` recusa containers existentes com os nomes da fixture. Após uma falha, consulte logs no diretório da execução e reconcilie os recursos antes de repetir; `stop` remove somente containers e redes de nomes atribuídos à execução selecionada, preservando todos os arquivos. Não usar prune ou limpeza global.

As credenciais são fictícias e a CA expira em dois dias. Nunca trocar esses arquivos por chaves reais. Os testes executam mudanças na lista local de autorização da própria fixture; essa lista não é mecanismo administrativo pronto para uso remoto.

## O que continua faltando

Emissão/resgate de convites, recuperação e troca de dispositivo, cadastro/administração autenticados, grupos oficiais, adaptação do transporte no app e nas extensões, bloqueio de todos os caminhos de fallback, download grande interrompido durante a revogação, aparelhos, APNs, distribuição e operação na VPS. O teste sentinela exercita a ponte; não prova a política completa de egress do iOS nem o comportamento de proxy interno SMP.

Aprovação deste experimento não libera piloto sensível ou deploy. Os 34 requisitos da especificação continuam pendentes como resultado de produto, até suas entregas próprias. A CI Foundation executa os checks locais sem rede/segredos; a prova Docker é manual, registrada por commit e revisada de forma independente.
