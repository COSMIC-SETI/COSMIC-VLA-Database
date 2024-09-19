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
from sqlalchemy.orm import RelationshipDirection

from sqlalchemy.dialects import mysql

TABLE_SUFFIX = os.environ.get("COSMIC_DB_TABLE_SUFFIX", "")

from typing_extensions import Annotated

String_DatasetID = Annotated[str, 60]
String_ScanID = Annotated[str, 100]
String_AntennaName = Annotated[str, 4]
String_JSON = str
String_URI = Annotated[str, 255]
String_Tuning = Annotated[str, 10]
String_SourceName = Annotated[str, 80]

class Base(DeclarativeBase):
    type_annotation_map = {
        String_DatasetID: String(60),
        String_ScanID: String(100),
        String_AntennaName: String(4),
        String_JSON: Text,
        String_URI: String(255),
        String_Tuning: String(10),
        String_SourceName: String(80),
        float: Double,
        datetime: DateTime().with_variant(
            mysql.DATETIME(fsp=6), 'mysql'
        )
    }

    def _get_str(
        self,
        verbosity: int = 0,
        join_lines: bool = True,
        include_limitless_strings: bool = False,
        indentation: int = 0,
        object_name: str = None
    ) -> str:
        attr_strs = []
        for key, col in self.__table__.columns.items():
            if type(col.type) == Text and verbosity < 1:
                continue

            attr_strs.append(f'{key}={getattr(self, key)}')

        indentation_str = "\t"*indentation
        primarystr = f"{indentation_str}{'' if object_name is None else f'{object_name}: '}{self.__class__.__name__}({', '.join(attr_strs)})"
        verbosity -= 2
        if verbosity < 0:
            if not join_lines:
                return [primarystr]
            return primarystr

        attr_strs = [primarystr]
        indentation_str += "\t"
        for attr_name, relationship in self.__mapper__.relationships.items():
            if relationship.direction == RelationshipDirection.MANYTOONE:
                continue

            attr = getattr(self, attr_name)
            if attr is None:
                attr_strs.append(f"{indentation_str}{attr_name}: {attr}")
            elif relationship.collection_class is None:
                attr_strs += attr._get_str(
                    verbosity,
                    join_lines=False,
                    include_limitless_strings=include_limitless_strings,
                    indentation=indentation+1,
                    object_name=attr_name
                )
            else:
                if relationship.collection_class == list:
                    attr_strs.append(f"{indentation_str}{attr_name}: [")
                    if len(attr) == 0:
                        attr_strs[-1] += "]"
                        continue

                    attr_enum_str_len = len(str(len(attr)))
                    for attr_idx, attr_ in enumerate(attr):
                        attr_strs += attr_._get_str(
                            verbosity,
                            join_lines=False,
                            include_limitless_strings=include_limitless_strings,
                            indentation=indentation+2,
                            object_name=f"#{str(attr_idx+1).ljust(attr_enum_str_len)}"
                        )
                    attr_strs.append(f"{indentation_str}]")
                else:
                    print("\t", attr_name, relationship.collection_class)

        return "\n".join(attr_strs) if join_lines else attr_strs


    def __repr__(self) -> str:
        return self._get_str(verbosity=0)


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

    antenna: Mapped[List["CosmicDB_ConfigurationAntenna"]] = relationship(
        back_populates="configuration", cascade="all, delete-orphan"
    )

class CosmicDB_ConfigurationAntenna(Base):
    __tablename__ = f"cosmic_configuration_antenna{TABLE_SUFFIX}"

    configuration_id: Mapped[int] = mapped_column(ForeignKey(f"cosmic_observation_configuration{TABLE_SUFFIX}.id"), primary_key=True)
    name: Mapped[String_AntennaName] = mapped_column(primary_key=True)
    
    configuration: Mapped["CosmicDB_ObservationConfiguration"] = relationship(
        back_populates="antenna"
    )

class CosmicDB_Observation(Base):
    __tablename__ = f"cosmic_observation{TABLE_SUFFIX}"

    id: Mapped[int] = mapped_column(primary_key=True)
    scan_id: Mapped[String_ScanID] = mapped_column(ForeignKey(f"cosmic_scan{TABLE_SUFFIX}.id"))
    configuration_id: Mapped[int] = mapped_column(ForeignKey(f"cosmic_observation_configuration{TABLE_SUFFIX}.id"))
    start: Mapped[datetime]
    end: Mapped[datetime]
    criteria_json: Mapped[String_JSON]
    validity_code: Mapped[int] = mapped_column(default=1) # TODO make this TINYINT...

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

    calibration: Mapped[Optional["CosmicDB_ObservationCalibration"]] = relationship(
        back_populates="observation", cascade="all, delete-orphan"
    )

