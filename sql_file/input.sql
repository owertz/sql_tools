select * from tab where tablename='a-b';


SELECT
    cbd10.datcrt
FROM
    cbd10 inner
JOIN zzc01 ON cbd10.codges = zzc01.argtbl
    inner
JOIN cbd13 ON cbd10.codopn = cbd13.codopn
    AND cbd10.codges = cbd13.codges
    AND cbd10.codzon = cbd13.codzon
    inner
JOIN cbd50 ON cbd10.codzon = cbd50.codzon
    AND cbd10.codges = cbd50.codges
WHERE
    cbd10.numcar_int = 'C2E20CBNEL828CN0'
;