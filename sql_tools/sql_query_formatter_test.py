import logging
import os
import re

from enum import Enum

from sql_query_configuration import Constants

__version__ = '0.0.1'
__author__ = 'OWE'

"""
This file contains a set of SQL queries used to perform unit testing on 'sql_query_formatter.py' script.


TODO
----
Legend
[ n ]: n-th task in the TODO list
[ . ]: task in progress.
[ * ]: task implemented.

Content
[  ] ...
      
FIXME
-----
-
"""
queries_for_unittest = [
    "myQuery1a", "myQuery1b", "myQuery1c", "myQuery1d", "myQuery1e", "myQuery1f", "myQuery1g", "myQuery1h", "myQuery1i", "myQuery1j", 
    "myQuery1k1", "myQuery1k2", "myQuery1k3", "myQuery1k4", "myQuery1m",
    "myQuery2", "myQuery2b", "myQuery2c",
    "myQuery3", "myQuery3b",
    "myQuery4a", "myQuery4b", "myQuery4c",
    "myQuery5a", "myQuery5b", "myQuery5c", "myQuery5d", "myQuery5e", "myQuery5f", "myQuery5g", "myQuery5h",
    "myQuery6a", "myQuery6b",
    "myQuery7a", "myQuery7b", "myQuery7c",
]

myQuery1a = "select   *  frOm user_tables   ;"
myQuery1a_expected = f"SELECT{Constants.NEW_LINE.value}{Constants.FOUR_SPACES.value}*{Constants.NEW_LINE.value}FROM{Constants.NEW_LINE.value}{Constants.FOUR_SPACES.value}user_tables{Constants.NEW_LINE.value};"
myQuery1a_expected_surrogate = myQuery1a_expected.replace(Constants.MONO_SPACE.value, Constants.SURROGATE.value)

myQuery1b = "select  TABLE_NAME  from user_tables;"
myQuery1b_expected = f"SELECT{Constants.NEW_LINE.value}{Constants.FOUR_SPACES.value}table_name{Constants.NEW_LINE.value}FROM{Constants.NEW_LINE.value}{Constants.FOUR_SPACES.value}user_tables{Constants.NEW_LINE.value};"
myQuery1b_expected_surrogate = myQuery1b_expected.replace(Constants.MONO_SPACE.value, Constants.SURROGATE.value)

myQuery1c = "select TABLE_NAME from user_tables where status like 'eg%' ;"
myQuery1c_expected = f"SELECT{Constants.NEW_LINE.value}{Constants.FOUR_SPACES.value}table_name{Constants.NEW_LINE.value}FROM{Constants.NEW_LINE.value}{Constants.FOUR_SPACES.value}user_tables{Constants.NEW_LINE.value}WHERE{Constants.NEW_LINE.value}{Constants.FOUR_SPACES.value}status{Constants.MONO_SPACE.value}LIKE{Constants.MONO_SPACE.value}'eg%'{Constants.NEW_LINE.value};"
myQuery1c_expected_surrogate = myQuery1c_expected.replace(Constants.MONO_SPACE.value, Constants.SURROGATE.value)

myQuery1d = "select username, ACCOUNT_STATUS from dba_users where account_status='EXPIRED';"
myQuery1d_expected = f"SELECT{Constants.NEW_LINE.value}{Constants.FOUR_SPACES.value}username,{Constants.NEW_LINE.value}{Constants.FOUR_SPACES.value}account_status{Constants.NEW_LINE.value}FROM{Constants.NEW_LINE.value}{Constants.FOUR_SPACES.value}dba_users{Constants.NEW_LINE.value}WHERE{Constants.NEW_LINE.value}{Constants.FOUR_SPACES.value}account_status{Constants.MONO_SPACE.value}={Constants.MONO_SPACE.value}'EXPIRED'{Constants.NEW_LINE.value};"
myQuery1d_expected_surrogate = myQuery1d_expected.replace(Constants.MONO_SPACE.value, Constants.SURROGATE.value)

myQuery1e = """select USERname , account_status from dba_users 
where account_status  ='EXPIRED' and other_field = 'myTESt'   ;"""
myQuery1e_expected = f"SELECT{Constants.NEW_LINE.value}{Constants.FOUR_SPACES.value}username,{Constants.NEW_LINE.value}{Constants.FOUR_SPACES.value}account_status{Constants.NEW_LINE.value}FROM{Constants.NEW_LINE.value}{Constants.FOUR_SPACES.value}dba_users{Constants.NEW_LINE.value}WHERE{Constants.NEW_LINE.value}{Constants.FOUR_SPACES.value}account_status{Constants.MONO_SPACE.value}={Constants.MONO_SPACE.value}'EXPIRED'{Constants.NEW_LINE.value}{Constants.FOUR_SPACES.value}AND{Constants.MONO_SPACE.value}other_field{Constants.MONO_SPACE.value}={Constants.MONO_SPACE.value}'myTESt'{Constants.NEW_LINE.value};"
myQuery1e_expected_surrogate = myQuery1e_expected.replace(Constants.MONO_SPACE.value, Constants.SURROGATE.value)

myQuery1f = """select numtie "my name", datnai "birthday" from pyd01 p01 where numtie='P00GABC' ;"""
myQuery1f_expected = f"SELECT{Constants.NEW_LINE.value}{Constants.FOUR_SPACES.value}numtie{Constants.MONO_SPACE.value}\"my{Constants.MONO_SPACE.value}name\",{Constants.NEW_LINE.value}{Constants.FOUR_SPACES.value}datnai{Constants.MONO_SPACE.value}\"birthday\"{Constants.NEW_LINE.value}FROM{Constants.NEW_LINE.value}{Constants.FOUR_SPACES.value}pyd01⎵p01{Constants.NEW_LINE.value}WHERE{Constants.NEW_LINE.value}{Constants.FOUR_SPACES.value}numtie{Constants.MONO_SPACE.value}={Constants.MONO_SPACE.value}'P00GABC'{Constants.NEW_LINE.value};"
myQuery1f_expected_surrogate = myQuery1f_expected.replace(Constants.MONO_SPACE.value, Constants.SURROGATE.value)

myQuery1g = """select p01.numtie "NAME", p20.roltie "ROLE" from pyd01 p01 
join pyd20 p20 on p20.numtie=p01.numtie 
where numtie = 'P00GABX';"""
myQuery1g_expected = f"SELECT{Constants.NEW_LINE.value}{Constants.FOUR_SPACES.value}p01.numtie{Constants.MONO_SPACE.value}\"NAME\",{Constants.NEW_LINE.value}{Constants.FOUR_SPACES.value}p20.roltie{Constants.MONO_SPACE.value}\"ROLE\"{Constants.NEW_LINE.value}FROM{Constants.NEW_LINE.value}{Constants.FOUR_SPACES.value}pyd01{Constants.MONO_SPACE.value}p01{Constants.NEW_LINE.value}JOIN{Constants.MONO_SPACE.value}pyd20{Constants.MONO_SPACE.value}p20{Constants.MONO_SPACE.value}ON{Constants.MONO_SPACE.value}p20.numtie{Constants.MONO_SPACE.value}={Constants.MONO_SPACE.value}p01.numtie{Constants.NEW_LINE.value}WHERE{Constants.NEW_LINE.value}{Constants.FOUR_SPACES.value}numtie{Constants.MONO_SPACE.value}={Constants.MONO_SPACE.value}'P00GABX'{Constants.NEW_LINE.value};"
myQuery1g_expected_surrogate = myQuery1g_expected.replace(Constants.MONO_SPACE.value, Constants.SURROGATE.value)

