from django import forms
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _

from PIL import Image
from dashboard.models import *
from datetime import date


class SigninForm(forms.Form):
    username = forms.CharField(max_length=20, widget=forms.TextInput(attrs={'required': "required",'class':'form-control','placeholder':'Username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control','placeholder':'Password','required':"required"}))


class CandidateSignupForm(forms.ModelForm):
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'required': 'true',
        'placeholder': 'Password'}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'required': 'true',
        'placeholder': 'Confirm Password'}))
    first_name = forms.CharField()
    last_name = forms.CharField()
    email = forms.EmailField()

    class Meta:
        model = Candidate
        fields = ["username", "email", "password1", "password2","first_name","last_name"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in iter(self.fields):
            self.fields[field].widget.attrs.update({'class': 'form-control'})
        self.fields["username"].widget.attrs.update(
            {'placeholder': 'Username *', 'required': 'true'})
        self.fields["email"].widget.attrs.update(
            {'placeholder': 'E-Mail *', 'required': 'true'})
        self.fields["first_name"].widget.attrs.update(
            {'placeholder': 'First Name *', 'required': 'true','pattern':'[A-Za-z]{1,20}','title':'First Name should only contain letters. e.g. Jabeen'})
        self.fields["last_name"].widget.attrs.update(
            {'placeholder': 'Last Name *', 'required': 'true','pattern':'[A-Za-z]{1,20}','title':'Last Name should only contain letters. e.g. Shrestha'})

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        
        if not password2:
            raise forms.ValidationError("You must confirm your password")
        if password1 != password2:
            raise forms.ValidationError("Your passwords do not match")

        if len(password1) < 5:
            raise forms.ValidationError("Password must be at least 5 characters!!")
        return password2

    def clean_username(self):
        username = self.cleaned_data['username']
      
        try:
            user = Candidate.objects.exclude(pk=self.instance.pk).get(username=username)
        except Candidate.DoesNotExist:
            return username
        raise forms.ValidationError(_("Username already exists"))
        

    def clean_email(self):
        email = self.cleaned_data.get('email')
        username = self.cleaned_data.get('username')
        user = User.objects.filter(email=email).exclude(username=username)
        candidate = get_candidate(user.first())
        if candidate:
            user.delete()
        if email and user.exists():
            raise forms.ValidationError('This email address is already used')
        return email

    def clean_mobile_number(self):
        mobile = self.cleaned_data.get('mobile_number')
        if len(mobile) != 10:
            raise forms.ValidationError("Mobile number must be 10 digit")
        return mobile


class CandidateCreateForm(forms.ModelForm):
    
    class Meta:
        model = Candidate
        fields = ['first_name', 'last_name', 'email', 'username', 'gender', 'dob','mobile_number','address']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in iter(self.fields):
            self.fields[field].widget.attrs.update({'class': 'form-control'})
        
        self.fields['username'].widget.attrs.update({'readonly':'true'})


    def clean_first_name(self):
        data = self.cleaned_data.get('first_name')
        if data is None or data == '':
            raise forms.ValidationError('This field is required.')
        return data

    def clean_last_name(self):
        data = self.cleaned_data.get('last_name')
        if data is None or data == '':
            raise forms.ValidationError('This field is required.')
        return data
    
    def clean_email(self):
        data = self.cleaned_data.get('email')
        if data is None or data == '':
            raise forms.ValidationError('This field is required.')
        return data

    def clean_dob(self):
        cleaned_data = self.cleaned_data
        dob = cleaned_data.get('dob')
        if dob > date.today():
            raise forms.ValidationError("Date of birth cannot be future date")                
        return dob


class CandidateExperienceCreateForm(forms.ModelForm):
    class Meta:
        model = WorkExperience
        fields = ['job_title','organization','is_working','start_date','end_date','job_description']

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        for field in iter(self.fields):
            self.fields[field].widget.attrs.update({'class':'form-control'})
                
        self.fields["job_title"].widget.attrs.update(
            {'placeholder': 'e.g, Accountant, Developer,...'})
            
    def clean(self):
        cleaned_data = self.cleaned_data
        end_date = cleaned_data.get('end_date')
        start_date = cleaned_data.get('start_date')
        d = cleaned_data.get('job_description')
        if end_date is not None:
            if end_date < start_date:
                raise forms.ValidationError({'end_date':'End Date cannot be less than Start Date'})
            if end_date > date.today():
                raise forms.ValidationError({'end_date':"End Date cannot be greater than Today's Date"})
        return cleaned_data
    
    def clean_end_date(self):
        status = self.cleaned_data.get('is_working')
        end_date = self.cleaned_data.get('end_date')

        if status == 'N' and end_date is None:
            raise forms.ValidationError('This field is required.')
        return end_date


class CandidateEducationCreateForm(forms.ModelForm):
    class Meta:
        model = EducationalQualification
        exclude = ['deleted_at','candidate']

    
class CandidateAboutMeCreateForm(forms.ModelForm):
    class Meta:
        model = Candidate
        fields = ['about_me','skills']

    def __init__(self, data = None,*args, **kwargs):
        data = self.check_skill_tags(data)
        super().__init__(data = data,*args, **kwargs)
        for field in iter(self.fields):
            self.fields[field].widget.attrs.update({'class':'form-control'})

    def check_skill_tags(self,data):
        from django.http import QueryDict
        if data!= None:
            data_dict = dict(data)

            data_dict['skills'] = list()
            for value in data.getlist('skills'):
                try:
                    value = int(value)
                    data_dict['skills'].append(value)
                except:
                    skill,_ = Skill.objects.get_or_create(name = value)
                    data_dict['skills'].append(skill.pk)
            
            data = QueryDict('', mutable=True)
            for key,values in data_dict.items():
                for value in values:
                    data.update({key:value})
        return data


class CandidateProfileDetailCreateForm(forms.ModelForm):
    first_name = forms.CharField()
    last_name = forms.CharField()

    class Meta:
        model = Candidate
        fields = ['first_name','last_name','dob','gender','mobile_number','address']

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        for field in iter(self.fields):
            self.fields[field].widget.attrs.update({'class':'form-control'})

    def clean_first_name(self):
        data  = self.cleaned_data.get('first_name')
        if data is None or data == '':
            raise forms.ValidationError('This field is required.')
        return data
    
    def clean_last_name(self):
        data = self.cleaned_data.get('last_name')
        if data is None or data == '':
            raise forms.ValidationError('This field is required.')
        return data


class CandidateProfileCompleteForm(forms.ModelForm):
    class Meta:
        model = Candidate
        fields = ['gender', 'dob']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in iter(self.fields):
            self.fields[field].widget.attrs.update({'class': 'form-control'})
    
    def clean_dob(self):
        cleaned_data = self.cleaned_data
        dob = cleaned_data.get('dob')
        if dob > date.today():
            raise forms.ValidationError("Date of birth cannot be future date")                
        return dob


class CandidatePhotoUpdateForm(forms.ModelForm):
    profile_image = forms.ImageField(label="", widget=forms.FileInput)
    x = forms.FloatField(widget=forms.HiddenInput())
    y = forms.FloatField(widget=forms.HiddenInput())
    width = forms.FloatField(widget=forms.HiddenInput())
    height = forms.FloatField(widget=forms.HiddenInput())

    class Meta:
        model = Candidate
        fields = ['profile_image', 'x', 'y', 'width', 'height']

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        for field in iter(self.fields):
            self.fields[field].widget.attrs.update({'class':'form-control'})
        self.fields['profile_image'].widget.attrs.update({'class':'form-control file-input', 'accept':'image/*'})
    
    def save(self):
        photo = super().save()

        x = self.cleaned_data.get('x')
        y = self.cleaned_data.get('y')
        w = self.cleaned_data.get('width')
        h = self.cleaned_data.get('height')

       
        image = Image.open(photo.profile_image)
        cropped_image = image.crop((x,y, w+x, h+y))
        resized_image = cropped_image.resize((200,200), Image.ANTIALIAS)
        resized_image.save(photo.profile_image.path)
        return photo


    