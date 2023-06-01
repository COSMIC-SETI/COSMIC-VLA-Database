# Table `cosmic_dataset`

Class [`cosmic_database.entities.CosmicDB_Dataset`](./classes.md#class-CosmicDB_Dataset)

Column | Type | Primary Key | Foreign Key(s) | Nullable
-|-|-|-|-
id | VARCHAR(60) | X |  | 

# Table `cosmic_scan`

Class [`cosmic_database.entities.CosmicDB_Scan`](./classes.md#class-CosmicDB_Scan)

Column | Type | Primary Key | Foreign Key(s) | Nullable
-|-|-|-|-
id | VARCHAR(100) | X |  | 
dataset_id | VARCHAR(60) |  | [cosmic_dataset](#table-cosmic_dataset).id | 
start | DATETIME |  |  | 
metadata_json | TEXT |  |  | 

# Table `cosmic_observation_configuration`

Class [`cosmic_database.entities.CosmicDB_ObservationConfiguration`](./classes.md#class-CosmicDB_ObservationConfiguration)

Column | Type | Primary Key | Foreign Key(s) | Nullable
-|-|-|-|-
id | INTEGER | X |  | 
scan_id | VARCHAR(100) |  | [cosmic_scan](#table-cosmic_scan).id | 
start | DATETIME |  |  | 
end | DATETIME |  |  | 
criteria_json | TEXT |  |  | 
configuration_json | TEXT |  |  | 
successful | BOOLEAN |  |  | 

# Table `cosmic_configuration_antenna`

Class [`cosmic_database.entities.CosmicDB_ConfigurationAntenna`](./classes.md#class-CosmicDB_ConfigurationAntenna)

Column | Type | Primary Key | Foreign Key(s) | Nullable
-|-|-|-|-
configuration_id | INTEGER | X | [cosmic_observation_configuration](#table-cosmic_observation_configuration).id | 
name | VARCHAR(4) | X |  | 

# Table `cosmic_observation`

Class [`cosmic_database.entities.CosmicDB_Observation`](./classes.md#class-CosmicDB_Observation)

Column | Type | Primary Key | Foreign Key(s) | Nullable
-|-|-|-|-
id | INTEGER | X |  | 
scan_id | VARCHAR(100) |  | [cosmic_scan](#table-cosmic_scan).id | 
configuration_id | INTEGER |  | [cosmic_observation_configuration](#table-cosmic_observation_configuration).id | 
start | DATETIME |  |  | 
end | DATETIME |  |  | 
criteria_json | TEXT |  |  | 

# Table `cosmic_observation_subband`

Class [`cosmic_database.entities.CosmicDB_ObservationSubband`](./classes.md#class-CosmicDB_ObservationSubband)

Column | Type | Primary Key | Foreign Key(s) | Nullable
-|-|-|-|-
observation_id | INTEGER | X | [cosmic_observation](#table-cosmic_observation).id | 
tuning | VARCHAR(10) | X |  | 
subband_offset | INTEGER | X |  | 
percentage_recorded | DOUBLE |  |  | 
successful_participation | BOOLEAN |  |  | 

# Table `cosmic_observation_calibration`

Class [`cosmic_database.entities.CosmicDB_ObservationCalibration`](./classes.md#class-CosmicDB_ObservationCalibration)

Column | Type | Primary Key | Foreign Key(s) | Nullable
-|-|-|-|-
id | INTEGER | X |  | 
observation_id | INTEGER |  | [cosmic_observation](#table-cosmic_observation).id | 
reference_antenna_name | VARCHAR(4) |  |  | 
flagged_percentage | DOUBLE |  |  | 
overall_grade | DOUBLE |  |  | 
file_uri | VARCHAR(255) |  |  | 

# Table `cosmic_calibration_gain`

Class [`cosmic_database.entities.CosmicDB_CalibrationGain`](./classes.md#class-CosmicDB_CalibrationGain)

Column | Type | Primary Key | Foreign Key(s) | Nullable
-|-|-|-|-
id | INTEGER | X |  | 
calibration_id | INTEGER |  | [cosmic_observation_calibration](#table-cosmic_observation_calibration).id | 
antenna_name | VARCHAR(4) |  |  | 
observation_id | INTEGER |  | [cosmic_observation_subband](#table-cosmic_observation_subband).observation_id | 
tuning | VARCHAR(10) |  | [cosmic_observation_subband](#table-cosmic_observation_subband).tuning | 
subband_offset | INTEGER |  | [cosmic_observation_subband](#table-cosmic_observation_subband).subband_offset | 
subband_channel_index | INTEGER |  |  | 
channel_frequency | DOUBLE |  |  | 
polarization | VARCHAR(10) |  |  | 
gain_real | DOUBLE |  |  | 
gain_imag | DOUBLE |  |  | 
gain_grade | DOUBLE |  |  | 

# Table `cosmic_observation_beam`

Class [`cosmic_database.entities.CosmicDB_ObservationBeam`](./classes.md#class-CosmicDB_ObservationBeam)

Column | Type | Primary Key | Foreign Key(s) | Nullable
-|-|-|-|-
id | INTEGER | X |  | 
observation_id | INTEGER |  | [cosmic_observation](#table-cosmic_observation).id | 
ra_radians | DOUBLE |  |  | 
dec_radians | DOUBLE |  |  | 
source | VARCHAR(80) |  |  | 
start | DATETIME |  |  | 
end | DATETIME |  |  | 

# Table `cosmic_observation_hit`

Class [`cosmic_database.entities.CosmicDB_ObservationHit`](./classes.md#class-CosmicDB_ObservationHit)

Column | Type | Primary Key | Foreign Key(s) | Nullable
-|-|-|-|-
id | INTEGER | X |  | 
beam_id | INTEGER |  | [cosmic_observation_beam](#table-cosmic_observation_beam).id | 
observation_id | INTEGER |  | [cosmic_observation_subband](#table-cosmic_observation_subband).observation_id | 
tuning | VARCHAR(10) |  | [cosmic_observation_subband](#table-cosmic_observation_subband).tuning | 
subband_offset | INTEGER |  | [cosmic_observation_subband](#table-cosmic_observation_subband).subband_offset | 
file_uri | VARCHAR(255) |  |  | 
file_local_enumeration | INTEGER |  |  | 
signal_frequency | DOUBLE |  |  | 
signal_index | INTEGER |  |  | 
signal_drift_steps | INTEGER |  |  | 
signal_drift_rate | DOUBLE |  |  | 
signal_snr | DOUBLE |  |  | 
signal_coarse_channel | INTEGER |  |  | 
signal_beam | INTEGER |  |  | 
signal_num_timesteps | INTEGER |  |  | 
signal_power | DOUBLE |  |  | 
signal_incoherent_power | DOUBLE |  |  | 
source_name | VARCHAR(80) |  |  | 
fch1_mhz | DOUBLE |  |  | 
foff_mhz | DOUBLE |  |  | 
tstart | DOUBLE |  |  | 
tsamp | DOUBLE |  |  | 
ra_hours | DOUBLE |  |  | 
dec_degrees | DOUBLE |  |  | 
telescope_id | INTEGER |  |  | 
num_timesteps | INTEGER |  |  | 
num_channels | INTEGER |  |  | 
coarse_channel | INTEGER |  |  | 
start_channel | INTEGER |  |  | 

# Table `cosmic_observation_stamp`

Class [`cosmic_database.entities.CosmicDB_ObservationStamp`](./classes.md#class-CosmicDB_ObservationStamp)

Column | Type | Primary Key | Foreign Key(s) | Nullable
-|-|-|-|-
id | INTEGER | X |  | 
observation_id | INTEGER |  | [cosmic_observation_subband](#table-cosmic_observation_subband).observation_id | 
tuning | VARCHAR(10) |  | [cosmic_observation_subband](#table-cosmic_observation_subband).tuning | 
subband_offset | INTEGER |  | [cosmic_observation_subband](#table-cosmic_observation_subband).subband_offset | 
file_uri | VARCHAR(255) |  |  | 
file_local_enumeration | INTEGER |  |  | 
source_name | VARCHAR(80) |  |  | 
ra_hours | DOUBLE |  |  | 
dec_degrees | DOUBLE |  |  | 
fch1_mhz | DOUBLE |  |  | 
foff_mhz | DOUBLE |  |  | 
tstart | DOUBLE |  |  | 
tsamp | DOUBLE |  |  | 
telescope_id | INTEGER |  |  | 
num_timesteps | INTEGER |  |  | 
num_channels | INTEGER |  |  | 
num_polarizations | INTEGER |  |  | 
num_antennas | INTEGER |  |  | 
coarse_channel | INTEGER |  |  | 
fft_size | INTEGER |  |  | 
start_channel | INTEGER |  |  | 
schan | INTEGER |  |  | 
obsid | VARCHAR(100) |  |  | 
signal_frequency | DOUBLE |  |  | 
signal_index | INTEGER |  |  | 
signal_drift_steps | INTEGER |  |  | 
signal_drift_rate | DOUBLE |  |  | 
signal_snr | DOUBLE |  |  | 
signal_beam | INTEGER |  |  | 
signal_coarse_channel | INTEGER |  |  | 
signal_num_timesteps | INTEGER |  |  | 
signal_power | DOUBLE |  |  | 
signal_incoherent_power | DOUBLE |  |  | 
beam_id | INTEGER |  | [cosmic_observation_beam](#table-cosmic_observation_beam).id | 
