# COSMIC Database

This library explicates the [entities](./docs/tables.md) of the database used to capture observational results from COSMIC.

The relationships are as follows.

Entity | Relationship | Entity
-|-|-
Dataset | 1:1 | Scan
Scan | 1:? | ObservationConfiguration
Scan | 1:? | Observation
Observation | 1:* | ObservationBeam
Observation | 1:* | ObservationStamp
ObservationBeam | 1:N | ObservationHit
