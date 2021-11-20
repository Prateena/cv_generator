
from io import BytesIO
from xhtml2pdf import pisa

from django.http import HttpResponse
from django.template.loader import get_template
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


def render_to_pdf(template_src, context_dict={}):
     template = get_template(template_src)
     html  = template.render(context_dict)
     result = BytesIO()
 
     #This part will create the pdf.
     pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
     if not pdf.err:
         return HttpResponse(result.getvalue(), content_type='application/pdf')
     return None