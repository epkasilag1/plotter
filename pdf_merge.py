from PyPDF2 import PdfFileMerger

pdfs = ['Philippines.pdf', 'RES.pdf']

merger = PdfFileMerger()

for pdf in pdfs:
    merger.append(pdf)

merger.write("Result.pdf")
merger.close()