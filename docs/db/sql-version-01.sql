select v.version
  from "muPiece" as p
  join "muVersion" as v on p.version_id = v.id
  limit 5
;
