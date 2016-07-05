from django.test import TestCase
from mutopia.utils import FTP_URL
from rdflib import Graph, URIRef, Namespace
import os.path
from mutopia.utils import id_from_footer

MP = Namespace('http://www.mutopiaproject.org/piece-data/0.1/')

class RDFTest(TestCase):
    def test_can_build_rdf_graph(self):
        path = 'mutopia/tests/for-testing.rdf'

        g = Graph().parse(path)
        self.assertTrue(isinstance(g, Graph))

        # Because our RDF's are defined as 'rdf:about:"."' the subject
        # line is an URI reference to the absolute dirname.
        subj = URIRef('file://' + os.path.dirname(os.path.abspath(path)) + '/')

        footer = g.value(subject=subj,predicate=MP.id)
        self.assertEquals(str(footer), "Mutopia-2014/02/24-411")
        _, id = id_from_footer(footer)
        self.assertEqual(int(id), 411)


    def test_throws_on_bad_rdf(self):
        path = 'mutopia/tests/not-here.rdf'
        with self.assertRaises(FileNotFoundError):
            g = Graph().parse(path)
