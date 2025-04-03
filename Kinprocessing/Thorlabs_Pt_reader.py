import os
import pandas as pd
import numpy as np

def read_thorlabs_powermeter(filename):
    """
    Reads the Thorlabs powermeter data from a CSV file.
    
    Parameters:
        filename (str): The path to the CSV file.
        
    Returns:
        pd.DataFrame: A DataFrame containing the powermeter data.
    """
    delimiter = ','
    # Read the CSV file
    with open(filename, 'r') as f:
        lines = f.readlines()
        read = True
        i = 0
        while read:
            if lines[i].startswith('Delimiter Used:'):
                delimiter = lines[i].split(':')[1].strip().split("'")[1]
                read = False
            elif lines[i].startswith('Samples'):
                read = False
                print('error while reading')
                return 
            i += 1
        i+=1
        metadata = {}
        read = True
        while read:
            if len(lines[i].split()) == 0:
                read = False
            else:
                ml = lines[i].strip().split(delimiter)
                if ml[0] == '':
                    pass
                else: 
                    metadata[ml[0]] = ml[1].split()
            i += 1
        i+=1
        # read the keys split by the delimiter
        keys = lines[i].strip().split(delimiter)[:-1]
        # read the data lines[i+1:]
        data = []
        for j in keys:
            data.append([])

        for j in range(i, len(lines)-1):
            # skip empty lines
            if len(lines[j].strip()) == 0:
                continue
            line = lines[1+j].strip()
            for key in range(len(keys)):
                data[key].append(line.split(delimiter)[key])
        
        # convert to DataFrame
        df = pd.DataFrame()
        for j in range(len(keys)):
            # Strip whitespace from keys
            clean_key = keys[j].strip()
            df[clean_key] = np.asarray(data[j])
        return df

def obtain_power_data(filename='Sample.csv'):
    """
    Obtains power data from the Thorlabs powermeter and returns a DataFrame with time and power.
    
    Returns:
        pd.DataFrame: A DataFrame containing the time in seconds and power values.
    """
    df = read_thorlabs_powermeter(filename)

    print('df:', df['Date (MM/dd/yyyy)'][:10])
    date_series = pd.to_datetime(pd.Series(df['Date (MM/dd/yyyy)'].str.strip()).astype(str), format='%m/%d/%Y')  # Convert date strings to datetime
    time_series = pd.to_timedelta(pd.Series(df['Time of day (hh:mm:ss)']).astype(str).str.strip())  # Convert time strings to timedelta
    
    # Combine date and time into a single datetime series
    datetime_series = date_series + time_series
    
    # Calculate time in seconds from the first entry
    t0 = datetime_series.iloc[0]
    time_in_seconds = (datetime_series - t0).dt.total_seconds()
    
    # Create DataFrame with time and power
    power_data = pd.DataFrame({
        't': time_in_seconds,
        'Power': df['Power (W)'].astype(float)  # Ensure power values are in float format
    })
    
    return power_data

def testrun():
    # # Example usage
    # change the path to your file
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    a = read_thorlabs_powermeter('Sample.csv')
    print(a.keys())
    #print(a['Time of day (hh:mm:ss) '])

    b = obtain_power_data()
    # plot b['Power'] vs b['t'] time in seconds
    print(b['Power'])
    print(b['t'])

if __name__ == "__main__":
    testrun()