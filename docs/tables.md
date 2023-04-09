# Table `cosmic_dataset`

Class `cosmic_database.entities.CosmicDB_Dataset`

Column | Type | Primary Key | Foreign Key(s) | Nullable
-|-|-|-|-
id | VARCHAR(20) | X |  | 

# Table `cosmic_scan`

Class `cosmic_database.entities.CosmicDB_Scan`

Column | Type | Primary Key | Foreign Key(s) | Nullable
-|-|-|-|-
id | VARCHAR(80) | X |  | 
dataset_id | VARCHAR(20) |  | [cosmic_dataset.id](#table-cosmic_dataset) | 
time_start_unix | FLOAT |  |  | 
metadata_json | TEXT |  |  | 

# Table `cosmic_observation_configuration`

Class `cosmic_database.entities.CosmicDB_ObservationConfiguration`

Column | Type | Primary Key | Foreign Key(s) | Nullable
-|-|-|-|-
id | VARCHAR(80) | X | [cosmic_scan.id](#table-cosmic_scan) | 
time_start_unix | FLOAT |  |  | 
time_end_unix | FLOAT |  |  | 
criteria_json | TEXT |  |  | 
configuration_json | TEXT |  |  | 
successful | BOOLEAN |  |  | 

# Table `cosmic_observation`

Class `cosmic_database.entities.CosmicDB_Observation`

Column | Type | Primary Key | Foreign Key(s) | Nullable
-|-|-|-|-
id | VARCHAR(80) | X | [cosmic_scan.id](#table-cosmic_scan) | 
time_start_unix | FLOAT |  |  | 
time_end_unix | FLOAT |  |  | 
criteria_json | TEXT |  |  | 

# Table `cosmic_observation_subband`

Class `cosmic_database.entities.CosmicDB_ObservationSubband`

Column | Type | Primary Key | Foreign Key(s) | Nullable
-|-|-|-|-
observation_id | VARCHAR(80) | X | [cosmic_observation.id](#table-cosmic_observation) | 
tuning | VARCHAR(80) | X |  | 
subband_offset | INTEGER | X |  | 
percentage_recorded | FLOAT |  |  | 
successful_participation | BOOLEAN |  |  | 

# Table `cosmic_observation_beam`

Class `cosmic_database.entities.CosmicDB_ObservationBeam`

Column | Type | Primary Key | Foreign Key(s) | Nullable
-|-|-|-|-
id | INTEGER | X |  | 
observation_id | VARCHAR(80) |  | [cosmic_observation.id](#table-cosmic_observation) | 
ra_radians | FLOAT |  |  | 
dec_radians | FLOAT |  |  | 
source | VARCHAR(80) |  |  | 
time_start_unix | FLOAT |  |  | 
time_end_unix | FLOAT |  |  | 

# Table `cosmic_observation_hit`

Class `cosmic_database.entities.CosmicDB_ObservationHit`

Column | Type | Primary Key | Foreign Key(s) | Nullable
-|-|-|-|-
id | INTEGER | X |  | 
beam_id | INTEGER |  | [cosmic_observation_beam.id](#table-cosmic_observation_beam) | 
observation_id | VARCHAR(80) |  | [cosmic_observation_subband.observation_id](#table-cosmic_observation_subband) | 
tuning | VARCHAR(80) |  | [cosmic_observation_subband.tuning](#table-cosmic_observation_subband) | 
subband_offset | INTEGER |  | [cosmic_observation_subband.subband_offset](#table-cosmic_observation_subband) | 
file_uri | VARCHAR(255) |  |  | 
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
source_name | VARCHAR(80) |  |  | 
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
observation_id | VARCHAR(80) |  | [cosmic_observation_subband.observation_id](#table-cosmic_observation_subband) | 
tuning | VARCHAR(80) |  | [cosmic_observation_subband.tuning](#table-cosmic_observation_subband) | 
subband_offset | INTEGER |  | [cosmic_observation_subband.subband_offset](#table-cosmic_observation_subband) | 
file_uri | VARCHAR(255) |  |  | 
file_local_enumeration | INTEGER |  |  | 
source_name | VARCHAR(80) |  |  | 
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
beam_id | INTEGER |  | [cosmic_observation_beam.id](#table-cosmic_observation_beam) | 
