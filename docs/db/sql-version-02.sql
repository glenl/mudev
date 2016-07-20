select v.version, count(*) as count
  from "muPiece" as p
  join "muVersion" as v on p.version_id = v.id
  group by v.version
  limit 5
;
