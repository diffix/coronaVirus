import os.path
import sys
import pprint
import sqlite3
from place import PlaceInfo

pp = pprint.PrettyPrinter(indent=2)

if len(sys.argv) > 1:
    outName = sys.argv[1]
else:
    outName = 'prox'


def doQuery(cur,sql):
    cur.execute(sql)
    data = cur.fetchall()
    cols = []
    for x in cur.description:
        cols.append(x[0])
    print(cols)
    pp.pprint(data)


def getQuery(cur,sql):
    cur.execute(sql)
    return(cur.fetchall())


def oneDayStats(cur,day):
    print(f"\n!!!!!!!!!!!!!!!!!!!!!!!!!!! {day} !!!!!!!!!!!!!!!!!!!!!!!!!!!")
    
    print("\n================================================================")
    print(f"\n--------    visits table {day}")
    sql = f'''
    select *
    from visits
    where strftime('%Y-%m-%d', start) = '{day}'
    limit 1
    '''
    doQuery(cur,sql)
    
    print(f"\n--------    total number visits {day}")
    sql = f'''
    select place_type, count(*) as cnt
    from visits
    where strftime('%Y-%m-%d', start) = '{day}'
    group by 1
    '''
    doQuery(cur,sql)
    
    print(f"\n--------    visits stats by place type {day}")
    sql = '''
    select distinct place_type from visits
    '''
    placeTypes = getQuery(cur,sql)
    for tup in placeTypes:
        placeType = tup[0]
        print(f"\n    ---- {placeType} {day}")
        sql = f'''select
            (cast((julianday(end) - julianday(start)) * 24 * 60 as int)/5)*5
                as visit_len_mins,
            count(*) as num_visits
            from visits
            where place_type = '{placeType}'
                and strftime('%Y-%m-%d', start) = '{day}'
            group by 1
            order by 1
            '''
        doQuery(cur,sql)
        print(f"        ---- {placeType} {day}")
        sql = f'''select
            count(*) as num_visits,
            min(start) as first_start,
            max(start) as last_start,
            min(end) as first_end,
            max(end) as last_end,
            round(min(cast((julianday(end) - julianday(start)) * 24 * 60 as real)),2)
                as shortest_visit_mins,
            round(max(cast((julianday(end) - julianday(start)) * 24 * 60 as real)),2)
                as longest_visit_mins,
            round(avg(cast((julianday(end) - julianday(start)) * 24 * 60 as real)),2)
                as average_visit_mins
            from visits
            where place_type = '{placeType}'
                and strftime('%Y-%m-%d', start) = '{day}'
            '''
        doQuery(cur,sql)
        print(f"        ---- {placeType} {day}")
        sql = f'''select
            max(num_visits) as max_num_visits,
            min(num_visits) as min_num_visits,
            round(avg(num_visits),2) as avg_num_visits
            from (
                select place_name, count(*) as num_visits
                from visits
                where place_type = '{placeType}'
                    and strftime('%Y-%m-%d', start) = '{day}'
                group by 1
            ) t
        '''
        doQuery(cur,sql)
    
        print(f"        ---- {placeType} {day}")
        sql = f'''select
            max(num_distinct_persons) as max_num_distinct_persons,
            min(num_distinct_persons) as min_num_distinct_persons,
            round(avg(num_distinct_persons),2) as avg_num_distinct_persons
            from (
                select place_name, count(distinct pid) as num_distinct_persons
                from visits
                where place_type = '{placeType}'
                    and strftime('%Y-%m-%d', start) = '{day}'
                group by 1
            ) t
        '''
        doQuery(cur,sql)
    
    print(f"\n--------    visits starts by hour {day}")
    sql = f'''
    select strftime('%H', start) as start_hour,
           count(*) as cnt
    from visits
    where strftime('%Y-%m-%d', start) = '{day}'
    group by 1
    '''
    doQuery(cur,sql)
    
    print(f"\n--------    visits ends by hour {day}")
    sql = f'''
    select strftime('%H', end) as end_hour,
           count(*) as cnt
    from visits
    where strftime('%Y-%m-%d', start) = '{day}'
    group by 1
    '''
    doQuery(cur,sql)
    
    print(f"\n--------    visits per person {day}")
    sql = f'''select
        num_visits, count(*) as cnt_persons
        from (
            select pid, count(*) as num_visits
            from visits
            where strftime('%Y-%m-%d', start) = '{day}'
            group by 1
        ) t
        group by 1
    '''
    doQuery(cur,sql)
    
    print("\n================================================================")
    print("\n--------    encounters table")
    sql = f'''
    select *
    from encounters
    where strftime('%Y-%m-%d', time) = '{day}'
    limit 1
    '''
    doQuery(cur,sql)
    
    print(f"\n--------    total number encounters {day}")
    sql = f'''
    select place_type, count(*) as cnt
    from encounters
    where strftime('%Y-%m-%d', time) = '{day}'
    group by 1
    '''
    doQuery(cur,sql)
    
    print(f"\n--------    encounters stats by place type {day}")
    sql = f'''
    select distinct place_type from encounters
    '''
    data = getQuery(cur,sql)
    for tup in data:
        placeType = tup[0]
        print(f"\n    ---- {placeType} {day}")
        sql = f'''select
            count(*) as num_encounters,
            min(time) as first_start,
            max(time) as last_start
            from encounters
            where place_type = '{placeType}'
               and strftime('%Y-%m-%d', time) = '{day}'
            '''
        doQuery(cur,sql)
        print("        ----")
        sql = f'''select
            max(num_encounters) as max_num_encounters,
            min(num_encounters) as min_num_encounters,
            round(avg(num_encounters),2) as avg_num_encounters
            from (
                select place_name, count(*) as num_encounters
                from encounters
                where place_type = '{placeType}'
                    and strftime('%Y-%m-%d', time) = '{day}'
                group by 1
            ) t
        '''
        doQuery(cur,sql)
    
    print(f"\n--------    encounters by hour {day}")
    sql = f'''
    select strftime('%H',time) as hour, count(*) as cnt
    from encounters
    where strftime('%Y-%m-%d', time) = '{day}'
    group by 1
    '''
    doQuery(cur,sql)
    
    print(f"\n--------    encounters per person {day}")
    sql = f'''select
        num_encounters, count(*) as cnt_persons
        from (
            select pid1, count(*) as num_encounters
            from encounters
            where strftime('%Y-%m-%d', time) = '{day}'
            group by 1
        ) t
        group by 1
    '''
    doQuery(cur,sql)


