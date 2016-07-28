#!/bin/sh
LOAD="python manage.py loaddata --settings=mudev.local_settings"
MODELS="Composer Contributor Style Instrument LPVersion License \
   Piece Tag RawInstrumentMap Collection                        \
   AssetMap UpdateMarker                                        \
"
APP="mutopia"

for t in $MODELS; do
    echo $t
    $LOAD ${APP}/fixtures/${t}.json
done
