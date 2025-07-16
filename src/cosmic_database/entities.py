import os
from datetime import datetime
from enum import Enum

from typing import List
from typing import Optional
from typing_extensions import Annotated

from sqlalchemy import ForeignKey
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

class DatabaseScope(str, Enum):
    Operation = "Operation"
    Storage = "Storage"

String_DatasetID = Annotated[str, 60]
String_ScanID = Annotated[str, 100]
String_AntennaName = Annotated[str, 4]
String_JSON = str
String_URI = Annotated[str, 255]
String_UUID = Annotated[str, 64]
String_Tuning = Annotated[str, 10]
String_SourceName = Annotated[str, 80]

class Base(DeclarativeBase):
    type_annotation_map = {
        String_DatasetID: String(String_DatasetID.__metadata__[0]),
        String_ScanID: String(String_ScanID.__metadata__[0]),
        String_AntennaName: String(String_AntennaName.__metadata__[0]),
        String_JSON: Text,
        String_URI: String(String_URI.__metadata__[0]),
        String_UUID: String(String_UUID.__metadata__[0]),
        String_Tuning: String(String_Tuning.__metadata__[0]),
        String_SourceName: String(String_SourceName.__metadata__[0]),
        float: Double,
        datetime: DateTime().with_variant(
            mysql.DATETIME(fsp=6), "mysql"
        )
    }

    def schema_string(self):
        lines = [
            f"{self.__qualname__}",
            f"Table: '{self.__table__}'",
            f"Fields:"
        ]

        value_matrix = []
        for col in self.__table__.columns:
            suffix = ''
            if col.primary_key:
                suffix +=' (PK)'
            if len(col.foreign_key) > 0:
                suffix +=' (FK)'
            value_matrix.append(
                [
                    f"{col.name}{suffix}",
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
        lines.append("Relations:")
        for relation, relationship in self.__mapper__.relationships.items():
            lines.append(f"\t{relation}: {relationship.mapper.entity.__qualname__}")

        return "\n".join(lines)

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

            attr_strs.append(f"{key}={getattr(self, key)}")

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

class CosmicDB_Filesystem(Base):
    __tablename__ = f"cosmic_filesystem{TABLE_SUFFIX}"
    uuid: Mapped[String_UUID] = mapped_column(primary_key=True)
    label: Mapped[String_URI]

    # files: Mapped[List["CosmicDB_File"]] = relationship(
    #     back_populates="filesystem"
    # )

    mount_history: Mapped[List["CosmicDB_FilesystemMount"]] = relationship(
        back_populates="filesystem"
    )

    observations: Mapped[List["CosmicDB_Observation"]] = relationship(
        back_populates="archival_filesystem"
    )

class CosmicDB_FilesystemMount(Base):
    __tablename__ = f"cosmic_filesystem_mount{TABLE_SUFFIX}"

    id: Mapped[int] = mapped_column(primary_key=True)
    filesystem_uuid: Mapped[String_UUID] = mapped_column(ForeignKey(f"{CosmicDB_Filesystem.__tablename__}.uuid"), index=True)

    host: Mapped[String_URI]
    host_mountpoint: Mapped[String_URI]
    start: Mapped[datetime] = mapped_column(index=True)
    end: Mapped[Optional[datetime]]

    network_uri: Mapped[Optional[String_URI]]

    filesystem: Mapped["CosmicDB_Filesystem"] = relationship(
        back_populates="mount_history"
    )

class CosmicDB_Dataset(Base):
    __tablename__ = f"cosmic_dataset{TABLE_SUFFIX}"

    id: Mapped[String_DatasetID] = mapped_column(primary_key=True)
    
    scans: Mapped[List["CosmicDB_Scan"]] = relationship(
        back_populates="dataset", cascade="all, delete-orphan"
    )

class CosmicDB_Scan(Base):
    __tablename__ = f"cosmic_scan{TABLE_SUFFIX}"

    id: Mapped[String_ScanID] = mapped_column(primary_key=True)
    dataset_id: Mapped[String_DatasetID] = mapped_column(ForeignKey(f"{CosmicDB_Dataset.__tablename__}.id"), index=True)
    start: Mapped[datetime]
    metadata_json: Mapped[String_JSON]
    
    dataset: Mapped["CosmicDB_Dataset"] = relationship(
        back_populates="scans"
    )

    configurations: Mapped[List["CosmicDB_Configuration"]] = relationship(
        back_populates="scan", cascade="all, delete-orphan"
    )

    observations: Mapped[List["CosmicDB_Observation"]] = relationship(
        back_populates="scan", cascade="all, delete-orphan"
    )

class CosmicDB_Configuration(Base):
    __tablename__ = f"cosmic_configuration{TABLE_SUFFIX}"

    id: Mapped[int] = mapped_column(primary_key=True)
    scan_id: Mapped[String_ScanID] = mapped_column(ForeignKey(f"{CosmicDB_Scan.__tablename__}.id"))

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
    
    observations: Mapped[List["CosmicDB_Observation"]] = relationship(
        back_populates="configuration", cascade="all, delete-orphan"
    )

class CosmicDB_ConfigurationAntenna(Base):
    __tablename__ = f"cosmic_configuration_antenna{TABLE_SUFFIX}"

    name: Mapped[String_AntennaName] = mapped_column(primary_key=True)
    configuration_id: Mapped[int] = mapped_column(ForeignKey(f"{CosmicDB_Configuration.__tablename__}.id"), primary_key=True)
    enumeration: Mapped[int]
    
    configuration: Mapped["CosmicDB_Configuration"] = relationship(
        back_populates="antenna"
    )

class CosmicDB_Observation(Base):
    __tablename__ = f"cosmic_observation{TABLE_SUFFIX}"

    id: Mapped[int] = mapped_column(primary_key=True) # support multiple observations per configuration
    scan_id: Mapped[String_ScanID] = mapped_column(ForeignKey(f"{CosmicDB_Scan.__tablename__}.id"))
    configuration_id: Mapped[int] = mapped_column(ForeignKey(f"{CosmicDB_Configuration.__tablename__}.id"))
    
    calibration_id: Mapped[int] = mapped_column(ForeignKey(f"cosmic_calibration{TABLE_SUFFIX}.id"))

    archival_filesystem_uuid: Mapped[int] = mapped_column(ForeignKey(f"{CosmicDB_Filesystem.__tablename__}.uuid"))

    start: Mapped[datetime]
    end: Mapped[datetime]
    criteria_json: Mapped[String_JSON]
    validity_code: Mapped[int] = mapped_column(default=1) # TODO make this TINYINT...

    
    archival_filesystem: Mapped["CosmicDB_Filesystem"] = relationship(
        back_populates="observations",
    )
    
    configuration: Mapped["CosmicDB_Configuration"] = relationship(
        back_populates="observations",
    )

    scan: Mapped["CosmicDB_Scan"] = relationship(
        back_populates="observations"
    )

    subbands: Mapped[List["CosmicDB_ObservationSubband"]] = relationship(
        back_populates="observation", cascade="all, delete-orphan"
    )

    beams: Mapped[List["CosmicDB_ObservationBeam"]] = relationship(
        back_populates="observation", cascade="all, delete-orphan"
    )

    active_calibration: Mapped[Optional["CosmicDB_Calibration"]] = relationship(
        back_populates="observations_applied",
        foreign_keys=[calibration_id]
    )

class CosmicDB_Calibration(Base):
    __tablename__ = f"cosmic_calibration{TABLE_SUFFIX}"

    id: Mapped[int] = mapped_column(primary_key=True)

    # ID of the observation that calibration was produced by
    observation_id: Mapped[int] = mapped_column(ForeignKey(f"{CosmicDB_Observation.__tablename__}.id"))

    reference_antenna_name: Mapped[String_AntennaName]
    overall_grade: Mapped[float]
    file_uri: Mapped[String_URI]

    observation : Mapped["CosmicDB_Observation"] = relationship(
        foreign_keys=observation_id
    )

    observations_applied : Mapped[List["CosmicDB_Observation"]] = relationship(
        back_populates="active_calibration",
        foreign_keys=CosmicDB_Observation.calibration_id
    )

    antenna: Mapped[List["CosmicDB_AntennaCalibration"]] = relationship(
        back_populates="calibration", cascade="all, delete-orphan"
    )

class CosmicDB_AntennaCalibration(Base):
    __tablename__ = f"cosmic_calibration_antenna_result{TABLE_SUFFIX}"

    calibration_id: Mapped[int] = mapped_column(ForeignKey(f"{CosmicDB_Calibration.__tablename__}.id"), primary_key=True)
    antenna_name: Mapped[String_AntennaName] = mapped_column(primary_key=True)
    tuning: Mapped[String_Tuning] = mapped_column(primary_key=True)

    coarse_channels_processed: Mapped[int]
    coarse_channels_flagged_rfi: Mapped[int]

    calibration: Mapped["CosmicDB_Calibration"] = relationship(
        back_populates="antenna"
    )

class CosmicDB_ObservationSubband(Base):
    __tablename__ = f"cosmic_observation_subband{TABLE_SUFFIX}"

    observation_id: Mapped[int] = mapped_column(ForeignKey(f"{CosmicDB_Observation.__tablename__}.id"), primary_key=True)
    tuning: Mapped[String_Tuning] = mapped_column(primary_key=True)
    subband_offset: Mapped[int] = mapped_column(primary_key=True)

    percentage_recorded: Mapped[float]
    successful_participation: Mapped[bool]

    node_uri: Mapped[String_URI]
    subband_length: Mapped[int]

    subband_frequency_lower_MHz: Mapped[float]
    subband_bandwidth_MHz: Mapped[float]

    observation: Mapped["CosmicDB_Observation"] = relationship(
        back_populates="subbands"
    )

class CosmicDB_ObservationBeam(Base):
    __tablename__ = f"cosmic_observation_beam{TABLE_SUFFIX}"

    observation_id: Mapped[int] = mapped_column(ForeignKey(f"{CosmicDB_Observation.__tablename__}.id"), primary_key=True)
    enumeration: Mapped[int] = mapped_column(primary_key=True) # enumerated from 0 per observation

    ra_radians: Mapped[float] = mapped_column(index=True)
    dec_radians: Mapped[float] = mapped_column(index=True)
    source: Mapped[String_SourceName] = mapped_column(index=True)
    start: Mapped[datetime] = mapped_column(index=True)
    end: Mapped[datetime]

    observation : Mapped["CosmicDB_Observation"] = relationship(
        back_populates="beams"
    )

### Observation Products below ###
# These are stored in a separate database that is local to the storage medium which can be physically relocated

class CosmicDB_StorageDatabaseInfo(Base):
    __tablename__ = f"cosmic_database_info{TABLE_SUFFIX}"

    # single entity per database
    id: Mapped[int] = mapped_column(primary_key=True)

    # Dislocated foreign key
    filesystem_uuid: Mapped[String_UUID] = mapped_column(
        index=True
    )

class CosmicDB_ObservationKey(Base):
    __tablename__ = f"cosmic_observation_key{TABLE_SUFFIX}"

    # This is the primary bridge between the storage database and that of COSMIC
    # Dislocated foreign keys
    observation_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)
    scan_id: Mapped[String_ScanID]
    configuration_id: Mapped[int]

    hits: Mapped[List["CosmicDB_ObservationHit"]] = relationship(
        back_populates="observation_key", cascade="all, delete-orphan"
    )

    stamps: Mapped[List["CosmicDB_ObservationStamp"]] = relationship(
        back_populates="observation_key", cascade="all, delete-orphan"
    )

class CosmicDB_File(Base):
    __tablename__ = f"cosmic_file{TABLE_SUFFIX}"

    id: Mapped[int] = mapped_column(primary_key=True)

    local_uri: Mapped[String_URI] = mapped_column(index=True, unique=True)
    
    flags: Mapped["CosmicDB_FileFlags"] = relationship(
        back_populates="file",
    )


class CosmicDB_FileFlags(Base):
    __tablename__ = f"cosmic_file_flags{TABLE_SUFFIX}"
    file_id: Mapped[int] = mapped_column(ForeignKey(f"{CosmicDB_File.__tablename__}.id"), primary_key=True)
    
    missing: Mapped[Optional[bool]]
    irregular_filename: Mapped[Optional[bool]]
    to_delete: Mapped[Optional[bool]]
    no_known_dataset: Mapped[Optional[bool]]

    file: Mapped["CosmicDB_File"] = relationship(
        back_populates="flags"
    )

class CosmicDB_ObservationStamp(Base):
    __tablename__ = f"cosmic_observation_stamp{TABLE_SUFFIX}"
    
    id: Mapped[int] = mapped_column(primary_key=True)

    observation_id: Mapped[int] = mapped_column(ForeignKey(f"{CosmicDB_ObservationKey.__tablename__}.observation_id"))

    # Dislocated foreign keys
    tuning: Mapped[String_Tuning]
    subband_offset: Mapped[int]

    file_id: Mapped[int] = mapped_column(ForeignKey(f"{CosmicDB_File.__tablename__}.id"), index=True)
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
    # Which beam this top-hit is in. -1 for incoherent beam, or no beam, enumerated from 0
    signal_coarse_channel: Mapped[int]
    # The number of timesteps in the associated filterbank. This does *not* use rounded-up-to-a-power-of-two timesteps.
    signal_num_timesteps: Mapped[int]
    # The total power that is normalized to calculate snr. snr = (power - median) / stdev
    signal_power: Mapped[float]
    # The total power for the same signal, calculated incoherently. This is available in the stamps files, but not in the top-hits files.
    signal_incoherent_power: Mapped[float]
    

    file: Mapped["CosmicDB_File"] = relationship()

    observation_key: Mapped["CosmicDB_ObservationKey"] = relationship(
        back_populates="stamps",
    )

    flags: Mapped["CosmicDB_StampFlags"] = relationship(
        back_populates="stamp",
        foreign_keys="CosmicDB_StampFlags.stamp_id"
    )
    
    hits: Mapped["CosmicDB_ObservationHit"] = relationship(
        back_populates="stamp",
    )

class CosmicDB_ObservationHit(Base):
    __tablename__ = f"cosmic_observation_hit{TABLE_SUFFIX}"
    
    id: Mapped[int] = mapped_column(primary_key=True)

    observation_id: Mapped[int] = mapped_column(ForeignKey(f"{CosmicDB_ObservationKey.__tablename__}.observation_id"))
    
    # Dislocated foreign keys
    tuning: Mapped[String_Tuning]
    subband_offset: Mapped[int]

    stamp_id: Mapped[Optional[int]] = mapped_column(ForeignKey(f"{CosmicDB_ObservationStamp.__tablename__}.id"))

    file_id: Mapped[int] = mapped_column(ForeignKey(f"{CosmicDB_File.__tablename__}.id"), index=True)
    # stamp index within file
    file_local_enumeration: Mapped[int]

    # The frequency the hit starts at
    signal_frequency: Mapped[float]
    # Which frequency bin the hit starts at. This is relative to the coarse channel.
    signal_index: Mapped[int]
    # How many bins the hit drifts over. This counts the drift distance over the full rounded-up power-of-two time range.
    signal_drift_steps: Mapped[int]
    # The drift rate in Hz/s
    signal_drift_rate: Mapped[float]
    # The signal-to-noise ratio for the hit
    signal_snr: Mapped[float]
    # Which coarse channel this hit is in
    signal_coarse_channel: Mapped[int]
    # Which beam this hit is in. -1 for incoherent beam, or no beam, enumerated from 0, effectively ObservationBeam.enumeration
    signal_beam: Mapped[int]
    # The number of timesteps in the associated filterbank. This does *not* use rounded-up-to-a-power-of-two timesteps.
    signal_num_timesteps: Mapped[int]
    # The total power that is normalized to calculate snr. snr = (power - median) / stdev
    signal_power: Mapped[float]

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
    ra_hours: Mapped[float] = mapped_column(index=True)
    # phase center DEC
    dec_degrees: Mapped[float] = mapped_column(index=True)
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


    file: Mapped["CosmicDB_File"] = relationship()

    observation_key: Mapped["CosmicDB_ObservationKey"] = relationship(
        back_populates="hits",
    )

    flags: Mapped["CosmicDB_HitFlags"] = relationship(
        back_populates="hit",
    )

    stamp: Mapped["CosmicDB_ObservationStamp"] = relationship(
        back_populates="hits",
    )

class CosmicDB_HitFlags(Base):
    __tablename__ = f"cosmic_hit_flags{TABLE_SUFFIX}"

    hit_id: Mapped[int] = mapped_column(ForeignKey(f"{CosmicDB_ObservationHit.__tablename__}.id"), primary_key=True)
    
    sarfi: Mapped[Optional[bool]]
    location_out_of_date: Mapped[Optional[bool]]
    no_stamp: Mapped[Optional[bool]]

    hit: Mapped["CosmicDB_ObservationHit"] = relationship(
        back_populates="flags"
    )

class CosmicDB_StampFlags(Base):
    __tablename__ = f"cosmic_stamp_flags{TABLE_SUFFIX}"

    stamp_id: Mapped[int] = mapped_column(ForeignKey(f"{CosmicDB_ObservationStamp.__tablename__}.id"), primary_key=True)
    
    sarfi: Mapped[Optional[bool]]
    location_out_of_date: Mapped[Optional[bool]]
    redundant_to: Mapped[Optional[int]] = mapped_column(ForeignKey(f"{CosmicDB_ObservationStamp.__tablename__}.id"))
    no_hits: Mapped[Optional[bool]]

    stamp: Mapped["CosmicDB_ObservationStamp"] = relationship(
        back_populates="flags",
        foreign_keys=stamp_id
    )

## Hardcoded meta-data about the overarching database

DATABASE_SCOPES = {
    DatabaseScope.Operation: [
        CosmicDB_Dataset,
        CosmicDB_Scan,
        CosmicDB_Configuration,
        CosmicDB_ConfigurationAntenna,
        CosmicDB_Calibration,
        CosmicDB_AntennaCalibration,
        CosmicDB_Observation,
        CosmicDB_ObservationSubband,
        CosmicDB_ObservationBeam,
        CosmicDB_Filesystem,
        CosmicDB_FilesystemMount,
    ],
    DatabaseScope.Storage: [
        CosmicDB_StorageDatabaseInfo,
        CosmicDB_ObservationKey,
        CosmicDB_File,
        CosmicDB_FileFlags,
        CosmicDB_ObservationStamp,
        CosmicDB_ObservationHit,
        CosmicDB_HitFlags,
        CosmicDB_StampFlags,
    ]
}


# Dislocated foreign key mappings
SCOPE_BRIDGES = {
    CosmicDB_Scan.id: CosmicDB_ObservationKey.scan_id,
    CosmicDB_Configuration.id: CosmicDB_ObservationKey.configuration_id,
    CosmicDB_Observation.id: CosmicDB_ObservationKey.observation_id,
    CosmicDB_ObservationBeam.enumeration: CosmicDB_ObservationHit.signal_beam,
    CosmicDB_Filesystem.uuid: CosmicDB_StorageDatabaseInfo.filesystem_uuid,
}