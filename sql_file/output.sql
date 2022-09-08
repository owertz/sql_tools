/* Query 1 */
SELECT
    COUNTry.country_name_eng,
    sum(casewhencall.id IS     NOT NULLthen1else0end) AS calls,    avg(isNULL(datediff(second, call.start_time, call.end_time),0)) AS avg_difference
FROM
    COUNTry
LEFT JOIN city ON city.country_id = COUNTry.id
LEFT JOIN customer ON city.id = customer.city_id
LEFT JOIN call ON call.customer_id = customer.id
GROUP BY
    COUNTry.id,
    COUNTry.country_name_eng HAVING avg(    isNULL (
    datediff (
second, call.start_time, call.end_time)    ,0)) > (
        SELECT
            avg(datediff(second, call.start_time, call.end_time))
        FROM
            call
    )
ORDER BY
    calls DESC,
    COUNTry.id ASC
;

/* Query 2 */
SELECT
    *
FROM
    disctr_md_mANDateoncontract
;