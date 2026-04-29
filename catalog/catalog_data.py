"""Catalog data: every browseable item across the entire HB5 library.

Each entry is a plain Python dict (intentionally simple - this is data,
not Blender properties). The browser UI mirrors entries into a Scene
CollectionProperty so Blender's UIList can iterate them.

KIND values drive the action verb shown in list-view detail cards:
    'product' - placeable in the scene  -> "Place at cursor"

Door styles, finishes, end conditions, and other per-cabinet
configurations are intentionally NOT in this catalog. They are
modifications applied to an existing cabinet via its Style Section /
right-click properties popup, not items to "place" from a library.

Inserts (rollouts, trash, dividers) are likewise NOT in this catalog.
They are placed via right-click on a face-frame bay, not from this
browse-and-place library.
"""

KIND_VERBS = {
    'product': 'Place at cursor',
}

KIND_ICONS = {
    'product': 'MESH_CUBE',
}


def _ff(cabinet_name, bay_qty=1):
    """Helper for face-frame cabinet entries that all share the same operator."""
    return {
        'action_operator': 'hb_face_frame.draw_cabinet',
        'action_args': {'cabinet_name': cabinet_name, 'bay_qty': bay_qty},
    }


def _todo(label):
    """Helper for catalog entries whose real operator hasn't been built yet."""
    return {
        'action_operator': 'hb_catalog.not_yet_implemented',
        'action_args': {'item_name': label},
    }


def _e(category, name, description, action, tags=None):
    """Build a catalog entry from compact data.

    The id is auto-derived from category + name (sanitised). Adding a
    new entry is one line at the call site below.
    """
    sanitised = (
        name.lower()
        .replace(' ', '_')
        .replace('-', '')
        .replace('?', '')
        .replace('(', '')
        .replace(')', '')
        .replace('/', '_')
        .replace(',', '')
    )
    while '__' in sanitised:
        sanitised = sanitised.replace('__', '_')
    sanitised = sanitised.strip('_')
    item_id = category.replace('/', '_') + '_' + sanitised
    return {
        'id': item_id,
        'code': '',
        'name': name,
        'description': description,
        'kind': 'product',
        'category': category,
        'tags': list(tags or []),
        'thumbnail': '',
        **action,
    }


