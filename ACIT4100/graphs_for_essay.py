import matplotlib.pyplot as plt; plt.rcdefaults()
import numpy as np
import matplotlib.pyplot as plt

"""
publishYears = (2019, 1999, 2006, 2016, 2002, 2014, 2012, 2004, 2009, 2017, 1998, 2007, 2008, 1977, 2006, 2019, 2020, 2020, 2018, 2019)
academicArticle = ("yes", "yes", "yes", "yes", "yes", "yes", "yes", "yes", "no", "yes", "yes", "yes", "yes", "yes", "yes", "no", "no", "no", "no", "no")

years = []
for i in range(min(publishYears), max(publishYears)+1):
    years.append([i, 0, 0])

for i in range(len(publishYears)):
    if academicArticle[i] == "yes":
        years[publishYears[i]-1977][1] += 1
    elif academicArticle[i] == "no":
        years[publishYears[i]-1977][2] += 1

academic_publish_years = []
nonAcademic_publish_years = []
for i in range(len(years)):
    academic_publish_years.append(years[:][i][1])
    nonAcademic_publish_years.append(years[:][i][2])

n_groups = len(years)

fig, ax = plt.subplots()
index = np.arange(n_groups)
bar_width = 0.35
opacity = 0.8

rects1 = plt.bar(index, academic_publish_years, bar_width, alpha=opacity, color='b', label='Academic article')
rects2 = plt.bar(index + bar_width, nonAcademic_publish_years, bar_width, alpha=opacity, color='g', label='Non-academic article')

myRange = []
for i in range(min(publishYears), max(publishYears)+1):
    myRange.append(i)

for i in range(len(myRange)):
    while myRange[i] >= 100:
        myRange[i] -= 100
    if myRange[i] < 10:
        myRange[i] = str("0" + str(myRange[i]))

plt.xlabel("Year")
plt.ylabel("Number of articles")
plt.title("Articles published")
plt.xticks(index + bar_width, myRange)
plt.legend()

plt.tight_layout()
plt.show()
"""



my_data = np.array([4, 1, 1, 4, 1, 1, 2, 1, 2, 2])
my_labels = "sEMG interpretation", "Evolvable hardware", "Complete prosthetics system", "Control systems", "Socket fitting", "Actuators", "Applications of an exoskeleton", "History and challenges", "AI in prosthetics", "Movement prediction/adaptation"

def absolute_value(val):
    a = np.round(val/100.*my_data.sum(), 0)
    return int(a)
plt.pie(my_data, labels = my_labels, autopct = absolute_value)
plt.title("Focus areas\n")
plt.axis('equal')
plt.show()
