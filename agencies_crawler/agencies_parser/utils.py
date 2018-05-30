import tldextract
import pandas as pd


def get_domain(url):
    if url:
        xtract = tldextract.extract(url)
        return xtract.domain


def to_excel(
        df, file_name='simple-report.xlsx', columns=None, use_index=False):
    writer = pd.ExcelWriter('reports/%s' % file_name, engine='xlsxwriter')
    extra_params = {}
    if columns:
        extra_params['columns'] = columns

    extra_params['index'] = use_index
    df.to_excel(writer, **extra_params)
    writer.save()
