![Class Diagram](./classes.png)

# Class `CosmicDB_Dataset`

Table [`cosmic_dataset`](./tables.md#table-cosmic_dataset)

Attribute | Type
-|-
id | `str`
scans | list([CosmicDB_Scan](#class-cosmicdb_scan))
# Class `CosmicDB_Scan`

Table [`cosmic_scan`](./tables.md#table-cosmic_scan)

Attribute | Type
-|-
dataset_id | `str`
id | `str`
metadata_json | `str`
start | `datetime`
dataset | [CosmicDB_Dataset](#class-cosmicdb_dataset)
configurations | list([CosmicDB_ObservationConfiguration](#class-cosmicdb_observationconfiguration))
observations | list([CosmicDB_Observation](#class-cosmicdb_observation))
# Class `CosmicDB_ObservationConfiguration`

Table [`cosmic_observation_configuration`](./tables.md#table-cosmic_observation_configuration)

Attribute | Type
-|-
configuration_json | `str`
criteria_json | `str`
end | `datetime`
id | `int`
scan_id | `str`
start | `datetime`
successful | `bool`
scan | [CosmicDB_Scan](#class-cosmicdb_scan)
antenna | list([CosmicDB_ConfigurationAntenna](#class-cosmicdb_configurationantenna))
# Class `CosmicDB_ConfigurationAntenna`

Table [`cosmic_configuration_antenna`](./tables.md#table-cosmic_configuration_antenna)

Attribute | Type
-|-
configuration_id | `int`
name | `str`
configuration | [CosmicDB_ObservationConfiguration](#class-cosmicdb_observationconfiguration)
# Class `CosmicDB_Observation`

Table [`cosmic_observation`](./tables.md#table-cosmic_observation)

Attribute | Type
-|-
configuration_id | `int`
criteria_json | `str`
end | `datetime`
id | `int`
scan_id | `str`
start | `datetime`
configuration | [CosmicDB_ObservationConfiguration](#class-cosmicdb_observationconfiguration)
scan | [CosmicDB_Scan](#class-cosmicdb_scan)
subbands | list([CosmicDB_ObservationSubband](#class-cosmicdb_observationsubband))
beams | list([CosmicDB_ObservationBeam](#class-cosmicdb_observationbeam))
calibration | [CosmicDB_ObservationCalibration](#class-cosmicdb_observationcalibration)
# Class `CosmicDB_ObservationSubband`

Table [`cosmic_observation_subband`](./tables.md#table-cosmic_observation_subband)

Attribute | Type
-|-
observation_id | `int`
percentage_recorded | `float`
subband_offset | `int`
successful_participation | `bool`
tuning | `str`
observation | [CosmicDB_Observation](#class-cosmicdb_observation)
hits | list([CosmicDB_ObservationHit](#class-cosmicdb_observationhit))
stamps | list([CosmicDB_ObservationStamp](#class-cosmicdb_observationstamp))
# Class `CosmicDB_ObservationCalibration`

Table [`cosmic_observation_calibration`](./tables.md#table-cosmic_observation_calibration)

Attribute | Type
-|-
file_uri | `str`
flagged_percentage | `float`
id | `int`
observation_id | `int`
overall_grade | `float`
reference_antenna_name | `str`
observation | [CosmicDB_Observation](#class-cosmicdb_observation)
gains | list([CosmicDB_CalibrationGain](#class-cosmicdb_calibrationgain))
# Class `CosmicDB_CalibrationGain`

Table [`cosmic_calibration_gain`](./tables.md#table-cosmic_calibration_gain)

Attribute | Type
-|-
antenna_name | `str`
calibration_id | `int`
channel_frequency | `float`
gain_imag | `float`
gain_real | `float`
id | `int`
polarization | `str`
tuning | `str`
calibration | [CosmicDB_ObservationCalibration](#class-cosmicdb_observationcalibration)
# Class `CosmicDB_ObservationBeam`

Table [`cosmic_observation_beam`](./tables.md#table-cosmic_observation_beam)

Attribute | Type
-|-
dec_radians | `float`
end | `datetime`
id | `int`
observation_id | `int`
ra_radians | `float`
source | `str`
start | `datetime`
observation | [CosmicDB_Observation](#class-cosmicdb_observation)
hits | list([CosmicDB_ObservationHit](#class-cosmicdb_observationhit))
# Class `CosmicDB_ObservationHit`

Table [`cosmic_observation_hit`](./tables.md#table-cosmic_observation_hit)

Attribute | Type
-|-
beam_id | `int`
coarse_channel | `int`
dec_degrees | `float`
fch1_mhz | `float`
file_local_enumeration | `int`
file_uri | `str`
foff_mhz | `float`
id | `int`
num_channels | `int`
num_timesteps | `int`
observation_id | `int`
ra_hours | `float`
signal_beam | `int`
signal_coarse_channel | `int`
signal_drift_rate | `float`
signal_drift_steps | `int`
signal_frequency | `float`
signal_incoherent_power | `float`
signal_index | `int`
signal_num_timesteps | `int`
signal_power | `float`
signal_snr | `float`
source_name | `str`
start_channel | `int`
subband_offset | `int`
telescope_id | `int`
tsamp | `float`
tstart | `float`
tuning | `str`
beam | [CosmicDB_ObservationBeam](#class-cosmicdb_observationbeam)
observation_subband | [CosmicDB_ObservationSubband](#class-cosmicdb_observationsubband)
# Class `CosmicDB_ObservationStamp`

Table [`cosmic_observation_stamp`](./tables.md#table-cosmic_observation_stamp)

Attribute | Type
-|-
beam_id | `int`
coarse_channel | `int`
dec_degrees | `float`
fch1_mhz | `float`
fft_size | `int`
file_local_enumeration | `int`
file_uri | `str`
foff_mhz | `float`
id | `int`
num_antennas | `int`
num_channels | `int`
num_polarizations | `int`
num_timesteps | `int`
observation_id | `int`
obsid | `str`
ra_hours | `float`
schan | `int`
signal_beam | `int`
signal_coarse_channel | `int`
signal_drift_rate | `float`
signal_drift_steps | `int`
signal_frequency | `float`
signal_incoherent_power | `float`
signal_index | `int`
signal_num_timesteps | `int`
signal_power | `float`
signal_snr | `float`
source_name | `str`
start_channel | `int`
subband_offset | `int`
telescope_id | `int`
tsamp | `float`
tstart | `float`
tuning | `str`
observation_subband | [CosmicDB_ObservationSubband](#class-cosmicdb_observationsubband)