import json
import yaml
import sqlalchemy

from cosmic_database import entities

class CosmicDB_Engine:

    def __init__(self, conf_yaml_filepath, **kwargs):
        with open(conf_yaml_filepath, "r") as yaml_fio:
            engine_url = sqlalchemy.engine.url.URL.create(
                **yaml.safe_load(yaml_fio)
            )
            # print(engine_url)
            self.engine = sqlalchemy.create_engine(
                engine_url,
                **kwargs
            )

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

    def commit_entities(self, entities: list):
        with self.session() as session:
            session.add_all(entities)
            session.commit()
