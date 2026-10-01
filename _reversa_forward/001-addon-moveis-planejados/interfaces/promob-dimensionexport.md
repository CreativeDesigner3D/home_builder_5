# Contrato: `DIMENSIONEXPORT` do Promob (importar/exportar)

> Feature `001-addon-moveis-planejados` · Requisito RF-058 · Evidências: `promob_pacote_completo.zip:configuracoes/PROMOBCONFIGURAÇÃOMEDIDASMEMOVEIS.xml`
> (idêntico ao `.dimensionExport`), `evidencias/issue20-configurador-dimensoes.png`.

## Formato de entrada (observado)

```xml
<DIMENSIONEXPORT VERSION="-1">
  <DEFINITION DESCRIPTION="ME MOVEIS  - COZ. ESCR." ISSYSTEM="False" CHANGED="True">
    <ATTRIBUTES>
      <ATTRIBUTE ID="ALT_ARM" VALUE="2400" />
      …
```

- Lista plana de pares `ID`/`VALUE` (692 no arquivo de referência); sem unidade, domínio nem rótulo.
- Decimais com vírgula (`0,4`, `16,8`); textos (`MDF`, `Vertical`, `Frontal`, `Sem fundo`, `Sem travessas`).
- Padrão do ID: `<LINHA>_<FAMÍLIA>_<COMPONENTE>[_<SUFIXO>]`. Linhas: `ALT`, `PROF`, `BAN`, `COZ`, `DOR`, `ESC`, `GAV`, `SAL`.

## Mapeamento confirmado (🟢 pela tela do Configurador na issue #20)

| Família Promob | Campo do padrão | Exemplo |
|---|---|---|
| `<L>_MAT_<COMP>` | `lines.<L>.sheets.<COMP>.material` | `COZ_MAT_LAT=MDF` |
| `<L>_L_<COMP>` | `…max_width` (mm) | `COZ_L_LAT=2730` |
| `<L>_C_<COMP>` | `…max_length` (mm) | `COZ_C_LAT=1810` |
| `<L>_ESP_<COMP>` | `…thickness` (mm) | `COZ_ESP_LAT=15` |
| `<L>_FIT_<COMP>_<n>A` | `…edges[n-1]` (mm) | `COZ_FIT_POR_4A=0,4` |
| `ALT_*`, `PROF_*` | `lines.*.external.*` conforme tabela do esquema | `ALT_ARM=2400`, `PROF_BAN=600` |

Tabela de componentes (`<COMP>` → código do padrão) mantida em `data/dimension_schema.py` (`promob_codes`), ex.: `LAT→LAT`,
`DIV→DIV`, `BAS→BAS`, `FUN_INF/FUN_SUP/FUN_ALT`, `PRAT`, `POR`, `TAMP`, `TAMPON`, `PAI`, `ROD`, `SAR`, `MOL`.

## Mapeamento parcial (🟡)

`AVA` (avanço), `REB` (rebaixo), `REC`/`RFB`/`RFD`/`RFL`/`RLB` (recuos/folgas), `TRA`/`SAR` (travessas/sarrafos),
`TIP`/`TIPO` (tipos enumerados), `MON` (montagem), `PRAT_REC`, `GAV_*`: mapeados quando a chave existe no esquema;
caso contrário vão para `raw_attributes`.

## Não reconhecidos

`BD`, `CR`, `CTO`, `ENT`, `AFB`, `ALF`, `CAV`, sufixos sem regra: preservados em `raw_attributes` e listados no relatório.

## Regras de conversão

- `VALUE` numérico: vírgula → ponto; interpretado como mm; `0` mantido como zero (sem significado implícito).
- Negativo aceito só onde o esquema permite (ex.: `DOR_AVA_FUN=-15`); fora disso, vai para `raw_attributes` com aviso.
- `DESCRIPTION` → `name` (espaços duplos normalizados); `source = PROMOB_IMPORT`; `market = BR`.

## Exportação de volta

- Reescreve todos os IDs mapeados a partir dos valores atuais + todos os `raw_attributes` inalterados.
- Números com vírgula decimal e sem zeros supérfluos; ordem original dos IDs preservada quando conhecida.
- Teste de aceite: importar o arquivo de referência e exportar produz os mesmos 692 pares (comparação por conjunto).

## Erros

| Situação | Comportamento |
|---|---|
| XML malformado | Recusa com linha/coluna |
| Raiz diferente de `DIMENSIONEXPORT` | Recusa |
| ID duplicado | Mantém o último, avisa |
| Arquivo sem atributos | Recusa |

## Limites

- Parser com `xml.etree.ElementTree` (stdlib), sem resolução de entidades externas.
- Arquivo de até alguns MB; leitura no thread principal.
