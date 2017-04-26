import datetime
import calendar
import time
import RupertMail

class task():
    """
    Schedule a task to happen
    """
    def __init__(self, func, schedule, **kwargs):
        self.func = func
        self.jobDone = False
        self.schedule = schedule
        self.args = kwargs

    def performTask(self):
        if self.jobDone == False:
            self.func(**self.args)
            self.jobDone = True

    def trySchedule(self):
        today = datetime.datetime.today()
        currentDayOfTheWeek = calendar.day_name[today.weekday()]
        currentHour = today.hour
        currentMin = today.minute
        try:
            if self.schedule[currentDayOfTheWeek] != None:
                if int(self.schedule[currentDayOfTheWeek]) <= currentHour:
                    self.performTask()

        # This is a slight hack and should be worked around quickly.
        # If a task hasn't declared tasks on a specific day
        # KeyError is rasised. If so, do nothing.
        except KeyError:
            pass



    def resetTask(self):
        self.jobDone = False

    def getStatus(self):
        print(self.jobDone)

class taskQue():

    def __init__(self, taskRegister):
        self.taskRegister = taskRegister
        self.taskQue = []

    def renderTaskQue(self):
        """
        Create a list of task objects
        """
        for pendingTask in self.taskRegister:
            # Check if there are arguments passed.
            try:
                args = self.taskRegister[pendingTask][2]
            except IndexError:
                args = {}

            # Create a list of task objects
            self.taskQue.append(task(
                        self.taskRegister[pendingTask][0],
                        self.taskRegister[pendingTask][1],
                        **args)
                        )

    def executeQue(self):
        for t in self.taskQue:
            try:
                t.trySchedule()
            except Exception as e:
                subj = "ERROR during execute:"
                errorMsg = "An error occured: \n" + str(e)
                RupertMail.sendEmailToAdmin(subj, errorMsg)
                print(subj, e)

    def getQue(self):
        return self.taskQue

    def resetQue(self):
        # Check if all tasks are complete
        todo = [1 if task.jobDone == False else 0 for task in self.getQue()]
        done = True if todo.count(0) == len(todo) else False

        if done == True:
            for t in self.taskQue:
                t.resetTask()
