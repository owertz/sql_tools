select numtie from (select x from pyd01);

select p05.refrel, p05.typrel, z7.libel1_1, p05.numtie_1,  p05.quarel_1, z8a.libel1_1, p05.numtie_2, p05.quarel_2, z8b.libel1_1, p05.datdeb, p05.datfin 
from pyd05_de p05
join zzpy7 z7 on z7.argtbl=p05.typrel
join zzpy8 z8a on z8a.argtbl=p05.quarel_1
join zzpy8 z8b on z8b.argtbl=p05.quarel_2
where (p05.numtie_1 in ('P0001LFT') or p05.numtie_2 in ('P0001LFT')) and trim(p05.staann) is null;