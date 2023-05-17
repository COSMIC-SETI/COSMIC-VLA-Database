import os
from datetime import datetime

from typing import List
from typing import Optional
from sqlalchemy import ForeignKey
from sqlalchemy import ForeignKeyConstraint
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy import DateTime
from sqlalchemy import Double
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from sqlalchemy.dialects import mysql

TABLE_SUFFIX = os.environ.get("COSMIC_DB_TABLE_SUFFIX", "")

from typing_extensions import Annotated

String_DatasetID = Annotated[str, 60]
String_ScanID = Annotated[str, 100]
String_JSON = str
String_URI = Annotated[str, 255]
String_Tuning = Annotated[str, 10]
String_SourceName = Annotated[str, 80]

class Base(DeclarativeBase):
    type_annotation_map = {
        String_DatasetID: String(60),
        String_ScanID: String(100),
        String_JSON: Text,
        String_URI: String(255),
        String_Tuning: String(10),
        String_SourceName: String(80),
        float: Double,
        datetime: DateTime().with_variant(
            mysql.DATETIME(fsp=6), 'mysql'
        )
    }

    def _get_str(self, verbosity: int) -> str:
        attr_strs = []
        for key, col in self.__table__.columns.items():
            if verbosity == 0:
                if type(col.type) != Text:
                    continue

            attr_strs.append(f'{key}={col.type}')

        retstr = f"{self.__class__.__name__}({', '.join(attr_strs)})"
        if verbosity == 1:
            return retstr


    def __repr__(self) -> str:
        return _get_str(verbosity=0)


class CosmicDB_Dataset(Base):
    __tablename__ = f"cosmic_dataset{TABLE_SUFFIX}"

    id: Mapped[String_DatasetID] = mapped_column(primary_key=True)
    
    scans: Mapped[List["CosmicDB_Scan"]] = relationship(
        back_populates="dataset", cascade="all, delete-orphan"
    )


class CosmicDB_Scan(Base):
    __tablename__ = f"cosmic_scan{TABLE_SUFFIX}"

    id: Mapped[String_ScanID] = mapped_column(primary_key=True)
    dataset_id: Mapped[String_DatasetID] = mapped_column(ForeignKey(f"cosmic_dataset{TABLE_SUFFIX}.id"))
    start: Mapped[datetime]
    metadata_json: Mapped[String_JSON]
    
    dataset: Mapped["CosmicDB_Dataset"] = relationship(
        back_populates="scans"
    )

    configurations: Mapped[List["CosmicDB_ObservationConfiguration"]] = relationship(
        back_populates="scan", cascade="all, delete-orphan"
    )

    observations: Mapped[List["CosmicDB_Observation"]] = relationship(
        back_populates="scan", cascade="all, delete-orphan"
    )

class CosmicDB_ObservationConfiguration(Base):
    __tablename__ = f"cosmic_observation_configuration{TABLE_SUFFIX}"

    id: Mapped[int] = mapped_column(primary_key=True)
    scan_id: Mapped[String_ScanID] = mapped_column(ForeignKey(f"cosmic_scan{TABLE_SUFFIX}.id"))
    start: Mapped[datetime]
    end: Mapped[datetime]
    criteria_json: Mapped[String_JSON]
    configuration_json: Mapped[String_JSON]
    successful: Mapped[bool]

    scan: Mapped["CosmicDB_Scan"] = relationship(
        back_populates="configurations"
    )

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

class CosmicDB_ObservationSubband(Base):
    __tablename__ = f"cosmic_observation_subband{TABLE_SUFFIX}"

    observation_id: Mapped[int] = mapped_column(ForeignKey(f"cosmic_observation{TABLE_SUFFIX}.id"), primary_key=True)
    tuning: Mapped[String_Tuning] = mapped_column(primary_key=True)
    subband_offset: Mapped[int] = mapped_column(primary_key=True)
    percentage_recorded: Mapped[float]
    successful_participation: Mapped[bool]

    observation: Mapped["CosmicDB_Observation"] = relationship(
        back_populates="subbands"
    )

    hits: Mapped[List["CosmicDB_ObservationHit"]] = relationship(
        back_populates="observation_subband", cascade="all, delete-orphan"
    )

    stamps: Mapped[List["CosmicDB_ObservationStamp"]] = relationship(
        back_populates="observation_subband", cascade="all, delete-orphan"
    )

