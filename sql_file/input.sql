select l.numcli as 'client', c.numcpt as 'account' from ccd01 c left join cld01 l on l.numcli=c.numcli where c.numcli='01010101';   

update cld01 set staann='D' datmaj=to_char(test, 'time') where numcli='01010101';   