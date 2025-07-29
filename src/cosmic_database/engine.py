import os
import yaml
from datetime import datetime

import sqlalchemy

from cosmic_database import entities

class CosmicDB_Engine:

    def __init__(
        self,
        engine_conf_yaml_filepath: str = None,
        scope: entities.DatabaseScope = None,
        engine_url: str = None,
        **kwargs
    ):
        """
        Parameters
        ----------

        """

        if engine_url is not None:
            if scope is None:
                raise ValueError("No scope specified.")
            self.engine_url = engine_url
            self.scope = scope  
        elif engine_conf_yaml_filepath is not None:
            self.engine_url, self.scope = self._create_url(
                engine_conf_yaml_filepath,
                scope
            )
        if not hasattr(self, "engine_url"):
            raise ValueError("Specify either a configuration YAML filepath, or both an engine URL and a Scope")

        kwargs["pool_recycle"] = kwargs.get("pool_recycle", 3600)
        self.engine = sqlalchemy.create_engine(
            self.engine_url,
            **kwargs
        )
    
    @staticmethod
    def _create_url(engine_conf_yaml_filepath, scope: entities.DatabaseScope = None):
        with open(engine_conf_yaml_filepath, "r") as yaml_fio:
            yaml_dict = yaml.safe_load(yaml_fio)
            if len(yaml_dict) == 1:
                scope, yaml_dict = next(iter(yaml_dict.items()))
                scope = entities.DatabaseScope(scope)
            else:
                assert any(scope.value in yaml_dict for scope in entities.DatabaseScope), f"Expecting a Multi-scope engine configuration YAML."
                assert scope is not None, f"Multi-scope engine configuration YAML requires a scope selection."
                try:
                    yaml_dict = yaml_dict[scope.value]
                except KeyError:
                    raise KeyError(f"'{scope.value}' not found in: {{{yaml_dict.keys()}}}")

            return sqlalchemy.engine.url.URL.create(
                **yaml_dict
            ), scope

    def session(self):
        """
        Returns
        -------
        sqlalchemy.orm.Session
        """
        return sqlalchemy.orm.Session(self.engine)

    def create_all_tables(self):
        """Setup schema according to all tables within scope under `cosmic_database.entities`."""
        return entities.Base.metadata.create_all(
            self.engine,
            tables = [
                entities.Base.metadata.tables[entity.__tablename__]
                for entity in entities.DATABASE_SCOPES[self.scope]
            ]
        )

    def commit_entity(self, entity):
        with self.session() as session:
            session.add(entity)
            session.commit()
            session.refresh(entity)

    def commit_entities(self, entities: list):
        with self.session() as session:
            session.add_all(entities)
            session.commit()

    def select_entity(self, entity_class, session=None, **criteria_kwargs):
        if session is None:
            with self.session() as session:
                return self.select_entity(entity_class, session, **criteria_kwargs)

        return session.scalars(
            sqlalchemy.select(entity_class)
            .where(*[
                getattr(entity_class, colname) == colval
                for colname, colval in criteria_kwargs.items()
            ])
        ).one_or_none()

    def update_entity(self,
        session,
        entity,
        field_update_filter=None,
        assert_exists=False
    ):
        # Returns 
        remote_entity = self.select_entity(
            session,
            entity.__class__,
            **{
               col.name: getattr(entity, col.name)
                for col in entity.__table__.columns
                if col.primary_key
            }
        )
        if remote_entity is None:
            if assert_exists:
                raise AssertionError(f"Provided entity does not exist for update: {entity}.")
            return True, entity
        
        for col in entity.__table__.columns:
            if col.primary_key:
                continue
            if field_update_filter is not None and col.name not in field_update_filter:
                continue
            setattr(remote_entity, col.name, getattr(entity, col.name))
        return False, remote_entity

    def update_entity_and_commit(self,
        session,
        entity,
        field_update_filter=None,
        assert_exists=False
    ):
        is_new, ent = self.update_entity(
            session,
            entity,
            field_update_filter=field_update_filter,
            assert_exists=assert_exists
        )
        if is_new:
            session.add(ent)
        session.commit()
        
        session.refresh(ent)
        return ent