myQuery1h = """select * from pyd01 where numtie in ('P001','P0 02');"""
myQuery1h_expected = f"SELECT{Constants.NEW_LINE.value}{Constants.FOUR_SPACES.value}*{Constants.NEW_LINE.value}FROM{Constants.NEW_LINE.value}{Constants.FOUR_SPACES.value}pyd01{Constants.NEW_LINE.value}WHERE{Constants.NEW_LINE.value}{Constants.FOUR_SPACES.value}numtie{Constants.MONO_SPACE.value}IN{Constants.MONO_SPACE.value}('P001',{Constants.MONO_SPACE.value}'P0{Constants.MONO_SPACE.value}02'){Constants.NEW_LINE.value};"
myQuery1h_expected_surrogate = myQuery1h_expected.replace(Constants.MONO_SPACE.value, Constants.SURROGATE.value)

myQuery1i = """select test " exists " from table_mandate_select " from" where joinn="order desc " order by 2;"""
myQuery1i_expected = f"SELECT{Constants.NEW_LINE.value}{Constants.FOUR_SPACES.value}test{Constants.MONO_SPACE.value}\"{Constants.MONO_SPACE.value}exists{Constants.MONO_SPACE.value}\"{Constants.NEW_LINE.value}FROM{Constants.NEW_LINE.value}{Constants.FOUR_SPACES.value}table_mandate_select{Constants.MONO_SPACE.value}\"{Constants.MONO_SPACE.value}from\"{Constants.NEW_LINE.value}WHERE{Constants.NEW_LINE.value}{Constants.FOUR_SPACES.value}joinn{Constants.MONO_SPACE.value}={Constants.MONO_SPACE.value}\"order{Constants.MONO_SPACE.value}desc{Constants.MONO_SPACE.value}\"{Constants.NEW_LINE.value}ORDER{Constants.MONO_SPACE.value}BY{Constants.NEW_LINE.value}{Constants.FOUR_SPACES.value}2{Constants.NEW_LINE.value};"
myQuery1i_expected_surrogate = myQuery1i_expected.replace(Constants.MONO_SPACE.value, Constants.SURROGATE.value)

myQuery1j = """select x, datfin || heufin, y, z from tab;"""
myQuery1j_expected = f"SELECT{Constants.NEW_LINE.value}{Constants.FOUR_SPACES.value}x,{Constants.NEW_LINE.value}{Constants.FOUR_SPACES.value}datfin{Constants.MONO_SPACE.value}||{Constants.MONO_SPACE.value}heufin,{Constants.NEW_LINE.value}{Constants.FOUR_SPACES.value}y,{Constants.NEW_LINE.value}{Constants.FOUR_SPACES.value}z{Constants.NEW_LINE.value}FROM{Constants.NEW_LINE.value}{Constants.FOUR_SPACES.value}tab{Constants.NEW_LINE.value};"
myQuery1j_expected_surrogate = myQuery1j_expected.replace(Constants.MONO_SPACE.value, Constants.SURROGATE.value)

myQuery1k1 = """select a|| sum(b) from pyd01;"""
myQuery1k1_expected = f"SELECT{Constants.NEW_LINE.value}{Constants.FOUR_SPACES.value}a{Constants.MONO_SPACE.value}||{Constants.MONO_SPACE.value}SUM(b){Constants.NEW_LINE.value}FROM{Constants.NEW_LINE.value}{Constants.FOUR_SPACES.value}pyd01{Constants.NEW_LINE.value};"
myQuery1k1_expected_surrogate = myQuery1k1_expected.replace(Constants.MONO_SPACE.value, Constants.SURROGATE.value)

myQuery1k2 = """select a||sum(b) from pyd01;"""
myQuery1k2_expected = f"SELECT{Constants.NEW_LINE.value}{Constants.FOUR_SPACES.value}a{Constants.MONO_SPACE.value}||{Constants.MONO_SPACE.value}SUM(b){Constants.NEW_LINE.value}FROM{Constants.NEW_LINE.value}{Constants.FOUR_SPACES.value}pyd01{Constants.NEW_LINE.value};"
myQuery1k2_expected_surrogate = myQuery1k2_expected.replace(Constants.MONO_SPACE.value, Constants.SURROGATE.value)

myQuery1k3 = """select a ||sum(b) from pyd01;"""
myQuery1k3_expected = f"SELECT{Constants.NEW_LINE.value}{Constants.FOUR_SPACES.value}a{Constants.MONO_SPACE.value}||{Constants.MONO_SPACE.value}SUM(b){Constants.NEW_LINE.value}FROM{Constants.NEW_LINE.value}{Constants.FOUR_SPACES.value}pyd01{Constants.NEW_LINE.value};"
myQuery1k3_expected_surrogate = myQuery1k3_expected.replace(Constants.MONO_SPACE.value, Constants.SURROGATE.value)

myQuery1k4 = """select a || sum(b) from pyd01;"""
myQuery1k4_expected = f"SELECT{Constants.NEW_LINE.value}{Constants.FOUR_SPACES.value}a{Constants.MONO_SPACE.value}||{Constants.MONO_SPACE.value}SUM(b){Constants.NEW_LINE.value}FROM{Constants.NEW_LINE.value}{Constants.FOUR_SPACES.value}pyd01{Constants.NEW_LINE.value};"
myQuery1k4_expected_surrogate = myQuery1k4_expected.replace(Constants.MONO_SPACE.value, Constants.SURROGATE.value)

myQuery1m = """select (a || sum(b)) from x;"""
myQuery1m_expected = f"SELECT{Constants.NEW_LINE.value}{Constants.FOUR_SPACES.value}(a{Constants.MONO_SPACE.value}||{Constants.MONO_SPACE.value}SUM(b)){Constants.NEW_LINE.value}FROM{Constants.NEW_LINE.value}{Constants.FOUR_SPACES.value}x{Constants.NEW_LINE.value};"
myQuery1m_expected_surrogate = myQuery1m_expected.replace(Constants.MONO_SPACE.value, Constants.SURROGATE.value)
""" 
{Constants.NEW_LINE.value}
{Constants.NEW_LINE.value}{Constants.FOUR_SPACES.value}
{Constants.NEW_LINE.value}{Constants.EIGHT_SPACES.value}
{Constants.NEW_LINE.value}{Constants.TWELVE_SPACES.value}
{Constants.FOUR_SPACES.value}
{Constants.MONO_SPACE.value}
"""



