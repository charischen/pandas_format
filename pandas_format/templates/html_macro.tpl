{% macro row_header(header, d) %}
	{% if bold_rows %}
		<th{{ d | inline }}>{{ header }}</th>
	{% else %}
		<td{{ d | inline }}>{{ header }}</th>
	{% endif %}
{% endmacro %}

{% macro column_header(header, i) %}
	{% set d = styler.header_style(i) %}
	<th{{ d | inline}}> {{ header }} </th>
{% endmacro %}

{% macro display_rows(rows, start) %}
	{% set dindex = rows.index.tolist() %}
	{% for tuple in rows.itertuples() %}
		{% set outerloop = loop %}
		<tr{{ styler.row_style(outerloop.index0 + start) | inline }}>
			{% if index %}
				{% if levels == 1 %}
					{% set d = styler.index_style(start + outerloop.index0) %}
					{{ row_header(tuple[0], d) }}
				{% else %}
					{% for i in tuple[0] %}
						{% set d = styler.index_style(start + outerloop.index0, loop.index0, outerloop.first) %}
						{% if "rowspan" in d %}
							{{ row_header(i, d) }}
						{% endif %}
					{% endfor %}
				{% endif %}
			{% endif %}
			{% if not split_cols %}
				{% for value in tuple[1:] %}
					{% set d = styler.value_style(outerloop.index0 + start, loop.index0) %}
					<td{{ d | inline }}>{{ value | format_value(outerloop.index0 + start, loop.index0) }}</td>
				{% endfor %}
			{% else %}
				{% for value in tuple[1:head_col + 1] %}
					{% set d = styler.value_style(outerloop.index0 + start, loop.index0) %}
					<td{{ d | inline }}>{{ value | format_value(outerloop.index0 + start, loop.index0) }}</td>
				{% endfor %}
				<td> &hellip; </td>
				{% for value in tuple[-tail_col:] %}
					{% set d = styler.value_style(outerloop.index0 + start, df | length - loop.revindex0) %}
					<td{{ d | inline }}>{{ value | format_value(outerloop.index0 + start, df | length - loop.revindex0) }} </td>
				{% endfor %}
			{% endif %}
		  </tr>
	{% endfor %}
{% endmacro %}
