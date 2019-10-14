from datetime import timezone, timedelta, datetime
import json
import logging
import shutil

from django.shortcuts import render
from django.views import generic, View
from django.http import JsonResponse, HttpResponse
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.utils.timezone import now
from oauth2_provider.views.generic import ProtectedResourceView

from elasticsearch import Elasticsearch
from tika import parser

from common import utility

from .models import *

logger = logging.getLogger(__name__)

class ApiEndpoint_Search(View):
    def get(self, request, *args, **kwargs):
        ret = {"code" : -1, "desc" : ""}
        es = Elasticsearch(settings.ELASTICSEARCH_HOST)
        docs = es.search(index='bookshelf', body={"query":{"multi_match":{"query": request.GET.get('keyword'), "fields":["title" if request.GET.get('category') == 0 else "content"]}}})
        ret["code"] = 1
        ret["desc"] = docs
        return JsonResponse(ret)

class ApiEndpoint_Upload(View):
    def post(self, request, *args, **kwargs):
        ret = {"code" : -1, "desc" : ""}
        es = Elasticsearch(settings.ELASTICSEARCH_HOST)
        myfile = request.FILES['payload']
        books = es.search(index='bookshelf', body={"_source":["title"], "query":{"bool":{"must":[{"match_phrase": {"title": myfile.name}},{"multi_match": {"query": myfile.name,"type": "most_fields","fields": ["title"]}}]}}})

        if books['hits']['total']['value'] > 0:
            logger.info('same title\'s book detected.')
            if request.POST.get('replace') == "1":
                logger.info('try to delete target book content.')
                es.delete_by_query(index='bookshelf', body={"query":{"bool":{"must":[{"match_phrase": {"title": "Swift Development with Cocoa.pdf"}},{"multi_match": {"query": "Swift Development with Cocoa.pdf","type": "most_fields","fields": ["title"] }}]}}})
            else:
                logger.info('Uploaded book already exists.')
                ret["code"] = -1
                ret["desc"] = "Uploaded book already exists."
                return JsonResponse(ret)

        fs = FileSystemStorage()
        filename = fs.save(myfile.name, myfile)
        parsed = parser.from_file(filename, xmlContent=True)
        paged = parsed["content"].split('<div class="page">')
        body = ""
        iPage = 1
        for page in paged[1:-2]:
            body = body + json.dumps({"index": {"_index": "bookshelf", "_type": "bookshelf_datas"}}) + '\n'
            body = body + json.dumps({"title":myfile.name, "page":iPage, "content":page}) + '\n'
            iPage = iPage + 1
        es.bulk(body)
        ret["code"] = 1
        ret["desc"] = "The Book has beend saved!"
        return JsonResponse(ret)

class ApiEndpoint_FlushAll(ProtectedResourceView):
    def get(self, request, *args, **kwargs):
        ret = {"code" : -1, "desc" : ""}
        try:
            es = Elasticsearch(settings.ELASTICSEARCH_HOST)
            es.delete_by_query(index='bookshelf', body={"query":{"match_all":{}}})
            ret["code"] = 1
            ret["desc"] = "그리고 아무도 없었다."
        except Exception as e:
            ret["desc"] = str(e)

        return JsonResponse(ret)


class ApiEndpoint_Download(View):
    def get(self, request, *args, **kwargs):
        book = Book.objects.filter(idx=request.GET.get('idx')).first()
        file_path = os.path.join(Book.BOOKS_PATH, book.path, book.name)
        with open(file_path, 'rb') as f:
            response = HttpResponse(f, content_type='application/force-download')
            response['Content-Length'] = len(response.content)
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
            return response


