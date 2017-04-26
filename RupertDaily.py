import RupertTaskManager as rtm
import datetime
import time
import yahoo_data_handler as ydh
import RupertCron

def debug(stringArg = "Mr Debug"):
    print(stringArg)


"""
CREATE DAILY TASKS
Add each tas to taskRegister as a dictionary entry.
Use key as a name identifier.
The value is a list: [function, {schedule}, {arguments}]
Ex:
    'TestTask':[myFunc, {'Friday':10}, {'myArg':'Test'}]
"""

taskRegister={
    "databaseDownload":[ydh.addDataToDatabase, {
                            'Monday':4,
                            'Tuesday':4,
                            'Wednesday':4,
                            'Thursday':4,
                            'Friday': 4,
                            'Saturday': None,
                            'Sunday':None
                            }],
    "CSVDownload":[ydh.collect_batch_data, {
                            'Monday':5,
                            'Tuesday':5,
                            'Wednesday':5,
                            'Thursday':5,
                            'Friday': 5,
                            'Saturday': None,
                            'Sunday':None
                            },
                            {'stocklist':'OMX-ST.txt'}],
    # "Debugging":[debug, {'Wednesday':9}]
}

# Create task que objects
tasks = rtm.taskQue(taskRegister)
tasks.renderTaskQue()

while True:
    tasks.executeQue()

    # Reset task que if new day @ 01:00
    currentHour = datetime.datetime.today().hour
    currentMin = datetime.datetime.today().minute
    print("TIME: " + str(currentHour) +":"+str(currentMin))
    if 2 > currentHour >= 1:
        tasks.resetQue()
        print("Que was reset!")

    # Sleep for _some_ time
    time.sleep(60*20) # Seconds