class CosmicDB_ObservationBeam(Base):
    __tablename__ = f"cosmic_observation_beam{TABLE_SUFFIX}"

    id: Mapped[int] = mapped_column(primary_key=True)
    observation_id: Mapped[int] = mapped_column(ForeignKey(f"cosmic_observation{TABLE_SUFFIX}.id"))

    ra_radians: Mapped[float]
    dec_radians: Mapped[float]
    source: Mapped[String_SourceName]
    start: Mapped[datetime]
    end: Mapped[datetime]

    observation : Mapped["CosmicDB_Observation"] = relationship(
        back_populates="beams"
    )

    hits: Mapped[List["CosmicDB_ObservationHit"]] = relationship(
        back_populates="beam", cascade="all, delete-orphan"
    )

class CosmicDB_ObservationHit(Base):
    __tablename__ = f"cosmic_observation_hit{TABLE_SUFFIX}"

    id: Mapped[int] = mapped_column(primary_key=True)
    beam_id: Mapped[int] = mapped_column(ForeignKey(f"cosmic_observation_beam{TABLE_SUFFIX}.id"))

    observation_id: Mapped[int]
    tuning: Mapped[String_Tuning]
    subband_offset: Mapped[int]

    file_uri: Mapped[String_URI]
    file_local_enumeration: Mapped[int]

    signal_frequency: Mapped[float]
    signal_index: Mapped[int]
    signal_drift_steps: Mapped[int]
    signal_drift_rate: Mapped[float]
    signal_snr: Mapped[float]
    signal_coarse_channel: Mapped[int]
    signal_beam: Mapped[int]
    signal_num_timesteps: Mapped[int]
    signal_power: Mapped[float]
    signal_incoherent_power: Mapped[float]
    source_name: Mapped[String_SourceName]
    fch1_mhz: Mapped[float]
    foff_mhz: Mapped[float]
    tstart: Mapped[float]
    tsamp: Mapped[float]
    ra_hours: Mapped[float]
    dec_degrees: Mapped[float]
    telescope_id: Mapped[int]
    num_timesteps: Mapped[int]
    num_channels: Mapped[int]
    coarse_channel: Mapped[int]
    start_channel: Mapped[int]

    beam: Mapped["CosmicDB_ObservationBeam"] = relationship(
        back_populates="hits"
    )

    observation_subband: Mapped["CosmicDB_ObservationSubband"] = relationship(
        back_populates="hits"
    )

    __table_args__ = (
        ForeignKeyConstraint(
            ['observation_id', 'tuning', 'subband_offset'],
            [f'cosmic_observation_subband{TABLE_SUFFIX}.observation_id', f'cosmic_observation_subband{TABLE_SUFFIX}.tuning', f'cosmic_observation_subband{TABLE_SUFFIX}.subband_offset'],
        ),
    )

class CosmicDB_ObservationStamp(Base):
    __tablename__ = f"cosmic_observation_stamp{TABLE_SUFFIX}"

    id: Mapped[int] = mapped_column(primary_key=True)

    observation_id: Mapped[int]
    tuning: Mapped[String_Tuning]
    subband_offset: Mapped[int]

    file_uri: Mapped[String_URI]
    file_local_enumeration: Mapped[int]

    source_name: Mapped[String_SourceName]
    ra_hours: Mapped[float]
    dec_degrees: Mapped[float]
    fch1_mhz: Mapped[float]
    foff_mhz: Mapped[float]
    tstart: Mapped[float]
    tsamp: Mapped[float]
    telescope_id: Mapped[int]
    num_timesteps: Mapped[int]
    num_channels: Mapped[int]
    num_polarizations: Mapped[int]
    num_antennas: Mapped[int]
    coarse_channel: Mapped[int]
    fft_size: Mapped[int]
    start_channel: Mapped[int]
    # signal: Mapped[float] :Hit.Signal;
    schan: Mapped[int]
    obsid: Mapped[String_ScanID]
    
    signal_frequency: Mapped[float]
    signal_index: Mapped[int]
    signal_drift_steps: Mapped[int]
    signal_drift_rate: Mapped[float]
    signal_snr: Mapped[float]
    signal_beam: Mapped[int]
    signal_coarse_channel: Mapped[int]
    signal_num_timesteps: Mapped[int]
    signal_power: Mapped[float]
    signal_incoherent_power: Mapped[float]

    beam_id: Mapped[int] = mapped_column(ForeignKey(f"cosmic_observation_beam{TABLE_SUFFIX}.id"))

    observation_subband: Mapped["CosmicDB_ObservationSubband"] = relationship(
        back_populates="stamps"
    )

    __table_args__ = (
        ForeignKeyConstraint(
            ['observation_id', 'tuning', 'subband_offset'],
            [f'cosmic_observation_subband{TABLE_SUFFIX}.observation_id', f'cosmic_observation_subband{TABLE_SUFFIX}.tuning', f'cosmic_observation_subband{TABLE_SUFFIX}.subband_offset'],
        ),
    )
