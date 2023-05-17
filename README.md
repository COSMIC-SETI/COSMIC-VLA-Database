# COSMIC Database

This library explicates the [entities](./docs/tables.md) of the database used to capture observational results from COSMIC.

The relationships are as follows.

Entity | Relationship | Entity
-|-|-
Dataset | 1:1 | Scan
Scan | 1:* | ObservationConfiguration
Scan | 1:* | Observation
Observation | 1:* | ObservationSubband
Observation | 1:* | ObservationBeam
ObservationBeam | 1:* | ObservationHit
ObservationSubband | 1:* | ObservationStamp
ObservationSubband | 1:* | ObservationHit

## Rundown

The programmatic interface is pythonic, using SQLAlchemy (see the page about using select statements, our implementation uses their Object Relational Mapper (ORM) entities (quickstart)).
The boilerplate script is (selecting CosmicDB_Observation entities that have a start field after 04/09, and before 04/10, and printing each result):

```
from sqlalchemy

from cosmic_database import entities
from cosmic_database.engine import CosmicDB_Engine

engine = CosmicDB_Engine(engine_conf_yaml_filepath="/home/cosmic/conf/cosmicdb_conf.yaml")

with engine.session() as session:
    for result in session.scalars(
        sqlalchemy.select(entities.CosmicDB_Observation)
        .where(
            entities.CosmicDB_Observation.start > datetime.fromisoformat("2023-04-09 00:00:00"),
            entities.CosmicDB_Observation.start < datetime.fromisoformat("2023-04-10 00:00:00"),
        )
    ):
        print(result)
```

Look at the definition for the ORM entities [here](./src/cosmic_database/entities.py) for the definition of nested entities and fields... For instance, the selected `CosmicDB_Observation` ORM entity instance is defined as

```
class CosmicDB_Observation(Base):
    __tablename__ = f"cosmic_observation{TABLE_SUFFIX}"

    id: Mapped[int] = mapped_column(primary_key=True)
    scan_id: Mapped[String_ScanID] = mapped_column(ForeignKey(f"cosmic_scan{TABLE_SUFFIX}.id"))
    configuration_id: Mapped[int] = mapped_column(ForeignKey(f"cosmic_observation_configuration{TABLE_SUFFIX}.id"))
    start: Mapped[datetime]
    end: Mapped[datetime]
    criteria_json: Mapped[String_JSON]

    configuration: Mapped["CosmicDB_ObservationConfiguration"] = relationship()

    scan: Mapped["CosmicDB_Scan"] = relationship(
        back_populates="observations"
    )

    subbands: Mapped[List["CosmicDB_ObservationSubband"]] = relationship(
        back_populates="observation", cascade="all, delete-orphan"
    )

    beams: Mapped[List["CosmicDB_ObservationBeam"]] = relationship(
        back_populates="observation", cascade="all, delete-orphan"
    )
```

I.e. asides from the fields of its cosmic_observation table, it has `CosmicDB_ObservationConfiguration, CosmicDB_Scan, List["CosmicDB_ObservationSubband"], List["CosmicDB_ObservationBeam"]` attributes... these would be accessible in the results of the boilerplate script above (ie result.subbands).

