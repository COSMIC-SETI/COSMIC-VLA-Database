import os

import pydot

from cosmic_database import entities
from sqlalchemy.orm import RelationshipDirection

def field_html(field: dict):
    '''
    Convert the key-values of an ordered dict into nested HTML elements.
    '''
    html = ""
    to_close = []
    for element, attributes in field.items():
        if element == "innerHtml":
            html += attributes
            break
        attr = ' '.join(
            f'{k}="{v}"'
            for k, v in attributes.items()
        )
        space = ' ' if len(attr) > 0 else ''
        html += f'<{element}{space}{attr}>'
        to_close.insert(0, element)
    for element in to_close:
        html += f'</{element}>'
    return html

DOCS_DIR = os.path.dirname(__file__)

table_class_map = {
    m.local_table.name: m.class_
    for m in entities.Base.registry.mappers
}

docstr_lines = []
for table_name, table in entities.Base.metadata.tables.items():
    docstr_lines += [
        f"# Table `{table_name}`",
        "",
        f"Class [`{table_class_map[table_name].__module__}.{table_class_map[table_name].__qualname__}`](./classes.md#class-{table_class_map[table_name].__qualname__})",
        "",
        "Column | Type | Primary Key | Foreign Key(s) | Indexed | Nullable | Unique",
        "-|-|-|-|-|-|-"
    ]
    for column_name, column in table.columns.items():
        docstr_lines.append(
            " | ".join([
                column_name,
                str(column.type),
                'X' if column.primary_key else '',
                ','.join([
                    f"[{fkey.column.table.name}](#table-{fkey.column.table.name}).{fkey.column.name}"
                    for fkey in column.foreign_keys
                ]),
                'X' if column.index else '',
                'X' if column.nullable else '',
                'X' if column.unique else '',
            ])
        )
    docstr_lines.append("")

with open(os.path.join(DOCS_DIR, "tables.md"), "w") as tables_fio:
    tables_fio.write('\n'.join(docstr_lines))

# Class diagraming

scoped_entity_graph = pydot.Dot(f"CosmicDB", graph_type="digraph", rankdir="LR", layout="dot", nodesep=0.25, ranksep=1)
scope_subgraph_map = {
    scope: pydot.Subgraph(graph_name=scope, label=f'"{scope} Scope"', cluster=True)
    for scope in entities.DATABASE_SCOPES.keys()
}

entity_fields_map = {}
entity_scope_map = {}
for one_end, other_end in entities.SCOPE_BRIDGES.items():
    edge_ends = []
    for end_tup in [(one_end, "e"), (other_end, "w")]:
        end, end_edge_portpos = end_tup
        end_class = table_class_map[end.table.name]
        edge_ends.append(f"{end_class.__qualname__}:{end.name}:{end_edge_portpos}")

        end_scope_name = None
        for scope, scope_entities in entities.DATABASE_SCOPES.items():
            if end_class in scope_entities:
                end_scope_name = scope
                break
        
        assert end_scope_name is not None
        entity_scope_map[end_class.__qualname__] = end_scope_name

        entity_bridge_fields = entity_fields_map.get(
            end_class.__qualname__,
            [{ # header
                "tr": {},
                "td": {
                    "bgcolor": "black",
                    "port": "class",
                },
                "font": {
                    "color": "white"
                },
                "innerHtml": end_class.__qualname__
            }],
        )
        entity_bridge_fields.append(
            {
                "tr": {},
                "td": {
                    "port": end.name
                },
                "innerHtml": end.name
            }
        )

        entity_fields_map[end_class.__qualname__] = entity_bridge_fields

    scoped_entity_graph.add_edge(
        pydot.Edge(
            edge_ends[0],
            edge_ends[1],
            arrowtail="none",
            dir="back",
            color="darkgrey",
            penwidth=3.0,
            weight=100
        )
    )

