##DEPENDENCIES:
#None

##DATA:

#Skosmos REST API instances:
skosmosinstances = [
    ["http://agrovoc.uniroma2.it/agrovoc", "AgroVoc"],
    ["https://bartoc-skosmos.unibas.ch", "Bartoc"],
    ["http://data.ub.uio.no/skosmos", "data.ub.uio.no"],
    ["https://finto.fi", "Finto"],
    ["http://data.legilux.public.lu/vocabulaires", "Legilux"],
    #["https://www.loterre.fr/skosmos", "Loterre"], #too slow
    ["http://194.254.239.28/skosmos", "MIMO"],
    ["http://vocabularies.unesco.org/browser", "UNESCO"],
    ["http://in-situ.theia-land.fr/vocabularies/Skosmos", "OZCAR-Theia"]
    ]

#SPARQL endpoints:
#structure: [[url_1, name_1, {queryname_1a : query_1a, queryname_1b : query_1b}], [url_2, name_2, {queryname_2a : query_2a, queryname_2b : query_2b}]]
sparqlendpoints = [
    ["http://vocab.getty.edu/sparql", "Getty Vocabularies",
    {"http://vocab.getty.edu/queries#Full_Text_Search_Query" :
        """
        select ?Subject ?Term ?Parents ?Descr ?ScopeNote ?Type (coalesce(?Type1,?Type2) as ?ExtraType) {
        ?Subject luc:term "!!SEARCHWORD!!"; a ?typ.
        ?typ rdfs:subClassOf gvp:Subject; rdfs:label ?Type.
        filter (?typ != gvp:Subject)
        optional {?Subject gvp:placeTypePreferred [gvp:prefLabelGVP [xl:literalForm ?Type1]]}
        optional {?Subject gvp:agentTypePreferred [gvp:prefLabelGVP [xl:literalForm ?Type2]]}
        optional {?Subject gvp:prefLabelGVP [xl:literalForm ?Term]}   
        optional {?Subject gvp:parentStringAbbrev ?Parents}
        optional {?Subject foaf:focus/gvp:biographyPreferred/schema:description ?Descr}
        optional {?Subject skos:scopeNote [dct:language gvp_lang:en; rdf:value ?ScopeNote]}}
        """,
     "http://vocab.getty.edu/queries#All_Data_for_Terms_of_Subject" :
        """
        select ?l ?lab ?lang ?pref ?historic ?display ?pos ?type ?kind ?flag ?start ?end ?comment {
        values ?s {tgn:7001393}
        values ?pred {xl:prefLabel xl:altLabel}
        ?s ?pred ?l.
        bind (if(exists{?s gvp:prefLabelGVP ?l},"pref GVP",if(?pred=xl:prefLabel,"pref","")) as ?pref)
        ?l xl:literalForm ?lab.
        optional {?l dct:language [gvp:prefLabelGVP [xl:literalForm ?lang]]}
        optional {?l gvp:displayOrder ?ord}
        optional {?l gvp:historicFlag [skos:prefLabel ?historic]}
        optional {?l gvp:termDisplay [skos:prefLabel ?display]}
        optional {?l gvp:termPOS [skos:prefLabel ?pos]}
        optional {?l gvp:termType [skos:prefLabel ?type]}
        optional {?l gvp:termKind [skos:prefLabel ?kind]}
        optional {?l gvp:termFlag [skos:prefLabel ?flag]}
        optional {?l gvp:estStart ?start}
        optional {?l gvp:estEnd ?end}
        optional {?l rdfs:comment ?comment}
        } order by ?ord
        """
    }]
    ]





