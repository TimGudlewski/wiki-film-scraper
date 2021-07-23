headers = {
    'Access-Control-Allow-Origin': "*",
    'Access-Control-Allow-Methods': "GET",
    'Access-Control-Allow-Headers': "Content-Type",
    'Access-Control-Max-Age': "3600",
    'User-Agent': "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0"
}

usr_agent = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/61.0.3163.100 Safari/537.36'
}

work_format_words = [
    'novelette',
    'novella',
    'novel',
    'teleplay',
    'play',
    'short story',
    'story',
    'book series',
    'radio series',
    'series',
    'serial'
]

labels_mapping_table = {
    'Screenplay by': "writing",
    'Written by': "writing",
    'Story by': "writing",
    'Language': "languages",
    'Country': "country",
    'Directed by': "direction",
    'Edited by': "editing",
    'Produced by': "production",
    'Productioncompanies': "production",
    'Productioncompany': "production",
    'Distributed by': "distribution",
    'Music by': "music",
    'Running time': "length",
    'Based on': "basis",
    'Cinematography': "cinematography",
    'Box office': "sales",
    'Budget': "budget",
    'Release date': "dates"
}