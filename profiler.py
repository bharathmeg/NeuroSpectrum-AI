changingParam = ['Speech_Disorder','Learning_Disorder','Genetic_Disorders','Depression','Intellectual_Disability','Social/Behavioural_Issues','Anxiety_Disorders','Jaundice','Family_Member_with_ASD']
changingValues = ['No','Yes']


def generateProfile(data):
    Person_Profile = []
    for x in data:
        if x in changingParam:
            newStrings = x.replace('_'," ") + '  :  ' + changingValues[int(data[x])]
        elif x == 'Gender':
            gender = ['Female','Male']
            newStrings = x.replace('_'," ") + '  :  ' + gender[int(data[x])]
        else:
            newStrings = x.replace('_'," ") + '  :  ' + data[x]
        Person_Profile.append(newStrings)
    print(Person_Profile)
    return Person_Profile
