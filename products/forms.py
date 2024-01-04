from django import forms
from django.utils.translation import gettext as _

from tinymce.widgets import TinyMCE

from . import models


class ProductAdminForm(forms.ModelForm):
    """ custom form for Product admin to override
    'description' field widget to tinymce """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['description_fa'].widget = TinyMCE()
        self.fields['description_en'].widget = TinyMCE()


class ProductPromotionAdminForm(forms.ModelForm):
    class Meta:
        model = models.ProductPromotion
        fields = ['discount_percent', 'product_variants', 'datetime_start', 'datetime_end']

    def clean_product_variants(self):
        """Check if there is active promotion for a selected product, prevent save"""

        product_variants = self.cleaned_data.get('product_variants')
        overlapping_promotions = models.ProductPromotion.active_manager.filter(
            product_variants__in=product_variants
        )
        if self.instance is not None:
            overlapping_promotions = overlapping_promotions.exclude(id=self.instance.id)

        if overlapping_promotions.exists():
            raise forms.ValidationError(
                _('There is already active promotions for product variants %(ids)s') % {
                    'ids': ', '.join(map(str, overlapping_promotions.values_list('product_variants__id', flat=True)))
                },
                'overlapping-promotion'
            )
        return product_variants

    def clean(self):
        cleaned_data = self.cleaned_data
        datetime_start = cleaned_data.get('datetime_start')
        datetime_end = cleaned_data.get('datetime_end')
        if datetime_end <= datetime_start:
            raise forms.ValidationError(_('End datetime must be greater than start datetime'), 'start-gt-end')
        return cleaned_data


class ProductVariantAdminForm(forms.ModelForm):
    class Meta:
        model = models.ProductVariant
        fields = '__all__'
        widgets = {
            'retail_price_toman': forms.NumberInput(attrs={'width': '300px'}),
            'store_price_toman': forms.NumberInput(attrs={'width': '300px'}),
        }

