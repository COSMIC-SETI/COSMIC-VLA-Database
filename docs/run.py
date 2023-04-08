import os

from cosmic_database import entities

DOCS_DIR = os.path.dirname(__file__)

docstr_lines = []
for table_name, table in entities.Base.metadata.tables.items():
    docstr_lines += [
        f"# Table `{table_name}`",
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
                    f"[{fkey.column.table.name}.{fkey.column.name}](#table-{fkey.column.table.name})"
                    for fkey in column.foreign_keys
                ]),
                'X' if column.nullable else '',
            ])
        )
    docstr_lines.append("")

with open(os.path.join(DOCS_DIR, "tables.md"), "w") as tables_fio:
    tables_fio.write('\n'.join(docstr_lines))
