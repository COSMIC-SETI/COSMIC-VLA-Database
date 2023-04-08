# COSMIC Database

This library explicates the [entities](./docs/tables.md) of the database used to capture observational results from COSMIC.

The relationships are as follows.

Entity | Relationship
-|-
Dataset | Scan (1:1)
Scan | ObservationConfiguration (1:1)
 | CalibrationObservation (1:?)
 | TargetObservation (1:?)
ObservationConfiguration |
CalibrationObservation |
TargetObservation | ObservationBeam (1:N)
 | ObservationStamp (1:N)
ObservationBeam | ObservationHit (1:N)
ObservationHit | 
ObservationStamp | 
