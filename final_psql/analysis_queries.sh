#How many ip’s responded to each scan. 
psql --host internet-research-observatory.cbl2cf4ozeq5.us-east-1.rds.amazonaws.com zmapdb -U iro_admin -c "SELECT * FROM ipcount ORDER BY count;"
#count per scan, ordered by country
psql --host internet-research-observatory.cbl2cf4ozeq5.us-east-1.rds.amazonaws.com zmapdb -U iro_admin -c "SELECT scan_id, countryabbr, SUM(count) FROM countrycount GROUP BY scan_id, countryabbr ORDER BY scan_id, countryabbr LIMIT 25;"
#Top country per scan
psql --host internet-research-observatory.cbl2cf4ozeq5.us-east-1.rds.amazonaws.com zmapdb -U iro_admin -c ";WITH cte AS (SELECT cc.scan_id, cc.countryabbr, c.countryname, sum(cc.count), ROW_NUMBER() OVER (PARTITION BY cc.scan_id ORDER BY SUM(cc.count) DESC) AS rn FROM countrycount cc LEFT JOIN (SELECT DISTINCT countryabbr, countryname FROM country) c ON cc.countryabbr = c.countryabbr GROUP BY cc.scan_id, cc.countryabbr, c.countryname, cc.count) SELECT * FROM cte WHERE rn =1;"
#Top 10 countries per scan
psql --host internet-research-observatory.cbl2cf4ozeq5.us-east-1.rds.amazonaws.com zmapdb -U iro_admin -c ";WITH cte AS (SELECT cc.scan_id, cc.countryabbr, c.countryname, sum(cc.count), ROW_NUMBER() OVER (PARTITION BY cc.scan_id ORDER BY SUM(cc.count) DESC) AS rn FROM countrycount cc LEFT JOIN (SELECT DISTINCT countryabbr, countryname FROM country) c ON cc.countryabbr = c.countryabbr GROUP BY cc.scan_id, cc.countryabbr, c.countryname, cc.count) SELECT * FROM cte WHERE rn <11;"
#Top 25 countries overall
psql --host internet-research-observatory.cbl2cf4ozeq5.us-east-1.rds.amazonaws.com zmapdb -U iro_admin -c "SELECT c.countryname, SUM(cc.count) FROM countrycount cc LEFT JOIN (SELECT DISTINCT countryabbr, countryname FROM country) c ON cc.countryabbr = c.countryabbr GROUP BY c.countryname ORDER BY sum(cc.count) DESC LIMIT 25;"
#Bottom 25 countries overall
psql --host internet-research-observatory.cbl2cf4ozeq5.us-east-1.rds.amazonaws.com zmapdb -U iro_admin -c "SELECT c.countryname, SUM(cc.count) FROM countrycount cc LEFT JOIN (SELECT DISTINCT countryabbr, countryname FROM country) c ON cc.countryabbr = c.countryabbr GROUP BY c.countryname ORDER BY sum(cc.count) ASC LIMIT 25;"