CATALOG = [
    # =======================================================================
    # Standard cabinets
    # =======================================================================
    _e('standard', 'Base',
       'Standard 1-door 1-drawer base cabinet.',
       _ff('Base Door'), tags=['base', 'standard']),
    _e('standard', 'Tall',
       'Tall pantry, oven, broom, or refrigerator surround.',
       _ff('Tall'), tags=['tall', 'pantry']),
    _e('standard', 'Upper',
       'Standard wall cabinet.',
       _ff('Upper'), tags=['wall', 'upper']),
    _e('standard', 'Upper Stacked',
       'Wall cabinet with stacked door configuration.',
       _ff('Upper Stacked'), tags=['wall', 'stacked']),
    _e('standard', 'Lap Drawer',
       'Lap drawer cabinet.',
       _ff('Lap Drawer'), tags=['drawer', 'lap']),
    _e('standard', 'Floating Base Cabinet',
       'Floating base cabinet (no toe kick).',
       _todo('Floating Base Cabinet'), tags=['base', 'floating']),

    # =======================================================================
    # Corner cabinets
    # =======================================================================
    _e('corner', 'Pie Cut Door - Left Opens First',
       'Pie cut corner; left door opens first.',
       _todo('Pie Cut Door (Left Opens First)'), tags=['pie cut', 'corner']),
    _e('corner', 'Pie Cut Door - Bi-fold',
       'Pie cut corner with bi-fold doors.',
       _todo('Pie Cut Door (Bi-fold)'), tags=['pie cut', 'bi-fold']),
    _e('corner', 'Pie Cut Door - Tray Compartment',
       'Pie cut corner with tray compartment.',
       _todo('Pie Cut Door (Tray Compartment)'), tags=['pie cut', 'tray']),
    _e('corner', 'Diagonal',
       'Diagonal corner cabinet.',
       _todo('Diagonal corner'), tags=['diagonal', 'corner']),
    _e('corner', 'Diagonal Sink - Full Height Doors',
       'Diagonal sink corner with full-height doors.',
       _todo('Diagonal Sink (Full Height Doors)'), tags=['diagonal', 'sink']),
    _e('corner', 'Diagonal Sink - Standard with False Front',
       'Diagonal sink corner, standard configuration with false drawer front.',
       _todo('Diagonal Sink (Standard, False Front)'), tags=['diagonal', 'sink', 'false front']),
    _e('corner', 'Pie Cut Drawer - 2',
       'Pie cut corner with 2 drawers.',
       _todo('Pie Cut Drawer (2)'), tags=['pie cut', 'drawer']),
    _e('corner', 'Pie Cut Drawer - 3',
       'Pie cut corner with 3 drawers.',
       _todo('Pie Cut Drawer (3)'), tags=['pie cut', 'drawer']),
    _e('corner', 'Pie Cut Drawer - 4',
       'Pie cut corner with 4 drawers.',
       _todo('Pie Cut Drawer (4)'), tags=['pie cut', 'drawer']),

    # =======================================================================
    # Appliance products
    # =======================================================================
    _e('appliance', 'Elevated Dishwasher - Standard',
       'Elevated dishwasher cabinet, standard.',
       _todo('Elevated Dishwasher (Standard)'), tags=['dishwasher', 'elevated']),
    _e('appliance', 'Elevated Dishwasher - With Drawer',
       'Elevated dishwasher cabinet with drawer.',
       _todo('Elevated Dishwasher (With Drawer)'), tags=['dishwasher', 'elevated', 'drawer']),
    _e('appliance', 'Dishwasher',
       'Dishwasher cabinet.',
       _todo('Dishwasher cabinet'), tags=['dishwasher']),
    _e('appliance', 'Single Oven',
       'Single oven cabinet.',
       _todo('Single Oven cabinet'), tags=['oven', 'single']),
    _e('appliance', 'Double Oven',
       'Double oven cabinet.',
       _todo('Double Oven cabinet'), tags=['oven', 'double']),
    _e('appliance', 'Microwave',
       'Microwave cabinet.',
       _todo('Microwave cabinet'), tags=['microwave']),
    _e('appliance', 'Microwave and Oven',
       'Combined microwave and oven cabinet.',
       _todo('Microwave and Oven'), tags=['oven', 'microwave']),
    _e('appliance', 'Refrigerator - Integrated Legs',
       'Refrigerator surround with integrated legs.',
       _todo('Refrigerator (Integrated Legs)'), tags=['refrigerator', 'legs']),
    _e('appliance', 'Refrigerator - Stile (in lieu of leg)',
       'Refrigerator surround with stile in lieu of leg.',
       _todo('Refrigerator (Stile)'), tags=['refrigerator', 'stile']),
    _e('appliance', 'Refrigerator Columns',
       'Refrigerator columns.',
       _todo('Refrigerator Columns'), tags=['refrigerator', 'columns']),
    _e('appliance', 'Refrigerator Pilasters?',
       'Refrigerator pilasters - confirm before placing.',
       _todo('Refrigerator Pilasters'), tags=['refrigerator', 'pilasters']),
    _e('appliance', 'Step-back Surround Set',
       'Step-back refrigerator surround set.',
       _todo('Step-back Surround Set'), tags=['refrigerator', 'surround']),
    _e('appliance', 'Range',
       'Range cabinet.',
       _todo('Range cabinet'), tags=['range']),
    _e('appliance', 'Standalone Refrigerator?',
       'Standalone refrigerator placeholder - confirm before placing.',
       _todo('Standalone Refrigerator'), tags=['refrigerator', 'standalone']),

    # =======================================================================
    # Vanities
    # =======================================================================
    _e('vanity', 'Vanity Special',
       'Special vanity cabinet.',
       _todo('Vanity Special'), tags=['vanity']),
    _e('vanity', 'Vanity Combination',
       'Combination vanity cabinet.',
       _todo('Vanity Combination'), tags=['vanity']),
    _e('vanity', 'Vanity Deluxe',
       'Deluxe vanity cabinet.',
       _todo('Vanity Deluxe'), tags=['vanity']),

    # =======================================================================
    # Parts
    # =======================================================================
    _e('parts', 'Loose Stile',
       'Loose stile.',
       _todo('Loose Stile'), tags=['stile']),
    _e('parts', 'End Leg - Left',
       'Left-side end leg.',
       _todo('End Leg (Left)'), tags=['leg', 'end']),
    _e('parts', 'End Leg - Right',
       'Right-side end leg.',
       _todo('End Leg (Right)'), tags=['leg', 'end']),
    _e('parts', 'Intermediate Leg',
       'Intermediate leg.',
       _todo('Intermediate Leg'), tags=['leg']),
    _e('parts', 'Vanity End Leg Assembly',
       'Vanity end leg assembly.',
       _todo('Vanity End Leg Assembly'), tags=['vanity', 'leg']),
    _e('parts', 'Vanity Support Leg - Square',
       'Square vanity support leg.',
       _todo('Vanity Support Leg (Square)'), tags=['vanity', 'leg', 'square']),
    _e('parts', 'Vanity Support Leg - Curved',
       'Curved vanity support leg.',
       _todo('Vanity Support Leg (Curved)'), tags=['vanity', 'leg', 'curved']),
    _e('parts', 'Vanity Fixed Shelf - Finished',
       'Finished vanity fixed shelf.',
       _todo('Vanity Fixed Shelf (Finished)'), tags=['vanity', 'shelf']),
    _e('parts', 'Vanity Fixed Shelf - Slotted',
       'Slotted vanity fixed shelf.',
       _todo('Vanity Fixed Shelf (Slotted)'), tags=['vanity', 'shelf', 'slotted']),
    _e('parts', 'Shelf - Floating',
       'Floating shelf.',
       _todo('Floating Shelf'), tags=['shelf', 'floating']),
    _e('parts', 'Shelf - Non-Floating',
       'Non-floating shelf.',
       _todo('Non-Floating Shelf'), tags=['shelf']),
    _e('parts', 'Shelf - Heavy Duty',
       'Heavy duty shelf.',
       _todo('Heavy Duty Shelf'), tags=['shelf', 'heavy duty']),

    # =======================================================================
    # Specialty
    # =======================================================================
    _e('specialty', 'Recessed Medicine Cabinet',
       'Recessed medicine cabinet.',
       _todo('Recessed Medicine Cabinet'), tags=['medicine', 'recessed']),
    _e('specialty', 'Tri-View Medicine Cabinet',
       'Tri-view medicine cabinet.',
       _todo('Tri-View Medicine Cabinet'), tags=['medicine', 'tri-view']),
    _e('specialty', 'Overstool - With Shelf',
       'Overstool with shelf.',
       _todo('Overstool (With Shelf)'), tags=['overstool']),
    _e('specialty', 'Overstool - With Towel Bar',
       'Overstool with towel bar.',
       _todo('Overstool (With Towel Bar)'), tags=['overstool', 'towel bar']),
    _e('specialty', 'Overstool - With Shelf and Towel Bar',
       'Overstool with shelf and towel bar.',
       _todo('Overstool (With Shelf and Towel Bar)'), tags=['overstool', 'shelf', 'towel bar']),
    _e('specialty', 'Mirror Frame - Shaker',
       'Shaker-style mirror frame.',
       _todo('Mirror Frame (Shaker)'), tags=['mirror', 'shaker']),
    _e('specialty', 'Mirror Frame - Colonial',
       'Colonial-style mirror frame.',
       _todo('Mirror Frame (Colonial)'), tags=['mirror', 'colonial']),
    _e('specialty', 'Mirror Frame - Clover',
       'Clover-style mirror frame.',
       _todo('Mirror Frame (Clover)'), tags=['mirror', 'clover']),
    _e('specialty', 'Mirror Frame - Gothic',
       'Gothic-style mirror frame.',
       _todo('Mirror Frame (Gothic)'), tags=['mirror', 'gothic']),
    _e('specialty', 'Tub Skirt - Finished',
       'Finished tub skirt.',
       _todo('Tub Skirt (Finished)'), tags=['tub skirt']),
    _e('specialty', 'Tub Skirt - Paneled',
       'Paneled tub skirt.',
       _todo('Tub Skirt (Paneled)'), tags=['tub skirt', 'paneled']),
    _e('specialty', 'Tub Skirt - Working or Removable Door',
       'Tub skirt with working or removable door.',
       _todo('Tub Skirt (Working / Removable Door)'), tags=['tub skirt', 'door']),
    _e('specialty', 'Tub Skirt - Removable Panels',
       'Tub skirt with removable panels.',
       _todo('Tub Skirt (Removable Panels)'), tags=['tub skirt', 'panels']),
    _e('specialty', 'Bookcase - Standard',
       'Standard bookcase.',
       _todo('Bookcase (Standard)'), tags=['bookcase']),
    _e('specialty', 'Bookcase - Storage Unit',
       'Bookcase as a storage unit.',
       _todo('Bookcase (Storage Unit)'), tags=['bookcase', 'storage']),
    _e('specialty', 'Bookcase Upper - Standard',
       'Standard upper bookcase.',
       _todo('Bookcase Upper (Standard)'), tags=['bookcase', 'upper']),
    _e('specialty', 'Bookcase Upper - Hutch',
       'Hutch upper bookcase.',
       _todo('Bookcase Upper (Hutch)'), tags=['bookcase', 'hutch']),
    _e('specialty', 'Bookcase Corner - Hutch',
       'Hutch corner bookcase.',
       _todo('Bookcase Corner (Hutch)'), tags=['bookcase', 'corner', 'hutch']),
    _e('specialty', 'Bookcase Corner - Storage',
       'Storage corner bookcase.',
       _todo('Bookcase Corner (Storage)'), tags=['bookcase', 'corner', 'storage']),
    _e('specialty', 'Bookcase Corner Upper - Standard',
       'Standard upper corner bookcase.',
       _todo('Bookcase Corner Upper (Standard)'), tags=['bookcase', 'corner', 'upper']),
    _e('specialty', 'Bookcase Corner Upper - Hutch',
       'Hutch upper corner bookcase.',
       _todo('Bookcase Corner Upper (Hutch)'), tags=['bookcase', 'corner', 'upper', 'hutch']),
    _e('specialty', 'Window Seat - Veneer Front',
       'Window seat with veneer front.',
       _todo('Window Seat (Veneer Front)'), tags=['window seat']),
    _e('specialty', 'Window Seat - Paneled Front',
       'Window seat with paneled front.',
       _todo('Window Seat (Paneled Front)'), tags=['window seat', 'paneled']),
    _e('specialty', 'Window Seat - With Doors',
       'Window seat with doors.',
       _todo('Window Seat (With Doors)'), tags=['window seat', 'doors']),
    _e('specialty', 'Window Seat - With Drawers',
       'Window seat with drawers.',
       _todo('Window Seat (With Drawers)'), tags=['window seat', 'drawers']),
    _e('specialty', 'Window Seat - Hinged Lid?',
       'Window seat with hinged lid - confirm before placing.',
       _todo('Window Seat (Hinged Lid)'), tags=['window seat', 'lid']),
    _e('specialty', 'Dresser - 5 Drawers',
       'Dresser with 5 drawers.',
       _todo('Dresser (5 Drawers)'), tags=['dresser', 'drawer']),
    _e('specialty', 'Dresser - 6 Drawers',
       'Dresser with 6 drawers.',
       _todo('Dresser (6 Drawers)'), tags=['dresser', 'drawer']),
    _e('specialty', 'Night Stand - Standard',
       'Standard night stand.',
       _todo('Night Stand (Standard)'), tags=['night stand']),
    _e('specialty', 'Night Stand - 3 Drawer',
       '3-drawer night stand.',
       _todo('Night Stand (3 Drawer)'), tags=['night stand', 'drawer']),

    # =======================================================================
    # Angled
    # =======================================================================
    _e('angled', 'Angled Ends with Doors',
       'Angled end cabinet with doors.',
       _todo('Angled Ends with Doors'), tags=['angled', 'ends', 'doors']),
    _e('angled', 'Double Angled Ends',
       'Double angled end cabinet.',
       _todo('Double Angled Ends'), tags=['angled', 'ends']),
    _e('angled', 'Angled Finished Ends',
       'Angled finished end cabinet.',
       _todo('Angled Finished Ends'), tags=['angled', 'ends', 'finished']),

    # =======================================================================
    # Misc
    # =======================================================================
    _e('misc', 'Half Wall',
       'Half wall.',
       _todo('Half Wall'), tags=['wall']),
    _e('misc', 'Support Frame',
       'Support frame.',
       _todo('Support Frame'), tags=['frame', 'support']),
    _e('misc', 'Face Frame and Doors',
       'Face frame and doors only (no carcass).',
       _todo('Face Frame and Doors'), tags=['face frame', 'doors']),
    _e('misc', 'X-Frame Ends',
       'X-frame ends.',
       _todo('X-Frame Ends'), tags=['x-frame', 'ends']),
]


def find_entry(item_id):
    """Return the catalog entry with the given id, or None."""
    for entry in CATALOG:
        if entry['id'] == item_id:
            return entry
    return None


def list_categories():
    """Unique sorted list of category paths in the catalog. Includes
    intermediate parents.
    """
    paths = set()
    for entry in CATALOG:
        cat = entry.get('category', '')
        if not cat:
            continue
        parts = cat.split('/')
        for i in range(1, len(parts) + 1):
            paths.add('/'.join(parts[:i]))
    return sorted(paths)


def category_label(path):
    if not path:
        return 'Everything'
    leaf = path.split('/')[-1]
    return leaf.replace('_', ' ').replace('-', ' ').title()


def category_indented_label(path):
    depth = path.count('/')
    indent = '    ' * depth
    return indent + category_label(path)
