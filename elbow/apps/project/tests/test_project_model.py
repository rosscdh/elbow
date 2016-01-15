# -*- coding: UTF-8 -*-
from . import TestCase
from model_mommy import mommy


class ProjectModelTest(TestCase):
    """
    Test basic model methods
    """
    def setUp(self):
        self.project = mommy.make('project.Project', name='My Basic Test Project')

    def test_url(self):
        """
        Autoslug should auto generate the slug field
        """
        self.assertEqual(self.project.url, u'/projects/my-basic-test-project/')

    def test_num_backers(self):
        self.assertEqual(self.project.num_backers, 0)

    def test_percent(self):
        self.assertEqual(self.project.percent, 0)

    def test_revenue(self):
        self.assertEqual(self.project.revenue, 0)


class ProjectModelWithOrdersTest(TestCase):
    """
    Test model methods with orders
    """
    def setUp(self):
        self.project = mommy.make('project.Project',
                                  name='My Test Project with Orders',
                                  amount=10000.00)
        self.orders = mommy.make('order.Order', _quantity=5,
                                 project=self.project,
                                 amount=1000.00)

    def test_url(self):
        """
        Autoslug should auto generate the slug field
        """
        self.assertEqual(self.project.url, u'/projects/my-test-project-with-orders/')

    def test_num_backers(self):
        self.assertEqual(self.project.num_backers, 5)

    def test_percent(self):
        self.assertEqual(self.project.percent, 50.0)

    def test_revenue(self):
        self.assertEqual(self.project.revenue, 5000.0)
