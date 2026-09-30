import copy

import pytest

from mlnyc_records.serialize import TeacherSetBib


class TestTeacherSetBib:
    def test_teacher_set_bib(self, stub_bib_data):
        set_bib = TeacherSetBib(**stub_bib_data)
        marc_record = set_bib.to_bib()
        field_strings = [str(i) for i in marc_record.fields]
        assert field_strings == [
            "=001  nn-mlnyc-0000001",
            "=003  BookOps",
            "=008  000101nuuuuuuuuxxu\\\\\\\\\\\\\\\\\\\\\\000\\0\\eng\\d",
            "=091  \\\\$aMLNYC SOC$fCLUB$pA$c[SHELF-NUMBER]",
            "=245  00$aFoo Bar Teacher Set.$pCopy 1 of 2",
            "=300  \\\\$a2 item(s)",
            '=500  \\\\$aSet consists of 2 copies of "Fake book 1".',
            "=520  \\\\$3Fake book 1.",
            "=521  2\\$aPre-K",
            "=526  8\\$aSocial Studies",
            "=690  \\7$aBook Club.$2bookops",
            "=730  02$aFake book 1.$x9781234567897",
            "=901  \\\\$amlnyc-bot$bCATBL",
            "=909  \\\\$aOCLC Holdings Exclusion",
            "=910  \\\\$aBL",
            "=949  \\\\$a*b2=8;b3=e;bn=ed;",
            "=949  \\\\$h10$i[BARCODE]-Fake book 1$nFake book "
            "1$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
            "=949  \\\\$h10$i[BARCODE]-Fake book 1$nFake book "
            "1$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
        ]

    @pytest.mark.parametrize(
        "pub_dates,record_type,lang,output",
        [
            (
                ["2000", "2001"],
                "a",
                "English",
                "i20002001xxu\\\\\\\\\\\\\\\\\\\\\\000\\0\\eng\\d",
            ),
            (
                ["2020"],
                "o",
                "English",
                "i20202020xxu\\\\\\\\\\\\\\\\\\\\\\\\\\|\\||eng\\d",
            ),
            (
                ["20uu"],
                "a",
                "Chinese",
                "i20uu20uuxxu\\\\\\\\\\\\\\\\\\\\\\000\\0\\chi\\d",
            ),
            ([], "o", "Other", "nuuuuuuuuxxu\\\\\\\\\\\\\\\\\\\\\\\\\\|\\|||||\\d"),
        ],
    )
    def test_teacher_set_bib_008_variants(
        self, stub_bib_data, pub_dates, record_type, lang, output
    ):
        set_data = copy.deepcopy(stub_bib_data)
        set_data["pub_dates"] = pub_dates
        set_data["record_type"] = record_type
        set_data["language"] = lang
        set_bib = TeacherSetBib(**set_data)
        marc_record = set_bib.to_bib()
        field_strings = [str(i) for i in marc_record.fields]
        assert field_strings == [
            "=001  nn-mlnyc-0000001",
            "=003  BookOps",
            f"=008  000101{output}",
            "=091  \\\\$aMLNYC SOC$fCLUB$pA$c[SHELF-NUMBER]",
            "=245  00$aFoo Bar Teacher Set.$pCopy 1 of 2",
            "=300  \\\\$a2 item(s)",
            '=500  \\\\$aSet consists of 2 copies of "Fake book 1".',
            "=520  \\\\$3Fake book 1.",
            "=521  2\\$aPre-K",
            "=526  8\\$aSocial Studies",
            "=690  \\7$aBook Club.$2bookops",
            "=730  02$aFake book 1.$x9781234567897",
            "=901  \\\\$amlnyc-bot$bCATBL",
            "=909  \\\\$aOCLC Holdings Exclusion",
            "=910  \\\\$aBL",
            "=949  \\\\$a*b2=8;b3=e;bn=ed;",
            "=949  \\\\$h10$i[BARCODE]-Fake book 1$nFake book "
            "1$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
            "=949  \\\\$h10$i[BARCODE]-Fake book 1$nFake book "
            "1$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
        ]

    def test_teacher_set_enhanced(self, stub_bib_data):
        set_data = copy.deepcopy(stub_bib_data)
        set_data["enhanced"] = "E"
        set_bib = TeacherSetBib(**set_data)
        marc_record = set_bib.to_bib()
        field_strings = [str(i) for i in marc_record.fields]
        assert field_strings == [
            "=001  nn-mlnyc-0000001",
            "=003  BookOps",
            "=008  000101nuuuuuuuuxxu\\\\\\\\\\\\\\\\\\\\\\000\\0\\eng\\d",
            "=091  \\\\$aMLNYC SOC$fCLUB E$pA$c[SHELF-NUMBER]",
            "=245  00$aFoo Bar Teacher Set.$pCopy 1 of 2",
            "=300  \\\\$a2 item(s)",
            '=500  \\\\$aSet consists of 2 copies of "Fake book 1".',
            "=520  \\\\$3Fake book 1.",
            "=521  2\\$aPre-K",
            "=526  8\\$aSocial Studies",
            "=690  \\7$aBook Club.$2bookops",
            "=730  02$aFake book 1.$x9781234567897",
            "=901  \\\\$amlnyc-bot$bCATBL",
            "=909  \\\\$aOCLC Holdings Exclusion",
            "=910  \\\\$aBL",
            "=949  \\\\$a*b2=8;b3=e;bn=ed;",
            "=949  \\\\$h10$i[BARCODE]-Fake book 1$nFake book "
            "1$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
            "=949  \\\\$h10$i[BARCODE]-Fake book 1$nFake book "
            "1$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
        ]

    @pytest.mark.parametrize(
        "title,field_245",
        [
            ("A Title", "=245  02$aA Title.$pCopy 1 of 2"),
            ("L'Title", "=245  02$aL'Title.$pCopy 1 of 2"),
            ("An Alternative Title", "=245  03$aAn Alternative Title.$pCopy 1 of 2"),
            ("El Title", "=245  03$aEl Title.$pCopy 1 of 2"),
            ("La Title", "=245  03$aLa Title.$pCopy 1 of 2"),
            ("Le Title", "=245  03$aLe Title.$pCopy 1 of 2"),
            ("The Titles", "=245  04$aThe Titles.$pCopy 1 of 2"),
            ("Las Titles", "=245  04$aLas Titles.$pCopy 1 of 2"),
            ("Los Titles", "=245  04$aLos Titles.$pCopy 1 of 2"),
            ("Les Titles", "=245  04$aLes Titles.$pCopy 1 of 2"),
            ("Title!", "=245  00$aTitle!$pCopy 1 of 2"),
            ("Title?", "=245  00$aTitle?$pCopy 1 of 2"),
        ],
    )
    def test_teacher_set_bib_title_variants(
        self, stub_bib_data, title, field_245, mock_now
    ):
        set_data = copy.deepcopy(stub_bib_data)
        set_data["set_title"] = title
        set_bib = TeacherSetBib(**set_data)
        marc_record = set_bib.to_bib()
        field_strings = [str(i) for i in marc_record.fields]
        assert field_strings == [
            "=001  nn-mlnyc-0000001",
            "=003  BookOps",
            "=008  000101nuuuuuuuuxxu\\\\\\\\\\\\\\\\\\\\\\000\\0\\eng\\d",
            "=091  \\\\$aMLNYC SOC$fCLUB$pA$c[SHELF-NUMBER]",
            field_245,
            "=300  \\\\$a2 item(s)",
            '=500  \\\\$aSet consists of 2 copies of "Fake book 1".',
            "=520  \\\\$3Fake book 1.",
            "=521  2\\$aPre-K",
            "=526  8\\$aSocial Studies",
            "=690  \\7$aBook Club.$2bookops",
            "=730  02$aFake book 1.$x9781234567897",
            "=901  \\\\$amlnyc-bot$bCATBL",
            "=909  \\\\$aOCLC Holdings Exclusion",
            "=910  \\\\$aBL",
            "=949  \\\\$a*b2=8;b3=e;bn=ed;",
            "=949  \\\\$h10$i[BARCODE]-Fake book 1$nFake book "
            "1$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
            "=949  \\\\$h10$i[BARCODE]-Fake book 1$nFake book "
            "1$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
        ]

    def test_teacher_set_bib_520_variants(self, stub_bib_data):
        set_data = copy.deepcopy(stub_bib_data)
        set_data["components"] = [("Book 1", "A large print book", 1, "Large print")]
        set_data["added_entries"] = [
            {
                "tag": "700",
                "ind1": "1",
                "ind2": "2",
                "subfields": [
                    ("a", "Foo, Bar,"),
                    ("d", "2000-"),
                    ("t", "Book 1."),
                    ("s", "Large print edition."),
                    ("x", "9781234567897"),
                ],
            }
        ]
        set_data["contents_note"] = 'Set consists of 1 copy of "Book 1".'
        set_data["physical_description"] = "1 item(s)"
        set_bib = TeacherSetBib(**set_data)
        marc_record = set_bib.to_bib()
        field_strings = [str(i) for i in marc_record.fields]
        assert field_strings == [
            "=001  nn-mlnyc-0000001",
            "=003  BookOps",
            "=008  000101nuuuuuuuuxxu\\\\\\\\\\\\\\\\\\\\\\000\\0\\eng\\d",
            "=091  \\\\$aMLNYC SOC$fCLUB$pA$c[SHELF-NUMBER]",
            "=245  00$aFoo Bar Teacher Set.$pCopy 1 of 2",
            "=300  \\\\$a1 item(s)",
            '=500  \\\\$aSet consists of 1 copy of "Book 1".',
            "=520  \\\\$3Book 1 [Large print]$aA large print book.",
            "=521  2\\$aPre-K",
            "=526  8\\$aSocial Studies",
            "=690  \\7$aBook Club.$2bookops",
            "=700  12$aFoo, Bar,$d2000-$tBook 1.$sLarge print edition.$x9781234567897",
            "=901  \\\\$amlnyc-bot$bCATBL",
            "=909  \\\\$aOCLC Holdings Exclusion",
            "=910  \\\\$aBL",
            "=949  \\\\$a*b2=8;b3=e;bn=ed;",
            "=949  \\\\$h10$i[BARCODE]-Book 1 [Large print]$nBook 1 [Large print]$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
        ]

    def test_teacher_set_bib_6xx_variants(self, stub_bib_data):
        set_data = copy.deepcopy(stub_bib_data)
        set_data["local_topic_term"] = ["Community"]
        set_data["local_genre_term"] = ["Award Winners", "Nonfiction"]
        set_bib = TeacherSetBib(**set_data)
        marc_record = set_bib.to_bib()
        field_strings = [str(i) for i in marc_record.fields]
        assert field_strings == [
            "=001  nn-mlnyc-0000001",
            "=003  BookOps",
            "=008  000101nuuuuuuuuxxu\\\\\\\\\\\\\\\\\\\\\\000\\0\\eng\\d",
            "=091  \\\\$aMLNYC SOC$fCLUB$pA$c[SHELF-NUMBER]",
            "=245  00$aFoo Bar Teacher Set.$pCopy 1 of 2",
            "=300  \\\\$a2 item(s)",
            '=500  \\\\$aSet consists of 2 copies of "Fake book 1".',
            "=520  \\\\$3Fake book 1.",
            "=521  2\\$aPre-K",
            "=526  8\\$aSocial Studies",
            "=690  \\7$aBook Club.$2bookops",
            "=691  \\7$aCommunity.$2bookops",
            "=695  \\7$aAward Winners.$2bookops",
            "=695  \\7$aNonfiction.$2bookops",
            "=730  02$aFake book 1.$x9781234567897",
            "=901  \\\\$amlnyc-bot$bCATBL",
            "=909  \\\\$aOCLC Holdings Exclusion",
            "=910  \\\\$aBL",
            "=949  \\\\$a*b2=8;b3=e;bn=ed;",
            "=949  \\\\$h10$i[BARCODE]-Fake book 1$nFake book 1$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
            "=949  \\\\$h10$i[BARCODE]-Fake book 1$nFake book 1$leduls$om$q30010$t252$u-$vLOGDOE/mlnyc-bot",
        ]
