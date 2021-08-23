from PyPDF2 import PdfFileMerger

pdfs = ['Philippines.pdf', 'RES.pdf']

merger = PdfFileMerger()

for pdf in pdfs:
    merger.append(pdf)

f = open('C:/EQP11-20/Programs/PLOT.OUT')
lines = f.readlines()
f.close()

date = lines[0][:6].replace(' ', '0')

merger.write(date + ".pdf")
merger.close()