select p01.numtie "NAME", p20.roltie "ROLE" from pyd01 p01 join pyd20 p20 on p20.numtie=p01.numtie where numtie = 'P00GABX';
select x, count(*) from tab where trim(staan) is null group by x;