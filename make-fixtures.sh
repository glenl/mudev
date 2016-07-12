#!/bin/sh
DUMP="python manage.py dumpdata --settings=mudev.local_settings"
MODELS="Composer Contributor Style Instrument LPVersion License \
   Piece RawInstrumentMap CollectionPiece Collection            \
   AssetMap UpdateMarker                                        \
"
APP="mutopia"

for t in $MODELS; do
    echo $t
    $DUMP -o ${APP}/fixtures/${t}.json ${APP}.${t}
done