class CosmicDB_ObservationSubband(Base):
    __tablename__ = f"cosmic_observation_subband{TABLE_SUFFIX}"

    observation_id: Mapped[int] = mapped_column(ForeignKey(f"cosmic_observation{TABLE_SUFFIX}.id"), primary_key=True)
    tuning: Mapped[String_Tuning] = mapped_column(primary_key=True)
    subband_offset: Mapped[int] = mapped_column(primary_key=True)
    percentage_recorded: Mapped[float]
    successful_participation: Mapped[bool]
    
    # node_uri: Mapped[String_URI]
    # subband_length: Mapped[int]

    observation: Mapped["CosmicDB_Observation"] = relationship(
        back_populates="subbands"
    )

    hits: Mapped[List["CosmicDB_ObservationHit"]] = relationship(
        back_populates="observation_subband", cascade="all, delete-orphan"
    )

    stamps: Mapped[List["CosmicDB_ObservationStamp"]] = relationship(
        back_populates="observation_subband", cascade="all, delete-orphan"
    )


class CosmicDB_ObservationCalibration(Base):
    __tablename__ = f"cosmic_observation_calibration{TABLE_SUFFIX}"

    id: Mapped[int] = mapped_column(primary_key=True)
    observation_id: Mapped[int] = mapped_column(ForeignKey(f"cosmic_observation{TABLE_SUFFIX}.id"))

    reference_antenna_name: Mapped[String_AntennaName]
    overall_grade: Mapped[float]
    file_uri: Mapped[String_URI]

    observation : Mapped["CosmicDB_Observation"] = relationship(
        back_populates="calibration"
    )

    antenna: Mapped[List["CosmicDB_AntennaCalibration"]] = relationship(
        back_populates="calibration", cascade="all, delete-orphan"
    )