docstr_lines = []
for db_scope, scope_entities in entities.DATABASE_SCOPES.items():
    docstr_lines.extend([
        f"# {db_scope} Database Scope"
        "",
        f"![{db_scope} Class Diagram](./classes_{db_scope}.png)",
        "",
    ])

    graph = pydot.Dot(f"CosmicDB_{db_scope}", graph_type="digraph", rankdir="LR", layout="dot", nodesep=0.5, ranksep=2.5)
    entity_graph = scope_subgraph_map[db_scope] #pydot.Dot(f"{db_scope}_Entities", graph_type="digraph", rankdir="LR", layout="dot", ranksep="1.0")
    scope_entity_relations = {}
    scope_fk_relations = {}
    
    # for class_table_name, class_table in entities.Base.metadata.tables.items():
    for class_ in scope_entities:
        entity_relations = []
        fk_relations = []

        # class_ = table_class_map[class_table_name]
        class_table_name = class_.__tablename__
        class_table = entities.Base.metadata.tables[class_table_name]

        docstr_lines += [
            f"## Class `{class_.__qualname__}`",
            "",
            f"Table [`{class_table_name}`](./tables.md#table-{class_table_name})",
            "",
            "Attribute | Type",
            "-|-",
        ]

        
        dot_node_pk_field = None
        dot_node_fk_fields = []
        dot_node_fields = []

        pk_insertion_index = 1
        for attr_name in dir(class_):
            if attr_name not in class_table.columns:
                continue
            
            docstr_lines.append(
                " | ".join([
                    attr_name,
                    f"`{column.type.python_type.__qualname__}`"
                ])
            )
            
            td = {
                "port": attr_name
            }

            display_name = attr_name
            column = class_table.columns[attr_name]
            if column.primary_key:
                td["port"] = "pk"
                td["bgcolor"] = "lightgrey"
                td["border"] = 3
                if column.type.python_type != int:
                    display_name += f" {{{column.type.python_type.__qualname__}}}"

            if column.nullable:
                td["bgcolor"] = "lightgrey:white"
                td["style"] = "radial"
                display_name += "*"
            if len(column.foreign_keys) > 0:
                display_name += " (FK)"
                fk_relations.append((
                    td["port"],
                    [
                        table_class_map[fk.column.table.name].__qualname__
                        for fk in column.foreign_keys
                    ]
                ))

            dot_node_field = {
                "tr": {},
                "td": td,
                "innerHtml": display_name
            }
            if column.primary_key:
                if dot_node_pk_field is None:
                    dot_node_pk_field = dot_node_field
                else:
                    dot_node_pk_field["innerHtml"] += "<br/>" + display_name
            elif len(column.foreign_keys) > 0:
                dot_node_fk_fields.append(dot_node_field)
            else:
                dot_node_fields.append(dot_node_field)
        
        dot_node_fields = [
            { # header
                "tr": {},
                "td": {
                    "bgcolor": "black",
                    "port": "class",
                },
                "font": {
                    "color": "white"
                },
                "innerHtml": class_.__qualname__
            },
            dot_node_pk_field
        ] + dot_node_fk_fields + dot_node_fields

        entity_relationship_field_index = len(dot_node_fields)
        for attr_name, relationship in class_.__mapper__.relationships.items():
            dot_node_fields.append(
                {
                    "tr": {},
                    "td": {
                        "bgcolor": "darkgrey",
                        "port": attr_name
                    },
                    "innerHtml": attr_name
                }
            )
            entity_relations.append(
                (relationship.mapper.entity.__qualname__, attr_name, relationship.direction)
            )

            type_str = f"[{relationship.mapper.entity.__qualname__}](#class-{relationship.mapper.entity.__qualname__.lower()})"
            if relationship.collection_class is not None:
                type_str = f"{relationship.collection_class.__qualname__}({type_str})"

            docstr_lines.append(
                " | ".join([
                    attr_name,
                    type_str
                ])
            )
        
        if class_.__qualname__ not in entity_fields_map:
            # entity doesn't bridge scopes and hasn't been processed
            entity_fields_map[class_.__qualname__] = dot_node_fields[0:1]
            scope_name = None
            for scope, scope_entities in entities.DATABASE_SCOPES.items():
                if class_ in scope_entities:
                    scope_name = scope
                    break
            
            assert scope_name is not None, f"{class_.__qualname__} has not been assigned to a scope."
            entity_scope_map[class_.__qualname__] = scope_name

        entity_fields_map[class_.__qualname__].extend(dot_node_fields[entity_relationship_field_index:])

        dot_node_fields = list(map(
            field_html,
            dot_node_fields
        ))
        
        table_rows = "\n\t".join(dot_node_fields)
        graph.add_node(
            pydot.Node(
                class_.__qualname__,
                shape="plain",
                label=f'<<table border="0" cellborder="1" cellspacing="0" cellpadding="4">\n\t{table_rows}\n</table>>'
            )
        )

        scope_entity_relations[class_.__qualname__] = entity_relations
        scope_fk_relations[class_.__qualname__] = fk_relations

    for entity_name, entity_relations in scope_entity_relations.items():
        for relationship in entity_relations:
            relation, entity_attr, direction = relationship
            if direction == RelationshipDirection.MANYTOONE:
                # skip edge if it's just the reverse of another
                is_reversal = False
                for other_relationhip in scope_entity_relations[relation]:
                    other_relation, _, other_direction = other_relationhip
                    if other_relation != entity_name:
                        continue
                    if other_direction == RelationshipDirection.ONETOMANY:
                        is_reversal = True
                    break
                if is_reversal:
                    direction = None

            arrowtail = "none"
            if direction == RelationshipDirection.ONETOMANY:
                arrowtail = "inv"
            
            for g in [graph, scoped_entity_graph]:
                g.add_edge(
                    pydot.Edge(
                        f"{entity_name}:{entity_attr}",
                        f"{relation}:class",
                        arrowtail=arrowtail,
                        dir="back",
                    )
                )

    for entity_name, fk_relations in scope_fk_relations.items():
        for fk_relation in fk_relations:
            entity_attr, fk_links = fk_relation
            for relation in fk_links:
                graph.add_edge(
                    pydot.Edge(
                        f"{entity_name}:{entity_attr}",
                        f"{relation}:pk",
                        arrowtail="none",
                        dir="back",
                        color="darkgrey",
                        penwidth=3.0,
                    )
                )

    
    legend_subgraph = pydot.Subgraph(graph_name="legend", label=f'"Legend"', cluster=True)
    for edge_name, edge_attr in {
        "Foreign Relations": {
            "arrowtail": "none",
            "dir": "back",
            "color": "black",
        },
        "Foreign Keys": {
            "arrowtail": "none",
            "dir": "back",
            "color": "darkgrey",
            "penwidth": 3.0,
        },
    }.items():
        
        for i in [0, 1]:
            legend_subgraph.add_node(
                pydot.Node(
                    f"{edge_name}_{i}",
                    label="" if i == 0 else edge_name,
                    shape="none",
                )
            )
        
        legend_subgraph.add_edge(
            pydot.Edge(
                f"{edge_name}_0",
                f"{edge_name}_1",
                **edge_attr
            )
        )

    graph.add_subgraph(legend_subgraph)
    graph.write_raw(f"classes_{db_scope}.dot")
    graph.write_png(f"classes_{db_scope}.png", prog="dot")


