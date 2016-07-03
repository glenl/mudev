select title,raw_instrument from "muPiece"
  where composer_id = 'BachJS'
     and piece_id in (
      select piece_id from "muPiece_instruments" where instrument_id='Violin'
    intersect
      select piece_id from "muPiece_instruments" where instrument_id='Cello'
  )
;
