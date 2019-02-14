/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this file,
 * You can obtain one at http://mozilla.org/MPL/2.0/. */


function toArray(iter) {
    if (iter === null) {
        return null;
    }
    return Array.prototype.slice.call(iter);
}

function find(selector, elem) {
    if (!elem) {
        elem = document;
    }
    return elem.querySelector(selector);
}

function find_all(selector, elem) {
    if (!elem) {
        elem = document;
    }
    return toArray(elem.querySelectorAll(selector));
}

function find_next(selector, elem) {
    while (elem && elem.nodeName != selector) {
        elem = elem.nextElementSibling;
    }

    return elem;
}

function sort_column(elem) {
    toggle_sort_states(elem);
    var colIndex = toArray(elem.parentNode.childNodes).indexOf(elem);
    var key;
    if (elem.classList.contains('numeric')) {
        key = key_num;
    } else if (elem.classList.contains('result')) {
        key = key_result;
    } else {
        key = key_alpha;
    }
    sort_table(elem, key(colIndex));
}

function show_all_extras(elem) {
    find_all('.col-result', find_next("TABLE", elem)).forEach(show_extras);
}

function hide_all_extras(elem) {
    find_all('.col-result', find_next("TABLE", elem)).forEach(hide_extras);
}

function show_extras(colresult_elem) {
    var extras = colresult_elem.parentNode.nextElementSibling;
    var expandcollapse = colresult_elem.firstElementChild;
    extras.classList.remove("collapsed");
    expandcollapse.classList.remove("expander");
    expandcollapse.classList.add("collapser");
}

function hide_extras(colresult_elem) {
    var extras = colresult_elem.parentNode.nextElementSibling;
    var expandcollapse = colresult_elem.firstElementChild;
    extras.classList.add("collapsed");
    expandcollapse.classList.remove("collapser");
    expandcollapse.classList.add("expander");
}

function show_filters() {
    var filter_items = document.getElementsByClassName('filter');
    for (var i = 0; i < filter_items.length; i++)
        filter_items[i].hidden = false;
}

function add_collapse() {
    // Add links for show/hide all
    find_all('table.results-table:not(.summary-table)').forEach(function(resulttable) {
        var showhideall = document.createElement("p");
        showhideall.innerHTML = '<a style="text-decoration:underline;cursor:pointer;" onclick="show_all_extras(this.parentElement)">Show all details</a> / ' +
            '<a style="text-decoration:underline;cursor:pointer;" onclick="hide_all_extras(this.parentElement)">Hide all details</a>';
        resulttable.parentElement.insertBefore(showhideall, resulttable);
    });

    // Add show/hide link to each result
    find_all('.col-result').forEach(function(elem) {
        var collapsed = get_query_parameter('collapsed') || 'Passed';
        var extras = elem.parentNode.nextElementSibling;
        var expandcollapse = document.createElement("span");
        if (collapsed.includes(elem.innerHTML)) {
            extras.classList.add("collapsed");
            expandcollapse.classList.add("expander");
        } else {
            expandcollapse.classList.add("collapser");
        }
        elem.appendChild(expandcollapse);

        elem.addEventListener("click", function(event) {
            if (event.currentTarget.parentNode.nextElementSibling.classList.contains("collapsed")) {
                show_extras(event.currentTarget);
            } else {
                hide_extras(event.currentTarget);
            }
        });
    })
}

function get_query_parameter(name) {
    var match = RegExp('[?&]' + name + '=([^&]*)').exec(window.location.search);
    return match && decodeURIComponent(match[1].replace(/\+/g, ' '));
}

function init() {
    reset_sort_headers();

    add_collapse();

    show_filters();

    toggle_sort_states(find('.initial-sort'));

    find_all('.sortable').forEach(function(elem) {
        elem.addEventListener("click",
                              function(event) {
                                  sort_column(elem);
                              }, false)
    });

    set_rel_class();

    hide_all_extras();
};

function sort_table(clicked, key_func) {
    var table = clicked.parentNode.parentNode.parentNode;
    var previous_sibling = table.previousSibling;
    var rows = find_all('.results-table-row:not([do_not_remove])', table);
    var reversed = !clicked.classList.contains('asc');
    var sorted_rows = sort(rows, key_func, reversed);
    /* Whole table is removed here because browsers acts much slower
     * when appending existing elements.
     */
    var thead = find('thead', table);
    var totals = find('.total', table);
    table.remove();
    var parent = document.createElement("table");
    parent.classList.add("results-table");
    parent.id = table.id;
    parent.appendChild(thead);
    sorted_rows.forEach(function(elem) {
        parent.appendChild(elem);
    });
    parent.append(totals);
    previous_sibling.parentNode.insertBefore(parent, previous_sibling.nextSibling);
}

