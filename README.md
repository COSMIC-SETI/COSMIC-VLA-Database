# COSMIC Database

This library explicates the [entities](./docs/tables.md) of the database used to capture observational results from COSMIC.

The relationships are as follows.

Entity | Relationship
-|-
Dataset | (1:1) Scan
Scan | (1:1) ObservationConfiguration
_ | (1:?) CalibrationObservation
_ | (1:?) TargetObservation
ObservationConfiguration |
CalibrationObservation |
TargetObservation | (1:N) ObservationBeam
_ | (1:N) ObservationStamp
ObservationBeam | (1:N) ObservationHit
ObservationHit | 
ObservationStamp | 
