# Padrões de código Blender 5.2 usados no CAFFMob Draw

Receitas verificadas contra a referência 5.2 (assinaturas copiadas do corpus). Cada seção aponta a página de origem
em `docs/rag/blender-api/corpus/`. Use estes padrões em vez de reinventar.

## Operador que altera dados (com Undo)

Referência: `bpy.types.Operator.md` (seção "Modifying Blender Data & Undo"), `bpy.props.md`.

```python
import bpy

class BTM_OT_exemplo(bpy.types.Operator):
    """Descrição curta (vira tooltip)"""
    bl_idname = "btm.exemplo"          # namespace novo: btm.* ou caffmob_draw.*
    bl_label = "Exemplo"
    bl_options = {'REGISTER', 'UNDO'}  # obrigatório quando o operador modifica dados

    largura: bpy.props.FloatProperty(name="Largura", default=0.6, min=0.0, unit='LENGTH')  # type: ignore

    @classmethod
    def poll(cls, context):
        if context.object is None:
            cls.poll_message_set("Selecione um objeto")
            return False
        return True

    def execute(self, context):
        context.object.btm_cabinet.width = self.largura
        return {'FINISHED'}
```

- `execute`/`invoke`/`modal` retornam um set: `{'FINISHED'}`, `{'CANCELLED'}`, `{'RUNNING_MODAL'}`, `{'PASS_THROUGH'}`.
- `{'CANCELLED'}` **não** cria passo de undo; se já alterou dados, retorne `{'FINISHED'}` (documentado em `bpy.types.Operator`).
- `poll_message_set(message, *args)` explica ao usuário por que o operador está desabilitado.
- Diálogos: `WindowManager.invoke_props_dialog(operator, *, width=300, title='', confirm_text='', cancel_default=False, ...)`;
  popup: `WindowManager.invoke_popup(operator, *, width=300, auto_keymap=False)` (`auto_keymap` é novo no 5.2).
- O `# type: ignore` nas anotações `bpy.props` é convenção do repo para silenciar o Pyright.

## Propriedades persistentes (PropertyGroup + PointerProperty)

Referência: `bpy.props.md`, `bpy.types.PropertyGroup.md`, `info_overview.md` ("Class Registration" → "Inter-Class Dependencies").

```python
class BTM_CabinetProps(bpy.types.PropertyGroup):
    width: bpy.props.FloatProperty(name="Largura", unit='LENGTH')  # type: ignore

def register():
    bpy.utils.register_class(BTM_CabinetProps)          # registrar o grupo ANTES de quem aponta para ele
    bpy.types.Object.btm_cabinet = bpy.props.PointerProperty(type=BTM_CabinetProps)

def unregister():
    del bpy.types.Object.btm_cabinet                     # remover a propriedade ANTES de desregistrar a classe
    bpy.utils.unregister_class(BTM_CabinetProps)
```

- Desde o **5.0**, valores de `bpy.props` ficam num armazenamento interno "system", separado das custom properties
  (`bpy.props.md`, exemplo Getter/Setter). **Não** leia/escreva uma propriedade `bpy.props` com `obj["nome"]`; use `obj.grupo.nome`.
  `obj["IS_MAIN_SCENE"]`-style continua válido para *custom properties* puras (tags do projeto).
- Callbacks `get`/`set`/`update` podem rodar em contexto com threads e causar loops; mantenha-os simples.
- `CollectionProperty.add()` pode realocar a coleção: não guarde referências a itens antigos depois de adicionar outros
  (`info_gotchas_crashes.md`).

## Registro de extensão e preferências

Referência: `bpy.utils.md`, `bpy.types.AddonPreferences.md`, `info_overview.md`.

- `class Prefs(bpy.types.AddonPreferences): bl_idname = __package__` — em extensões, o id é o pacote completo.
- Acesso: `context.preferences.addons[__package__].preferences`.
- Arquivos do usuário: `bpy.utils.extension_path_user(package, *, path='', create=False)` → diretório gravável por extensão.
  A pasta da própria extensão é apagada a cada atualização e pode ser somente leitura.
- Permissão de arquivos já declarada em `blender_manifest.toml` (`[permissions] files = ...`).

## Handlers de aplicação e timers

