# Table `cosmic_dataset`

Class `cosmic_database.entities.CosmicDB_Dataset`

Column | Type | Primary Key | Foreign Key(s) | Nullable
-|-|-|-|-
id | VARCHAR(60) | X |  | 

# Table `cosmic_scan`

Class `cosmic_database.entities.CosmicDB_Scan`

Column | Type | Primary Key | Foreign Key(s) | Nullable
-|-|-|-|-
id | VARCHAR(100) | X |  | 
dataset_id | VARCHAR(60) |  | [cosmic_dataset.id](#table-cosmic_dataset) | 
start | DATETIME |  |  | 
metadata_json | TEXT |  |  | 

# Table `cosmic_observation_configuration`

Class `cosmic_database.entities.CosmicDB_ObservationConfiguration`

Column | Type | Primary Key | Foreign Key(s) | Nullable
-|-|-|-|-
id | INTEGER | X |  | 
scan_id | VARCHAR(100) |  | [cosmic_scan.id](#table-cosmic_scan) | 
start | DATETIME |  |  | 
end | DATETIME |  |  | 
criteria_json | TEXT |  |  | 
configuration_json | TEXT |  |  | 
successful | BOOLEAN |  |  | 

# Table `cosmic_observation`

Class `cosmic_database.entities.CosmicDB_Observation`

Column | Type | Primary Key | Foreign Key(s) | Nullable
-|-|-|-|-
id | INTEGER | X |  | 
scan_id | VARCHAR(100) |  | [cosmic_scan.id](#table-cosmic_scan) | 
configuration_id | INTEGER |  | [cosmic_observation_configuration.id](#table-cosmic_observation_configuration) | 
start | DATETIME |  |  | 
end | DATETIME |  |  | 
criteria_json | TEXT |  |  | 

# Table `cosmic_observation_subband`

Class `cosmic_database.entities.CosmicDB_ObservationSubband`

Column | Type | Primary Key | Foreign Key(s) | Nullable
-|-|-|-|-
observation_id | INTEGER | X | [cosmic_observation.id](#table-cosmic_observation) | 
tuning | VARCHAR(10) | X |  | 
subband_offset | INTEGER | X |  | 
percentage_recorded | DOUBLE |  |  | 
successful_participation | BOOLEAN |  |  | 

# Table `cosmic_observation_beam`

Class `cosmic_database.entities.CosmicDB_ObservationBeam`

Column | Type | Primary Key | Foreign Key(s) | Nullable
-|-|-|-|-
id | INTEGER | X |  | 
observation_id | INTEGER |  | [cosmic_observation.id](#table-cosmic_observation) | 
ra_radians | DOUBLE |  |  | 
dec_radians | DOUBLE |  |  | 
source | VARCHAR(80) |  |  | 
start | DATETIME |  |  | 
end | DATETIME |  |  | 

# Table `cosmic_observation_hit`

Class `cosmic_database.entities.CosmicDB_ObservationHit`

Column | Type | Primary Key | Foreign Key(s) | Nullable
-|-|-|-|-
id | INTEGER | X |  | 
beam_id | INTEGER |  | [cosmic_observation_beam.id](#table-cosmic_observation_beam) | 
observation_id | INTEGER |  | [cosmic_observation_subband.observation_id](#table-cosmic_observation_subband) | 
tuning | VARCHAR(10) |  | [cosmic_observation_subband.tuning](#table-cosmic_observation_subband) | 
subband_offset | INTEGER |  | [cosmic_observation_subband.subband_offset](#table-cosmic_observation_subband) | 
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

Class `cosmic_database.entities.CosmicDB_ObservationStamp`

Column | Type | Primary Key | Foreign Key(s) | Nullable
-|-|-|-|-
id | INTEGER | X |  | 
observation_id | INTEGER |  | [cosmic_observation_subband.observation_id](#table-cosmic_observation_subband) | 
tuning | VARCHAR(10) |  | [cosmic_observation_subband.tuning](#table-cosmic_observation_subband) | 
subband_offset | INTEGER |  | [cosmic_observation_subband.subband_offset](#table-cosmic_observation_subband) | 
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
beam_id | INTEGER |  | [cosmic_observation_beam.id](#table-cosmic_observation_beam) | 
