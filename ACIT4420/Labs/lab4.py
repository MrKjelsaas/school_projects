from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
import wmi

c = wmi.WMI()

processes = []

for process in c.Win32_Process():
    processes.append([process.Name, process.ProcessId])

for i in range(len(processes)):
    processes[i][0] = processes[i][0].lower() # We do this because .sort() sorts upper case characters first
processes.sort()


# Time to make a pdf
myPdf = canvas.Canvas("lab4.pdf")

for i in range(len(processes)):
        myString = str(processes[i][0]) + "   " + str(processes[i][1])
        myPdf.drawString(2*cm, (29-(i*0.5))*cm, myString)

myPdf.showPage()
myPdf.save()
