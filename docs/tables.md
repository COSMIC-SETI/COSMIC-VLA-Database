# Table `cosmic_filesystem`

Class [`cosmic_database.entities.CosmicDB_Filesystem`](./classes.md#class-CosmicDB_Filesystem)

Column | Type | Primary Key | Foreign Key(s) | Indexed | Nullable | Unique
-|-|-|-|-|-|-
uuid | VARCHAR(64) | X |  |  |  | 
label | VARCHAR(255) |  |  |  |  | 

# Table `cosmic_filesystem_mount`

Class [`cosmic_database.entities.CosmicDB_FilesystemMount`](./classes.md#class-CosmicDB_FilesystemMount)

Column | Type | Primary Key | Foreign Key(s) | Indexed | Nullable | Unique
-|-|-|-|-|-|-
id | INTEGER | X |  |  |  | 
filesystem_uuid | VARCHAR(64) |  | [cosmic_filesystem](#table-cosmic_filesystem).uuid | X |  | 
host | VARCHAR(255) |  |  |  |  | 
host_mountpoint | VARCHAR(255) |  |  |  |  | 
start | DATETIME |  |  | X |  | 
end | DATETIME |  |  |  | X | 
network_uri | VARCHAR(255) |  |  |  | X | 

# Table `cosmic_dataset`

Class [`cosmic_database.entities.CosmicDB_Dataset`](./classes.md#class-CosmicDB_Dataset)

Column | Type | Primary Key | Foreign Key(s) | Indexed | Nullable | Unique
-|-|-|-|-|-|-
id | VARCHAR(60) | X |  |  |  | 

# Table `cosmic_scan`

Class [`cosmic_database.entities.CosmicDB_Scan`](./classes.md#class-CosmicDB_Scan)

Column | Type | Primary Key | Foreign Key(s) | Indexed | Nullable | Unique
-|-|-|-|-|-|-
id | VARCHAR(100) | X |  |  |  | 
dataset_id | VARCHAR(60) |  | [cosmic_dataset](#table-cosmic_dataset).id | X |  | 
start | DATETIME |  |  |  |  | 
metadata_json | TEXT |  |  |  |  | 

# Table `cosmic_configuration`

Class [`cosmic_database.entities.CosmicDB_Configuration`](./classes.md#class-CosmicDB_Configuration)

Column | Type | Primary Key | Foreign Key(s) | Indexed | Nullable | Unique
-|-|-|-|-|-|-
id | INTEGER | X |  |  |  | 
scan_id | VARCHAR(100) |  | [cosmic_scan](#table-cosmic_scan).id |  |  | 
start | DATETIME |  |  |  |  | 
end | DATETIME |  |  |  |  | 
criteria_json | TEXT |  |  |  |  | 
configuration_json | TEXT |  |  |  |  | 
successful | BOOLEAN |  |  |  |  | 

# Table `cosmic_configuration_antenna`

Class [`cosmic_database.entities.CosmicDB_ConfigurationAntenna`](./classes.md#class-CosmicDB_ConfigurationAntenna)

Column | Type | Primary Key | Foreign Key(s) | Indexed | Nullable | Unique
-|-|-|-|-|-|-
name | VARCHAR(4) | X |  |  |  | 
configuration_id | INTEGER | X | [cosmic_configuration](#table-cosmic_configuration).id |  |  | 
enumeration | INTEGER |  |  |  |  | 

# Table `cosmic_observation`

Class [`cosmic_database.entities.CosmicDB_Observation`](./classes.md#class-CosmicDB_Observation)

Column | Type | Primary Key | Foreign Key(s) | Indexed | Nullable | Unique
-|-|-|-|-|-|-
id | INTEGER | X |  |  |  | 
scan_id | VARCHAR(100) |  | [cosmic_scan](#table-cosmic_scan).id |  |  | 
configuration_id | INTEGER |  | [cosmic_configuration](#table-cosmic_configuration).id |  |  | 
calibration_id | INTEGER |  | [cosmic_calibration](#table-cosmic_calibration).id |  |  | 
archival_filesystem_uuid | VARCHAR(64) |  | [cosmic_filesystem](#table-cosmic_filesystem).uuid |  |  | 
start | DATETIME |  |  |  |  | 
end | DATETIME |  |  |  |  | 
criteria_json | TEXT |  |  |  |  | 
validity_code | INTEGER |  |  |  |  | 

# Table `cosmic_calibration`

Class [`cosmic_database.entities.CosmicDB_Calibration`](./classes.md#class-CosmicDB_Calibration)

Column | Type | Primary Key | Foreign Key(s) | Indexed | Nullable | Unique
-|-|-|-|-|-|-
id | INTEGER | X |  |  |  | 
observation_id | INTEGER |  | [cosmic_observation](#table-cosmic_observation).id |  |  | 
reference_antenna_name | VARCHAR(4) |  |  |  |  | 
overall_grade | DOUBLE |  |  |  |  | 
file_uri | VARCHAR(255) |  |  |  |  | 

# Table `cosmic_calibration_antenna_result`

Class [`cosmic_database.entities.CosmicDB_AntennaCalibration`](./classes.md#class-CosmicDB_AntennaCalibration)

Column | Type | Primary Key | Foreign Key(s) | Indexed | Nullable | Unique
-|-|-|-|-|-|-
calibration_id | INTEGER | X | [cosmic_calibration](#table-cosmic_calibration).id |  |  | 
antenna_name | VARCHAR(4) | X |  |  |  | 
tuning | VARCHAR(10) | X |  |  |  | 
coarse_channels_processed | INTEGER |  |  |  |  | 
coarse_channels_flagged_rfi | INTEGER |  |  |  |  | 

# Table `cosmic_observation_subband`

Class [`cosmic_database.entities.CosmicDB_ObservationSubband`](./classes.md#class-CosmicDB_ObservationSubband)

Column | Type | Primary Key | Foreign Key(s) | Indexed | Nullable | Unique
-|-|-|-|-|-|-
observation_id | INTEGER | X | [cosmic_observation](#table-cosmic_observation).id |  |  | 
tuning | VARCHAR(10) | X |  |  |  | 
subband_offset | INTEGER | X |  |  |  | 
percentage_recorded | DOUBLE |  |  |  |  | 
successful_participation | BOOLEAN |  |  |  |  | 
node_uri | VARCHAR(255) |  |  |  |  | 
subband_length | INTEGER |  |  |  |  | 
subband_frequency_lower_MHz | DOUBLE |  |  |  |  | 
subband_bandwidth_MHz | DOUBLE |  |  |  |  | 

# Table `cosmic_observation_beam`

Class [`cosmic_database.entities.CosmicDB_ObservationBeam`](./classes.md#class-CosmicDB_ObservationBeam)

Column | Type | Primary Key | Foreign Key(s) | Indexed | Nullable | Unique
-|-|-|-|-|-|-
observation_id | INTEGER | X | [cosmic_observation](#table-cosmic_observation).id |  |  | 
enumeration | INTEGER | X |  |  |  | 
ra_radians | DOUBLE |  |  | X |  | 
dec_radians | DOUBLE |  |  | X |  | 
source | VARCHAR(80) |  |  | X |  | 
start | DATETIME |  |  | X |  | 
end | DATETIME |  |  |  |  | 

# Table `cosmic_database_info`

Class [`cosmic_database.entities.CosmicDB_StorageDatabaseInfo`](./classes.md#class-CosmicDB_StorageDatabaseInfo)

Column | Type | Primary Key | Foreign Key(s) | Indexed | Nullable | Unique
-|-|-|-|-|-|-
id | INTEGER | X |  |  |  | 
filesystem_uuid | VARCHAR(64) |  |  | X |  | 

# Table `cosmic_observation_key`

Class [`cosmic_database.entities.CosmicDB_ObservationKey`](./classes.md#class-CosmicDB_ObservationKey)

Column | Type | Primary Key | Foreign Key(s) | Indexed | Nullable | Unique
-|-|-|-|-|-|-
observation_id | INTEGER | X |  |  |  | 
scan_id | VARCHAR(100) |  |  |  |  | 
configuration_id | INTEGER |  |  |  |  | 

# Table `cosmic_file`

Class [`cosmic_database.entities.CosmicDB_File`](./classes.md#class-CosmicDB_File)

Column | Type | Primary Key | Foreign Key(s) | Indexed | Nullable | Unique
-|-|-|-|-|-|-
id | INTEGER | X |  |  |  | 
local_uri | VARCHAR(255) |  |  | X |  | X

# Table `cosmic_file_flags`

Class [`cosmic_database.entities.CosmicDB_FileFlags`](./classes.md#class-CosmicDB_FileFlags)

Column | Type | Primary Key | Foreign Key(s) | Indexed | Nullable | Unique
-|-|-|-|-|-|-
file_id | INTEGER | X | [cosmic_file](#table-cosmic_file).id |  |  | 
missing | BOOLEAN |  |  |  | X | 
irregular_filename | BOOLEAN |  |  |  | X | 
to_delete | BOOLEAN |  |  |  | X | 
no_known_dataset | BOOLEAN |  |  |  | X | 

# Table `cosmic_observation_stamp`

Class [`cosmic_database.entities.CosmicDB_ObservationStamp`](./classes.md#class-CosmicDB_ObservationStamp)

Column | Type | Primary Key | Foreign Key(s) | Indexed | Nullable | Unique
-|-|-|-|-|-|-
id | INTEGER | X |  |  |  | 
observation_id | INTEGER |  | [cosmic_observation_key](#table-cosmic_observation_key).observation_id |  |  | 
tuning | VARCHAR(10) |  |  |  |  | 
subband_offset | INTEGER |  |  |  |  | 
file_id | INTEGER |  | [cosmic_file](#table-cosmic_file).id | X |  | 
file_local_enumeration | INTEGER |  |  |  |  | 
source_name | VARCHAR(80) |  |  |  |  | 
ra_hours | DOUBLE |  |  |  |  | 
dec_degrees | DOUBLE |  |  |  |  | 
fch1_mhz | DOUBLE |  |  |  |  | 
foff_mhz | DOUBLE |  |  |  |  | 
tstart | DOUBLE |  |  |  |  | 
tsamp | DOUBLE |  |  |  |  | 
telescope_id | INTEGER |  |  |  |  | 
num_timesteps | INTEGER |  |  |  |  | 
num_channels | INTEGER |  |  |  |  | 
num_polarizations | INTEGER |  |  |  |  | 
num_antennas | INTEGER |  |  |  |  | 
coarse_channel | INTEGER |  |  |  |  | 
fft_size | INTEGER |  |  |  |  | 
start_channel | INTEGER |  |  |  |  | 
schan | INTEGER |  |  |  |  | 
obsid | VARCHAR(100) |  |  |  |  | 
signal_frequency | DOUBLE |  |  |  |  | 
signal_index | INTEGER |  |  |  |  | 
signal_drift_steps | INTEGER |  |  |  |  | 
signal_drift_rate | DOUBLE |  |  |  |  | 
signal_snr | DOUBLE |  |  |  |  | 
signal_beam | INTEGER |  |  |  |  | 
signal_coarse_channel | INTEGER |  |  |  |  | 
signal_num_timesteps | INTEGER |  |  |  |  | 
signal_power | DOUBLE |  |  |  |  | 
signal_incoherent_power | DOUBLE |  |  |  |  | 

# Table `cosmic_observation_hit`

Class [`cosmic_database.entities.CosmicDB_ObservationHit`](./classes.md#class-CosmicDB_ObservationHit)

Column | Type | Primary Key | Foreign Key(s) | Indexed | Nullable | Unique
-|-|-|-|-|-|-
id | INTEGER | X |  |  |  | 
observation_id | INTEGER |  | [cosmic_observation_key](#table-cosmic_observation_key).observation_id |  |  | 
tuning | VARCHAR(10) |  |  |  |  | 
subband_offset | INTEGER |  |  |  |  | 
stamp_id | INTEGER |  | [cosmic_observation_stamp](#table-cosmic_observation_stamp).id |  | X | 
file_id | INTEGER |  | [cosmic_file](#table-cosmic_file).id | X |  | 
file_local_enumeration | INTEGER |  |  |  |  | 
signal_frequency | DOUBLE |  |  |  |  | 
signal_index | INTEGER |  |  |  |  | 
signal_drift_steps | INTEGER |  |  |  |  | 
signal_drift_rate | DOUBLE |  |  |  |  | 
signal_snr | DOUBLE |  |  |  |  | 
signal_coarse_channel | INTEGER |  |  |  |  | 
signal_beam | INTEGER |  |  |  |  | 
signal_num_timesteps | INTEGER |  |  |  |  | 
signal_power | DOUBLE |  |  |  |  | 
source_name | VARCHAR(80) |  |  |  |  | 
fch1_mhz | DOUBLE |  |  |  |  | 
foff_mhz | DOUBLE |  |  |  |  | 
tstart | DOUBLE |  |  | X |  | 
tsamp | DOUBLE |  |  |  |  | 
ra_hours | DOUBLE |  |  | X |  | 
dec_degrees | DOUBLE |  |  | X |  | 
telescope_id | INTEGER |  |  |  |  | 
num_timesteps | INTEGER |  |  |  |  | 
num_channels | INTEGER |  |  |  |  | 
coarse_channel | INTEGER |  |  |  |  | 
start_channel | INTEGER |  |  |  |  | 

# Table `cosmic_hit_flags`

Class [`cosmic_database.entities.CosmicDB_HitFlags`](./classes.md#class-CosmicDB_HitFlags)

Column | Type | Primary Key | Foreign Key(s) | Indexed | Nullable | Unique
-|-|-|-|-|-|-
hit_id | INTEGER | X | [cosmic_observation_hit](#table-cosmic_observation_hit).id |  |  | 
sarfi | BOOLEAN |  |  |  | X | 
location_out_of_date | BOOLEAN |  |  |  | X | 
no_stamp | BOOLEAN |  |  |  | X | 

# Table `cosmic_stamp_flags`

Class [`cosmic_database.entities.CosmicDB_StampFlags`](./classes.md#class-CosmicDB_StampFlags)

Column | Type | Primary Key | Foreign Key(s) | Indexed | Nullable | Unique
-|-|-|-|-|-|-
stamp_id | INTEGER | X | [cosmic_observation_stamp](#table-cosmic_observation_stamp).id |  |  | 
sarfi | BOOLEAN |  |  |  | X | 
location_out_of_date | BOOLEAN |  |  |  | X | 
redundant_to | INTEGER |  | [cosmic_observation_stamp](#table-cosmic_observation_stamp).id |  | X | 
no_hits | BOOLEAN |  |  |  | X | 
