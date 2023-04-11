import json
import yaml
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
        help="The SQLAlchemy.engine.url.URL string specifying the database."
    )
    parser.add_argument(
        "-c", "--engine-configuration",
        type=str,
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

def cli_inspect():
    import argparse
    from datetime import datetime

    from cosmic_database import entities

    criterion_operations = {
        "eq": lambda lhs, rhs: lhs == rhs,
        "gt": lambda lhs, rhs: lhs > rhs,
        "geq": lambda lhs, rhs: lhs >= rhs,
        "lt": lambda lhs, rhs: lhs < rhs,
        "leq": lambda lhs, rhs: lhs <= rhs,
        "neq": lambda lhs, rhs: lhs != rhs,
        "in": lambda lhs, rhs: lhs.in_(rhs),
    }
    order_operations = {
        "asc": lambda col: col.asc(),
        "desc": lambda col: col.desc(),
    }

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
        "entity",
        type=str,
        choices=[
            m.class_.__qualname__[9:] # after 'CosmicDB_' prefix
            for m in entities.Base.registry.mappers
        ],
        help="The entity to view.",
    )
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
    parser.add_argument(
        "-o",
        "--orderby",
        nargs=2,
        type=str,
        metavar=("field", "direction"),
        default=None,
        help=f"Order the selected instances. 'direction' is an element of {order_operations.keys()}."
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

    value_conversions = {
        datetime: lambda val: datetime.fromisoformat(val),
        int: lambda val: int(val),
        float: lambda val: float(val),
        str: lambda val: val,
    }

    entity_col_map = {
        col.name: col
        for col in args.entity.__table__.columns
    }

    criteria = []
    if args.where_criteria is not None:
        for criterion in args.where_criteria:
            field, comp, val = criterion
            if field not in entity_col_map:
                print(f"Specified field '{field}' is not found in '{entity_name}'.\n\t{criterion}")
                exit(1)
            if comp not in criterion_operations:
                print(f"Specified comparison operation '{comp}' is not known.\n\t{criterion}")
                exit(1)
            
            col = entity_col_map[field]
            if comp == "in":
                value = list(
                    map(
                        value_conversions[col.type.python_type],
                        val.split(';')
                    )
                )
            else:
                value = value_conversions[col.type.python_type](val)
            criteria.append(criterion_operations[comp](col, value))

    ordering = None
    if args.orderby is not None:
        field, direction = args.orderby
        if field not in entity_col_map:
            print(f"Specified field '{field}' is not found in '{entity_name}'.\n\t{args.orderby}")
            exit(1)
        if direction not in order_operations:
            print(f"Specified direction '{direction}' is not known.\n\t{args.orderby}")
            exit(1)
        ordering = order_operations[direction](entity_col_map[field])

    engine = CosmicDB_Engine(engine_conf_yaml_filepath=args.cosmicdb_engine_configuration)

    with engine.session() as session:
        scalars = [
            scalar
            for scalar_enum, scalar in enumerate(session.scalars(
                sqlalchemy.select(args.entity)
                .where(*criteria)
                .order_by(ordering)
            ))
            if args.limit is None or scalar_enum < args.limit
        ]
        scalar_num_str_len = len(str(len(scalars)))
        for scalar_enum, scalar in enumerate(scalars):
            print(f"#{str(scalar_enum+1).ljust(scalar_num_str_len)} {scalar}")
