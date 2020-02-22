var specialElementHandlers = {
    '#prt-btn': function (element, renderer) {
        return true;
    }
};

$(document).on("click", "#print", function () {   
    var doc = new jsPDF('p', 'pt', 'a4');
        doc.text($('#client').text(), 25, 30)
        doc.autoTable({html: '#notes-table', 
                    title: 'Title',
                   columnStyles: {
                    0: {cellWidth: 40},
                    1: {cellWidth: 130},
                    2: {cellWidth: 100}
                   },        
        'elementHandlers': specialElementHandlers,
            
    });

    doc.save($('#client').text() + '-notes.pdf');
});
