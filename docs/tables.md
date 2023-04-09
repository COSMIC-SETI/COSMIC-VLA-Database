# Table `cosmic_dataset`

Class `cosmic_database.entities.CosmicDB_Dataset`

Column | Type | Primary Key | Foreign Key(s) | Nullable
-|-|-|-|-
id | VARCHAR | X |  | 

# Table `cosmic_scan`

Class `cosmic_database.entities.CosmicDB_Scan`

Column | Type | Primary Key | Foreign Key(s) | Nullable
-|-|-|-|-
id | VARCHAR | X |  | 
dataset_id | VARCHAR |  | [cosmic_dataset.id](#table-cosmic_dataset) | 
time_start_unix | FLOAT |  |  | 
metadata_json | VARCHAR |  |  | 

# Table `cosmic_observation_configuration`

Class `cosmic_database.entities.CosmicDB_ObservationConfiguration`

Column | Type | Primary Key | Foreign Key(s) | Nullable
-|-|-|-|-
id | VARCHAR | X | [cosmic_scan.id](#table-cosmic_scan) | 
time_start_unix | FLOAT |  |  | 
time_end_unix | FLOAT |  |  | 
criteria_json | VARCHAR |  |  | 
configuration_json | VARCHAR |  |  | 
successful | BOOLEAN |  |  | 

# Table `cosmic_calibration_observation`

Class `cosmic_database.entities.CosmicDB_CalibrationObservation`

Column | Type | Primary Key | Foreign Key(s) | Nullable
-|-|-|-|-
id | VARCHAR | X | [cosmic_scan.id](#table-cosmic_scan) | 
time_start_unix | FLOAT |  |  | 
time_end_unix | FLOAT |  |  | 
criteria_json | VARCHAR |  |  | 
results_uri | VARCHAR |  |  | 
measure | FLOAT |  |  | 
successful | BOOLEAN |  |  | 

# Table `cosmic_target_observation`

Class `cosmic_database.entities.CosmicDB_TargetObservation`

Column | Type | Primary Key | Foreign Key(s) | Nullable
-|-|-|-|-
id | VARCHAR | X | [cosmic_scan.id](#table-cosmic_scan) | 
time_start_unix | FLOAT |  |  | 
time_end_unix | FLOAT |  |  | 
criteria_json | VARCHAR |  |  | 
successful | BOOLEAN |  |  | 

# Table `cosmic_seti_beam`

Class `cosmic_database.entities.CosmicDB_ObservationBeam`

Column | Type | Primary Key | Foreign Key(s) | Nullable
-|-|-|-|-
id | INTEGER | X |  | 
observation_id | VARCHAR |  | [cosmic_target_observation.id](#table-cosmic_target_observation) | 
file_uri | VARCHAR |  |  | 
file_local_enumeration | INTEGER |  |  | 
ra_radians | FLOAT |  |  | 
dec_radians | FLOAT |  |  | 
source | VARCHAR |  |  | 
time_start_unix | FLOAT |  |  | 
time_end_unix | FLOAT |  |  | 

# Table `cosmic_observation_hit`

Class `cosmic_database.entities.CosmicDB_ObservationHit`

Column | Type | Primary Key | Foreign Key(s) | Nullable
-|-|-|-|-
id | INTEGER | X |  | 
beam_id | INTEGER |  | [cosmic_seti_beam.id](#table-cosmic_seti_beam) | 
file_uri | VARCHAR |  |  | 
file_local_enumeration | INTEGER |  |  | 
signal_frequency | FLOAT |  |  | 
signal_index | INTEGER |  |  | 
signal_drift_steps | INTEGER |  |  | 
signal_drift_rate | FLOAT |  |  | 
signal_snr | FLOAT |  |  | 
signal_coarse_channel | INTEGER |  |  | 
signal_beam | INTEGER |  |  | 
signal_num_timesteps | INTEGER |  |  | 
signal_power | FLOAT |  |  | 
signal_incoherent_power | FLOAT |  |  | 
source_name | VARCHAR |  |  | 
fch1_mhz | FLOAT |  |  | 
foff_mhz | FLOAT |  |  | 
tstart | FLOAT |  |  | 
tsamp | FLOAT |  |  | 
ra_hours | FLOAT |  |  | 
dec_degrees | FLOAT |  |  | 
telescope_id | INTEGER |  |  | 
num_timesteps | INTEGER |  |  | 
num_channels | INTEGER |  |  | 
coarse_channel | INTEGER |  |  | 
start_channel | INTEGER |  |  | 

# Table `cosmic_observation_stamp`

Class `cosmic_database.entities.CosmicDB_ObservationStamp`

Column | Type | Primary Key | Foreign Key(s) | Nullable
-|-|-|-|-
id | INTEGER | X |  | 
observation_id | VARCHAR |  | [cosmic_target_observation.id](#table-cosmic_target_observation) | 
file_uri | VARCHAR |  |  | 
file_local_enumeration | INTEGER |  |  | 
source_name | VARCHAR |  |  | 
ra_hours | FLOAT |  |  | 
dec_degrees | FLOAT |  |  | 
fch1_mhz | FLOAT |  |  | 
foff_mhz | FLOAT |  |  | 
tstart | FLOAT |  |  | 
tsamp | FLOAT |  |  | 
telescope_id | INTEGER |  |  | 
num_timesteps | INTEGER |  |  | 
num_channels | INTEGER |  |  | 
num_polarizations | INTEGER |  |  | 
num_antennas | INTEGER |  |  | 
coarse_channel | INTEGER |  |  | 
fft_size | INTEGER |  |  | 
start_channel | INTEGER |  |  | 
schan | INTEGER |  |  | 
signal_frequency | FLOAT |  |  | 
signal_index | INTEGER |  |  | 
signal_drift_steps | INTEGER |  |  | 
signal_drift_rate | FLOAT |  |  | 
signal_snr | FLOAT |  |  | 
signal_beam | INTEGER |  |  | 
signal_coarse_channel | INTEGER |  |  | 
signal_num_timesteps | INTEGER |  |  | 
signal_power | FLOAT |  |  | 
signal_incoherent_power | FLOAT |  |  | 
beam_id | INTEGER |  | [cosmic_seti_beam.id](#table-cosmic_seti_beam) | 
