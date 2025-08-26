from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from coffeenotes.forms import CoffeenoteForm
from coffeenotes.models import Coffeenote
from shop.models import Shop

def coffeenote(request):
    coffeenotes = Coffeenote.objects.all()
    context = {'coffeenotes': coffeenotes}
    return render(request, "coffeenotes/top.html", context)

@login_required
def coffeenote_new(request):
    if request.method == 'POST':
        form = CoffeenoteForm(request.POST)
        if form.is_valid():
            coffeenote = form.save(commit=False)
            coffeenote.created_by = request.user
            coffeenote.save()
            return redirect(coffeenote_detail, coffeenote_id=coffeenote.pk)
    else:
        form = CoffeenoteForm()
    return render(request, "coffeenotes/coffeenote_new.html", {'form': form})

@login_required
def coffeenote_edit(request, coffeenote_id):
    coffeenote = get_object_or_404(Coffeenote, pk=coffeenote_id)
    if coffeenote.created_by_id != request.user.id:
        return HttpResponseForbidden("You don't have permission to edit this coffeenote.")

    if request.method == "POST":
        form = CoffeenoteForm(request.POST)
        if form.is_valid():
            # 手動でモデルに反映して保存
            coffeenote.shop = Shop.objects.create(
                name=form.cleaned_data['shop_name'],
                address=form.cleaned_data['shop_address'],
            )
            coffeenote.bean = form.cleaned_data['bean']
            coffeenote.roast_level = form.cleaned_data['roast_level']
            coffeenote.extract_method = form.cleaned_data['extract_method']
            coffeenote.grind_size = form.cleaned_data['grind_size']
            coffeenote.memo = form.cleaned_data['memo']
            coffeenote.smell = form.cleaned_data['smell']
            coffeenote.acdity = form.cleaned_data['acdity']
            coffeenote.body = form.cleaned_data['body']
            coffeenote.aftertaste = form.cleaned_data['aftertaste']
            coffeenote.bitterness = form.cleaned_data['bitterness']
            coffeenote.save()
            return redirect('coffeenote_detail', coffeenote_id=coffeenote.id)
    else:
        # モデルから初期値を抽出してフォームに渡す
        form = CoffeenoteForm(initial={
            'shop_name': coffeenote.shop.name,
            'shop_address': coffeenote.shop.address,
            'bean': coffeenote.bean,
            'roast_level': coffeenote.roast_level,
            'extract_method': coffeenote.extract_method,
            'grind_size': coffeenote.grind_size,
            'memo': coffeenote.memo,
            'smell': coffeenote.smell,
            'acdity': coffeenote.acdity,
            'body': coffeenote.body,
            'aftertaste': coffeenote.aftertaste,
            'bitterness': coffeenote.bitterness
        })

    return render(request, 'coffeenotes/coffeenote_edit.html', {'form': form})

def coffeenote_detail(request, coffeenote_id):
    coffeenote = get_object_or_404(Coffeenote, pk=coffeenote_id)
    return render(request, 'coffeenotes/coffeenote_detail.html', {'coffeenote': coffeenote})