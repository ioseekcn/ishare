# coding: utf-8
"""
Created by Lu Jianxin at 2019/03/08 16:56, for any questions contact me with jeeysie@gmail.com.
Some ideas of the file:
    0. 首页
"""

from django.views.generic import View
from django.shortcuts import render, redirect, resolve_url
from django.contrib.syndication.views import Feed

from db import models
from db.utils import get_value_from_db

from ljx import settings


class OpenView(View):
    """
    任何方法都允许的视图：
        写这个类是为了类里面可以写多个方法来完成任务， 如果使用基于函数的视图也能实现对任意请求方式响应，但是缺点在于不能在内部定义多个方法
    """

    def get(self, request, *args, **kwargs):
        # 集成了这个类的子类必须实现自己的get方法
        raise NotImplementedError(
            "You must override the function 'get' as you extend %s".format(self.__class__.__name__)
        )

    def post(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)


# ---------------------------------
# 首页， 首页跳转
# ---------------------------------
class Index(OpenView):
    """
    首页视图
    """

    def get(self, request, *args, **kwargs):
        # 获取首页动态内容
        data = {
            'banners': self.get_banners(),
            'headlines': self.get_headlines(),
            'table': self.get_table(),
            'ad': self.get_ad(),
            'blog_list': self.get_blog_list(),
            'page': {
                'title': '首页 | 陆鉴鑫的博客',
                'keywords': '文艺青年、技术干货、个人博客、原创文章、内容创作、程序员、文学创作',
                'description': '陆鉴鑫的博客，一个助力实现文学梦想，技术干货创作和分享的开放平台。',
            }
        }
        return render(request, 'db/index.html', data)

    def get_banners(self):
        num = int(get_value_from_db('BAN_SHOW_NUM', 4))
        queryset = models.Blog.objects.filter(
            is_active=True,
            is_top=True,
            cat__is_active=True
        ).order_by('-add')[:num]
        return queryset

    def get_headlines(self):
        num = int(get_value_from_db('BAN_SHOW_NUM', 4))
        queryset = models.Blog.objects.filter(
            is_active=True,
            is_top=True,
            cat__is_active=True
        ).order_by('-add')[num:(num + 2)]
        return queryset

    def get_table(self):
        d = {'cat': 1, 'arts': None}
        num = int(get_value_from_db('TABLE_SHOW_NUM', 6))
        d['arts'] = models.Blog.objects.filter(
            is_active=True,
            cat__is_active=True,
            cat__pre_cat='A'
        ).order_by('-add')[:num]
        return d

    def get_ad(self):
        import datetime
        now = datetime.datetime.now()
        return models.Advertisement.objects.filter(end__gt=now, adtype=1).order_by('?').first()

    def get_blog_list(self):
        num = int(get_value_from_db('BLOG_LIST_SHOW_NUM', 10))
        query = models.Blog.objects.order_by('-add').filter(
            is_active=True,
            cat__is_active=True,
            cat__pre_cat='B'
        )[:num]
        return query


def goto_index(request):
    return redirect(to=resolve_url('index'), permanent=True)


def password_reset(request, uid):
    # 解决后台管理中的bug
    uri = 'xauth/'
    if request.user.is_authenticated:
        uri = '/xauth/account/password/'
    return redirect(uri)


class ArticleFeed(Feed):
    """
    RSS订阅-文章
    """
    title = "RSS of {domain}".format(domain=settings.SITE["dns"])
    link = "/feed/"
    description = "Latest articles in site"

    def items(self):
        obj = models.Expand.objects.filter(key="RSS_NUM").first()
        num = int(obj.value) if obj else settings.RSS_NUM
        return models.Blog.objects.filter(is_active=True, cat__is_active=True).order_by("-add")[:num]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.description()

    def item_link(self, item):
        return "/x/art/{pk}".format(pk=item.pk)

    def item_author_name(self, item):
        return item.author.username

    def item_author_email(self, item):
        return item.author.email

    def item_author_link(self, item):
        return settings.SITE["host"] if item.author.is_superuser else ""

    def item_updateddate(self, item):
        return item.mod

    def item_pubdate(self, item):
        if hasattr(item, "pub"):
            pub = getattr(item, "pub")
            if pub:
                return pub
        return item.add

    def item_copyright(self, item):
        return "All Rights Reserved {} And The Author: {}.".format(settings.SITE["dns"], item.author.username)

    def feed_copyright(self):
        return "All Rights Reserved {}.".format(settings.SITE["dns"])

    def author_email(self):
        return settings.SITE["email"]["me"]

    def author_link(self):
        return settings.SITE["host"]

    def author_name(self):
        return settings.SITE["author"]

    def item_guid(self, item):
        return item.pk
