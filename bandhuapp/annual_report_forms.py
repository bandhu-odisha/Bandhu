from django import forms

from .models import AnnualReport


class AnnualReportUploadForm(forms.ModelForm):
    """Year-wise annual report upload (PDF file or Google Drive link)."""

    class Meta:
        model = AnnualReport
        fields = ('year', 'title', 'pdf_file', 'external_url', 'is_published')
        widgets = {
            'year': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 2000,
                'max': 2100,
                'placeholder': 'e.g. 2024',
            }),
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Optional — defaults to “Annual Report {year}”',
            }),
            'pdf_file': forms.ClearableFileInput(attrs={
                'class': 'form-control-file',
                'accept': 'application/pdf,.pdf',
            }),
            'external_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://drive.google.com/...',
            }),
            'is_published': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        help_texts = {
            'year': 'One report per calendar / financial year.',
            'pdf_file': 'Upload a PDF, or leave empty if you only use a Drive link below.',
            'external_url': 'Public Google Drive or other link. Used when no PDF is uploaded.',
            'is_published': 'Show this report in the site footer for visitors.',
        }

    def clean(self):
        cleaned = super().clean()
        pdf = cleaned.get('pdf_file')
        url = (cleaned.get('external_url') or '').strip()
        if self.instance and self.instance.pk:
            has_pdf = bool(pdf) or (not pdf and self.instance.pdf_file)
        else:
            has_pdf = bool(pdf)
        if not has_pdf and not url:
            raise forms.ValidationError(
                'Upload a PDF file or paste a Google Drive / public link.'
            )
        return cleaned
