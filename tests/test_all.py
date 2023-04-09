import os
import json
import yaml
import sqlalchemy

from cosmic_database import entities
from cosmic_database.engine import CosmicDB_Engine

dbconf_filepath = os.path.join(os.path.dirname(__file__), "database_conf.yaml")
print(dbconf_filepath)

engine = CosmicDB_Engine(engine_conf_yaml_filepath=dbconf_filepath, echo=False)

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
    
    engine.commit_entities([
        entities.CosmicDB_Scan(
            id = scan["id"],
            dataset_id = scan["dataset_id"],
            time_start_unix = scan["time_start_unix"],
            metadata_json = json.dumps(scan["metadata_json"]),
        )
        for scan in json_data["scans"]
    ])

    engine.commit_entities([
        entities.CosmicDB_ObservationConfiguration(
            id = config["id"],
            time_start_unix = config["time_start_unix"],
            time_end_unix = config["time_end_unix"],
            criteria_json = json.dumps(config["criteria_json"]),
            configuration_json = json.dumps(config["configuration_json"]),
            successful = config["successful"],
        )
        for config in json_data["configurations"]
    ])

    engine.commit_entities([
        entities.CosmicDB_Observation(
            id = obs["id"],
            time_start_unix = obs["time_start_unix"],
            time_end_unix = obs["time_end_unix"],
            criteria_json = json.dumps(obs["criteria_json"]),
        )
        for obs in json_data["observations"]
    ])

    engine.commit_entities([
        entities.CosmicDB_ObservationSubband(**obs_subband)
        for obs_subband in json_data["observation_subbands"]
    ])

    engine.commit_entities([
        entities.CosmicDB_ObservationBeam(**obs_beam)
        for obs_beam in json_data["observation_beams"]
    ])

    engine.commit_entities([
        entities.CosmicDB_ObservationHit(**obs_hit)
        for obs_hit in json_data["observation_hits"]
    ])

    with engine.session() as session:

        for scan in session.scalars(
            sqlalchemy.select(entities.CosmicDB_Scan)
        ):
            print(scan)
            print(scan.configuration)
            print(scan.observation)
            print(scan.observation.subbands)
            print(scan.observation.beams)
            print(scan.observation.beams[0].hits)
    