def get_storage_filesystem_latest_mount(
    engine_conf_yaml_filepath: str
):
    cosmicdb_operation_engine = CosmicDB_Engine(engine_conf_yaml_filepath, scope=entities.DatabaseScope.Operation)
    cosmicdb_storage_engine = CosmicDB_Engine(engine_conf_yaml_filepath, scope=entities.DatabaseScope.Storage)
    storage_filesystem_uuid = cosmicdb_storage_engine.select_entity(
        entities.CosmicDB_StorageDatabaseInfo
    ).filesystem_uuid
    assert storage_filesystem_uuid is not None # not nullable, so should be impossible
    filesystem_entity = cosmicdb_operation_engine.select_entity(
        entities.CosmicDB_Filesystem,
        uuid = storage_filesystem_uuid
    )
    assert filesystem_entity is not None, f"No Operation Filesystem entity with UUID: {storage_filesystem_uuid}"

    with cosmicdb_operation_engine.session() as session:
        return filesystem_entity.get_latest_mount(session)

def get_storage_filesystem_latest_network_uri(
    engine_conf_yaml_filepath: str
):
    storage_filesystem_latest_mount = get_storage_filesystem_latest_mount(engine_conf_yaml_filepath)
    assert storage_filesystem_latest_mount.is_current(), f"Filesystem's latest mount is closed: {storage_filesystem_latest_mount}"
    assert storage_filesystem_latest_mount.network_uri is not None, f"No given network mount for the filesystem's latest mount: {storage_filesystem_latest_mount}"
    return storage_filesystem_latest_mount.network_uri

def cli_add_engine_arguments(parser, add_scope_argument: bool = True):
    parser.add_argument(
        "--engine-configuration",
        type=str,
        default="/home/cosmic/conf/cosmicdb_v2.0_conf.yaml",
        help="The YAML file path containing the instantiation arguments for the SQLAlchemy.engine.url.URL instance specifying the database."
    )
    if add_scope_argument is not False:
        parser.add_argument(
            "--scope",
            type=str,
            default=None,
            choices=[
                v
                for v, __ in entities.DatabaseScope.__members__.items()
            ],
            help="Scope selection for multi-scope configurations."
        )

def cli_parse_engine_scope_argument(args):
    if hasattr(args, "scope") and args.scope is not None:
        args.scope = entities.DatabaseScope(args.scope)
    else:
        try:
            args.scope = entities.ENTITY_SCOPE_MAP[args.entity]
        except KeyError as err:
            raise ValueError(f"args.entity is not scoped: {args.entity}") from err

def cli_create_all_tables():
    import argparse
    
    parser = argparse.ArgumentParser(
        description="COSMIC Database: create all the tables.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "-u", "--engine-url",
        type=str,
        default=None,
        help="The SQLAlchemy.engine.url.URL string specifying the database."
    )
    cli_add_engine_arguments(parser)

    args = parser.parse_args()
    cli_parse_engine_scope_argument(args)
    
    engine = CosmicDB_Engine(engine_url = args.engine_url, engine_conf_yaml_filepath = args.engine_configuration, scope = args.scope)
    engine.create_all_tables()


