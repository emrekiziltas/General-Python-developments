import webbrowser

# Path to the input file
url_file = r"C:/Users/ek675/OneDrive - University of Cambridge/Documents/INI/Codes/isaac_url.txt"

# Open and read the file
with open(url_file , 'r') as file:
    urls = file.readlines()

# Strip any whitespace or newline characters and open each URL
for url in urls:
    clean_url = url.strip()
    if clean_url:  # Ensure it's not an empty line
        webbrowser.open_new_tab(clean_url)
