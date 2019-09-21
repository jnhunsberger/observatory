#if directory already exists, remove it
rm -rf ipCountry
mkdir ipCountry
#load original csv file, remove header row, and move to final directory
wget https://s3.amazonaws.com/zmap-vb/IPCountry.csv -P ipCountry
tail -n +2 ipCountry/IPCountry.csv > ipCountry/country.csv
#create postgres table
psql --host internet-research-observatory.cbl2cf4ozeq5.us-east-1.rds.amazonaws.com zmapdb -U iro_admin -c "DROP TABLE IF EXISTS Country;"
psql --host internet-research-observatory.cbl2cf4ozeq5.us-east-1.rds.amazonaws.com zmapdb -U iro_admin -c "DROP TABLE IF EXISTS ipcount;"
psql --host internet-research-observatory.cbl2cf4ozeq5.us-east-1.rds.amazonaws.com zmapdb -U iro_admin -c "DROP TABLE IF EXISTS countrycount;" 
psql --host internet-research-observatory.cbl2cf4ozeq5.us-east-1.rds.amazonaws.com zmapdb -U iro_admin -c "CREATE TABLE Country                                                        
     (ipStart bigint,
     ipEnd bigint,
     countryAbbr varchar(15),
     countryName varchar(50));"
psql --host internet-research-observatory.cbl2cf4ozeq5.us-east-1.rds.amazonaws.com zmapdb -U iro_admin -c "CREATE TABLE ipcount                                                        
     (scan_id varchar(50),
     count int);"
psql --host internet-research-observatory.cbl2cf4ozeq5.us-east-1.rds.amazonaws.com zmapdb -U iro_admin -c "CREATE TABLE countrycount
     (scan_id varchar(50),
     countryAbbr varchar(15),
     count int);"
#copy data to table
psql --host internet-research-observatory.cbl2cf4ozeq5.us-east-1.rds.amazonaws.com zmapdb -U iro_admin -c "\copy Country FROM 'ipCountry/country.csv' DELIMITER ',' CSV;"
