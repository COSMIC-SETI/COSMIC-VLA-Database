import os
import json
import yaml
import sqlalchemy

from cosmic_database import entities
from cosmic_database.engine import CosmicDB_Engine

dbconf_filepath = os.path.join(os.path.dirname(__file__), "database_conf.yaml")
print(dbconf_filepath)

engine = CosmicDB_Engine(dbconf_filepath, echo=True)

engine.create_all_tables()

data_filepath = os.path.join(os.path.dirname(__file__), "data.json")
print(data_filepath)

with open(data_filepath, "r") as json_fio:
    json_data = json.load(json_fio)

    with engine.session() as session:
        assert session.scalars(
            sqlalchemy.select(entities.CosmicDB_Dataset).where(entities.CosmicDB_Dataset.id == json_data["datasets"][0]["id"])
        ).one_or_none() is None

    engine.commit_entities([
        entities.CosmicDB_Dataset(
            **entitydata
        )
        for entitydata in json_data["datasets"]
    ])
    
    with engine.session() as session:
        assert session.scalars(
            sqlalchemy.select(entities.CosmicDB_Dataset).where(entities.CosmicDB_Dataset.id == json_data["datasets"][0]["id"])
        ).one_or_none() is not None

    engine.commit_entities([
        entities.CosmicDB_Scan(
            id = scan["id"],
            dataset_id = scan["dataset_id"],
            time_start_unix = scan["time_start_unix"],
            metadata_json = json.dumps(scan["metadata_json"]),
        )
        for scan in json_data["scans"]
    ])

    with engine.session() as session:

        for scan in session.scalars(
            sqlalchemy.select(entities.CosmicDB_Scan)#.where(entities.CosmicDB_Scan.time_start_unix.in_([1680675440.009397]))
        ):
            print(scan)
    