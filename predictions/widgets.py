from django import forms


class BlobaxFormMixin:
    """Consistent modern form styling."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            css = 'form-control bx-input'
            if isinstance(field.widget, forms.Textarea):
                css += ' bx-textarea'
            field.widget.attrs.setdefault('class', css)
