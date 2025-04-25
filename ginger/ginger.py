import os
# Original PDF from the game manual on steam: https://store.steampowered.com/manual/3418910
# Then converted into .txt via an online converter
# This program takes the txt and converts it into a .csv
txtfile = "./ginger_dictionary_paper_edition_v13.txt"
output_name = "ginger.csv"
cwd = os.getcwd()
outpath = os.path.join(cwd,output_name)
# header for csv columns
header = "Entry,Definition\n"

with open(txtfile,'r') as f:
  text = f.read()

text_list = text.split('\n')
past_intro = False
entries_dict = {} # entry: def
entry = ''
entry_def = ''
for line in text_list:
  # skip the first few lines
  # GINGER
  # vh cxqku ee dudi kytu
  # (c) kevin du 2025
  stripped_line = line.strip()
  if not past_intro:
    if stripped_line == '':
      past_intro = True
      print('Past the intro')
    continue
  if stripped_line == '' or stripped_line.find('/') != -1:
    continue

  if len(stripped_line.split(' ')) == 1 and stripped_line.find('.') == -1:
    # if it's a single word and no punctuation, then it's an entry.
    # first we save the previous entry, then track the new one.
    if entry:
      if not entry_def:
        print(f"There is an entry without a definition: {entry}")
      entries_dict[entry] = entry_def
    entry = stripped_line
    entry_def = ''
  elif entry:
    entry_def += stripped_line + ' '

if entry:
  entries_dict[entry] = entry_def
print(f"Length of entries: {len(entries_dict)}")

csv_text = header
for k,v in entries_dict.items():
  csv_text += f"{k},{v}" + '\n'

with open(outpath,'w') as f:
  f.write(csv_text)
print('Done!')