myQuery2 = """select    perm.APP_FK_COD , perm.RESOURCE_TYPE_FK_COD,   perm.PROFILE_FK_COD from EROLE_PERMISSION perm where 
perm.PROFILE_FK_COD = prof.PROFILE_COD
and grouplk.PROFILE_FK_COD =prof.PROFILE_COD and profgrp.PROFILEGROUP_COD= grouplk.PROFILE_GROUP_FK_COD
order by perm.RESOURCE_FK_COD desc   , perm.APP_FK_COD   Desc  ;"""
myQuery2_expected = f"SELECT{Constants.NEW_LINE.value}{Constants.FOUR_SPACES.value}perm.app_fk_cod,{Constants.NEW_LINE.value}{Constants.FOUR_SPACES.value}perm.resource_type_fk_cod,{Constants.NEW_LINE.value}{Constants.FOUR_SPACES.value}perm.profile_fk_cod{Constants.NEW_LINE.value}FROM{Constants.NEW_LINE.value}{Constants.FOUR_SPACES.value}erole_permission{Constants.MONO_SPACE.value}perm{Constants.NEW_LINE.value}WHERE{Constants.NEW_LINE.value}{Constants.FOUR_SPACES.value}perm.profile_fk_cod{Constants.MONO_SPACE.value}={Constants.MONO_SPACE.value}prof.profile_cod{Constants.NEW_LINE.value}{Constants.FOUR_SPACES.value}AND{Constants.MONO_SPACE.value}grouplk.profile_fk_cod{Constants.MONO_SPACE.value}={Constants.MONO_SPACE.value}prof.profile_cod{Constants.NEW_LINE.value}{Constants.FOUR_SPACES.value}AND{Constants.MONO_SPACE.value}profgrp.profilegroup_cod{Constants.MONO_SPACE.value}={Constants.MONO_SPACE.value}grouplk.profile_group_fk_cod{Constants.NEW_LINE.value}ORDER BY{Constants.NEW_LINE.value}{Constants.FOUR_SPACES.value}perm.resource_fk_cod{Constants.MONO_SPACE.value}DESC,{Constants.NEW_LINE.value}{Constants.FOUR_SPACES.value}perm.app_fk_cod{Constants.MONO_SPACE.value}DESC{Constants.NEW_LINE.value};"
myQuery2_expected_surrogate = myQuery2_expected.replace(Constants.MONO_SPACE.value, Constants.SURROGATE.value)

myQuery2b = """select * from pyd05_de where (numtie_1 in ('') or numtie_2 in ('')) order by refrel asc;"""
myQuery2b_expected = f"SELECT{Constants.NEW_LINE.value}{Constants.FOUR_SPACES.value}*{Constants.NEW_LINE.value}FROM{Constants.NEW_LINE.value}{Constants.FOUR_SPACES.value}pyd05_de{Constants.NEW_LINE.value}WHERE{Constants.NEW_LINE.value}{Constants.FOUR_SPACES.value}(numtie_1{Constants.MONO_SPACE.value}IN{Constants.MONO_SPACE.value}(''){Constants.MONO_SPACE.value}OR{Constants.MONO_SPACE.value}numtie_2{Constants.MONO_SPACE.value}IN{Constants.MONO_SPACE.value}('')){Constants.NEW_LINE.value}ORDER{Constants.MONO_SPACE.value}BY{Constants.NEW_LINE.value}{Constants.FOUR_SPACES.value}refrel{Constants.MONO_SPACE.value}ASC{Constants.NEW_LINE.value};"
myQuery2b_expected_surrogate = myQuery2b_expected.replace(Constants.MONO_SPACE.value, Constants.SURROGATE.value)

myQuery2c = """select * from pyd05_de where trim(staan) is null and (numtie_1 in ('P0001R6E') or numtie_2 in ('P0001R6E')) order by heumaj;"""
myQuery2c_expected = f"SELECT{Constants.NEW_LINE.value}{Constants.FOUR_SPACES.value}*{Constants.NEW_LINE.value}FROM{Constants.NEW_LINE.value}{Constants.FOUR_SPACES.value}pyd05_de{Constants.NEW_LINE.value}WHERE{Constants.NEW_LINE.value}{Constants.FOUR_SPACES.value}TRIM(staan){Constants.MONO_SPACE.value}IS{Constants.MONO_SPACE.value}NULL{Constants.NEW_LINE.value}{Constants.FOUR_SPACES.value}AND{Constants.MONO_SPACE.value}(numtie_1{Constants.MONO_SPACE.value}IN{Constants.MONO_SPACE.value}('P0001R6E'){Constants.MONO_SPACE.value}OR{Constants.MONO_SPACE.value}numtie_2{Constants.MONO_SPACE.value}IN{Constants.MONO_SPACE.value}('P0001R6E')){Constants.NEW_LINE.value}ORDER⎵BY{Constants.NEW_LINE.value}{Constants.FOUR_SPACES.value}heumaj{Constants.NEW_LINE.value};"
myQuery2c_expected_surrogate = myQuery2c_expected.replace(Constants.MONO_SPACE.value, Constants.SURROGATE.value)

myQuery3 = """select test from DMD01 d01 where exists (  select null from zz051 z51 where z51.x =d01.y and z51.TEST='COMPLETED') order by test desc;"""
myQuery3_expected = f"SELECT{Constants.NEW_LINE.value}{Constants.FOUR_SPACES.value}test{Constants.NEW_LINE.value}FROM{Constants.NEW_LINE.value}{Constants.FOUR_SPACES.value}dmd01{Constants.MONO_SPACE.value}d01{Constants.NEW_LINE.value}WHERE{Constants.NEW_LINE.value}{Constants.FOUR_SPACES.value}EXISTS{Constants.MONO_SPACE.value}({Constants.NEW_LINE.value}{Constants.EIGHT_SPACES.value}SELECT{Constants.NEW_LINE.value}{Constants.TWELVE_SPACES.value}NULL{Constants.NEW_LINE.value}{Constants.EIGHT_SPACES.value}FROM{Constants.NEW_LINE.value}{Constants.TWELVE_SPACES.value}zz051 z51{Constants.NEW_LINE.value}{Constants.EIGHT_SPACES.value}WHERE{Constants.NEW_LINE.value}{Constants.TWELVE_SPACES.value}z51.x{Constants.MONO_SPACE.value}={Constants.MONO_SPACE.value}d01.y{Constants.NEW_LINE.value}{Constants.TWELVE_SPACES.value}AND z51.test{Constants.MONO_SPACE.value}={Constants.MONO_SPACE.value}'COMPLETED'{Constants.NEW_LINE.value}{Constants.FOUR_SPACES.value}){Constants.NEW_LINE.value}ORDER{Constants.MONO_SPACE.value}BY{Constants.NEW_LINE.value}{Constants.FOUR_SPACES.value}test{Constants.MONO_SPACE.value}DESC{Constants.NEW_LINE.value};"
myQuery3_expected_surrogate = myQuery3_expected.replace(Constants.MONO_SPACE.value, Constants.SURROGATE.value)

myQuery3b = """select * from pyd01 p01 where not exists (select null from pyd20 p20 where p20.numtie=p01.numtie and p20.numtie not like 'P00B%') and p01.numtie like 'P000%' order by 1 desc;"""
myQuery3b_expected = f"SELECT{Constants.NEW_LINE.value}{Constants.FOUR_SPACES.value}*{Constants.NEW_LINE.value}FROM{Constants.NEW_LINE.value}{Constants.FOUR_SPACES.value}pyd01{Constants.MONO_SPACE.value}p01{Constants.NEW_LINE.value}WHERE{Constants.NEW_LINE.value}{Constants.FOUR_SPACES.value}NOT{Constants.MONO_SPACE.value}EXISTS{Constants.MONO_SPACE.value}({Constants.NEW_LINE.value}{Constants.EIGHT_SPACES.value}SELECT{Constants.NEW_LINE.value}{Constants.TWELVE_SPACES.value}NULL{Constants.NEW_LINE.value}{Constants.EIGHT_SPACES.value}FROM{Constants.NEW_LINE.value}{Constants.TWELVE_SPACES.value}pyd20{Constants.MONO_SPACE.value}p20{Constants.NEW_LINE.value}{Constants.EIGHT_SPACES.value}WHERE{Constants.NEW_LINE.value}{Constants.TWELVE_SPACES.value}p20.numtie{Constants.MONO_SPACE.value}={Constants.MONO_SPACE.value}p01.numtie{Constants.NEW_LINE.value}{Constants.TWELVE_SPACES.value}AND{Constants.MONO_SPACE.value}p20.numtie{Constants.MONO_SPACE.value}NOT{Constants.MONO_SPACE.value}LIKE{Constants.MONO_SPACE.value}'P00B%'{Constants.NEW_LINE.value}{Constants.FOUR_SPACES.value}){Constants.NEW_LINE.value}{Constants.FOUR_SPACES.value}AND{Constants.MONO_SPACE.value}p01.numtie{Constants.MONO_SPACE.value}LIKE{Constants.MONO_SPACE.value}'P000%'{Constants.NEW_LINE.value}ORDER{Constants.MONO_SPACE.value}BY{Constants.NEW_LINE.value}{Constants.FOUR_SPACES.value}1{Constants.MONO_SPACE.value}DESC{Constants.NEW_LINE.value};"
myQuery3b_expected_surrogate = myQuery3b_expected.replace(Constants.MONO_SPACE.value, Constants.SURROGATE.value)

