import os

from cosmic_database import entities

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


docstr_lines = []

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

    for attr_name in dir(class_):
        if attr_name not in class_table.columns:
            continue

        docstr_lines.append(
            " | ".join([
                attr_name,
                f"`{class_table.columns[attr_name].type.python_type.__qualname__}`"
            ])
        )

    for attr_name, relationship in class_.__mapper__.relationships.items():
        type_str = f"[{relationship.mapper.entity.__qualname__}](#class-{relationship.mapper.entity.__qualname__.lower()})"
        if relationship.collection_class is not None:
            type_str = f"{relationship.collection_class.__qualname__}({type_str})"

        docstr_lines.append(
            " | ".join([
                attr_name,
                type_str
            ])
        )

    docstr_lines.append("")

with open(os.path.join(DOCS_DIR, "classes.md"), "w") as classes_fio:
    classes_fio.write('\n'.join(docstr_lines))
