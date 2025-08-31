from django import forms

class ScrapingForm(forms.Form):
    url = forms.URLField(label='URL для парсинга')
    fields_to_scrape = forms.CharField(
        label='Поля для парсинга (через запятую)',
        help_text='Например: title, price, description'
    )