Referência: `bpy.app.handlers.md`, `bpy.app.timers.md`.

```python
from bpy.app.handlers import persistent

@persistent                       # sem isto o handler é removido ao abrir outro .blend
def load_file_post(_dummy):
    ...

def register():
    if load_file_post not in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.append(load_file_post)
```

- `bpy.app.timers.register(function, *, first_interval=0, persistent=False)`: a função retorna `None` para parar
  ou um float (segundos) para repetir. Útil para adiar trabalho que não pode rodar dentro de um handler/draw.
- Não altere dados de cena dentro de `depsgraph_update_*`/`frame_change_*` sem cuidado (ver "Note on Altering Data" em `bpy.app.handlers.md`).

## Operador modal + desenho na viewport (GPU)

Referência: `bpy.types.SpaceView3D.md`, `gpu.md`, `gpu.shader.md`, `gpu.state.md`, `gpu_extras.batch.md`, `blf.md`.

```python
import bpy, gpu, blf
from gpu_extras.batch import batch_for_shader

def _draw_3d(op, context):
    shader = gpu.shader.from_builtin('POLYLINE_UNIFORM_COLOR')
    batch = batch_for_shader(shader, 'LINES', {"pos": op.pontos})
    gpu.state.blend_set('ALPHA')
    shader.uniform_float("viewportSize", gpu.state.viewport_get()[2:])
    shader.uniform_float("lineWidth", 2.0)
    shader.uniform_float("color", (0.0, 0.5, 0.7, 1.0))
    batch.draw(shader)
    gpu.state.blend_set('NONE')

def _draw_2d(op, context):
    blf.size(0, 14)                  # blf.size(fontid, size) — sem argumento dpi
    blf.position(0, 20, 20, 0)
    blf.color(0, 1, 1, 1, 1)
    blf.draw(0, "Largura: 600 mm")

class BTM_OT_modal(bpy.types.Operator):
    bl_idname = "btm.modal_exemplo"
    bl_label = "Modal"

    def invoke(self, context, event):
        self.pontos = []
        args = (self, context)
        self._h3d = bpy.types.SpaceView3D.draw_handler_add(_draw_3d, args, 'WINDOW', 'POST_VIEW')
        self._h2d = bpy.types.SpaceView3D.draw_handler_add(_draw_2d, args, 'WINDOW', 'POST_PIXEL')
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        context.area.tag_redraw()
        if event.type in {'RIGHTMOUSE', 'ESC'}:
            self._cleanup()
            return {'CANCELLED'}
        return {'RUNNING_MODAL'}

    def _cleanup(self):
        bpy.types.SpaceView3D.draw_handler_remove(self._h3d, 'WINDOW')
        bpy.types.SpaceView3D.draw_handler_remove(self._h2d, 'WINDOW')
```

- `draw_handler_add(callback, args, region_type, draw_type)`: argumentos **posicionais**; `POST_VIEW` = 3D, `POST_PIXEL` = 2D.
- **Sempre** remova os handlers em todos os caminhos de saída (confirmar, cancelar, erro); handlers órfãos continuam desenhando.
- Shaders builtin válidos no 5.2: `UNIFORM_COLOR`, `FLAT_COLOR`, `SMOOTH_COLOR`, `IMAGE`, `IMAGE_COLOR`, `POLYLINE_UNIFORM_COLOR`,
  `POLYLINE_FLAT_COLOR`, `POLYLINE_SMOOTH_COLOR`, `POINT_UNIFORM_COLOR`, `POINT_FLAT_COLOR` (+ variantes `IMAGE_*_SCENE_LINEAR_*`).
  Nomes antigos com prefixo `2D_`/`3D_` **não existem** — use `compat.get_builtin_shader()` ou os nomes acima.
- Para linhas com espessura, prefira `POLYLINE_*` com os uniforms `viewportSize` + `lineWidth` — é o que os exemplos de `gpu.md` usam.
  `gpu.state.line_width_set` (usado ~90x no repo) apenas "especifica a largura de linhas rasterizadas"; ao tocar nesses trechos,
  confirme visualmente o resultado (a referência não garante espessura > 1 com shaders não-POLYLINE).
