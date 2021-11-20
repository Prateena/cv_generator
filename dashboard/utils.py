from django.http import QueryDict

def check_skill_tags(data,model):
    if data!= None:
        data_dict = dict(data)
        data_dict['skill_required'] = list()
        for value in data.getlist('skill_required'):
            try:
                value = int(value)
                data_dict['skill_required'].append(value)
            except:
                skill,_ = model.objects.get_or_create(name = value)
                data_dict['skill_required'].append(skill.pk)
        
        data = QueryDict('', mutable=True)
        for key,values in data_dict.items():
            for value in values:
                data.update({key:value})
    return data
