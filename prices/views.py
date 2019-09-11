from django.http import JsonResponse
from django.views.generic import View

from .utils.data_reader import get_prices


class PriceHistoryAjaxView(View):
    def get(self, request, *args, **kwargs):
        # リクエストから年を取得（デフォルトは 2019）
        year = int(request.GET.get('year') or 2019)

        # BTC価格の一覧を DataFrame で取得
        df = get_prices(year)

        # JSONレスポンスで返す
        return JsonResponse(df.to_dict(orient='record'), safe=False)


price_history_ajax = PriceHistoryAjaxView.as_view()