- Timer para redesenho contínuo: `wm.event_timer_add(time_step, *, window=None)` e `wm.event_timer_remove(timer)`.

## Picking, raycast e projeção

Referência: `bpy.types.Scene.md`, `bpy_extras.view3d_utils.md`, `bpy.types.Context.md`.

```python
from bpy_extras import view3d_utils

region, rv3d = context.region, context.region_data
coord = (event.mouse_region_x, event.mouse_region_y)
origem = view3d_utils.region_2d_to_origin_3d(region, rv3d, coord)
direcao = view3d_utils.region_2d_to_vector_3d(region, rv3d, coord)
depsgraph = context.evaluated_depsgraph_get()
hit, loc, normal, index, obj, matrix = context.scene.ray_cast(depsgraph, origem, direcao)
tela = view3d_utils.location_3d_to_region_2d(region, rv3d, loc, default=None)  # None se fora da vista
```

## BMesh (geometria por código)

Referência: `bmesh.md`, `bmesh.types.md`, `bmesh.ops.md`, `info_gotchas_meshes.md`.

```python
import bmesh

me = bpy.data.meshes.new("Painel")
bm = bmesh.new()
try:
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=(0.6, 0.018, 0.72), verts=bm.verts)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(me)
finally:
    bm.free()                     # sempre liberar
me.update()
```

- Em Edit Mode: `bm = bmesh.from_edit_mesh(me)` … `bmesh.update_edit_mesh(me, loop_triangles=True, destructive=True)` (não chame `free`).
- Operadores do repo: `create_cube`, `create_cone`, `extrude_face_region`, `translate`, `transform`, `remove_doubles`, `dissolve_limit`,
  `recalc_face_normals`, `reverse_faces`, `triangle_fill`, `join_triangles`, `delete` — todos em `bmesh.ops.md`.
- `bmesh.ops.*` retornam dicts (ex.: `extrude_face_region(...)["geom"]`), consulte a seção "Returns" de cada um.
- Para malhas simples, `Mesh.from_pydata(vertices, edges, faces, shade_flat=True)` + `Mesh.update()` é mais direto.

## Dados avaliados (modificadores/GN aplicados)

Referência: `bpy.types.Context.md`, `bpy.types.ID.md`, `bpy.types.Depsgraph.md`.

```python
depsgraph = context.evaluated_depsgraph_get()
obj_eval = obj.evaluated_get(depsgraph)
mesh_eval = obj_eval.to_mesh()
try:
    ...  # ler vértices/bounding box finais (ex.: extração de peças no cutting/)
finally:
    obj_eval.to_mesh_clear()
```

- Depois de alterar dados e antes de ler resultados avaliados: `context.view_layer.update()`.

## Carregar dados de .blend (assets, GN, perfis)

Referência: `bpy.types.BlendDataLibraries.md`.

```python
with bpy.data.libraries.load(filepath, link=False) as (data_from, data_to):
    data_to.node_groups = [n for n in data_from.node_groups if n == "CabinetPart"]
# fora do with, data_to.node_groups contém os IDs carregados (ou None para os que falharam)
```

- Assinatura 5.2: `load(filepath, *, link=False, pack=False, relative=False, set_fake=False, recursive=False, reuse_local_id=False, assets_only=False, ...)`.
- `bpy.data.libraries.write(filepath, datablocks, ...)` salva um conjunto de IDs (usado na biblioteca de detalhes).

## Drivers

Referência: `bpy.types.bpy_struct.md` (`driver_add`), `bpy.types.FCurve.md`, `bpy.types.Driver.md`, `bpy.types.DriverVariable.md`.

```python
fcurve = obj.driver_add("location", 0)          # driver_add(path, index=-1, /)
drv = fcurve.driver
drv.type = 'SCRIPTED'
var = drv.variables.new()
var.name = "w"
var.targets[0].id = cabinet_obj
var.targets[0].data_path = "btm_cabinet.width"
drv.expression = "w / 2"
```

- Funções usadas em expressões ficam em `bpy.app.driver_namespace` (o projeto injeta `hb_driver_functions` no `load_post`).
- Para inputs de Geometry Nodes, gere o data path com `compat.gn_input_data_path(mod, nome)` (ver `03_compatibilidade_5x.md`).
