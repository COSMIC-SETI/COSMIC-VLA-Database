import os

import pydot

from cosmic_database import entities

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
        "Column | Type | Primary Key | Foreign Key(s) | Nullable",
        "-|-|-|-|-"
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
                'X' if column.nullable else '',
            ])
        )
    docstr_lines.append("")

with open(os.path.join(DOCS_DIR, "tables.md"), "w") as tables_fio:
    tables_fio.write('\n'.join(docstr_lines))

# Class diagraming
docstr_lines = [
    "![Class Diagram](./classes.png)",
    "",
]

graph = pydot.Dot("CosmicDB", graph_type="digraph", rankdir="LR")

for class_table_name, class_table in entities.Base.metadata.tables.items():
    class_ = table_class_map[class_table_name]

    docstr_lines += [
        f"# Class `{class_.__qualname__}`",
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
                f"{relationship.mapper.entity.__qualname__}:class")
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
    
    table_rows = "\n\t".join(
        map(
            field_html,
            dot_node_fields
        )
    )
    
    graph.add_node(
        pydot.Node(
            class_.__qualname__,
            shape="plain",
            label=f'<<table border="0" cellborder="1" cellspacing="0" cellpadding="4">\n\t{table_rows}\n</table>>'
        )
    )

graph.write_raw("classes.dot")
graph.write_png("classes.png", prog="dot")

with open(os.path.join(DOCS_DIR, "classes.md"), "w") as classes_fio:
    classes_fio.write('\n'.join(docstr_lines))
