import pikepdf

with pikepdf.open("/Users/arjav/Desktop/FinScope/sample_data/Acct Statement_1032_16062026_18.23.42.pdf", password="329297286") as pdf:
    pdf.save("/Users/arjav/Desktop/FinScope/sample_data/Acct_unlocked.pdf")