myQuery4a = """select    COUNT(alertDescription.ALERT_OID) "ALT_ALERT_DESCRIPTION - RECORDS COUNT"
from    ALT_ALERT_DESCRIPTION alertDescription 
where exists(select null from ALT_ALERT alert where 
            alert.ALT_ALERT_OID=alertDescriptiON.ALERT_OID 
            and alert.expiry_date < replace( (sysdate - &days), '/', '.')
    );"""
myQuery4a_expected = f"SELECT{Constants.NEW_LINE.value}{Constants.FOUR_SPACES.value}COUNT(alertdescription.alert_oid){Constants.MONO_SPACE.value}\"ALT_ALERT_DESCRIPTION{Constants.MONO_SPACE.value}-{Constants.MONO_SPACE.value}RECORDS{Constants.MONO_SPACE.value}COUNT\"{Constants.NEW_LINE.value}FROM{Constants.NEW_LINE.value}{Constants.FOUR_SPACES.value}alt_alert_description{Constants.MONO_SPACE.value}alertdescription{Constants.NEW_LINE.value}WHERE{Constants.NEW_LINE.value}{Constants.FOUR_SPACES.value}EXISTS{Constants.MONO_SPACE.value}({Constants.NEW_LINE.value}{Constants.EIGHT_SPACES.value}SELECT{Constants.NEW_LINE.value}{Constants.TWELVE_SPACES.value}NULL{Constants.NEW_LINE.value}{Constants.EIGHT_SPACES.value}FROM{Constants.NEW_LINE.value}{Constants.TWELVE_SPACES.value}alt_alert{Constants.MONO_SPACE.value}alert{Constants.NEW_LINE.value}{Constants.EIGHT_SPACES.value}WHERE{Constants.NEW_LINE.value}{Constants.TWELVE_SPACES.value}alert.alt_alert_oid{Constants.MONO_SPACE.value}={Constants.MONO_SPACE.value}alertdescription.alert_oid{Constants.NEW_LINE.value}{Constants.TWELVE_SPACES.value}AND{Constants.MONO_SPACE.value}alert.expiry_date{Constants.MONO_SPACE.value}<{Constants.MONO_SPACE.value}REPLACE((sysdate - &days),{Constants.MONO_SPACE.value}'/',{Constants.MONO_SPACE.value}'.'){Constants.NEW_LINE.value}{Constants.FOUR_SPACES.value}){Constants.NEW_LINE.value};"
myQuery4a_expected_surrogate = myQuery4a_expected.replace(Constants.MONO_SPACE.value, Constants.SURROGATE.value)

myQuery4b = """SELECT 
    COUNT(alertDescription.ALERT_OID) "ALT_ALERT_DESCRIPTION - RECORDS COUNT"
FROM 
    ALT_ALERT_DESCRIPTION alertDescription 
WHERE 
    EXISTS (
        SELECT 
            NULL 
        from 
            ALT_ALERT alert 
        WHERE 
            alert.ALT_ALERT_OID=alertDescriptiON.ALERT_OID 
            AND alert.expiry_date < REPLACE((sysdate - &days), '/', '.')
    )
;"""
myQuery4b_expected = myQuery4a_expected
myQuery4b_expected_surrogate = myQuery4a_expected_surrogate

myQuery4c = """SELECT DISTINCT EP_TABLEPARAM.ID TABLEID FROM EP_TABLEPARAM;"""
myQuery4c_expected = f"SELECT{Constants.MONO_SPACE.value}DISTINCT{Constants.NEW_LINE.value}{Constants.FOUR_SPACES.value}ep_tableparam.id{Constants.MONO_SPACE.value}tableid{Constants.NEW_LINE.value}FROM{Constants.NEW_LINE.value}{Constants.FOUR_SPACES.value}ep_tableparam{Constants.NEW_LINE.value};"
myQuery4c_expected_surrogate = myQuery4c_expected.replace(Constants.MONO_SPACE.value, Constants.SURROGATE.value)


myQuery5a = """select * from ALT_CLIENTALERTDATA cl where cl.alt_clientalertdata_oid = (
    select c.alt_clientalertdata_oid from ALT_CLIENTALERTDATA c 
    left outer join ALT_ALERT a on c.alt_clientalertdata_oid = a.clientalertdata 
        where a.clientalertdata is null 
        and c.alt_clientalertdata_oid=cl.alt_clientalertdata_oid
    )
;"""
myQuery5a_expected= f"SELECT{Constants.NEW_LINE.value}{Constants.FOUR_SPACES.value}*{Constants.NEW_LINE.value}FROM{Constants.NEW_LINE.value}{Constants.FOUR_SPACES.value}alt_clientalertdata{Constants.MONO_SPACE.value}cl{Constants.NEW_LINE.value}WHERE{Constants.NEW_LINE.value}{Constants.FOUR_SPACES.value}cl.alt_clientalertdata_oid{Constants.MONO_SPACE.value}={Constants.MONO_SPACE.value}({Constants.NEW_LINE.value}{Constants.EIGHT_SPACES.value}SELECT{Constants.NEW_LINE.value}{Constants.TWELVE_SPACES.value}c.alt_clientalertdata_oid{Constants.NEW_LINE.value}{Constants.EIGHT_SPACES.value}FROM{Constants.NEW_LINE.value}{Constants.TWELVE_SPACES.value}alt_clientalertdata{Constants.MONO_SPACE.value}c{Constants.NEW_LINE.value}{Constants.EIGHT_SPACES.value}LEFT{Constants.MONO_SPACE.value}OUTER{Constants.MONO_SPACE.value}JOIN{Constants.MONO_SPACE.value}alt_alert{Constants.MONO_SPACE.value}a{Constants.MONO_SPACE.value}ON{Constants.MONO_SPACE.value}c.alt_clientalertdata_oid{Constants.MONO_SPACE.value}={Constants.MONO_SPACE.value}a.clientalertdata{Constants.NEW_LINE.value}{Constants.EIGHT_SPACES.value}WHERE{Constants.NEW_LINE.value}{Constants.TWELVE_SPACES.value}a.clientalertdata{Constants.MONO_SPACE.value}IS{Constants.MONO_SPACE.value}NULL{Constants.NEW_LINE.value}{Constants.TWELVE_SPACES.value}AND{Constants.MONO_SPACE.value}c.alt_clientalertdata_oid{Constants.MONO_SPACE.value}={Constants.MONO_SPACE.value}cl.alt_clientalertdata_oid{Constants.NEW_LINE.value}{Constants.FOUR_SPACES.value}){Constants.NEW_LINE.value};"
myQuery5a_expected_surrogate = myQuery5a_expected.replace(Constants.MONO_SPACE.value, Constants.SURROGATE.value)

