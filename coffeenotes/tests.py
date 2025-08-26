from django.contrib.auth import get_user_model
from django.http import HttpRequest
from django.test import TestCase, Client, RequestFactory
from django.urls import resolve
from coffeenotes.models import Coffeenote
from coffeenotes.views import top, coffeenote_new, coffeenote_edit, coffeenote_detail
from shop.models import Shop

UserModel = get_user_model()

class TopPageTest(TestCase):
    def test_top_returns_200_and_expected_title(self):
        response = self.client.get('/')
        self.assertContains(response, "CoffeeNote", status_code=200)

    def test_top_uses_expected_template(self):
        response = self.client.get('/')
        self.assertTemplateUsed(response, "coffeenotes/top.html")

class TopPageRenderCoffeenotesTest(TestCase):
    def setUp(self):
        self.user = UserModel.objects.create(
            username="testuser",
            email="test@example.com",
            password="secret"
        )
        self.shop = Shop.objects.create(
            name="店名1",
            address="場所1"
        )
        self.coffeenote = Coffeenote.objects.create(
            shop=self.shop,
            bean="豆1",
            roast_level="浅煎り",
            extract_method="ペーパードリップ",
            grind_size="粗挽き",
            memo="メモ",
            smell=1,
            acdity=2,
            body=3,
            aftertaste=4,
            bitterness=5,
            created_by=self.user
        )

class CreateCoffeenoteTest(TestCase):
    def setUp(self):
        self.user = UserModel.objects.create(
            username="testuser",
            email="test@example.com",
            password="secret"
        )
        self.shop = Shop.objects.create(
            name="店名1",
            address="場所1"
        )
        self.client.force_login(self.user)

    def test_render_creation_form(self):
        response = self.client.get("/coffeenotes/new/")
        self.assertContains(response, "コーヒーノートの登録", status_code=200)

    def test_create_coffeenote(self):
        data = {'shop' : self.shop, 'bean' : '豆1', 'roast_level' : '浅煎り', 'extract_method' : 'ペーパードリップ',
            'grind_size' : '粗挽き', 'memo' : 'メモ', 'smell' : 1, 'acdity' : 2, 'body' : 3, 'aftertaste' : 4,
            'bitterness' : 5, 'created_by' : self.user}
        self.client.post("/coffeenotes/new/", data)
        coffeenote = Coffeenote.objects.get(shop=self.shop)
        self.assertEqual('浅煎り', coffeenote.roast_level)
        self.assertEqual('ペーパードリップ', coffeenote.extract_method)

class CoffeenoteDetailTest(TestCase):
    def setUp(self):
        self.user = UserModel.objects.create(
            username="testuser",
            email="test@example.com",
            password="secret",
        )
        self.shop = Shop.objects.create(
            name="店名1",
            address="場所1"
        )
        self.coffeenote = Coffeenote.objects.create(
            shop=self.shop,
            bean="豆1",
            roast_level="浅煎り",
            extract_method="ペーパードリップ",
            grind_size="粗挽き",
            memo="メモ",
            smell=1,
            acdity=2,
            body=3,
            aftertaste=4,
            bitterness=5,
            created_by=self.user
        )
        def test_should_use_expected_template(self):
            response = self.client.get("/coffeenotes/%s/" % self.coffeenote.id)
            self.assertTemplateUsed(response, "coffeenotes/coffeenote_detail.html")

        def test_top_page_returns_200_and_expected_heading(self):
            response = self.client.get("/coffeenotes/%s/" % self.coffeenote.id)
            self.assertContains(response, self.coffeenote.bean, status_code=200)

class EditCoffeenoteTest(TestCase):
    def test_should_resolve_coffeenote_edit(self):
        found = resolve('/coffeenotes/1/edit/')
        self.assertEqual(coffeenote_edit, found.func)