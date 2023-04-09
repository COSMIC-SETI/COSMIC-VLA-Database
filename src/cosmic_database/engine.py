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

    def update_entity(self, sesion, entity, assert_exists=False):
        remote_entity = self.select_entity(
            session,
            entity.__class__,
            **{
                getattr(entity.__class__, col.name): getattr(entity, col.name)
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
        # session.execute(
        #     sqlalchemy.update(entity.__class__)
        #     .where(*primary_key_criteria)
        #     .values(**value_updates)
        # )


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