myQuery5b = """SELECT 
    COUNT(addr.ALT_ADDRESS_OID) "ALT_ADDRESS - RECORDS COUNT"
FROM 
    ALT_ADDRESS addr 
WHERE 
    addr.ALT_ADDRESS_OID = (
        SELECT 
            ad.ALT_ADDRESS_OID 
        FROM 
            ALT_ADDRESS ad 
        LEFT OUTER JOIN ALT_CLIENTALERTDATA c ON ad.ALT_ADDRESS_OID = c.addressid 
        LEFT OUTER JOIN ALT_ALERT a ON c.alt_clientalertdata_oid = a.clientalertdata 
        WHERE 
            a.clientalertdata IS NULL 
            AND ad.ALT_ADDRESS_OID=addr.ALT_ADDRESS_OID
        )
;"""
myQuery5b_expected = f"SELECT{Constants.NEW_LINE.value}{Constants.FOUR_SPACES.value}COUNT(addr.alt_address_oid){Constants.MONO_SPACE.value}\"ALT_ADDRESS{Constants.MONO_SPACE.value}-{Constants.MONO_SPACE.value}RECORDS{Constants.MONO_SPACE.value}COUNT\"{Constants.NEW_LINE.value}FROM{Constants.NEW_LINE.value}{Constants.FOUR_SPACES.value}alt_address{Constants.MONO_SPACE.value}addr{Constants.NEW_LINE.value}WHERE{Constants.NEW_LINE.value}{Constants.FOUR_SPACES.value}addr.alt_address_oid{Constants.MONO_SPACE.value}={Constants.MONO_SPACE.value}({Constants.NEW_LINE.value}{Constants.EIGHT_SPACES.value}SELECT{Constants.NEW_LINE.value}{Constants.TWELVE_SPACES.value}ad.alt_address_oid{Constants.NEW_LINE.value}{Constants.EIGHT_SPACES.value}FROM{Constants.NEW_LINE.value}{Constants.TWELVE_SPACES.value}alt_address{Constants.MONO_SPACE.value}ad{Constants.NEW_LINE.value}{Constants.EIGHT_SPACES.value}LEFT{Constants.MONO_SPACE.value}OUTER{Constants.MONO_SPACE.value}JOIN{Constants.MONO_SPACE.value}alt_clientalertdata{Constants.MONO_SPACE.value}c{Constants.MONO_SPACE.value}ON{Constants.MONO_SPACE.value}ad.alt_address_oid{Constants.MONO_SPACE.value}={Constants.MONO_SPACE.value}c.addressid{Constants.NEW_LINE.value}{Constants.EIGHT_SPACES.value}LEFT{Constants.MONO_SPACE.value}OUTER{Constants.MONO_SPACE.value}JOIN{Constants.MONO_SPACE.value}alt_alert{Constants.MONO_SPACE.value}a{Constants.MONO_SPACE.value}ON{Constants.MONO_SPACE.value}c.alt_clientalertdata_oid{Constants.MONO_SPACE.value}={Constants.MONO_SPACE.value}a.clientalertdata{Constants.NEW_LINE.value}{Constants.EIGHT_SPACES.value}WHERE{Constants.NEW_LINE.value}{Constants.TWELVE_SPACES.value}a.clientalertdata{Constants.MONO_SPACE.value}IS{Constants.MONO_SPACE.value}NULL{Constants.NEW_LINE.value}{Constants.TWELVE_SPACES.value}AND{Constants.MONO_SPACE.value}ad.alt_address_oid{Constants.MONO_SPACE.value}={Constants.MONO_SPACE.value}addr.alt_address_oid{Constants.NEW_LINE.value}{Constants.FOUR_SPACES.value}){Constants.NEW_LINE.value};"
myQuery5b_expected_surrogate = myQuery5b_expected.replace(Constants.MONO_SPACE.value, Constants.SURROGATE.value)

myQuery5c = """
Select 
p01.numtie, p01.nomabr, zz1.libel1_1 "3rd party Type", 
zz3.libel1_1 "3rd party detailed role"
from pyd01_de p01
join 
pyd20_de p20 on p20.numtie= p01.numtie
join zzpy1 zz1 on zz1.argtbl = p01.typtie
join zzpy3 zz3 on zz3.argtbl =p20.detrol
where 
p20.roltie='02'
and p20.detrol='01' and p01.datnai>(SELECT substr(codtb1, 1, 4)-18||substr(codtb1, 5, 4) from zz002)
and p01.typtie ='01' order by datnai asc;
"""
myQuery5c_expected = f"SELECT{Constants.NEW_LINE.value}{Constants.FOUR_SPACES.value}p01.numtie,{Constants.NEW_LINE.value}{Constants.FOUR_SPACES.value}p01.nomabr,{Constants.NEW_LINE.value}{Constants.FOUR_SPACES.value}zz1.libel1_1{Constants.MONO_SPACE.value}\"3rd{Constants.MONO_SPACE.value}party{Constants.MONO_SPACE.value}Type\",{Constants.NEW_LINE.value}{Constants.FOUR_SPACES.value}zz3.libel1_1{Constants.MONO_SPACE.value}\"3rd{Constants.MONO_SPACE.value}party{Constants.MONO_SPACE.value}detailed{Constants.MONO_SPACE.value}role\"{Constants.NEW_LINE.value}FROM{Constants.NEW_LINE.value}{Constants.FOUR_SPACES.value}pyd01_de{Constants.MONO_SPACE.value}p01{Constants.NEW_LINE.value}JOIN{Constants.MONO_SPACE.value}pyd20_de{Constants.MONO_SPACE.value}p20{Constants.MONO_SPACE.value}ON{Constants.MONO_SPACE.value}p20.numtie{Constants.MONO_SPACE.value}={Constants.MONO_SPACE.value}p01.numtie{Constants.NEW_LINE.value}JOIN{Constants.MONO_SPACE.value}zzpy1{Constants.MONO_SPACE.value}zz1{Constants.MONO_SPACE.value}ON{Constants.MONO_SPACE.value}zz1.argtbl{Constants.MONO_SPACE.value}={Constants.MONO_SPACE.value}p01.typtie{Constants.NEW_LINE.value}JOIN{Constants.MONO_SPACE.value}zzpy3{Constants.MONO_SPACE.value}zz3{Constants.MONO_SPACE.value}ON{Constants.MONO_SPACE.value}zz3.argtbl{Constants.MONO_SPACE.value}={Constants.MONO_SPACE.value}p20.detrol{Constants.NEW_LINE.value}WHERE{Constants.NEW_LINE.value}{Constants.FOUR_SPACES.value}p20.roltie{Constants.MONO_SPACE.value}={Constants.MONO_SPACE.value}'02'{Constants.NEW_LINE.value}{Constants.FOUR_SPACES.value}AND{Constants.MONO_SPACE.value}p20.detrol{Constants.MONO_SPACE.value}={Constants.MONO_SPACE.value}'01'{Constants.NEW_LINE.value}{Constants.FOUR_SPACES.value}AND{Constants.MONO_SPACE.value}p01.datnai{Constants.MONO_SPACE.value}>{Constants.MONO_SPACE.value}({Constants.NEW_LINE.value}{Constants.EIGHT_SPACES.value}SELECT{Constants.NEW_LINE.value}{Constants.TWELVE_SPACES.value}SUBSTR(codtb1,{Constants.MONO_SPACE.value}1,{Constants.MONO_SPACE.value}4){Constants.MONO_SPACE.value}-{Constants.MONO_SPACE.value}18{Constants.MONO_SPACE.value}||{Constants.MONO_SPACE.value}SUBSTR(codtb1,{Constants.MONO_SPACE.value}5,{Constants.MONO_SPACE.value}4){Constants.NEW_LINE.value}{Constants.EIGHT_SPACES.value}FROM{Constants.NEW_LINE.value}{Constants.TWELVE_SPACES.value}zz002{Constants.NEW_LINE.value}{Constants.FOUR_SPACES.value}){Constants.NEW_LINE.value}{Constants.FOUR_SPACES.value}AND{Constants.MONO_SPACE.value}p01.typtie{Constants.MONO_SPACE.value}={Constants.MONO_SPACE.value}'01'{Constants.NEW_LINE.value}ORDER{Constants.MONO_SPACE.value}BY{Constants.NEW_LINE.value}{Constants.FOUR_SPACES.value}datnai{Constants.MONO_SPACE.value}ASC{Constants.NEW_LINE.value};"
myQuery5c_expected_surrogate = myQuery5c_expected.replace(Constants.MONO_SPACE.value, Constants.SURROGATE.value)