class CosmicDB_AntennaCalibration(Base):
    __tablename__ = f"cosmic_calibration_antenna_result{TABLE_SUFFIX}"

    calibration_id: Mapped[int] = mapped_column(ForeignKey(f"cosmic_observation_calibration{TABLE_SUFFIX}.id"), primary_key=True)
    antenna_name: Mapped[String_AntennaName] = mapped_column(primary_key=True)
    tuning: Mapped[String_Tuning] = mapped_column(primary_key=True)

    coarse_channels_processed: Mapped[int]
    coarse_channels_flagged_rfi: Mapped[int]

    calibration: Mapped["CosmicDB_ObservationCalibration"] = relationship(
        back_populates="antenna"
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
    
    stamps: Mapped[List["CosmicDB_ObservationStamp"]] = relationship(
        back_populates="beam", cascade="all, delete-orphan"
    )

class CosmicDB_ObservationHit(Base):
    __tablename__ = f"cosmic_observation_hit{TABLE_SUFFIX}"

    id: Mapped[int] = mapped_column(primary_key=True)
    # database ObservationBeam primary_key
    beam_id: Mapped[int] = mapped_column(ForeignKey(f"cosmic_observation_beam{TABLE_SUFFIX}.id"))

    # database Observation primary_key 
    observation_id: Mapped[int] = mapped_column(ForeignKey(f"cosmic_observation{TABLE_SUFFIX}.id"))
    # Antenna LO name
    tuning: Mapped[String_Tuning]
    # subband coarse-channel offset (lower bound of subband)
    subband_offset: Mapped[int]

    # storage filepath
    file_uri: Mapped[String_URI]
    # stamp index within file
    file_local_enumeration: Mapped[int]

    # The frequency the top-hit starts at
    signal_frequency: Mapped[float]
    # Which frequency bin the top-hit starts at. This is relative to the coarse channel.
    signal_index: Mapped[int]
    # How many bins the top-hit drifts over. This counts the drift distance over the full rounded-up power-of-two time range.
    signal_drift_steps: Mapped[int]
    # The drift rate in Hz/s
    signal_drift_rate: Mapped[float]
    # The signal-to-noise ratio for the top-hit
    signal_snr: Mapped[float]
    # Which coarse channel this top-hit is in
    signal_coarse_channel: Mapped[int]
    # Which beam this top-hit is in. -1 for incoherent beam, or no beam
    signal_beam: Mapped[int]
    # The number of timesteps in the associated filterbank. This does *not* use rounded-up-to-a-power-of-two timesteps.
    signal_num_timesteps: Mapped[int]
    # The total power that is normalized to calculate snr. snr = (power - median) / stdev
    signal_power: Mapped[float]
    # The total power for the same signal, calculated incoherently. This is available in the stamps files, but not in the top-hits files.
    signal_incoherent_power: Mapped[float]

    # scan source name
    source_name: Mapped[String_SourceName]
    # center-frequency of the first channel in the stamp
    fch1_mhz: Mapped[float]
    # channel bandwidth
    foff_mhz: Mapped[float]
    # start time of stamp (unix)
    tstart: Mapped[float] = mapped_column(index=True)
    # spectrum timespan (seconds)
    tsamp: Mapped[float]
    # phase center RA
    ra_hours: Mapped[float]
    # phase center DEC
    dec_degrees: Mapped[float]
    # telescope ID (Breakthrough listen convention???)
    telescope_id: Mapped[int]
    # spectra count
    num_timesteps: Mapped[int]
    # channel count
    num_channels: Mapped[int]
    # top-hit's coarse-channel index (relative to subband, zero-indexed I believe)
    coarse_channel: Mapped[int]
    # stamp fine-channel index (within coarse-channel)
    start_channel: Mapped[int]

    beam: Mapped["CosmicDB_ObservationBeam"] = relationship(
        back_populates="hits"
    )

    observation: Mapped["CosmicDB_Observation"] = relationship(
        overlaps="hits"
    )

    observation_subband: Mapped["CosmicDB_ObservationSubband"] = relationship(
        back_populates="hits",
        overlaps="observation"
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

    # database Observation primary_key 
    observation_id: Mapped[int] = mapped_column(ForeignKey(f"cosmic_observation{TABLE_SUFFIX}.id"))
    # Antenna LO name
    tuning: Mapped[String_Tuning]
    # subband coarse-channel offset (lower bound of subband)
    subband_offset: Mapped[int]

    # storage filepath
    file_uri: Mapped[String_URI]
    # stamp index within file
    file_local_enumeration: Mapped[int]

    # scan source name
    source_name: Mapped[String_SourceName]
    # phase center RA
    ra_hours: Mapped[float]
    # phase center DEC
    dec_degrees: Mapped[float]
    # center-frequency of the first channel in the stamp
    fch1_mhz: Mapped[float]
    # channel bandwidth
    foff_mhz: Mapped[float]
    # start time of stamp (unix)
    tstart: Mapped[float]
    # spectrum timespan (seconds)
    tsamp: Mapped[float]
    # telescope ID (Breakthrough listen convention???)
    telescope_id: Mapped[int]
    # spectra count
    num_timesteps: Mapped[int]
    # channel count
    num_channels: Mapped[int]
    # polarization count
    num_polarizations: Mapped[int]
    # antenna count
    num_antennas: Mapped[int]
    # top-hit's coarse-channel index (relative to subband, zero-indexed I believe)
    coarse_channel: Mapped[int]
    # upchannelisation rate
    fft_size: Mapped[int]
    # stamp fine-channel index (within coarse-channel)
    start_channel: Mapped[int]
    # subband coarse-channel offset (lower bound of subband)
    schan: Mapped[int]
    # scan observation ID
    obsid: Mapped[String_ScanID]
    
    # The frequency the top-hit starts at
    signal_frequency: Mapped[float]
    # Which frequency bin the top-hit starts at. This is relative to the coarse channel.
    signal_index: Mapped[int]
    # How many bins the top-hit drifts over. This counts the drift distance over the full rounded-up power-of-two time range.
    signal_drift_steps: Mapped[int]
    # The drift rate in Hz/s
    signal_drift_rate: Mapped[float]
    # The signal-to-noise ratio for the top-hit
    signal_snr: Mapped[float]
    # Which coarse channel this top-hit is in
    signal_beam: Mapped[int]
    # Which beam this top-hit is in. -1 for incoherent beam, or no beam
    signal_coarse_channel: Mapped[int]
    # The number of timesteps in the associated filterbank. This does *not* use rounded-up-to-a-power-of-two timesteps.
    signal_num_timesteps: Mapped[int]
    # The total power that is normalized to calculate snr. snr = (power - median) / stdev
    signal_power: Mapped[float]
    # The total power for the same signal, calculated incoherently. This is available in the stamps files, but not in the top-hits files.
    signal_incoherent_power: Mapped[float]

    # database ObservationBeam primary_key
    beam_id: Mapped[int] = mapped_column(ForeignKey(f"cosmic_observation_beam{TABLE_SUFFIX}.id"))

    observation: Mapped["CosmicDB_Observation"] = relationship(
        overlaps="stamps"
    )

    observation_subband: Mapped["CosmicDB_ObservationSubband"] = relationship(
        back_populates="stamps",
        overlaps="observation"
    )
    
    beam: Mapped["CosmicDB_ObservationBeam"] = relationship(
        back_populates="stamps"
    )

    __table_args__ = (
        ForeignKeyConstraint(
            ['observation_id', 'tuning', 'subband_offset'],
            [f'cosmic_observation_subband{TABLE_SUFFIX}.observation_id', f'cosmic_observation_subband{TABLE_SUFFIX}.tuning', f'cosmic_observation_subband{TABLE_SUFFIX}.subband_offset'],
        ),
    )