def cli_create_engine_url():
    import argparse
    
    parser = argparse.ArgumentParser(
        description="COSMIC Database: show the URL generated from a configuration file.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    cli_add_engine_arguments(parser)

    args = parser.parse_args()
    cli_parse_engine_scope_argument(args)

    url, scope = CosmicDB_Engine._create_url(args.engine_configuration, args.scope)
    print(f"{scope.value}: '{url}'")


criterion_operations = {
    "is": lambda lhs, rhs: lhs.is_(rhs),
    "isnot": lambda lhs, rhs: lhs.is_not(rhs),
    "eq": lambda lhs, rhs: lhs == rhs,
    "gt": lambda lhs, rhs: lhs > rhs,
    "geq": lambda lhs, rhs: lhs >= rhs,
    "lt": lambda lhs, rhs: lhs < rhs,
    "leq": lambda lhs, rhs: lhs <= rhs,
    "neq": lambda lhs, rhs: lhs != rhs,
    "in": lambda lhs, rhs: lhs.in_(rhs),
    "like": lambda lhs, rhs: lhs.like(rhs),
    "ilike": lambda lhs, rhs: lhs.ilike(rhs),
    "contains": lambda lhs, rhs: lhs.contains(rhs),
    "icontains": lambda lhs, rhs: lhs.icontains(rhs),
    "startswith": lambda lhs, rhs: lhs.startswith(rhs),
    "istartswith": lambda lhs, rhs: lhs.istartswith(rhs),
    "endswith": lambda lhs, rhs: lhs.endswith(rhs),
    "iendswith": lambda lhs, rhs: lhs.iendswith(rhs),
}

order_operations = {
    "asc": lambda col: col.asc(),
    "desc": lambda col: col.desc(),
}

value_conversions = {
    datetime: lambda val: datetime.fromisoformat(val),
    int: lambda val: int(val),
    float: lambda val: float(val),
    str: lambda val: val,
    bool: lambda val: str(val).lower()[0] == "t",
}

def cli_replace_fieldnames_with_column_instances(
    entity_class_map,
    fieldnames: list,
    element_getter = lambda element: element,
    element_setter = lambda element, replacement: replacement
):
    entity_col_map = {
        entity: {
            col.name: col
            for col in entity_class.__table__.columns

        }
        for entity, entity_class in entity_class_map.items()
    }

    ret_list = []
    for el_ in fieldnames:
        el = element_getter(el_)
        entity = None

        if "." in el:
            relation, relation_el = el.rsplit(".", maxsplit=1)
            if relation in entity_col_map:
                entity = relation
                el = relation_el

        col_map = entity_col_map[entity]

        try:
            replacement = col_map[el]
        except KeyError as err:
            entity_class = entity_class_map[entity]
            raise KeyError(f"{err.args[0]} not found as a column in the table ('{entity_class.__table__}') for {entity_class}.")
        ret_list.append(element_setter(el_, replacement))

    return ret_list

def cli_add_where_argument(parser):
    parser.add_argument(
        "-w",
        "--where-criteria",
        type=str,
        nargs=3,
        action="append",
        metavar=("field", "comparison", "value[;value;...]"),
        help=f"""
            Instance selection field criterion.
            The comparison value is an element of {', '.join(criterion_operations.keys())}.
            Only the 'in' operator supports multiple values, which are semi-colon delimited.
            DateTime values must be given as ISO formatted strings.
        """,
    )

def cli_parse_where_criterion(operand, operator: str, value:str):
    if operator not in criterion_operations:
        raise ValueError(
            f"Specified comparison operation '{operator}' is not known."
        )

    value_type = type(operand)
    if isinstance(operand, sqlalchemy.sql.schema.Column):
        value_type = operand.type.python_type
    elif isinstance(operand, list):
        raise ValueError("Where criterion for a list is not supported.")

    if operator == "in":
        value = list(
            map(
                value_conversions[value_type],
                value.split(';')
            )
        )
    else:
        if value_type not in value_conversions:
            assert value in ["null", "none", "None", "NULL"], f"Can only compare entity ({operand}) against `None`."
            assert operator in ["is", "isnot"], f"Only 'is' and 'isnot' compare entities ({operand})."
            return criterion_operations[operator](operand, None)

        if value in ["null", "none", "None", "NULL"]:
            value = None
        else:
            assert operator not in ["is", "isnot"], f"Only use 'is' and 'isnot' to compare entities."
            value = value_conversions[value_type](value)
    return criterion_operations[operator](operand, value)

def cli_parse_where_arguments(entity_class_map, where_criteria: list):
    if where_criteria is None:
        return []

    return [
        cli_parse_where_criterion(column, comp, val)
        for column, comp, val in cli_replace_fieldnames_with_column_instances(
            entity_class_map,
            where_criteria,
            element_getter=lambda el: el[0],
            element_setter=lambda el, replacement: (replacement, *el[1:])
        )
    ]

def cli_add_orderby_argument(parser):
    parser.add_argument(
        "-o",
        "--orderby",
        nargs=2,
        type=str,
        metavar=("field", "direction"),
        default=None,
        help=f"Order the selected instances. 'direction' is an element of {order_operations.keys()}."
    )

def cli_parse_orderby_argument(entity_class_map, orderby):
    if orderby is None:
        return None
    field, direction = orderby
    if direction not in order_operations:
        raise ValueError(f"Specified order-by direction '{direction}' is not known.")
    return order_operations[direction](
        cli_replace_fieldnames_with_column_instances(
            entity_class_map,
            [field]
        )[0]
    )

def cli_alter_db():
    import argparse

    parser = argparse.ArgumentParser(
        description="Minor interface to create or drop COSMIC database tables and columns.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    cli_add_engine_arguments(parser, add_scope_argument=False)
    parser.add_argument(
        "entity",
        type=str,
        choices=[
            m.class_.__qualname__[9:] # after 'CosmicDB_' prefix
            for m in entities.Base.registry.mappers
        ],
        help="The entity to alter.",
    )
    parser.add_argument(
        "field",
        nargs="?",
        type=str,
        default=None,
        help="The field of the entity to alter (omit to affect the entity's table).",
    )
    parser.add_argument(
        "-d", "--drop",
        action="store_true",
        help="Remove the field from the entity.",
    )
    parser.add_argument(
        "-c", "--create",
        action="store_true",
        help="Create the table for the entity.",
    )

    args = parser.parse_args()
    
    assert sum([args.drop, args.create]) == 1, "Choose one alteration!"

    entity_name = f"CosmicDB_{args.entity}"
    args.entity = getattr(entities, entity_name)
    cli_parse_engine_scope_argument(args)

    engine = CosmicDB_Engine(engine_conf_yaml_filepath=args.engine_configuration, scope=args.scope)
    assert args.entity in entities.DATABASE_SCOPES[engine.scope]
    if args.field is None:
        if args.create:
            args.entity.__table__.create(engine.engine)
        elif args.drop:
            args.entity.__table__.drop(engine.engine)
        return
    
    from alembic.migration import MigrationContext
    from alembic.operations import Operations

    with engine.engine.connect() as conn:
        ctx = MigrationContext.configure(conn)
        op = Operations(ctx)

        args.field = getattr(args.entity, args.field)
        if args.create:
            op.add_column(args.entity.__table__.fullname, args.field)
        elif args.drop:
            op.drop_column(args.entity.__table__.fullname, args.field.name)

def cli_write_filesystem_mount():
    import argparse
    from datetime import datetime
    now_str = datetime.now().isoformat()

    parser = argparse.ArgumentParser(
        description="Minor interface to write COSMIC FilesystemMount and Filesystem entities.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    cli_add_engine_arguments(parser, add_scope_argument=False)
    
    parser.add_argument(
        "--uuid",
        type=str,
        required=True,
        help="The filesystem's uuid, see `$ lsblk -o name,size,mountpoint,label,uuid`.",
    )
    parser.add_argument(
        "--host",
        type=str,
        required=True,
        help="The host of the filesystem.",
    )
    parser.add_argument(
        "--label",
        type=str,
        default=None,
        help="The filesystem's label, see `$ lsblk -o name,size,mountpoint,label,uuid`. Optional for existing Filesystems.",
    )
    parser.add_argument(
        "--time",
        type=str,
        default=now_str,
        help="The start time of mount (ISO format, `date -Iseconds`). Is also set as the end time of the prior mount. Defaults to now.",
    )
    parser.add_argument(
        "--first-mount",
        action='store_true',
        help="Expect no previous mount history.",
    )
    parser.add_argument(
        "--prompt",
        action='store_true',
        help="Prompt before committing.",
    )

    args = parser.parse_args()


    engine = CosmicDB_Engine(
        engine_conf_yaml_filepath=args.engine_configuration,
        scope=entities.DatabaseScope.Operation
    )
    with engine.session() as session:
        filesystem_entity = session.scalars(
            sqlalchemy.select(
                entities.CosmicDB_Filesystem
            ).where(
                entities.CosmicDB_Filesystem.uuid == args.uuid
            )
        ).one_or_none()
        if filesystem_entity is None:
            assert args.first_mount, f"Filesystem is new to the database."

            filesystem_entity = entities.CosmicDB_Filesystem(
                uuid=args.uuid,
                label=args.label,
            )
            session.add(filesystem_entity)
            print(f"Committing: {filesystem_entity}")
            if args.prompt:
                assert input("Continue (Y/n)? ") in ["Y", "y", "yes", ""]
            session.commit()
        else:
            last_mount = filesystem_entity.get_latest_mount(session)
            if args.first_mount:
                assert last_mount is None, f"Unexpected previous mount for existing filesystem: {last_mount}.\nRemove `--first-mount`."
            else:
                assert last_mount is not None, f"No previous mount to close for existing: {filesystem_entity}.\nConsider `--first-mount`."

                assert last_mount.is_current()
                last_mount.end = value_conversions[datetime](args.time)
                print(f"Updated: {last_mount}")
                if args.prompt:
                    assert input("Continue (Y/n)? ") in ["Y", "y", "yes", ""]
                session.commit()
        
        filesystem_mount_entity = entities.CosmicDB_FilesystemMount(
            filesystem_uuid=args.uuid,
            host=args.host,
            host_mountpoint=f"/srv/{filesystem_entity.label}",
            network_uri=f"/mnt/{args.host}/{filesystem_entity.label}",
            start=value_conversions[datetime](args.time)
        )

        print(f"Committing: {filesystem_mount_entity}")
        if args.prompt:
            assert input("Continue (Y/n)? ") in ["Y", "y", "yes", ""]
        session.add(filesystem_mount_entity)
        session.commit()

def cli_write():
    import argparse

    parser = argparse.ArgumentParser(
        description="Minor interface to write COSMIC database entities.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    cli_add_engine_arguments(parser, add_scope_argument=False)
    parser.add_argument(
        "entity",
        type=str,
        choices=[
            m.class_.__qualname__[9:] # after 'CosmicDB_' prefix
            for m in entities.Base.registry.mappers
        ],
        help="The entity to alter.",
    )
    parser.add_argument(
        "fields",
        nargs="*",
        action="extend",
        metavar=("'name value' pair"),
        help="The entity's field and value.",
    )

    args = parser.parse_args()

    entity_name = f"CosmicDB_{args.entity}"
    args.entity = getattr(entities, entity_name)

    cli_parse_engine_scope_argument(args)

    assert len(args.fields)%2 == 0, "Provide field names and values in pairs."
    given_field_values = {
        args.fields[i+0]: args.fields[i+1]
        for i in range(0, len(args.fields), 2)
    }

    field_values = {}
    for field, column in entities.Base.metadata.tables[args.entity.__tablename__].columns.items():
        if field not in given_field_values:
            assert (column.primary_key and column.type.python_type == int) or column.nullable, f"No required value provided for '{field}': {column.type.python_type.__name__} ({column.type})"
            continue
        
        field_values[field] = value_conversions[
            column.type.python_type
        ](given_field_values.pop(field))
    
    assert len(given_field_values) == 0, f"Provided extraneous values: {given_field_values}"
    
    entity = args.entity(**field_values)

    engine = CosmicDB_Engine(engine_conf_yaml_filepath=args.engine_configuration, scope=args.scope)
    with engine.session() as session:
        session.add(entity)
        try:
            session.commit()
        except BaseException as err:
            raise ValueError(f"{entity}") from err

        session.refresh(entity)
        print(entity)

def cli_inspect():
    import argparse

    parser = argparse.ArgumentParser(
        description="Minor interface to expose COSMIC database entities.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    cli_add_engine_arguments(parser, add_scope_argument=False)
    parser.add_argument(
        "--pandas-output-filepath",
        type=str,
        default=None,
        help="The output file path to which a pandas-dataframe-pickle of the results are written.",
    )
    parser.add_argument(
        "entity",
        type=str,
        choices=[
            m.class_.__qualname__[9:] # after 'CosmicDB_' prefix
            for m in entities.Base.registry.mappers
        ],
        help="The entity to view.",
    )
    cli_add_where_argument(parser)
    parser.add_argument(
        "-S",
        "--entity-schema",
        action="store_true",
        help="Show the structure of the entity instead of an instance."
    )
    parser.add_argument(
        "-d",
        "--distinct",
        action="store_true",
        help="Specify that the results should be distinct. Particularly useful with join queries that have sparse selections."
    )
    parser.add_argument(
        "-l",
        "--limit",
        type=int,
        default=None,
        help="Limit the number of instances selected."
    )
    parser.add_argument(
        "--pandas-chunksize",
        type=int,
        default=int(1e6),
        help="The pandas chunksize limit for queries."
    )
    cli_add_orderby_argument(parser)    
    parser.add_argument(
        "-v",
        "--verbosity",
        action="count",
        default=0,
        help="Increase the verbosity of the entity strings."
    )
    parser.add_argument(
        "-s",
        "--select",
        action="append",
        type=str,
        metavar="field",
        default=None,
        help=f"Specify a field selection. The asterisk (*) symbol will select all fields, but usually needs to be encapsulated in quotes."
    )
    parser.add_argument(
        "-j",
        "--join",
        action="append",
        type=str,
        metavar="relationship",
        default=None,
        help=f"Specify a relationship to join on."
    )
    parser.add_argument(
        "--show-dataframe",
        action="store_true",
        help="Show the results as dataframe."
    )

    args = parser.parse_args()

    entity_name = f"CosmicDB_{args.entity}"
    args.entity = getattr(entities, entity_name)
    cli_parse_engine_scope_argument(args)

    if args.entity_schema:
        print(entities.Base.schema_string(args.entity))
        return

    """
    The default entity is keyed under `None`. All relations are keyed
    under the names of the relationship-field for the default entity.
    """
    entity_class_map = {
        None: args.entity
    }
    join = []
    if args.join is not None:
        for relation in args.join:
            entity_key = None
            if "." in relation:
                removed_relation, relation_field = relation.rsplit(".", maxsplit=1)
                if removed_relation in entity_class_map:
                    entity_key = removed_relation
                    relation = relation_field
                else:
                    print(f"If join '{relation}' was meant to be that of the '{removed_relation}' removed relation, --join that removed relation prior.")
                    break
            entity = entity_class_map[entity_key]

            if relation not in entity.__mapper__.relationships:
                raise ValueError(f"Selected relation '{relation}' is not found in '{entity}'. Relationships are:\n{entity.__mapper__.relationships.keys()}")
            relation_key = relation if entity_key is None else f"{entity_key}.{relation}"
            entity_class_map[relation_key] = entity.__mapper__.relationships[relation].mapper.entity
            join.append(getattr(entity, relation))

    selection = list(entity_class_map.values())
    if args.select is not None:
        selection = []
        for field in args.select:
            entity = args.entity
            if "." in field:
                relation, relation_field = field.rsplit(".", maxsplit=1)
                if relation in entity_class_map:
                    entity = entity_class_map[relation]
                    field = relation_field
                else:
                    print(f"If selection '{field}' was meant to be that of the '{relation}' relation, --join the relation.")
                    break

            if field == "*":
                selection.append(entity)
                continue

            if not hasattr(entity, field):
                raise ValueError(f"Selected field '{field}' is not found in '{entity}'.")
            if field not in entity.__table__.columns:
                raise ValueError(f"Selected field '{field}' is not a column of in '{entity}'.")
            selection.append(
                getattr(entity, field)
            )

    criteria = cli_parse_where_arguments(entity_class_map, args.where_criteria)
    ordering = cli_parse_orderby_argument(entity_class_map, args.orderby)

    sql_query = sqlalchemy.select(*selection)
    for relation in join:
        sql_query = sql_query.join(relation)
    sql_query = (sql_query
        .where(*criteria)
        .order_by(ordering)
        .limit(args.limit)
    )
    if args.distinct:
        sql_query = sql_query.distinct()

    engine = CosmicDB_Engine(
        engine_conf_yaml_filepath=args.engine_configuration,
        scope=args.scope
    )

    pandas_output_filepath_splitext = None
    if (args.show_dataframe
      or args.pandas_output_filepath is not None
      or args.select is not None
    ):
        import pandas
        for chunk_i, df in enumerate(pandas.read_sql_query(
            sql = sql_query,
            con = engine.engine,
            chunksize=args.pandas_chunksize
        )):
            print(f"dataframe #{chunk_i}\n", df)
            if args.pandas_output_filepath is not None:
                if chunk_i == 1:
                    pandas_output_filepath_splitext = os.path.splitext(args.pandas_output_filepath)
                if chunk_i > 0:
                    args.pandas_output_filepath = f"{pandas_output_filepath_splitext[0]}.{chunk_i}{pandas_output_filepath_splitext[1]}"
                print(f"Output: {args.pandas_output_filepath}")
                df.to_pickle(args.pandas_output_filepath)
    else:
        with engine.session() as session:
            results = session.scalars(sql_query).all()
            result_num_str_len = len(str(len(results)))
            for result_enum, result in enumerate(results):
                try:
                    result_str = "\n\t" + "\n\t".join(
                        res._get_str(args.verbosity)
                        for res in result
                    )
                except TypeError:
                    result_str = result._get_str(args.verbosity)
                print(f"#{str(result_enum+1).ljust(result_num_str_len)} {result_str}")
