-- Display "hanging" versions
SELECT id,version FROM "muVersion" AS v
    WHERE v.id NOT IN (
          SELECT version_id FROM "muPiece" 
          group by version_id
          )
;
