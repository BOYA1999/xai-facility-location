# Referenced datasets

No data files are included in this repository. The sources below were cited as public overlays for failure-boundary or out-of-region stress tests, not as validation of the Guangzhou case-study hazard layer. Access information was checked on 2026-08-08.

## Sources used by the completed external adversarial ablation

### OpenStreetMap

- Source: OpenStreetMap contributors via Nominatim and Overpass public endpoints.
- Landing page: https://www.openstreetmap.org
- Role: public roads, candidate facilities, and water features used to construct the Guangzhou proxy and 20-city network instances.
- License: Open Database License 1.0; attribution and produced-work/database obligations must be reviewed for any redistribution.
- Important limitation: OSM completeness, positional accuracy, facility attributes, and update state vary by location. The release contains no raw OSM response or derived geometry.

### WorldPop 2020 China population raster

- Product: 2020 China 1-km aggregated population raster, `chn_ppp_2020_1km_Aggregated.tif`.
- Direct product URL: https://data.worldpop.org/GIS/Population/Global_2000_2020_1km/2020/CHN/chn_ppp_2020_1km_Aggregated.tif
- Role: demand weights for the public Guangzhou proxy and one population axis of the 20-city campaign.
- Scholarly citation: Tatem, A. J. (2017). WorldPop, open data for spatial demography. *Scientific Data*, 4, 170004. https://doi.org/10.1038/sdata.2017.4
- Important limitation: gridded resident population is a demand proxy, not observed emergency-service demand.

### GHS-POP R2023A, 2020 epoch

- Product page: https://human-settlement.emergency.copernicus.eu/ghs_pop2023.php
- DOI: https://doi.org/10.2905/2FF68A52-5B5B-4A22-8F40-C41DA8332CFE
- Role: independent population-surface axis in the 20-city campaign.
- Important limitation: it is a second exposure proxy, not ground truth or a participant dataset.

### USGS ShakeMap

- Product page: https://earthquake.usgs.gov/data/shakemap/
- Manual DOI: https://doi.org/10.5066/F7D21VPQ
- Role: six archived historical shaking fields converted by a fixed model into road-failure probabilities.
- Important limitation: the resulting failures are modeled scenarios, not observed road closures.

## 1. NASA Global Landslide Catalog Export

- Source: NASA Open Data Portal
- Landing page: https://data.nasa.gov/dataset/global-landslide-catalog-export-f07b6
- Scope: a one-time export of the Global Landslide Catalog containing reported rainfall-triggered landslide events; the portal describes the export as current through 2016.
- Intended role: external event overlay for omitted-hazard and point-buffer sensitivity tests.
- Important limitation: point records do not establish polygon extent. Any conversion from events to exclusion zones requires a declared buffer and sensitivity analysis.
- License status: the landing page does not state a reusable-data license clearly enough for this release to redistribute the file. Users must check the current portal terms before downloading or reusing it.
- Related scholarly citation: Kirschbaum, D. B., Adler, R., Hong, Y., Hill, S. & Lerner-Lam, A. (2010). A global landslide catalog for hazard applications: method, results, and limitations. *Natural Hazards*, 52, 561–575. https://doi.org/10.1007/s11069-009-9401-4

## 2. Landslide Inventories across the United States, version 3.0

- Source: U.S. Geological Survey
- Version: 3.0, February 2025
- DOI: https://doi.org/10.5066/P14AJF8I
- Landing page: https://www.usgs.gov/data/landslide-inventories-across-united-states-ver-30-february-2025
- Rights: CC0 1.0 Universal, as stated on the USGS landing page.
- Intended role: high-confidence out-of-region stress tests and provenance-aware failure analysis.
- Geographic limitation: this U.S. dataset must not be presented as Guangzhou validation.
- Preferred citation: Belair, G. M., Mirus, B. B., Luna, L. V. & Jones, E. S. (2025). *Landslide inventories across the United States (ver. 3.0, February 2025).* U.S. Geological Survey data release. https://doi.org/10.5066/P14AJF8I

## 3. Global Flood Database, version 1

- Source: Google Earth Engine Data Catalog
- Earth Engine ID: `GLOBAL_FLOOD_DB/MODIS_EVENTS/V1`
- Landing page: https://developers.google.com/earth-engine/datasets/catalog/GLOBAL_FLOOD_DB_MODIS_EVENTS_V1
- Scope: maps for 913 flood events occurring from 2000 to 2018.
- Terms: Creative Commons Attribution NonCommercial 4.0 International (CC BY-NC 4.0), as stated on the catalog page.
- Intended role: event-time holdout, hazard-layer omission, and failure-threshold stress tests.
- Redistribution note: the non-commercial terms must be reviewed for the intended use. This repository links to the catalog and does not redistribute the raster data.
- Related scholarly citation: Tellman, B. et al. (2021). Satellite imaging reveals increased proportion of population exposed to floods. *Nature*, 596, 80–86. https://doi.org/10.1038/s41586-021-03695-w

## Reproducible acquisition record

For any future experiment, record the dataset version, access date, selected files or Earth Engine assets, spatial/temporal filters, coordinate reference system, preprocessing commands, applicable license, and SHA-256 checksum where a downloadable file is used. Do not commit third-party raw data unless redistribution is explicitly permitted.