function sort(items, key_func, reversed) {
    var sort_array = items.map(function(item, i) {
        return [key_func(item), i];
    });
    var multiplier = reversed ? -1 : 1;

    sort_array.sort(function(a, b) {
        var key_a = a[0];
        var key_b = b[0];
        return multiplier * (key_a >= key_b ? 1 : -1);
    });

    return sort_array.map(function(item) {
        var index = item[1];
        return items[index];
    });
}

function key_alpha(col_index) {
    return function(elem) {
        return elem.childNodes[1].childNodes[col_index].firstChild.data.toLowerCase();
    };
}

function key_num(col_index) {
    return function(elem) {
        return parseFloat(elem.childNodes[1].childNodes[col_index].firstChild.data);
    };
}

function key_result(col_index) {
    return function(elem) {
        var strings = ['error', 'failed', 'rerun', 'xfailed', 'xpassed',
                       'skipped', 'passed'];
        return strings.indexOf(elem.childNodes[1].childNodes[col_index].firstChild.data);
    };
}

function reset_sort_headers() {
    find_all('.sort-icon').forEach(function(elem) {
        elem.parentNode.removeChild(elem);
    });
    find_all('.sortable').forEach(function(elem) {
        var icon = document.createElement("div");
        icon.className = "sort-icon";
        icon.textContent = "vvv";
        elem.insertBefore(icon, elem.firstChild);
        elem.classList.remove("desc", "active");
        elem.classList.add("asc", "inactive");
    });
}

function toggle_sort_states(elem) {
    //if active, toggle between asc and desc
    if (elem.classList.contains('active')) {
        elem.classList.toggle('asc');
        elem.classList.toggle('desc');
    }

    //if inactive, reset all other functions and add ascending active
    if (elem.classList.contains('inactive')) {
        reset_sort_headers();
        elem.classList.remove('inactive');
        elem.classList.add('active');
    }
}

function is_all_rows_hidden(value) {
    return value.hidden == false;
}

function filter_table(elem) {
    var outcome_att = "data-test-result";
    var outcome = elem.getAttribute(outcome_att);
    var class_outcome = outcome + " results-table-row";
    var suffix_id = elem.getAttribute("data-suffix-id");
    var table = find_next("TABLE", elem);

    var outcome_rows = Array.from(table.getElementsByClassName(class_outcome));

    for(var i = 0; i < outcome_rows.length; i++){
        outcome_rows[i].hidden = !elem.checked;
    }


    var rows = find_all('.results-table-row').filter(is_all_rows_hidden);
    var all_rows_hidden = rows.length == 0 ? true : false;
    var not_found_message = document.getElementById("not-found-message" + suffix_id);
    if (not_found_message) {
        not_found_message.hidden = !all_rows_hidden;
    }
}

function update_check_boxes(checked_status, outcome) {
    var data_att = "[data-test-result='" + outcome + "']";
    var check_boxes = document.querySelectorAll(data_att);

    check_boxes.forEach(function(element) { 
        element.checked = checked_status;
    });
}

function scroll_to(elem) {
    var id = elem.id;
    var heading_id = "#heading-" + id;
    var heading = document.querySelector(heading_id);
    var scroll_distance = heading.getBoundingClientRect().y;

    window.scrollBy({
        left: 0, 
        top: scroll_distance, 
        behavior: "auto"
    });
}

function scroll_to_top() {
    window.scrollTo({
        left: 0,
        top: 0,
        behavior: "auto"
    });
}

function scroll_to_parent(name) {
    var heading_id = "#heading-" + name;
    var heading = document.querySelector(heading_id);
    scroll_distance = heading.getBoundingClientRect().y;

    window.scrollBy({
        left: 0,
        top: scroll_distance,
        behavior: "auto"
    });
}

function set_rel_class() {
    var rel_pass_elements = document.querySelectorAll(".rel_pass");

    rel_pass_elements.forEach(function(elem) {
        var rel_pass = parseFloat(elem.innerHTML);

        if (rel_pass == 100) {
            elem.classList.add("passed");
            elem.parentElement.classList.add("passed");
        } else {
            elem.classList.add("close-to-pass");
            elem.classList.add("failed");
            elem.parentElement.classList.add("failed");
        }

        elem.classList.remove("rel_pass");
    });
}
