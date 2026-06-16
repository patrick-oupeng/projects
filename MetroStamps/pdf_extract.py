import os
from pypdf import PdfReader as r

DEFAULT_DIRECTORY="./timetables"
OUTPUT_DIRECTORY="./csv-timetables"
DEFAULT_FILE=None
# DEFAULT_FILE="101a.PDF"


def extract_single_file(file_to_extract: str, testing: bool = False):
    output_filename = ""
    num_cols = 0
    output_columns = []
    try:
        page1 = r(file_to_extract).get_page(0)
        # Expects the default format of timetable pdfs.
        lines = page1.extract_text().split('\n')
    except Exception as e:
        print(f"error reading file {file_to_extract}: {e}")
    
    # we'll need to track where we are in the output string.
    column = 0
    hour = 0
    minute = None
    ####
    # idea is that in each column, it needs to start with a relatively small number,
    # and as far as I can tell it's pretty much guaranteed that you will end up with
    # a final minute in column b that is less than the hour in column c
    # also, each column has the hour and then a maximum of 8 values
    # you might have:
    #  13 00 09 18 27 36 45 54 13 03 07 11 15 19 23 27 31 13 03 07 11 15 19 23 27 31
    # which should output
    # [{13: [0, 9, 18, 27, 36, 45, 54]}, {13: [...]}]
    for l in lines:
        if output_filename == "" and l.find('時刻表') != -1:
            output_filename = f"{l.replace('時刻表','')}.csv"
            if testing:
                print(f"saving to {output_filename}")
            if l.find("小鼻灘") != -1 or l.find("新北投") != -1:
                return output_filename, None
            continue
        if num_cols ==0 and l.find('時') != -1 and l.find('Hour') != -1:
            num_cols = l.count('Hour')
            output_columns = [{} for _ in range(num_cols)]
            continue
        if output_filename != "" and num_cols != 0 and l.split(' ')[0].isdigit():
            times = l.split(' ')
            start_ind = 0
            if hour ==0 or int(times[0]) == (hour + 1) % 24:
                hour = int(times[0])
                start_ind = 1
            for i in range(len(times)):
                if i < start_ind:
                    continue
                current_number = int(times[i])
                if minute == None:
                    minute = current_number
                    # now we also need to make sure what column we should be in
                    if output_columns[column].get(hour, None) != None:
                        try:
                            print(f"recalculating column... | column {column} | hour {hour}")
                            print(output_columns[column][hour])
                            while minute < output_columns[column][hour][-1]:
                                column += 1 
                        except IndexError as e:
                            print("Tried to go over too far on the columns. Not sure why, this was working earlier.")
                            print(f"file {file_to_extract}")
                            print(f"hour {hour} | minute {minute} | column {column}")
                            print(f"full line {l}")
                            raise(e)
                elif current_number < minute:
                    # If I found the hour in another column, increment the column, reset the minute, and continue.
                    if current_number == (hour + 1) %  24:
                        hour = current_number
                        print()
                    column +=1
                    minute=None
                    continue
                elif output_filename.find("台電大樓站往松山站") != -1 and minute == 46 and current_number == 54:
                    column += 1
                    minute = current_number
                else:
                    minute = current_number
                if output_columns[column].get(hour, None) == None:
                    output_columns[column][hour] = []
                if testing:
                    print(f"column {column +1} | hour {hour} | minute {minute}")
                output_columns[column][hour].append(minute)
            minute = None
            column = 0
    if testing:
        print("\n\noutput dict:")
        for ind in range(len(output_columns)):
            print(f"Column {ind+1}:")
            col = output_columns[ind]
            for h in col.keys():
                ms = col[h]
                print(f"{h} | {ms}")
            print()
    return output_filename, output_columns

def extract_all_files(directory_to_walk: str):
    for _, _, filenames in os.walk(directory_to_walk):
        for f in filenames:
            print(f"Reading {f}...", end="\r")
            filename_to_read = os.path.join(directory_to_walk, f)
            save_as, output = extract_single_file(filename_to_read)
            if output == None:
                print(f"unable to read {f} normally")
            else:
                print("converting to csv...", end="\r")
                csv_cols = convert_output_cols_to_csv(output)
                full_savepath = os.path.join(OUTPUT_DIRECTORY, save_as)
                for column_number in range(len(csv_cols)):
                    full_savepath = full_savepath.replace(".csv", f"-{column_number+1}.csv")
                    content = csv_cols[column_number]
                    with open(full_savepath, 'w') as f:
                        f.write(content)
                    print(f"Saved {full_savepath}")

def convert_output_cols_to_csv(output_cols_dict):
    csv_by_column = []
    for column in range(len(output_cols_dict)):
        csv = "Hour,Minute\n"
        for k in output_cols_dict[column].keys():
            csv += str(k) + ','
            minutes = output_cols_dict[column][k]
            csv += ",".join([str(m) for m in minutes])
            csv += "\n"
        csv_by_column.append(csv)
    return csv_by_column



def main():
    if DEFAULT_FILE != None and os.path.isfile(os.path.join(DEFAULT_DIRECTORY, DEFAULT_FILE)):
        file_to_test = os.path.join(os.getcwd(), DEFAULT_DIRECTORY, DEFAULT_FILE)
        _, _ = extract_single_file(file_to_test, testing=True)
    else:
        extract_all_files(os.path.join(os.getcwd(), DEFAULT_DIRECTORY))



if __name__ == '__main__':
    main()