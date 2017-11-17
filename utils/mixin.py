from django.contrib.auth.decorators import login_required
from django.views.generic import View


class LoginRequiredMixin(View):
    @classmethod
    def as_view(cls, **initkwargs):
        # 调用父类的的as_view
        view = super(LoginRequiredMixin, cls).as_view(**initkwargs)
        return login_required(view)
