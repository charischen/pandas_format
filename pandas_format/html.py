from collections import Mapping, Sequence

import numpy as np
import pandas as pd
from pandas.core.common import is_float_dtype

from jinja2 import Environment, PackageLoader
import markupsafe

env = Environment(loader=PackageLoader("pandas_format"), trim_blocks=True,
                  lstrip_blocks=True)

def _inline(key, value):
    if value is None:
        return str(key)
    else:
        return str(key) + "=" + repr(value)
def dict_to_inline(d):
    if d:
        return " " + " ".join(_inline(k, v) for k, v in d.items())
    else:
        return ""

env.filters["inline"] = dict_to_inline

def _to_html(df, header=True, index=True, index_names=True,
             bold_rows=True, max_rows=float('inf'), max_cols=float('inf'),
             show_dimensions=False, styler=None):

    env.filters["format_value"] = styler.format_value
    env.globals["styler"] = styler

    template = env.get_template("html.tpl")

    if isinstance(df.index, pd.MultiIndex):
        levels = len(df.index.levels)
    else:
        levels = 1

    return template.render(df=df, levels=levels, bold_rows=bold_rows,
                           header=header, index=index, index_names=index_names,
                           max_rows=max_rows, max_cols=max_cols,
                           show_dimensions=show_dimensions)

def to_html(df, buf=None, columns=None, col_space=None, header=True,
            index=True, na_rep='NaN', formatters=None, float_format=str,
            sparsify=True, index_names=True, justify=None, bold_rows=True,
            classes=None, escape=True, max_rows=float('inf'),
            max_cols=float('inf'), show_dimensions=False):
    if columns is not None:
        df = df[columns]

    index_names = index_names and any(df.index.names)
    styler = HtmlStyler(df, col_space, na_rep, formatters, float_format,
                        justify, sparsify, classes, escape)

    ret = _to_html(df, header, index, index_names, bold_rows, max_rows,
                   max_cols, show_dimensions, styler)
    if buf is None:
        return ret
    else:
        buf.write(ret)

class Styler(object):
    def __init__(self, df):
        self.df = df
        self.indices = df.index.tolist()
    def format_value(self, value):
        return markupsafe.escape(str(value))

    def index_style(self, i, level=None, first=False):
        return {}

    def header_style(self, i):
        return {}

    def value_style(self, row, col):
        return {}

    def tbody_style(self):
        return {}

    def thead_style(self):
        return {}

    def row_style(self, i):
        return {}

    def table_style(self):
        return {"border": 1, "class": "dataframe"}


class HtmlStyler(Styler):
    def __init__(self, df, col_space=None, na_rep='NaN', formatters=None,
                 float_format=str, justify=None, sparsify=True, classes=None,
                 escape=True):
        super(HtmlStyler, self).__init__(df)

        self.col_space = col_space
        self.na_rep = na_rep
        self.escape = escape
        self.justify = justify

        self.float_format = float_format
        self.sparsify = sparsify

        self.formatters = formatters
        self.classes = classes

        if isinstance(self.formatters, Sequence):
            if len(self.formatters) != len(self.df.columns):
                raise IndexError

    def format_value(self, value, row, col):
        if self.formatters is not None:
            columns = self.df.columns
            if isinstance(self.formatters, Mapping):
                column = columns[col]
                if column in self.formatters:
                    return self.formatters[column](value)
            elif isinstance(self.formatters, Sequence):
                if len(columns) == len(self.formatters):
                    return self.formatters[col](value)
                else:
                    raise IndexError
            else:
                raise Exception

        if value != value:
            value = self.na_rep
        elif is_float_dtype(np.array(value)):
            value = self.float_format(value)
        else:
            value = str(value)

        if self.escape:
            return markupsafe.escape(value)
        else:
            return value

    def index_style(self, i, level=None, first=False):
        inline = {}
        if self.col_space is not None:
            inline["style"] = "min-width: {};".format(self.col_space)

        if level is not None and self.sparsify:
            current = self.indices[i][level]
            if first or self.indices[i-1][level] != current:
                inline["rowspan"] = 1
                for index in self.indices[i+1:]:
                    if index[level] == current:
                        inline["rowspan"] += 1
                    else:
                        break
        return inline

    def header_style(self, i):
        if self.col_space is not None:
            return {"style": "min-width: {};".format(self.col_space)}
        else:
            return {}

    def table_style(self):
        inline = super(HtmlStyler, self).table_style()
        if isinstance(self.classes, str):
            inline["class"] += " " + self.classes
        elif self.classes is not None:
            inline["class"] += " " + " ".join(self.classes)
        return inline

    def thead_style(self):
        if self.justify is not None:
            return {"style": "text-align: {};".format(self.justify)}
        else:
            return {}
