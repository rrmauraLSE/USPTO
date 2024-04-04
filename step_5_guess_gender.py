import gender_guesser.detector as gender

# TODO: many names that are just a letter: A. N.

"""The result will be: 

unknown (name not found), 
andy (androgynous), 
male, 
female,
mostly_male, 
mostly_female. 

The difference between andy and unknown is that the former is found to have
the same probability to be male than to be female, while the later means
that the name wasn’t found in the database."""

ssa_folder = "C:\Users\Roberto\Documents\GitHub Repositories\USPTO\data\names_US_SSA"

# ssa_names = open('data/names/yob2000.txt', 'r').readlines()
# create a dictionary that maps names to gender using the Social Security Administration data

# first a dictionary taht counts how many times a name appears as male and how many as female. 
# then create a second dictionary that maps the name to mostly male, mostly female, male, female, andy and unknown

def create_dict():
    names = {}
    with open(ssa_folder, 'r') as f:
        for line in f:
            name, gender, count = line.strip().split(',')
            if name not in names:
                names[name] = {'male': 0, 'female': 0}
            if gender == 'M':
                names[name]['male'] += int(count)
            elif gender == 'F':
                names[name]['female'] += int(count)




LIST_NAME_UNKNOWNS = []

def get_list_genders(inventors):
    list_genders = []
    for i in inventors:
        first_name = i['first_name']
        
        # take into account spaces and "-", e.g. Jean-Francois
        
        # if there is a space, take the first name
        if ' ' in first_name:
            first_name = first_name.split(' ')[0]

        # if there is a -, take the first name
        if '-' in first_name:
            first_name = first_name.split('-')[0]

        # get gender
        gender = d.get_gender(first_name)

        list_genders.append(gender)
        if gender == 'unknown':
            LIST_NAME_UNKNOWNS.append(first_name)
    
    return list_genders

# df['inventors_gender'] = df['inventors'].apply(lambda x: get_list_genders(x))

if __name__ == "__main__":
    d = gender.Detector(case_sensitive=False)
    print(d.get_gender(u"Francois")) # male
    print(d.get_gender(u"Pauley")) # andy, i.e. androgynous
    


"""Emily,F,25691
Emma,F,22714
Madison,F,20201
Hannah,F,17638
Olivia,F,16152
Abigail,F,15931
Alexis,F,14867
Ashley,F,14517
Elizabeth,F,14116
Samantha,F,13869
Isabella,F,13781"""