# Contrato: Definição de Padrão de Dimensões (`.btmdim.json`)

> Feature `001-addon-moveis-planejados` · Requisitos RF-050a, RF-057, RN-23, RN-24 · Modelo em `data-delta.md` §1.

## Finalidade

Distribuir o padrão de dimensões da empresa entre computadores e projetos (o "Salvar como" do Configurador do Promob).

## Local

- Exportação/importação manual: qualquer pasta escolhida pelo usuário.
- Biblioteca de definições do usuário: `bpy.utils.extension_path_user(__package__, path="standards", create=True)`
  (`docs/rag/blender-api/corpus/bpy.utils.md#bpy.utils.extension_path_user`).

## Estrutura

```json
{
  "schema": "blendertomob.dimension-standard",
  "schema_version": 1,
  "uid": "8c1e…",
  "name": "ME MOVEIS - COZ. ESCR.",
  "market": "BR",
  "source": "USER",
  "version": 7,
  "updated_at": "2026-10-01T10:00:00-03:00",
  "unit": "mm",
  "max_measures": { "module_width_max": 1200, "module_height_max": 2700, "module_depth_max": 900,
                    "sheet_width_max": 2730, "sheet_length_max": 1810 },
  "lines": {
    "COZ": {
      "external": { "base_height": 720, "base_depth": 550, "upper_depth": 350, "tall_height": 2200,
                    "toe_kick_height": 100, "toe_kick_setback": 50, "install_height_upper": 1500 },
      "sheets": {
        "LAT": { "material": "MDF", "max_width": 2730, "max_length": 1810, "thickness": 18,
                 "edges": [0, 0, 0, 0.4] }
      },
      "components": { "ROD_HEIGHT": 100 }
    }
  },
  "raw_attributes": [ { "id": "COZ_BD_LAT_INF", "value": "3" } ]
}
```

## Regras

- Valores sempre em mm no arquivo, com ponto decimal (o arquivo não segue a localidade; a interface sim).
- Chaves desconhecidas em `lines.*` são ignoradas com aviso; `raw_attributes` é preservado sem interpretação.
- Valor fora do domínio do esquema (`data/dimension_schema.py`) → a importação lista o erro e não aplica a definição.
- Importar definição de outra linha num projeto não a aplica sozinha: só a disponibiliza; aplicar a uma linha diferente é
  recusado com mensagem (RF-057).
- Definições embutidas não são exportadas como `BUILTIN`; uma cópia exportada vira `USER`.

## Erros

| Situação | Comportamento |
|---|---|
| JSON inválido | Recusa; mensagem com linha/coluna |
| `schema_version` maior que o suportado | Recusa; pede atualização da extensão |
| `schema_version` menor | Migra em memória e informa |
| Nome igual a uma definição existente | Pergunta: substituir, renomear ou cancelar (Promob RF76) |
| Sem permissão de escrita | Mensagem com o caminho; nada é gravado parcialmente |

## Idempotência

Exportar → importar → exportar produz o mesmo conteúdo (exceto `updated_at` se a definição for alterada).
