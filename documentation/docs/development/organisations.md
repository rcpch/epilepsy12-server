---
title: Organisations, Trusts and Levels of Abstraction
reviewers: Dr Simon Chapman
---

## Levels of Abstraction

The organisational structure of health care in England and Wales influences reporting and table structure.

### Organisations and Trusts

This is the lowest level of abstraction and represents either an acute or a community hospital/organisation responsible for epilepsy care of children and young people. There are often several organisations in a Trust. Each organisation, like each Trust, has its own ODS code, and from year to year there is movement between trusts as organisations change their allegiances between trusts when mergers are carried out. The organisation model therefore has more than once instance for some organisations, as their parent status or other details such as name change.

On a monthly basis the NHS ODS API is polled with any changes to organisational structure, and the local database record for that organisation is updated to reflect the latest changes.

### Integrated Care Boards

These were introduced in 2022 and superceded Clinical Commissioning Groups (CCGs) as the geographical commissioning areas within the NHS. The are 42 ICBs and trusts and their organisations fit neatly inside them like Russian dolls. Each ICB has its own ODS code and the ICB model is taken directly from NHS Digital with its boundary shapes for mapping, and is versioned. Currently there is no automated process to check for changes to boundaries or ICB membership and update the records. Note there are no ICBs in Wales.

### Local Health Boards

These exist only in Wales and are both equivalent to Trust and ICB in England. One LHB might have several organisations and commissioning also is distributed across the 7 LHBs. As above, the model is taken from NHS Digital and includes the boundary shapes for mapping. Note there is no automated process currently to check for changes to boundaries or LHB membership and update the records.

### OPENUK Networks

These are [networks](https://www.rcpch.ac.uk/resources/open-uk-organisation-paediatric-epilepsy-networks-uk) of NHS Health Boards and Trusts that provide care for children with epilepsies, organised regionally and overseen by a UK Working Group. Not all centres are members of an OPEN UK network. There are no boundary shapes to describe each region, but each one has its own identifier, and therefore there is an entity model to hold information on each OPEN UK network referenced by each organisation.

### NHS England Regions

There are 7 of these in England and their model is taken from NHS Digital. Each one has its own boundary code. ICBs fit neatly inside each one.

### Local Authorities

Local authority codes for each organisation are not stored except for those organisations in London. Local authorities are administrative regions not related to health or the NHS. In London local authorities are usually referred to as London Boroughs. There is a boundary model for London Boroughs taken from NHS Digital and this is used only for mapping. As above, although versioned, there is no process in place to check for updates nationally and update the database record.

### Jersey and the Channel Islands

Jersey joined Epilepsy12 in 2024. Jersey is in the Channel Islands and part of the UK but does not participate in the NHS. There are reciprocal agreements about some hospital treatment, but inpatient care is free only to people who have been resident for 6 months and have a Health Card.

***Organisational structure***
The E12 structure is that organisations have a Trust or Local Health Board as their parent. There is a hierarchy above this which varies between England and Wales. Organisations and Trusts in England might have the same name, but will always have separate ODS codes, which are often similar. Jersey General Hospital in St Helier is a Trust which provides medical care directly. To work around this, Jersey General Hospital has been created both as an Organisation and a Trust, each with the same ODS code, so that it is its own parent.

***Levels of Abstraction***
Jersey has been added as a separate country, so that it can report at the level of organisation, Open UK Network, trust and country, though the numbers for these 3 hierarchies will be the same.

## Maps

Django GIS and the additional Postgres support for geoJSON are both reasons why these tools were used for this project. The Organisation View presents a dashboard that includes a scatterplot of patients specific to that organisation, with mean, median, minimum and maximum distances for patients to travel to clinic. There are also maps with boundaries demarcating health geographies such as NHS England regions and Integrated Care Boards. These are provided by `.shp` files which contain the coordinates for plotting the shapes on top of the maps. There is documentation on adding shape files [here](shape-files.md)

The basic maps are provided by [MapBox](https://www.mapbox.com/) using their free tier, with the API key stored in credentials. An API key is required.

E12 currently looks up postcodes against an API which returns longitude and latitude, and these are stored in the model (using SRID 27700) and this is used to plot them on the scatter plots. This currently does not function for Jersey as longitude and latitude for post codes are currently not stored.
