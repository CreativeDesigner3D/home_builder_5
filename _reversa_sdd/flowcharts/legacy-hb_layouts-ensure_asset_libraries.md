# `ensure_asset_libraries` / `refresh_user_libraries` — registro idempotente de bibliotecas de assets

Local: `blendertomob/hb_assets.py:209` e `:230`. Auxiliares: `_ensure_internal_id` `:83`, `_get_library_name` `:90`,
`_register_library_by_name` `:101`, `_register_user_entry` `:122`, `_remove_library_for_entry` `:166`,
`_cleanup_orphaned_libraries` `:182`. Chamado em `register()` do add-on (`blendertomob/__init__.py:248`). 🟢

## Fluxograma

```mermaid
flowchart TD
    A[ensure_asset_libraries] --> B[_remove_library_exact 'Home Builder Extended']
    B --> C[_register_library_by_name 'Home Builder', blendertomob/assets]
    C --> C1{path é diretório?}
    C1 -- não --> D
    C1 -- sim --> C2{já existe lib com esse nome?}
    C2 -- sim --> C3[atualiza path se diferente]
    C2 -- não --> C4[asset_libraries.new · import_method APPEND]
    C3 & C4 --> D[Para cada BTM_AssetLibraryEntry das prefs]
    D --> E[_ensure_internal_id: uuid4.hex 12 chars se vazio]
    E --> F[_register_user_entry]
    F --> F1{library_path definido e é diretório?}
    F1 -- não --> D
    F1 -- sim --> F2[nome esperado = 'HB: nome [id]']
    F2 --> F3{lib com prefixo 'HB: ' e sufixo '[id]'?}
    F3 -- sim --> F4[renomeia/atualiza path · APPEND]
    F3 -- não --> F5[asset_libraries.new · APPEND]
    F4 & F5 --> D
    D -- fim --> G[_cleanup_orphaned_libraries]
    G --> G1[valid_ids = ids das entradas]
    G1 --> G2{lib começa com 'HB: '?}
    G2 -- não --> G5[mantém]
    G2 -- sim --> G3{tem '[id]' no fim?}
    G3 -- sim, id ∉ valid_ids --> G4[remove]
    G3 -- sim, id válido --> G5
    G3 -- não, legado sem tag --> G4

    R[refresh_user_libraries] --> R1[Para cada entrada: garante id]
    R1 --> R2{path válido?}
    R2 -- sim --> F
    R2 -- não --> R3[_remove_library_for_entry]
    R3 --> G
```

## Explicação

- **Chave estável** 🟢: o vínculo entre a entrada do add-on e a `UserAssetLibrary` do Blender é o `internal_id`
  embutido no nome (`HB: <nome> [<id>]`), então renomear a entrada apenas renomeia a biblioteca, sem órfãos
  (`blendertomob/hb_assets.py:90-98`, `:139-149`).
- **Idempotência** 🟢: repetir `ensure_asset_libraries` não duplica bibliotecas (busca por nome/tag antes de `new`).
- **Diferença entre caminhos** 🟢: `ensure_asset_libraries` NÃO remove a biblioteca de uma entrada cujo caminho ficou
  inválido (apenas não registra); `refresh_user_libraries` remove. A limpeza de órfãos só age sobre ids ausentes.
- **Diretório inválido** 🟢: a biblioteca embutida não é registrada se `blendertomob/assets` não existir.
- 🟡 Nome da biblioteca embutida é "Home Builder" (herança do HB5), não "BlenderToMob".
- 🟢 `unregister` chama `remove_asset_libraries`, que remove a embutida e as das entradas (`:223-227`), alterando as
  preferências do usuário a cada desativação.
