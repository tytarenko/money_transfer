import json

from django.conf import settings
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import render, redirect

from .analyzer import parse_file, analyze_transfers
from .forms import UploadFileForm
from .models import TransactionModel
from .utils import handle_uploaded_file


def upload_file(request):
    if request.method == "POST":
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            handle_uploaded_file(request.FILES["file"])
            return redirect("analyzer:uploaded")
    else:
        form = UploadFileForm()
    return render(request, "analyzer/upload_file.html", {"form": form})


def uploaded(request):
    data = parse_file(settings.TMP_XLSX_FILEPATH)
    with transaction.atomic():
        for account, date, credit, debit in data:
            TransactionModel.objects.create(
                account_id=account,
                date=date,
                amount=credit if credit > 0 else debit,
                transaction_type=TransactionModel.TransactionType.CREDIT if credit > 0 else TransactionModel.TransactionType.DEBIT
            )
    return HttpResponse("File upload successful, parsed and stored to DB")


def report(request):
    credits = (TransactionModel.objects
               .filter(transaction_type=TransactionModel.TransactionType.CREDIT)
               .values_list("account_id", "date", "amount"))
    debits = (TransactionModel.objects
              .filter(transaction_type=TransactionModel.TransactionType.DEBIT)
              .values_list("account_id", "date", "amount"))

    response_data = {
        "result": analyze_transfers(credits, debits),
        # "error": None #TODO
    }

    return HttpResponse(
        json.dumps(response_data, indent=4, sort_keys=True, default=str),
        content_type="application/json")
