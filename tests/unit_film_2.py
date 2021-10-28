# Run this test from the project root directory
from tests.core import *
from wfs.helpers.info import labels_mapping_table

work_attrs_expected_norm = [["novel"], ["1938"], ["Raymond Sherwood King"], ["If I Die Before I Wake"], []]
work_attrs_expected_writ = [["novel"], [], ["Georges Simenon"], ["Night at the Crossroads"], []]


class TestFilm(TestBase):
    def test_init(self):
        self.assertListEqual(self.film.titles, [])
        self.assertListEqual(self.film.cast, [])
    

    def test_titles(self):
        # Multiple alt titles
        self.intra_setup_film_titles('hollow_triumph.html')
        details_expected = ["Hollow Triumph", "Hollow Triumph", "The Man Who Murdered Himself", "The Scar"]
        notes_expected = [["page"], ["summary"], ["alt"], ["alt"]]
        self.assertEqual(len(self.film.titles), 4)
        for i in range(4):
            self.assertEqual(self.film.titles[i].detail, details_expected[i])
            self.assertListEqual(self.film.titles[i].notes, notes_expected[i])
        # Page parenthetical note
        self.intra_setup_film_titles('suddenly.html')
        self.assertListEqual(self.film.titles[0].notes, ["page", "1954 film"])
    

    def test_cast_ul(self):
        # Uls in a table
        self.intra_setup_film_cast('caged.html', 'set_cast_ul')
        self.assertEqual(self.film.cast[6].detail, "Jan Sterling")
        self.assertEqual(self.film.cast[6].role, "Jeta Kovsky aka \"Smoochie\"")
        self.assertEqual(len(self.film.cast), 12)
        # Empty lis skipped
        self.intra_setup_film_cast('the_chase.html', 'set_cast_ul')
        self.assertEqual(len(self.film.cast), 12)
        # Nested lis
        self.intra_setup_film_cast('the_lady_from_shanghai.html', 'set_cast_ul')
        self.assertEqual(self.film.cast[0].detail, "Rita Hayworth")
        self.assertEqual(self.film.cast[0].role, "Elsa \"Rosalie\" Bannister")
        self.assertListEqual(self.film.cast[0].notes, ["singing voice was dubbed by Anita Kert Ellis"])
    

    def test_cast_table(self):
        self.intra_setup_film_cast('pushover.html', 'set_cast_table')
        self.assertEqual(self.film.cast[0].detail, "Fred MacMurray")
        self.assertListEqual(self.film.cast[0].notes, [])
        self.assertEqual(self.film.cast[0].role, "Paul Sheridan")
        self.assertEqual(len(self.film.cast), 17)
    

    def test_infobox(self):
        # Normal
        self.intra_setup_film_infobox('the_seventh_victim.html')
        self.assertEqual(self.film.direction[0].detail, "Mark Robson")
        self.assertListEqual(self.film.direction[0].notes, [])
        # Special method present
        self.assertEqual(self.film.dates[0].detail, "1943-08-21")
        # Special method absent
        for money_label in ['sales', 'budget']:
            self.assertIsNone(getattr(self.film, money_label, None))
        # Multiple parentheticals
        self.intra_setup_film_infobox('the_pawnbroker.html')
        self.assertListEqual(self.film.distribution[1].notes, ["via Republic Pictures", "current"])
        # Spread notes
        self.intra_setup_film_infobox('the_lady_from_shanghai.html')
        for i in range(1, 4):
            self.assertListEqual(self.film.writing[i].notes, ["uncredited"])
        # Custom mapping table
        self.intra_setup_film_infobox('raw_deal.html', mapping_table={'Cinematography': "dp"})
        self.assertEqual(self.film.dp[0].detail, "John Alton")
        for val in list(labels_mapping_table.values()):
            self.assertIsNone(getattr(self.film, val, None))


    def test_basis(self):
        # Normal
        self.intra_setup_film_basis('the_lady_from_shanghai.html')
        for i, key in enumerate(self.film.basis.fycws_keys):
            self.assertListEqual(work_attrs_expected_norm[i], getattr(self.film.basis, key))
        # From writers
        self.intra_setup_film_basis('la_nuit_du_carrefour.html')
        for i, key in enumerate(self.film.basis.fycws_keys):
            self.assertListEqual(work_attrs_expected_writ[i], getattr(self.film.basis, key))
