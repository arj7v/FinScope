import pikepdf

with pikepdf.open("/Users/arjav/Desktop/FinScope/sample_data/5010XXXXXX1032_7d1548cc_16Jul2026_TO_15Aug2026_142140508.pdf", password="ARJA1208") as pdf:
    pdf.save("/Users/arjav/Desktop/FinScope/sample_data/Statement2_unlocked.pdf")