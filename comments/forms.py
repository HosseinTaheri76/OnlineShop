import json

from django import forms
from django.utils.translation import gettext_lazy as _

from .models import ProductComment
from config.utils.forms.bootstrap import BootstrapFormMixin


class ProductCommentForm(BootstrapFormMixin, forms.ModelForm):
    field_attrs = {
        'body': {'style': 'height: 150px'},
        'pros': {'class': 'commentTags tag-pos form-control', 'placeholder': _('Add more with enter button')},
        'cons': {'class': 'commentTags tag-neg form-control', 'placeholder': _('Add more with enter button')},
        'save_info': {'class': 'form-check-input'}
    }

    save_info = forms.BooleanField(
        label=_('Save my name and email for next time I comment'),
        required=False,
        initial=False
    )

    class Meta:
        model = ProductComment
        fields = ('fullname', 'email', 'score', 'body', 'pros', 'cons',)
        labels = {
            'email': _('Please enter your email'),
            'fullname': _('Please enter you fullname'),
            'body': _('Comment text')
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, attrs in self.field_attrs.items():
            self.fields[field_name].widget.attrs.update(attrs)

    def _clean_pros_cons(self, field_name):
        """Method for parse Json string of fields pros and cons it they are valid"""
        pros_cons = self.cleaned_data.get(field_name, '')
        if pros_cons != '':
            try:
                return ','.join(d['value'] for d in json.loads(pros_cons))
            except json.JSONDecodeError:
                raise forms.ValidationError(_('Invalid value'), 'invalid_pros_cons')
        return pros_cons

    def clean_pros(self):
        return self._clean_pros_cons('pros')

    def clean_cons(self):
        return self._clean_pros_cons('cons')