myQuery5d = """
select b.clientdto_clientreference "Client NUMCLI", c.clientname, a.oid "Portfolio ID", a.clientportfolioid "Portfolio reference", a.clientportfoliolinkreference "Client-Portfolio link reference", a.startdate "Start date", a.enddate "End date" from CLIENTPORTFOLIOLINKDTO a
join clientdto_clientportfoliolinkdto b on b.clientportfoliolinklist_oid = a.oid
join clientdto c on c.clientreference = b.clientdto_clientreference
where clientdto_clientreference = 'C001';
"""
myQuery5d_expected = f"SELECT{Constants.NEW_LINE.value}{Constants.FOUR_SPACES.value}b.clientdto_clientreference{Constants.MONO_SPACE.value}\"Client{Constants.MONO_SPACE.value}NUMCLI\",{Constants.NEW_LINE.value}{Constants.FOUR_SPACES.value}c.clientname,{Constants.NEW_LINE.value}{Constants.FOUR_SPACES.value}a.oid{Constants.MONO_SPACE.value}\"Portfolio ID\",{Constants.NEW_LINE.value}{Constants.FOUR_SPACES.value}a.clientportfolioid{Constants.MONO_SPACE.value}\"Portfolio reference\",{Constants.NEW_LINE.value}{Constants.FOUR_SPACES.value}a.clientportfoliolinkreference{Constants.MONO_SPACE.value}\"Client - Portfolio link reference\",{Constants.NEW_LINE.value}{Constants.FOUR_SPACES.value}a.startdate{Constants.MONO_SPACE.value}\"Start date\",{Constants.NEW_LINE.value}{Constants.FOUR_SPACES.value}a.enddate{Constants.MONO_SPACE.value}\"End date\"{Constants.NEW_LINE.value}FROM{Constants.NEW_LINE.value}{Constants.FOUR_SPACES.value}clientportfoliolinkdto{Constants.MONO_SPACE.value}a{Constants.NEW_LINE.value}JOIN{Constants.MONO_SPACE.value}clientdto_clientportfoliolinkdto{Constants.MONO_SPACE.value}b{Constants.MONO_SPACE.value}ON{Constants.MONO_SPACE.value}b.clientportfoliolinklist_oid{Constants.MONO_SPACE.value}={Constants.MONO_SPACE.value}a.oid{Constants.NEW_LINE.value}JOIN{Constants.MONO_SPACE.value}clientdto{Constants.MONO_SPACE.value}c{Constants.MONO_SPACE.value}ON{Constants.MONO_SPACE.value}c.clientreference{Constants.MONO_SPACE.value}={Constants.MONO_SPACE.value}b.clientdto_clientreference{Constants.NEW_LINE.value}WHERE{Constants.NEW_LINE.value}{Constants.FOUR_SPACES.value}clientdto_clientreference{Constants.MONO_SPACE.value}={Constants.MONO_SPACE.value}'C001'{Constants.NEW_LINE.value};"
myQuery5d_expected_surrogate = myQuery5d_expected.replace(Constants.MONO_SPACE.value, Constants.SURROGATE.value)

myQuery5e = """
SELECT DISTINCT X.ID, 
LISTAGG (DECODE(a)) WITHIN GROUP (ORDER BY X.ID, Y.oid, cl_bk.columnordernumber) OVER (PARTITION BY X.oid, Y.oid) "OCCUR_BK",
COUNT(x)
FROM X 
JOIN Y ON Y.TABLE_OID = X.OID
LEFT JOIN Z ON X.OID = i.table_oid
LEFT OUTER JOIN Z ON X.OID = i.table_oid
LEFT INNER JOIN Z ON X.OID = i.table_oid and x.w = zk.table_id
WHERE X.ID in ('DAILY_BANKING_CHANNEL')
ORDER BY X.id, Y.oid
;
"""
myQuery5e_expected = f"SELECT DISTINCT{Constants.NEW_LINE.value}{Constants.FOUR_SPACES.value}x.id,{Constants.NEW_LINE.value}{Constants.FOUR_SPACES.value}LISTAGG(DECODE(a)){Constants.NEW_LINE.value}{Constants.EIGHT_SPACES.value}WITHIN{Constants.MONO_SPACE.value}GROUP{Constants.MONO_SPACE.value}(ORDER{Constants.MONO_SPACE.value}BY{Constants.MONO_SPACE.value}x.id,{Constants.MONO_SPACE.value}y.oid,{Constants.MONO_SPACE.value}cl_bk.columnordernumber){Constants.NEW_LINE.value}{Constants.EIGHT_SPACES.value}OVER{Constants.MONO_SPACE.value}(PARTITION{Constants.MONO_SPACE.value}BY{Constants.MONO_SPACE.value}x.oid,{Constants.MONO_SPACE.value}y.oid) \"OCCUR_BK\",{Constants.NEW_LINE.value}{Constants.FOUR_SPACES.value}COUNT(x){Constants.NEW_LINE.value}FROM{Constants.NEW_LINE.value}{Constants.FOUR_SPACES.value}x{Constants.NEW_LINE.value}JOIN{Constants.MONO_SPACE.value}y{Constants.MONO_SPACE.value}ON{Constants.MONO_SPACE.value}y.table_oid{Constants.MONO_SPACE.value}={Constants.MONO_SPACE.value}x.oid{Constants.NEW_LINE.value}LEFT{Constants.MONO_SPACE.value}JOIN{Constants.MONO_SPACE.value}z{Constants.MONO_SPACE.value}ON{Constants.MONO_SPACE.value}x.oid{Constants.MONO_SPACE.value}={Constants.MONO_SPACE.value}i.table_oid{Constants.NEW_LINE.value}LEFT{Constants.MONO_SPACE.value}OUTER{Constants.MONO_SPACE.value}JOIN{Constants.MONO_SPACE.value}z{Constants.MONO_SPACE.value}ON{Constants.MONO_SPACE.value}x.oid{Constants.MONO_SPACE.value}={Constants.MONO_SPACE.value}i.table_oid{Constants.NEW_LINE.value}LEFT{Constants.MONO_SPACE.value}INNER{Constants.MONO_SPACE.value}JOIN{Constants.MONO_SPACE.value}z{Constants.MONO_SPACE.value}ON{Constants.MONO_SPACE.value}x.oid{Constants.MONO_SPACE.value}={Constants.MONO_SPACE.value}i.table_oid{Constants.NEW_LINE.value}{Constants.FOUR_SPACES.value}AND{Constants.MONO_SPACE.value}x.w{Constants.MONO_SPACE.value}={Constants.MONO_SPACE.value}zk.table_id{Constants.NEW_LINE.value}WHERE{Constants.NEW_LINE.value}{Constants.FOUR_SPACES.value}x.id{Constants.MONO_SPACE.value}IN{Constants.MONO_SPACE.value}('DAILY_BANKING_CHANNEL'){Constants.NEW_LINE.value}ORDER{Constants.MONO_SPACE.value}BY{Constants.NEW_LINE.value}{Constants.FOUR_SPACES.value}x.id,{Constants.NEW_LINE.value}{Constants.FOUR_SPACES.value}y.oid{Constants.NEW_LINE.value};"
myQuery5e_expected_surrogate = myQuery5e_expected.replace(Constants.MONO_SPACE.value, Constants.SURROGATE.value)

