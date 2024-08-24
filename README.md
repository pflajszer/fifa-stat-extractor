# Fifa Stat Extractor

## Problem

FIFA (or now EA Sports FC) does not provide an API for developers to analyze match stats. You can view your player statistics in-game, but those are already aggregated and while interesting to look at, they don't satisfied my data craving. 

## Solution

This is an attempt at scraping match statistics from EA SPORTS FC 'Match Facts' screen. The data is saved into JSON and CSV formats and can be later picked up to be ingested further.

## Prerequisites

- 'Match facts' screenshots (I've provided [test images](tests/test-data) in this repo for quickstart) transported onto your hard drive

## Supported platforms

The listed configuration has been tested and should work everywhere.


- Games:
    - EA Sports FC 2024

I'm hoping the Match Facts remains fairly static, Looking at [FIFA 23](https://platform.polygon.com/wp-content/uploads/sites/2/chorus/uploads/chorus_asset/file/24081980/FIFA_23_20221004120157.jpg?quality=90&strip=all&crop=0%2C0%2C100%2C100&w=750) stats, there's a chance this structure is retained in the next generation. Although I already see some differences between 23 and 24, so I'm expecting the pixel bounding boxes will have to be updated 

- Consoles:
    - PS5

If the 'Match Facts' screen differs based on the platform you're running the game on (Xbox, PS, PC), [additional annotations](annotation-export) would have to be added to support that.

- Resolution:
    - 3840x2160 px

For 16:9 screens, so the vast majority, supporting different resolutions could be as easy as dividing/multiplying the existing bounding box coordinates, but this will have to be proven to be true.


## Quickstart

```bash

cd ~
git clone git@github.com:pflajszer/fifa-stat-extractor.git
mkdir fifa-stats
cp fifa-stat-extractor/tests/test-data/* fifa-stats/source_data
export FIFA_WORKDIR="~/test-stats/"
cd fifa-stat-extractor
make run 



```