vars = [
    report_name,
    report_datetime,
    username,
    operating_system,
    python_version,
    n_tests,
    runtime,

]

test_vars = [
    result,
    name,
    duration,
    log,
]

<tbody class="failed results-table-row">
    <tr>
        <td class="col-result">{{ result }}</td>
        <td class="col-name">{{ name }}}</td>
        <td class="col-duration">{{ duration }}</td>
        <td class="col-links"></td></tr>
    <tr>
        <td class="extra" colspan="4">
            <div class="log">{{ log }}</div>
        </td>
    </tr>
</tbody>
<tbody class="passed results-table-row">
    <tr>
        <td class="col-result">{{ result }}</td>
        <td class="col-name">{{ name }}}</td>
        <td class="col-duration">{{ duration }}</td>
        <td class="col-links"></td></tr>
    <tr>
        <td class="extra" colspan="4">
            <div class="log">{{ log }}</div>
        </td>
    </tr>
</tbody>