myQuery5f = """select * from pyd01 where datnai > (select SUBSTR(codtb1, 1, 4) - 18 || SUBSTR(codtb1, 5, 4) from zz002);"""
myQuery5f_expected = f"SELECT{Constants.NEW_LINE.value}{Constants.FOUR_SPACES.value}*{Constants.NEW_LINE.value}FROM{Constants.NEW_LINE.value}{Constants.FOUR_SPACES.value}pyd01{Constants.NEW_LINE.value}WHERE{Constants.NEW_LINE.value}{Constants.FOUR_SPACES.value}datnai{Constants.MONO_SPACE.value}>{Constants.MONO_SPACE.value}({Constants.NEW_LINE.value}{Constants.EIGHT_SPACES.value}SELECT{Constants.NEW_LINE.value}{Constants.TWELVE_SPACES.value}SUBSTR(codtb1,{Constants.MONO_SPACE.value}1,{Constants.MONO_SPACE.value}4){Constants.MONO_SPACE.value}-{Constants.MONO_SPACE.value}18{Constants.MONO_SPACE.value}||{Constants.MONO_SPACE.value}SUBSTR(codtb1,{Constants.MONO_SPACE.value}5,{Constants.MONO_SPACE.value}4){Constants.NEW_LINE.value}{Constants.EIGHT_SPACES.value}FROM{Constants.NEW_LINE.value}{Constants.TWELVE_SPACES.value}zz002{Constants.NEW_LINE.value}{Constants.FOUR_SPACES.value}){Constants.NEW_LINE.value};"
myQuery5f_expected_surrogate = myQuery5f_expected.replace(Constants.MONO_SPACE.value, Constants.SURROGATE.value)

myQuery5g = """select substr(codtb1, 1, 4)-18||substr(codtb1, 5, 4) from tab;"""
myQuery5g_expected = f"SELECT{Constants.NEW_LINE.value}{Constants.FOUR_SPACES.value}SUBSTR(codtb1,{Constants.MONO_SPACE.value}1,{Constants.MONO_SPACE.value}4){Constants.MONO_SPACE.value}-{Constants.MONO_SPACE.value}18{Constants.MONO_SPACE.value}||{Constants.MONO_SPACE.value}SUBSTR(codtb1,{Constants.MONO_SPACE.value}5,{Constants.MONO_SPACE.value}4){Constants.NEW_LINE.value}FROM{Constants.NEW_LINE.value}{Constants.FOUR_SPACES.value}tab{Constants.NEW_LINE.value};"
myQuery5g_expected_surrogate = myQuery5g_expected.replace(Constants.MONO_SPACE.value, Constants.SURROGATE.value)

myQuery5h = """select p01.numtie from pyd01_de p01 join pyd05_de p05 on (p05.numtie_1 = p01.numtie or p05.numtie_2 = p01.numtie);"""
myQuery5h_expected = f"SELECT{Constants.NEW_LINE.value}{Constants.FOUR_SPACES.value}p01.numtie{Constants.NEW_LINE.value}FROM{Constants.NEW_LINE.value}{Constants.FOUR_SPACES.value}pyd01_de{Constants.MONO_SPACE.value}p01{Constants.NEW_LINE.value}JOIN{Constants.MONO_SPACE.value}pyd05_de{Constants.MONO_SPACE.value}p05{Constants.MONO_SPACE.value}ON{Constants.MONO_SPACE.value}(p05.numtie_1{Constants.MONO_SPACE.value}={Constants.MONO_SPACE.value}p01.numtie{Constants.MONO_SPACE.value}OR{Constants.MONO_SPACE.value}p05.numtie_2{Constants.MONO_SPACE.value}={Constants.MONO_SPACE.value}p01.numtie){Constants.NEW_LINE.value};"
myQuery5h_expected_surrogate = myQuery5h_expected.replace(Constants.MONO_SPACE.value, Constants.SURROGATE.value)

myQuery6a = """select op_cod, structure_element_fk_cod, status, opt_fk_cod, version, update_date, update_user_id from eorg_op where op_cod in (
select op_cod from eorg_op 
minus
select op_fk_cod from eorg_allocation_op_user);"""
myQuery6a_expected = f"SELECT{Constants.NEW_LINE.value}{Constants.FOUR_SPACES.value}op_cod,{Constants.NEW_LINE.value}{Constants.FOUR_SPACES.value}structure_element_fk_cod,{Constants.NEW_LINE.value}{Constants.FOUR_SPACES.value}status,{Constants.NEW_LINE.value}{Constants.FOUR_SPACES.value}opt_fk_cod,{Constants.NEW_LINE.value}{Constants.FOUR_SPACES.value}version,{Constants.NEW_LINE.value}{Constants.FOUR_SPACES.value}update_date,{Constants.NEW_LINE.value}{Constants.FOUR_SPACES.value}update_user_id{Constants.NEW_LINE.value}FROM{Constants.NEW_LINE.value}{Constants.FOUR_SPACES.value}eorg_op{Constants.NEW_LINE.value}WHERE{Constants.NEW_LINE.value}{Constants.FOUR_SPACES.value}op_cod{Constants.MONO_SPACE.value}IN{Constants.MONO_SPACE.value}({Constants.NEW_LINE.value}{Constants.EIGHT_SPACES.value}SELECT{Constants.NEW_LINE.value}{Constants.TWELVE_SPACES.value}op_cod{Constants.NEW_LINE.value}{Constants.EIGHT_SPACES.value}FROM{Constants.NEW_LINE.value}{Constants.TWELVE_SPACES.value}eorg_op{Constants.NEW_LINE.value}{Constants.EIGHT_SPACES.value}MINUS{Constants.NEW_LINE.value}{Constants.EIGHT_SPACES.value}SELECT{Constants.NEW_LINE.value}{Constants.TWELVE_SPACES.value}op_fk_cod{Constants.NEW_LINE.value}{Constants.EIGHT_SPACES.value}FROM{Constants.NEW_LINE.value}{Constants.TWELVE_SPACES.value}eorg_allocation_op_user{Constants.NEW_LINE.value}{Constants.FOUR_SPACES.value}){Constants.NEW_LINE.value};"
myQuery6a_expected_surrogate = myQuery6a_expected.replace(Constants.MONO_SPACE.value, Constants.SURROGATE.value)

