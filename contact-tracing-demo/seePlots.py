import os.path
import sys
import pprint
import sqlite3
import numpy as np
import matplotlib.pyplot as plt
from place import PlaceInfo

pp = pprint.PrettyPrinter(indent=2)

if len(sys.argv) > 1:
    outName = sys.argv[1]
else:
    outName = 'prox'

def getQuery(cur,sql):
    cur.execute(sql)
    return(cur.fetchall())

def getListsFromQuery(cur, sql):
    cur.execute(sql)
    ans = cur.fetchall()
    width = len(ans[0])
    depth = len(ans)
    x = np.empty([depth,width])
    for r in range(depth):
        for i in range(width):
            x[r,i] = ans[r][i]
    return x

dbDir = os.path.join('out')
dbPath = os.path.join('out',outName+'.db')
conn = sqlite3.connect(dbPath)
cur = conn.cursor()
print(f"Plots for DB {outName}.db")

sql = "select lat, lon from encounters"
colors = ['red','green','blue']
roles = ['worker','student','home']
for i in range(len(colors)):
    sql = f'''
select lat, lon from
people join encounters
on people.id = encounters.pid1
where role = '{roles[i]}'
'''
    x = getListsFromQuery(cur,sql)
    plt.scatter(x[:,1],x[:,0],s=1,alpha=0.2,c=colors[i],label=roles[i])
plt.plot(7.7396,49.4253,markersize=15,color='black', marker='x')
plt.legend()
plt.title("All encounters by role")
plt.show()

sql = f'''
select lat, lon from
people join encounters
on people.id = encounters.pid1
where strftime('%H', time) in ('14')
'''
x = getListsFromQuery(cur,sql)
plt.scatter(x[:,1],x[:,0],s=1,alpha=0.2,c='red',label='day')
sql = f'''
select lat, lon from
people join encounters
on people.id = encounters.pid1
where strftime('%H', time) in ('00','01','02','03','04','05','06','07')
'''
x = getListsFromQuery(cur,sql)
plt.scatter(x[:,1],x[:,0],s=1,alpha=0.2,c='blue',label='night')
plt.plot(7.7396,49.4253,markersize=15,color='black', marker='x')
plt.legend()
plt.title("All encounters by time of day")
plt.show()



sql = f'''
select lat, lon from
people join encounters
on people.id = encounters.pid1
where role = '{roles[i]}' and
   lat between 49.422 and 49.430 and
   lon between 7.735 and 7.75
'''
