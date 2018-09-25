from django.http import JsonResponse
from django.views.generic import View

from .utils.data_reader import get_prices


class HistoryAjaxView(View):
    def get(self, request, *args, **kwargs):
        # BTC価格の一覧を DataFrame で取得
        df = get_prices()

        # JSONレスポンスで返す
        return JsonResponse(df.to_dict(orient='record'), safe=False)


history_ajax = HistoryAjaxView.as_view()