myQuery6b = """select op_cod, structure_element_fk_cod from eorg_op where op_cod in (
select op_cod from eorg_op 
minus
select op_fk_cod from eorg_allocation_op_user)
order by structure_element_fk_cod, op_cod;"""
myQuery6b_expected = f"SELECT{Constants.NEW_LINE.value}{Constants.FOUR_SPACES.value}op_cod,{Constants.NEW_LINE.value}{Constants.FOUR_SPACES.value}structure_element_fk_cod{Constants.NEW_LINE.value}FROM{Constants.NEW_LINE.value}{Constants.FOUR_SPACES.value}eorg_op{Constants.NEW_LINE.value}WHERE{Constants.NEW_LINE.value}{Constants.FOUR_SPACES.value}op_cod{Constants.MONO_SPACE.value}IN{Constants.MONO_SPACE.value}({Constants.NEW_LINE.value}{Constants.EIGHT_SPACES.value}SELECT{Constants.NEW_LINE.value}{Constants.TWELVE_SPACES.value}op_cod{Constants.NEW_LINE.value}{Constants.EIGHT_SPACES.value}FROM{Constants.NEW_LINE.value}{Constants.TWELVE_SPACES.value}eorg_op{Constants.NEW_LINE.value}{Constants.EIGHT_SPACES.value}MINUS{Constants.NEW_LINE.value}{Constants.EIGHT_SPACES.value}SELECT{Constants.NEW_LINE.value}{Constants.TWELVE_SPACES.value}op_fk_cod{Constants.NEW_LINE.value}{Constants.EIGHT_SPACES.value}FROM{Constants.NEW_LINE.value}{Constants.TWELVE_SPACES.value}eorg_allocation_op_user{Constants.NEW_LINE.value}{Constants.FOUR_SPACES.value}){Constants.NEW_LINE.value}ORDER{Constants.MONO_SPACE.value}BY{Constants.NEW_LINE.value}{Constants.FOUR_SPACES.value}structure_element_fk_cod,{Constants.NEW_LINE.value}{Constants.FOUR_SPACES.value}op_cod{Constants.NEW_LINE.value};"
myQuery6b_expected_surrogate = myQuery6b_expected.replace(Constants.MONO_SPACE.value, Constants.SURROGATE.value)

myQuery7a = """SELECT numtie, COUNT(*) FROM pyd75_de group by numtie having count(*)>1;"""
myQuery7a_expected = f"SELECT{Constants.NEW_LINE.value}{Constants.FOUR_SPACES.value}numtie,{Constants.NEW_LINE.value}{Constants.FOUR_SPACES.value}COUNT(*){Constants.NEW_LINE.value}FROM{Constants.NEW_LINE.value}{Constants.FOUR_SPACES.value}pyd75_de{Constants.NEW_LINE.value}GROUP{Constants.MONO_SPACE.value}BY{Constants.NEW_LINE.value}{Constants.FOUR_SPACES.value}numtie{Constants.MONO_SPACE.value}HAVING{Constants.MONO_SPACE.value}COUNT(*){Constants.MONO_SPACE.value}>{Constants.MONO_SPACE.value}1{Constants.NEW_LINE.value};"
myQuery7a_expected_surrogate = myQuery7a_expected.replace(Constants.MONO_SPACE.value, Constants.SURROGATE.value)

myQuery7b = """select a, b, c from x where a='I' group by a having count(*)> 1, b having count(*) >2 order by c desc;"""
myQuery7b_expected = f"SELECT{Constants.NEW_LINE.value}{Constants.FOUR_SPACES.value}a,{Constants.NEW_LINE.value}{Constants.FOUR_SPACES.value}b,{Constants.NEW_LINE.value}{Constants.FOUR_SPACES.value}c{Constants.NEW_LINE.value}FROM{Constants.NEW_LINE.value}{Constants.FOUR_SPACES.value}x{Constants.NEW_LINE.value}WHERE{Constants.NEW_LINE.value}{Constants.FOUR_SPACES.value}a{Constants.MONO_SPACE.value}={Constants.MONO_SPACE.value}'I'{Constants.NEW_LINE.value}GROUP{Constants.MONO_SPACE.value}BY{Constants.NEW_LINE.value}{Constants.FOUR_SPACES.value}a{Constants.MONO_SPACE.value}HAVING{Constants.MONO_SPACE.value}COUNT(*){Constants.MONO_SPACE.value}>{Constants.MONO_SPACE.value}1,{Constants.NEW_LINE.value}{Constants.FOUR_SPACES.value}b{Constants.MONO_SPACE.value}HAVING COUNT(*){Constants.MONO_SPACE.value}>{Constants.MONO_SPACE.value}2{Constants.NEW_LINE.value}ORDER{Constants.MONO_SPACE.value}BY{Constants.NEW_LINE.value}{Constants.FOUR_SPACES.value}c{Constants.MONO_SPACE.value}DESC{Constants.NEW_LINE.value};"
myQuery7b_expected_surrogate = myQuery7b_expected.replace(Constants.MONO_SPACE.value, Constants.SURROGATE.value)

myQuery7c = """select x, count(*) from tab where trim(staan) is null group by x;"""
myQuery7c_expected = f"SELECT{Constants.NEW_LINE.value}{Constants.FOUR_SPACES.value}x,{Constants.NEW_LINE.value}{Constants.FOUR_SPACES.value}COUNT(*){Constants.NEW_LINE.value}FROM{Constants.NEW_LINE.value}{Constants.FOUR_SPACES.value}tab{Constants.NEW_LINE.value}WHERE{Constants.NEW_LINE.value}{Constants.FOUR_SPACES.value}TRIM(staan){Constants.MONO_SPACE.value}IS{Constants.MONO_SPACE.value}NULL{Constants.NEW_LINE.value}GROUP{Constants.MONO_SPACE.value}BY{Constants.NEW_LINE.value}{Constants.FOUR_SPACES.value}x{Constants.NEW_LINE.value};"
myQuery7c_expected_surrogate = myQuery7c_expected.replace(Constants.MONO_SPACE.value, Constants.SURROGATE.value)


myQuery_test = """select op_cod, structure_element_fk_cod, status, opt_fk_cod, version, update_date, update_user_id from eorg_op where op_cod in (
select op_cod from eorg_op
minus
select op_fk_cod from eorg_allocation_op_user);"""


""" 
{Constants.NEW_LINE.value}
{Constants.NEW_LINE.value}{Constants.FOUR_SPACES.value}
{Constants.NEW_LINE.value}{Constants.EIGHT_SPACES.value}
{Constants.NEW_LINE.value}{Constants.TWELVE_SPACES.value}
{Constants.FOUR_SPACES.value}
{Constants.MONO_SPACE.value}
"""

if __name__ == '__main__':
    #print(myQuery7b_expected)
    pass


"""
Query to be tested
------------------

[1]

SELECT 
	country.country_name_eng,
	SUM(CASE WHEN call.id IS NOT NULL THEN 1 ELSE 0 END) AS calls,
	AVG(ISNULL(DATEDIFF(SECOND, call.start_time, call.end_time),0)) AS avg_difference
FROM country 
LEFT JOIN city ON city.country_id = country.id
LEFT JOIN customer ON city.id = customer.city_id
LEFT JOIN call ON call.customer_id = customer.id
GROUP BY 
	country.id,
	country.country_name_eng
HAVING AVG(ISNULL(DATEDIFF(SECOND, call.start_time, call.end_time),0)) > (SELECT AVG(DATEDIFF(SECOND, call.start_time, call.end_time)) FROM call)
ORDER BY calls DESC, country.id ASC;


"""