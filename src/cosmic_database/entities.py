import os

from typing import List
from typing import Optional
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

TABLE_SUFFIX = os.environ.get("COSMIC_DB_TABLE_SUFFIX", "")

class Base(DeclarativeBase):
    pass

class CosmicDB_Dataset(Base):
    __tablename__ = f"cosmic_dataset{TABLE_SUFFIX}"

    id: Mapped[str] = mapped_column(primary_key=True)
    
    scan: Mapped[List["CosmicDB_Scan"]] = relationship(
        back_populates="dataset", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"COSMIC_DATASET(id={self.id})"

class CosmicDB_Scan(Base):
    __tablename__ = f"cosmic_scan{TABLE_SUFFIX}"

    id: Mapped[str] = mapped_column(primary_key=True)
    dataset_id: Mapped[str] = mapped_column(ForeignKey(f"cosmic_dataset{TABLE_SUFFIX}.id"))
    time_start_unix: Mapped[float]
    metadata_json: Mapped[str]
    
    dataset: Mapped["CosmicDB_Dataset"] = relationship(
        back_populates="scan"
    )

    configuration: Mapped[Optional["CosmicDB_ObservationConfiguration"]] = relationship(
        back_populates="scan", cascade="all, delete-orphan"
    )

    calibration_observation: Mapped[Optional["CosmicDB_CalibrationObservation"]] = relationship(
        back_populates="scan", cascade="all, delete-orphan"
    )

    target_observation: Mapped[Optional["CosmicDB_TargetObservation"]] = relationship(
        back_populates="scan", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"COSMIC_SCAN({', '.join(f'{key}={getattr(self, key)}' for key in ['id', 'time_start_unix'])})"

class CosmicDB_ObservationConfiguration(Base):
    __tablename__ = f"cosmic_observation_configuration{TABLE_SUFFIX}"

    id: Mapped[str] = mapped_column(ForeignKey(f"cosmic_scan{TABLE_SUFFIX}.id"), primary_key=True)
    time_start_unix: Mapped[float]
    time_end_unix: Mapped[float]
    criteria_json: Mapped[str]
    configuration_json: Mapped[str]
    successful: Mapped[bool]

    scan: Mapped["CosmicDB_Scan"] = relationship(
        back_populates="configuration"
    )

    def __repr__(self) -> str:
        return f"COSMIC_OBS_CONF({', '.join(f'{key}={getattr(self, key)}' for key in ['id', 'time_start_unix', 'time_end_unix', 'successful'])})"

class CosmicDB_CalibrationObservation(Base):
    __tablename__ = f"cosmic_calibration_observation{TABLE_SUFFIX}"

    id: Mapped[str] = mapped_column(ForeignKey(f"cosmic_scan{TABLE_SUFFIX}.id"), primary_key=True)
    time_start_unix: Mapped[float]
    time_end_unix: Mapped[float]
    criteria_json: Mapped[str]
    results_uri: Mapped[str]
    measure: Mapped[float]
    successful: Mapped[bool]

    scan: Mapped["CosmicDB_Scan"] = relationship(
        back_populates="calibration_observation"
    )

    def __repr__(self) -> str:
        return f"COSMIC_CAL_OBS({', '.join(f'{key}={getattr(self, key)}' for key in ['id', 'time_start_unix', 'time_end_unix', 'successful'])})"

class CosmicDB_TargetObservation(Base):
    __tablename__ = f"cosmic_target_observation{TABLE_SUFFIX}"

    id: Mapped[str] = mapped_column(ForeignKey(f"cosmic_scan{TABLE_SUFFIX}.id"), primary_key=True)
    time_start_unix: Mapped[float]
    time_end_unix: Mapped[float]
    criteria_json: Mapped[str]
    successful: Mapped[bool]

    scan: Mapped["CosmicDB_Scan"] = relationship(
        back_populates="target_observation"
    )

    beams: Mapped[List["CosmicDB_ObservationBeam"]] = relationship(
        back_populates="observation", cascade="all, delete-orphan"
    )

    stamps: Mapped[List["CosmicDB_ObservationStamp"]] = relationship(
        back_populates="observation", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"COSMIC_TARGET_OBS({', '.join(f'{key}={getattr(self, key)}' for key in ['id', 'time_start_unix', 'time_end_unix', 'successful'])})"

class CosmicDB_ObservationBeam(Base):
    __tablename__ = f"cosmic_seti_beam{TABLE_SUFFIX}"

    id: Mapped[int] = mapped_column(primary_key=True)
    observation_id: Mapped[str] = mapped_column(ForeignKey(f"cosmic_target_observation{TABLE_SUFFIX}.id"))

    file_uri: Mapped[str]
    file_local_enumeration: Mapped[int]

    ra_radians: Mapped[float]
    dec_radians: Mapped[float]
    source: Mapped[str]
    time_start_unix: Mapped[float]
    time_end_unix: Mapped[float]

    observation : Mapped["CosmicDB_TargetObservation"] = relationship(
        back_populates="beams"
    )

    hits: Mapped[List["CosmicDB_ObservationHit"]] = relationship(
        back_populates="beam", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"COSMIC_SETI_BEAM({', '.join(f'{key}={getattr(self, key)}' for key in ['id', 'scan_id', 'ra_radians', 'dec_radians', 'source'])})"

class CosmicDB_ObservationHit(Base):
    __tablename__ = f"cosmic_observation_hit{TABLE_SUFFIX}"

    id: Mapped[int] = mapped_column(primary_key=True)
    beam_id: Mapped[int] = mapped_column(ForeignKey(f"cosmic_seti_beam{TABLE_SUFFIX}.id"))
    
    file_uri: Mapped[str]
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
    source_name: Mapped[str]
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

    def __repr__(self) -> str:
        return f"COSMIC_OBS_HIT({', '.join(f'{key}={getattr(self, key)}' for key in ['file_uri', 'file_local_enumeration'])})"

class CosmicDB_ObservationStamp(Base):
    __tablename__ = f"cosmic_observation_stamp{TABLE_SUFFIX}"

    id: Mapped[int] = mapped_column(primary_key=True)
    observation_id: Mapped[str] = mapped_column(ForeignKey(f"cosmic_target_observation{TABLE_SUFFIX}.id"))

    file_uri: Mapped[str]
    file_local_enumeration: Mapped[int]

    source_name: Mapped[str]
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
    # obsid: Mapped[str]
    
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

    beam_id: Mapped[int] = mapped_column(ForeignKey(f"cosmic_seti_beam{TABLE_SUFFIX}.id"))

    observation: Mapped["CosmicDB_TargetObservation"] = relationship(
        back_populates="stamps"
    )

    def __repr__(self) -> str:
        return f"COSMIC_OBS_STAMP({', '.join(f'{key}={getattr(self, key)}' for key in ['file_uri', 'file_local_enumeration'])})"
