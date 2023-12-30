from django.forms import ModelForm
from tinymce.widgets import TinyMCE


class ProductAdminForm(ModelForm):
    """ custom form for Product admin to override
    'description' field widget to tinymce """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['description_fa'].widget = TinyMCE()
        self.fields['description_en'].widget = TinyMCE()

