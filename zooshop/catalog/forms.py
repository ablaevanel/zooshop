from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Client, Client_order, Review
from django.contrib.auth.models import User


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['text', 'rating']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Ваш отзыв...'}),
            'rating': forms.NumberInput(attrs={'min': 1, 'max': 5, 'placeholder': 'Оценка от 1 до 5'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['text'].label = "Текст отзыва"
        self.fields['rating'].label = "Оценка"
        self.fields['rating'].widget.attrs.update({'class': 'form-control'})
        self.fields['text'].widget.attrs.update({'class': 'form-control'})


class ProductSortForm(forms.Form):
    SORT_CHOICES = [
        ('price_asc', 'Цена по возрастанию'),
        ('price_desc', 'Цена по убыванию'),
        ('name_asc', 'По имени (А-Я)'),
        ('name_desc', 'По имени (Я-А)'),
    ]

    sort_by = forms.ChoiceField(choices=SORT_CHOICES, required=False, label="Сортировать по")

    search = forms.CharField(
        required=False,
        label='Поиск',
        widget=forms.TextInput(attrs={'placeholder': 'Введите название товара'})
    )


class OrderSortForm(forms.Form):
    SORT_CHOICES_DATE = [
        ('date_asc', 'Дата заказа по возрастанию'),
        ('date_desc', 'Дата заказа по убыванию'),
    ]

    sort_by_date = forms.ChoiceField(choices=SORT_CHOICES_DATE, required=False, label="Сортировать по дате")

    SORT_CHOICES_STATUS = [
        ('all', 'Все'),
        ('accepted', 'Принят'),
        ('gathered', 'Собран'),
        ('delivered', 'Доставлен'),
        ('issued', 'Выдан'),
    ]

    sort_by_status = forms.ChoiceField(choices=SORT_CHOICES_STATUS, required=False, label="Сортировать по статусу")


class OrderStatusChangeForm(forms.ModelForm):
    class Meta:
        model = Client_order
        fields = ['status']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'status': 'Статус заказа',
        }


class ClientRegistrationForm(UserCreationForm):
    phone = forms.CharField(max_length=11, label='Телефон')
    address = forms.CharField(max_length=500, label='Адрес')

    class Meta:
        model = User
        fields = ['username',
                  'email',
                  'password1',
                  'password2',
                  'first_name',
                  'last_name',]

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            Client.objects.create(
                user=user,
                phone=self.cleaned_data['phone'],
                address=self.cleaned_data['address'],
                first_name=self.cleaned_data['first_name'],
                last_name=self.cleaned_data['last_name'],
            )
        return user
