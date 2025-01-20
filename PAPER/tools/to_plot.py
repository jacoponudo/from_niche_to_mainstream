palette = {
    'usenet': '#D2B48C',    # Giallo seppia per Usenet
    'reddit': '#FF4500',    # Rosso acceso
    'gab': '#008000',       # Verde
    'twitter': '#1DA1F2',   # Blu di Twitter
    'facebook': '#1877F2',  # Blu di Facebook
    'voat': '#8A2BE2'     # Viola per Voat
}


import re

# Function to extract numbers from a string
def extract_number(bin_string):
    match = re.search(r'\d+', bin_string)  # Find the first number in the string
    return float(match.group()) if match else float('inf')  # Return the number or a large value

d1=10
d2=10

t=35
T=55
xl=40
yl=40