class ApiEndpoint_Scan(View):

    def updateElasticSearch(self, es, book):
        books = es.search(index='bookshelf', body={"_source":["title"], "query":{"bool":{"must":[{"match_phrase": {"title": book.name}}, {"multi_match": {"query": book.name, "type": "most_fields", "fields": ["title"]}}]}}})

        if books['hits']['total']['value'] > 0:
            logger.info('same title\'s book(%s) detected. try to delete target book content.', book.name)
            es.delete_by_query(index='bookshelf', body={"query":{"bool":{"must":[{"match_phrase": {"title": book.name}}, {"multi_match": {"query": book.name, "type": "most_fields", "fields": ["title"] }}]}}})

        logger.info('update elastic search %s', book.name)

        #Tika has an error with filename that has include None Ascii Code.        
        if not utility.isAscii(book.name):
            #copy file before parse pdf. then change name only use ascii code.
            shutil.copy(src=book.fullpath(), dst=os.path.join(settings.TEMP_DIR, 'book.pdf'))
            parsed = parser.from_file(os.path.join(settings.TEMP_DIR, 'book.pdf'), xmlContent=True)
        else:
            parsed = parser.from_file(book.fullpath(), xmlContent=True)
        paged = parsed["content"].split('<div class="page">')
        body = ""
        iPage = 1
        for page in paged[1:-2]:
            body = body + json.dumps({"index": {"_index": "bookshelf", "_type": "bookshelf_datas"}}) + '\n'
            body = body + json.dumps({"title":book.name, "page":iPage, "content":page, "idx":book.idx, "path":book.path}) + '\n'
            iPage = iPage + 1
        es.bulk(body)

    def validBook(self, filename, dirname, es):
        book = Book.objects.filter(name=filename, path=dirname[len(Book.BOOKS_PATH) + 1:]).first()
        if book is None:
            book = Book()
        else:
            if datetime.fromtimestamp(os.path.getmtime(os.path.join(dirname, filename))) <= book.updDate:
                logger.info('skip book %s', os.path.join(dirname, filename))
                book.size = os.path.getsize(os.path.join(dirname, filename))
                book.save()
                return False

        book.name = filename
        book.path = dirname[len(Book.BOOKS_PATH) + 1:]        
        book.md5 = utility.getFileMd5(os.path.join(dirname, filename))
        book.size = os.path.getsize(os.path.join(dirname, filename))
        book.updDate = now()
        book.save()
        self.updateElasticSearch(es, book)

        return True

    def get(self, request, *args, **kwargs):
        targetpath = Book.BOOKS_PATH

        logger.debug("get ApiEndpoint_Scan target path is '%s'", Book.BOOKS_PATH)

        ret = {"code" : -1, "desc" : "", "skip" : 0, "proc" : 0, "total" : 0}        
        es = Elasticsearch(settings.ELASTICSEARCH_HOST)

        try:
            Book.objects.update(size=0)
            for dirname, dirnames, filenames in os.walk(targetpath):
                for filename in filenames:
                    fname, ext = os.path.splitext(filename)
                    logger.info('%s %s', filename, ext.lower())
                    if ext.lower() != ".pdf":
                        continue
                    ret["total"] = ret["total"] + 1
                    result = self.validBook(filename, dirname, es)
                    if result:
                        ret["proc"] = ret["proc"] + 1
                    else:
                        ret["skip"] = ret["skip"] + 1
            Book.objects.filter(size=0).delete()
            ret["code"] = 1
        except Exception as e:
            utility.logExceptionWithTraceBack(logger, e)
        return JsonResponse(ret)


class LibrarianView(generic.ListView):
    def get(self, request, *args, **kwargs):
        """return EBooks."""
        from_ = request.GET.get('from') if request.GET.get('from') is not None and int(request.GET.get('from')) > 0 else 0
        keyword_ = request.GET.get('keyword') if request.GET.get('keyword') is not None else ""
        category_ = 0 if request.GET.get('category') is None or request.GET.get('category') == "0" else 1
        es = Elasticsearch(settings.ELASTICSEARCH_HOST)
        if category_ == 1:
            docs = es.search(index='bookshelf', body={"query":{"multi_match":{"query": keyword_, "fields":["title" if category_ == 0 else "content"]}}}, from_=from_)
            return render(request, 'librarian.html', {'result' : docs, 'category': category_, 'keyword': keyword_, 'from_': from_})
        else:
            docs = Book.objects.filter(name__contains=keyword_)
            docs = docs.values()
            return render(request, 'librarian.html', {'titles' : docs, 'category': category_, 'keyword': keyword_, 'from_': from_})

class BookStandView(generic.View):
    def get(self, request, *args, **kwargs):
        """return EBook"""
        return render(request, 'bookstand.html', {'idx' : request.GET.get('idx')})
