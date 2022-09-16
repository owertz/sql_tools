SELECT
    cbd10.datcrt,
    cbd10.datmaj,
    cbd10.heumaj,
    cbd10.usrmaj,
    cbd10.pgmmaj,
    cbd10.refopn,
    cbd10.staopn,
    cbd10.numcar_int,
    cbd10.codges,
    zzc01.libel1_1,
    cbd10.codopn,
    cbd13.libopn_1,
    cbd10.codzon,
    cbd50.libzon_1,
    cbd10.datopn,
    cbd10.valatt_car_new,
    cbd10.valatt_car_old
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
