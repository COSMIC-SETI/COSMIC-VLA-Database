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

docstr_lines = []
for db_scope, scope_entities in entities.DATABASE_SCOPES.items():
    docstr_lines.extend([
        f"# {db_scope} Database Scope"
        "",
        f"![{db_scope} Class Diagram](./classes_{db_scope}.png)",
        "",
    ])

    graph = pydot.Dot(f"CosmicDB_{db_scope}", graph_type="digraph", rankdir="LR")
    entity_graph = pydot.Dot(f"{db_scope}_Entities", graph_type="digraph", rankdir="LR")
    scope_entity_relations = {}
    
    # for class_table_name, class_table in entities.Base.metadata.tables.items():
    for class_ in scope_entities:
        entity_relations = []

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

        
        dot_node_fields = [
            {
                "tr": {},
                "td": {
                    "bgcolor": "black",
                    "port": "class",
                },
                "font": {
                    "color": "white"
                },
                "innerHtml": class_.__qualname__
            }
        ]

        for attr_name in dir(class_):
            if attr_name not in class_table.columns:
                continue
            
            dot_node_fields.append(
                {
                    "tr": {},
                    "td": {},
                    "innerHtml": attr_name
                }
            )

            docstr_lines.append(
                " | ".join([
                    attr_name,
                    f"`{class_table.columns[attr_name].type.python_type.__qualname__}`"
                ])
            )

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
            
            graph.add_edge(
                pydot.Edge(
                    f"{class_.__qualname__}:{attr_name}",
                    f"{relationship.mapper.entity.__qualname__}:class"
                )
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
    
        
        table_rows = "\n\t".join(dot_node_fields[0:1] + dot_node_fields[entity_relationship_field_index:])
        entity_graph.add_node(
            pydot.Node(
                class_.__qualname__,
                shape="plain",
                label=f'<<table border="0" cellborder="1" cellspacing="0" cellpadding="4">\n\t{table_rows}\n</table>>'
            )
        )
        
        scope_entity_relations[class_.__qualname__] = entity_relations

    graph.write_raw(f"classes_{db_scope}.dot")
    graph.write_png(f"classes_{db_scope}.png", prog="dot")
    
    print(scope_entity_relations)
    for entity_name, entity_relations in scope_entity_relations.items():

        entity_table_rows = []
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
                    print(f"IsReversal({entity_name}->{relation})")
                    continue

            print(f"{entity_name}:{entity_attr} -> {relation}: {direction}")
            entity_graph.add_edge(
                pydot.Edge(
                    f"{entity_name}:{entity_attr}",
                    f"{relation}:class",
                    arrowhead="crow" if RelationshipDirection.ONETOMANY else "none"
                )
            )

    entity_graph.write_raw(f"entities_{db_scope}.dot")
    entity_graph.write_png(f"entities_{db_scope}.png", prog="dot")

with open(os.path.join(DOCS_DIR, "classes.md"), "w") as classes_fio:
    classes_fio.write('\n'.join(docstr_lines))