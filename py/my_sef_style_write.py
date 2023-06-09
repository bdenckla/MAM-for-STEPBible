"""
Exports:
    write_bkg_in_csv_and_un_fmts
    write_bkg_in_un_fmt
    bkg_path
"""

import csv
import my_html
import my_sef_header
import my_uni_heb
import my_open
import my_sef_cmn
import my_tanakh_book_names as my_tbn


def write_bkg_in_csv_and_un_fmts(variant, bkg_name, verses):
    """ Write a Sefaria-style book in two formats:
        1. Sefaria format (CSV/HTML)
        2. "Unicode names" format
    """
    csv_path = bkg_path(variant, bkg_name)
    _write_bkg_in_csv_fmt(csv_path, variant, verses)
    write_bkg_in_un_fmt(variant, bkg_name, verses)


def _write_bkg_in_csv_fmt(path, variant, verses):
    """ Write Sefaria-style file in CSV format """
    book_out = {}
    bkid = None
    dic_alef = dict(verses.get('cant_alef') or [])
    dic_bet = dict(verses.get('cant_bet') or [])
    for bcvt, html_els in verses['cant_dual']:
        if bkid is None:
            bkid = my_tbn.bcvt_get_bkid(bcvt)
        else:
            assert bkid == my_tbn.bcvt_get_bkid(bcvt)
        dual = _html_str(html_els)
        if variant.get('variant_include_abcants'):
            alef = _html_str(dic_alef.get(bcvt))
            bet = _html_str(dic_bet.get(bcvt))
            book_out[bcvt] = dual, alef, bet
        else:
            book_out[bcvt] = (dual,)

    def _write_callback(file_handle):
        _write_bkg_in_csv_fmt2(variant, bkid, book_out, file_handle)

    my_open.with_tmp_openw(path, _write_callback, newline='')


def _html_str(html_els):
    return ''.join(map(my_html.el_to_str, html_els)) if html_els else ''


def _write_bkg_in_csv_fmt2(variant, bkid, contents, file_handle):
    writer = csv.writer(file_handle)
    exclude_header = variant.get('variant_exclude_header_from_csv')
    if not exclude_header:
        header = my_sef_header.sef_header(bkid)
        for hkey, hval in header.items():
            writer.writerow((hkey, hval))
    sef_bkna = my_sef_cmn.SEF_ENGLISH_BOOK_NAMES[bkid]
    for bcvt, verse in contents.items():
        chnu = my_tbn.bcvt_get_chnu(bcvt)
        vrnu = my_tbn.bcvt_get_vrnu(bcvt)
        bcv_str = f'{sef_bkna} {chnu}:{vrnu}'
        writer.writerow((bcv_str, *verse))


def write_bkg_in_un_fmt(variant, bkg_name, verses):
    """ Write book group in "Unicode names" format. """
    my_uni_heb.do_quick_test()
    path = bkg_path(variant, bkg_name, fmt_is_unicode_names=True)
    title = f'unicode_names {bkg_name}'
    if variant.get('variant_include_abcants'):
        dic_alef = dict(verses.get('cant_alef') or [])
        dic_bet = dict(verses.get('cant_bet') or [])
    else:
        dic_alef = {}
        dic_bet = {}

    def _write_callback(out_fp):
        out_fp.write(f'{title}\n')
        for bcvt, html_els in verses['cant_dual']:
            multiverse = {
                'cant_dual': html_els,
                'cant_alef': dic_alef.get(bcvt),
                'cant_bet': dic_bet.get(bcvt)
            }
            my_uni_heb.write_verse_un(out_fp, bcvt, multiverse)

    my_open.with_tmp_openw(path, _write_callback)


def bkg_path(variant, bkg_name, fmt_is_unicode_names=False):
    """ Return path based on book group name bkg_name. """
    if fmt_is_unicode_names:
        fmt = 'unicode_names'
    else:
        fmt = variant.get('variant_file_format') or 'csv'
    path_qual = variant.get('variant_path_qual') or ''
    # vpq examples include '' (the empty string) and '-ajf'
    folders = {
        'unicode_names': f'unicode-names{path_qual}',
        'csv': f'csv{path_qual}',
        'xml': f'xml{path_qual}',
    }
    exts = {
        'unicode_names': '.txt',
        'csv': '.csv',
        'xml': '.xml',
    }
    mam_for_xxx = variant.get('variant_mam_for_xxx') or 'MAM-for-Sefaria'
    parent = f'../{mam_for_xxx}/out'
    path = f'{parent}/{folders[fmt]}/{bkg_name}{exts[fmt]}'
    return path
