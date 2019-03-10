$( function() {
  $("#filter").change(function () {
    var filter = $(this).children("option:selected").val()
    var table = document.getElementById("table")

    for (var i=1; i < table.rows.length; i++) {

    if (filter == "All") {
      $(table.rows[i]).css({"display": "table-row"})
    }
    else if ($(table.rows[i].children[3]).text() == filter) {
      $(table.rows[i]).css({"display": "table-row"})
    }
    else {
      $(table.rows[i]).css({"display": "none"})

    }
}
  });
});