dbDir = os.path.join('out')
dbPath = os.path.join('out',outName+'.db')
conn = sqlite3.connect(dbPath)
cur = conn.cursor()

print(f"Stats for DB {outName}.db")

print("\n================================================================")
print("\n--------    people table")
sql = '''
select *
from people
limit 1
'''
doQuery(cur,sql)

print("\n--------    age buckets")
sql = '''
select round((age/5)-1/2)*5 as age, count(*)
from people
group by 1
'''
doQuery(cur, sql)

for place in PlaceInfo.getPlaceNames():
    print(f"\n--------    {place} freq buckets")
    sql = f'''
    select min({place}_visit_freq) as min_visit_freq,
           max({place}_visit_freq) as max_visit_freq,
           round(avg({place}_visit_freq),2) as avg_visit_freq
    from people
    '''
    doQuery(cur, sql)
    print(f"\n--------    {place} favorite buckets")
    sql = f'''
    select
        min(fav_cnt) as min_fav_cnt,
        max(fav_cnt) as max_fav_cnt,
        avg(fav_cnt) as avg_fav_cnt
    from (
        select {place}_first_fav, count(*) as fav_cnt
        from people
        group by 1 ) t
    '''
    doQuery(cur, sql)
    print(f"\n--------    {place} second favorite buckets")
    sql = f'''
    select
        min(fav_cnt) as min_fav_cnt,
        max(fav_cnt) as max_fav_cnt,
        avg(fav_cnt) as avg_fav_cnt
    from (
        select {place}_second_fav, count(*) as fav_cnt
        from people
        group by 1 ) t
    '''
    doQuery(cur, sql)

print("\n================================================================")
print("\n--------    homes table")
sql = '''
select *
from homes
limit 1
'''
doQuery(cur,sql)

print("\n--------    number of homes")
sql = '''
select count(*) as number_of_homes
from homes
'''
doQuery(cur,sql)

for person in ['adults','children','people']:
    print(f"\n--------    num {person}")
    sql = f'''
        select {person}, count(*) as cnt
        from homes
        group by 1
    '''
    doQuery(cur,sql)

print("\n--------    people totals (should match)")
sql = '''
select sum(adults) + sum(children) as people1,
       sum(people) as people2
from homes
'''
doQuery(cur,sql)

for cap in ['work_capacity', 'visit_capacity']:
    print(f"\n--------    home {cap}")
    sql = f'''
    select min({cap}) as min,
           max({cap}) as max,
           round(avg({cap}),2) as avg
    from homes
    '''
    doQuery(cur, sql)

print("\n================================================================")
print("\n--------    workPlaces table")
sql = '''
select *
from workPlaces
limit 1
'''
doQuery(cur,sql)

print("\n--------    number of workPlaces")
sql = '''
select type, count(*) as cnt
from workPlaces
group by 1
'''
doQuery(cur,sql)

for place in PlaceInfo.getPlaceNames():
    print(f"\n--------    {place} capacity")
    sql = f'''
    select
           min(work_capacity) as min_work_cap,
           max(work_capacity) as max_work_cap,
           round(avg(work_capacity),2) as avg_work_cap,
           min(visit_capacity) as min_visit_cap,
           max(visit_capacity) as max_visit_cap,
           round(avg(visit_capacity),2) as avg_visit_cap
    from workPlaces
    where type = '{place}'
    '''
    doQuery(cur, sql)

sql = '''
select distinct strftime('%Y-%m-%d', start) as day
from visits
group by 1
'''
days = getQuery(cur,sql)
for tup in days:
    oneDayStats(cur,tup[0])

conn.close()
