{% macro row_header(header, d) %}
	{% if bold_rows %}
		<th{{ d | inline }}>{{ header | format_value }}</th>
	{% else %}
		<td{{ d | inline }}>{{ header | format_value }}</th>
	{% endif %}
{% endmacro %}

{% macro column_header(header, i) %}
	{% set d = styler.column_style(i) %}
	<th{{ d | inline}}> {{ header }} </th>
{% endmacro %}

{% macro display_rows(rows, start) %}
	{% set dindex = rows.index.tolist() %}
	{% for tuple in rows.itertuples() %}
		{% set outerloop = loop %}
		<tr>
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
					<td{{ d | inline }}>{{ value | format_value }}</td>
				{% endfor %}
			{% else %}
				{% for value in tuple[1:head_col + 1] %}
					{% set d = styler.value_style(outerloop.index0 + start, loop.index0) %}
					<td{{ d | inline }}>{{ value | format_value }}</td>
				{% endfor %}
				<td> &hellip; </td>
				{% for value in tuple[-tail_col:] %}
					{% set d = styler.value_style(outerloop.index0 + start, loop.index0 + tail_col) %}
					<td{{ d | inline }}>{{ value | format_value }}</td>
				{% endfor %}
			{% endif %}
		  </tr>
	{% endfor %}
{% endmacro %}
