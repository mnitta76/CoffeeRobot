from django import forms
from coffeenotes.models import Coffeenote

class CoffeenoteForm(forms.Form):

    shop_name = forms.CharField(
        label='購入店',
        max_length=128,
    )

    shop_address = forms.CharField(
        label='場所',
        max_length=128,
    )

    bean = forms.CharField(
        label='名称',
        max_length=64,
    )

    roast_level = forms.ChoiceField(
        label='焙煎度',
        choices=(
            ('light_roast', '浅煎り'),
            ('medium_roast', '中煎り'),
            ('dark_roast', '深煎り')
        ),
        widget=forms.widgets.Select
    )

    extract_method = forms.ChoiceField(
        label='抽出方法',
        choices=(
            ('light_roast', 'ペーパードリップ'),
            ('medium_roast', 'ネルドリップ'),
            ('espresso', 'エスプレッソ'),
            ('siphon', 'サイフォン'),
            ('cafepress', 'カフェプレス')
        ),
        widget=forms.widgets.Select
    )

    grind_size = forms.ChoiceField(
        label='粗挽き',
        choices=(
            ('coarse', '粗挽き'),
            ('medium_coarse', '中粗挽き'),
            ('medium', '中挽き'),
            ('medium_fine', '中細挽き'),
            ('fine', '細挽き'),
            ('turkish', '極細挽き')
        ),
        widget=forms.widgets.Select
    )

    memo = forms.CharField(
        label='memo',
        max_length=256,
    )

    smell = forms.TypedChoiceField(
        label='香り',
        choices=(
            (1, '1'),
            (2, '2'),
            (3, '3'),
            (4, '4'),
            (5, '5')
        ),
        coerce=int
    )

    acdity = forms.TypedChoiceField(
        label='酸味',
        choices=(
            (1, '1'),
            (2, '2'),
            (3, '3'),
            (4, '4'),
            (5, '5')
        ),
        coerce=int
    )

    body = forms.TypedChoiceField(
        label='コク',
        choices=(
            (1, '1'),
            (2, '2'),
            (3, '3'),
            (4, '4'),
            (5, '5')
        ),
        coerce=int
    )

    aftertaste = forms.TypedChoiceField(
        label='後味',
        choices=(
            (1, '1'),
            (2, '2'),
            (3, '3'),
            (4, '4'),
            (5, '5')
        ),
        coerce=int
    )

    bitterness = forms.TypedChoiceField(
        label='苦味',
        choices=(
            (1, '1'),
            (2, '2'),
            (3, '3'),
            (4, '4'),
            (5, '5')
        ),
        coerce=int
    )