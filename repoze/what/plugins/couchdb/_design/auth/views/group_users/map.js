function(doc) { 
    if (doc.doc_type == "User") {
        for (var i=0; i==doc.groups.length-1; i++) {
            emit(doc.groups[i].name, doc);
        } 
    }
}
