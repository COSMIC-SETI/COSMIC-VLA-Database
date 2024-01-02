import json
import yaml
from datetime import datetime

import pandas
import sqlalchemy

from cosmic_database import entities

class CosmicDB_Engine:

    def __init__(
        self,
        engine_url: str = None,
        engine_conf_yaml_filepath: str = None,
        **kwargs
    ):
        """
        Parameters
        ----------

        """

        if engine_conf_yaml_filepath is not None:
            engine_url = self._create_url(engine_conf_yaml_filepath)
        
        if engine_url is None:
            raise ValueError("No value provided for the engine URL.")

        kwargs["pool_recycle"] = kwargs.get("pool_recycle", 3600)
        self.engine = sqlalchemy.create_engine(
            engine_url,
            **kwargs
        )
    
    @staticmethod
    def _create_url(engine_conf_yaml_filepath):
        with open(engine_conf_yaml_filepath, "r") as yaml_fio:
            engine_url = sqlalchemy.engine.url.URL.create(
                **yaml.safe_load(yaml_fio)
            )
        return engine_url

    def session(self):
        """
        Returns
        -------
        sqlalchemy.orm.Session
        """
        return sqlalchemy.orm.Session(self.engine)

    def create_all_tables(self):
        """Setup schema according to all tables under `cosmic_database.entities`."""
        return entities.Base.metadata.create_all(self.engine)

    def commit_entity(self, entity):
        with self.session() as session:
            session.add(entity)
            session.commit()
            session.refresh(entity)

    def commit_entities(self, entities: list):
        with self.session() as session:
            session.add_all(entities)
            session.commit()

    def select_entity(self, session, entity_class, **criteria_kwargs):
        return session.execute(
            sqlalchemy.select(entity_class)
            .where(*[
                getattr(entity_class, colname) == colval
                for colname, colval in criteria_kwargs.items()
            ])
        ).scalar_one_or_none()

    def update_entity(self, session, entity, assert_exists=False):
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
            session.add(entity)
        else:
            for col in entity.__table__.columns:
                if not col.primary_key:
                    setattr(remote_entity, col.name, getattr(entity, col.name))
            
        session.commit()
        session.refresh(remote_entity)
        return remote_entity


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
    parser.add_argument(
        "-c", "--engine-configuration",
        type=str,
        default=None,
        help="The YAML file path containing the instantiation arguments for the SQLAlchemy.engine.url.URL instance specifying the database."
    )

    args = parser.parse_args()
    
    engine = CosmicDB_Engine(engine_url = args.engine_url, engine_conf_yaml_filepath = args.engine_configuration)
    engine.create_all_tables()


def cli_create_engine_url():
    import argparse
    
    parser = argparse.ArgumentParser(
        description="COSMIC Database: show the URL generated from a configuration file.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "engine_configuration",
        type=str,
        help="The YAML file path containing the instantiation arguments for the SQLAlchemy.engine.url.URL instance specifying the database."
    )

    args = parser.parse_args()
    
    print(CosmicDB_Engine._create_url(args.engine_configuration))


criterion_operations = {
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
}

def cli_replace_fieldnames_with_column_instances(
    entity_class,
    fieldnames: list,
    element_getter = lambda element: element,
    element_setter = lambda element, replacement: replacement
):
    entity_col_map = {
        col.name: col
        for col in entity_class.__table__.columns
    }

    ret_list = []
    for el_ in fieldnames:
        el = element_getter(el_)

        try:
            replacement = entity_col_map[el]
        except KeyError as err:
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
        value = value_conversions[value_type](value)
    return criterion_operations[operator](operand, value)

def cli_parse_where_arguments(entity_class, where_criteria: list):
    if where_criteria is None:
        return []

    return [
        cli_parse_where_criterion(column, comp, val)
        for column, comp, val in cli_replace_fieldnames_with_column_instances(
            entity_class,
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

def cli_parse_orderby_argument(entity_class, orderby):
    if orderby is None:
        return None
    field, direction = orderby
    if direction not in order_operations:
        raise ValueError(f"Specified order-by direction '{direction}' is not known.")
    return order_operations[direction](
        cli_replace_fieldnames_with_column_instances(
            entity_class,
            [field]
        )[0]
    )

def cli_inspect():
    import argparse

    from cosmic_database import entities

    parser = argparse.ArgumentParser(
        description="Minor interface to expose COSMIC database entities.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--cosmicdb-engine-configuration",
        type=str,
        default="/home/cosmic/conf/cosmicdb_conf.yaml",
        help="The YAML file path specifying the COSMIC database.",
    )
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
        "-s",
        "--entity-schema",
        action="store_true",
        help="Show the structure of the entity instead of an instance."
    )
    parser.add_argument(
        "-l",
        "--limit",
        type=int,
        default=None,
        help="Limit the number of instances selected."
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
        "-S",
        "--select",
        action="append",
        type=str,
        metavar="field",
        default=None,
        help=f"Specify a field selection."
    )

    args = parser.parse_args()

    entity_name = f"CosmicDB_{args.entity}"
    args.entity = getattr(entities, entity_name)

    if args.entity_schema:
        lines = [
            f"{args.entity.__qualname__}",
            f"Table: '{args.entity.__table__}'",
            f"Fields:"
        ]

        value_matrix = []
        col_name_max = max(map(len, (col.name for col in args.entity.__table__.columns)))
        for col in args.entity.__table__.columns:
            value_matrix.append(
                [
                    f"{col.name}{' (PK)' if col.primary_key else ''}",
                    f"{col.type} ({col.type.python_type.__name__})"
                ]
            )
        
        value_matrix_col_maxes = [
            max(map(len, (value_row[coli] for value_row in value_matrix)))
            for coli in range(len(value_matrix[0]))
        ]
        lines += [
            "\t" + " ".join(list(
                map(lambda iv_tup: iv_tup[1].ljust(value_matrix_col_maxes[iv_tup[0]]), enumerate(value_row))
            ))
            for value_row in value_matrix
        ]
        print('\n'.join(lines))

        exit(0)

    selection = [args.entity]
    if args.select is not None:
        selection = []
        for field in args.select:
            if not hasattr(args.entity, field):
                print(f"Selected field '{field}' is not found in '{entity_name}'.")
            selection.append(
                getattr(args.entity, field)
            )

    criteria = cli_parse_where_arguments(args.entity, args.where_criteria)
    ordering = cli_parse_orderby_argument(args.entity, args.orderby)

    engine = CosmicDB_Engine(engine_conf_yaml_filepath=args.cosmicdb_engine_configuration)

    sql_selection = (sqlalchemy
        .select(*selection)
        .where(*criteria)
        .order_by(ordering)
        .limit(args.limit)
    )

    if args.pandas_output_filepath is not None or args.select is not None:
        df = pandas.read_sql_query(
            sql = sql_selection,
            con = engine.engine
        )
        print(df)
        if args.pandas_output_filepath is not None:
            print(f"Output: {args.pandas_output_filepath}")
            df.to_pickle(args.pandas_output_filepath)
    else:
        with engine.session() as session:
            scalars = list(
                session.scalars(sql_selection)
            )
            scalar_num_str_len = len(str(len(scalars)))
            for scalar_enum, scalar in enumerate(scalars):
                print(f"#{str(scalar_enum+1).ljust(scalar_num_str_len)} {scalar._get_str(args.verbosity)}")
