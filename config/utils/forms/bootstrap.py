from django import forms


class BootstrapFormMixin:
    """ A class which utilizes a form to be displayed using Bootstrap. """

    extra_classes = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_fields_attrs(self.fields, self.get_extra_classes())

    def get_extra_classes(self):
        return self.extra_classes

    @staticmethod
    def set_fields_attrs(fields, extra_classes=None):
        """ Set proper bootstrap attributes for the form fields. """
        base_form_class = f'form-control'
        base_form_class = f'{base_form_class} {extra_classes}' if extra_classes else base_form_class

        for field in fields.values():
            field.widget.attrs['class'] = base_form_class

    def full_clean(self):
        super().full_clean()
        # add class is-invalid to field that has error
        for field_name, errors in self.errors.items():
            widget_attrs = self.fields[field_name].widget.attrs
            widget_attrs['class'] = widget_attrs.get('class', '') + ' is-invalid'