with open(os.path.join(DOCS_DIR, "classes.md"), "w") as classes_fio:
    classes_fio.write('\n'.join(docstr_lines))

for entity_name, fields in entity_fields_map.items():
    scope = entity_scope_map[entity_name]
    subgraph = scope_subgraph_map[scope]
    
    table_rows = list(map(
        field_html,
        fields
    ))
    
    table_rows = "\n\t".join(table_rows)
    
    subgraph.add_node(
        pydot.Node(
            entity_name,
            shape="plain",
            label=f'<<table border="0" cellborder="1" cellspacing="0" cellpadding="4">\n\t{table_rows}\n</table>>'
        )
    )

for _, subgraph in scope_subgraph_map.items():
    scoped_entity_graph.add_subgraph(subgraph)

legend_subgraph = pydot.Subgraph(graph_name="legend", label=f'"Legend"', cluster=True)
for edge_name, edge_attr in {
    "Foreign Relations": {
        "arrowtail": "none",
        "dir": "back",
        "color": "black",
    },
    "Dislocated Foreign Keys": {
        "arrowtail": "none",
        "dir": "back",
        "color": "darkgrey",
        "penwidth": 3.0,
    },
}.items():
    
    for i in [0, 1]:
        legend_subgraph.add_node(
            pydot.Node(
                f"{edge_name}_{i}",
                label="" if i == 0 else edge_name,
                shape="none",
            )
        )
    
    legend_subgraph.add_edge(
        pydot.Edge(
            f"{edge_name}_0",
            f"{edge_name}_1",
            **edge_attr
        )
    )


scoped_entity_graph.add_subgraph(legend_subgraph)

scoped_entity_graph.write_raw(f"entity_relationships.dot")
scoped_entity_graph.write_png(f"entity_relationships.png", prog="dot")