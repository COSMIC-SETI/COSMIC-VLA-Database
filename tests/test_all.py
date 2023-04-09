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
        assert engine.select_entity(session, entities.CosmicDB_Dataset, id = json_data["datasets"][0]["id"]) is None

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
        dataset = engine.select_entity(session, entities.CosmicDB_Dataset, id = json_data["datasets"][0]["id"])
        assert dataset is not None
        print(dataset)
    
    engine.commit_entities([
        entities.CosmicDB_Scan(
            id = scan["id"],
            dataset_id = scan["dataset_id"],
            time_start_unix = scan["time_start_unix"],
            metadata_json = json.dumps(scan["metadata_json"]),
        )
        for scan in json_data["scans"]
    ])

    for config in json_data["configurations"]:
        db_config = entities.CosmicDB_ObservationConfiguration(
            scan_id = config["id"],
            time_start_unix = config["time_start_unix"],
            time_end_unix = config["time_end_unix"],
            criteria_json = json.dumps(config["criteria_json"]),
            configuration_json = json.dumps(config["configuration_json"]),
            successful = False,
        )
        engine.commit_entity(db_config)
        print(db_config.id)

    engine.commit_entities([
        entities.CosmicDB_Observation(
            scan_id = obs["scan_id"],
            time_start_unix = obs["time_start_unix"],
            time_end_unix = obs["time_end_unix"],
            criteria_json = json.dumps(obs["criteria_json"]),
        )
        for obs in json_data["observations"]
    ])

    with engine.session() as session:
        for obs_subband in json_data["observation_subbands"]:
            session.add(
                entities.CosmicDB_ObservationSubband(
                    observation_id = engine.select_entity(
                        session,
                        entities.CosmicDB_Scan,
                        id = obs_subband.pop("scan_id")
                    ).observations[-1].id,
                    tuning = obs_subband["tuning"],
                    subband_offset = obs_subband["subband_offset"],
                    percentage_recorded = obs_subband["percentage_recorded"],
                    successful_participation = obs_subband["successful_participation"]
                )
            )

        for obs_beam in json_data["observation_beams"]:
            if "observation_id" not in obs_beam:
                obs_beam["observation_id"] = engine.select_entity(
                    session,
                    entities.CosmicDB_Scan,
                    id = obs_beam.pop("scan_id")
                ).observations[-1].id
            
            session.add(
                entities.CosmicDB_ObservationBeam(**obs_beam)
            )
        session.commit()

    engine.commit_entities([
        entities.CosmicDB_ObservationHit(**obs_hit)
        for obs_hit in json_data["observation_hits"]
    ])

    engine.commit_entities([
        entities.CosmicDB_ObservationStamp(**obs_stamp)
        for obs_stamp in json_data["observation_stamps"]
    ])

    with engine.session() as session:

        for scan in session.scalars(
            sqlalchemy.select(entities.CosmicDB_Scan)
        ):
            print(scan)
            print(scan.configurations)
            print(scan.observations)
            print(scan.observations[-1])
            print(scan.observations[-1].subbands)
            print(scan.observations[-1].beams)
            print(scan.observations[-1].beams[0].hits)
            print(scan.observations[-1].subbands[0].stamps)
            print(scan.observations[-1].subbands[0].hits)
    