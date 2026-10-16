# Assets e distribuição

A licença [ASSETS_LICENSE.md](../../assets/ASSETS_LICENSE.md) cobre elementos gráficos em diferentes pastas. Para um app modificado, trate como bloqueado todo elemento visual upstream até revisão individual e substituição ou autorização adequada. Preservar arquivos no histórico do fork não é aprovação de distribuição.

[asset-policy.json](asset-policy.json) registra o gate da fundação: nenhum asset aprovado e nenhuma release autorizada. O inventário por arquivo e dependência pertence à issue de assets; deve registrar caminho/hash, origem, licença, uso, permissão/prova e substituição. Conferir também recursos em apps/ios, docs e extensões; não limitar a busca à pasta assets.

```bash
python3.12 tools/taverna/check_foundation.py --release-assets
```

Na fundação, esse comando deve falhar com BLOCKED e exit 2. A publicação de código preserva atribuições, AGPL e a licença própria dos assets. Um build local experimental e um release distribuído têm gates distintos. Nenhuma personalização visual ou distribuição está aprovada por este documento.
