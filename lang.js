
function setLanguage(lang) {
    // Fallback
    if(!['nl', 'en'].includes(lang)) {
        lang = 'nl'
    }
    
    // Iterate trough all elements that have data-lang attribute
    $("[data-lang]").each(function(i, obj) {
        key = $(obj).data("lang")
        // Check if attribute should be used
        if('attr' in langs[lang][key]) {
            $(obj).attr(langs[lang][key]['attr'], langs[lang][key]['text']);
        }
        else {
            $(obj).text(langs[lang][key]['text']);
        }
    });

}

var langs = {
    en: {
        ok: {text: "Ok"},
        cancel: {text: "Cancel"},
        skip: {text: "Skip"},
        
        place_photo: {text: "Open the Scanner and place the photograph facing down. After placing the photo, close the scanner lid and press the scan button on this screen to scan the photograph."},
        start_scan: {text: "Start scan"},
        scanning: {text: "Scanning..."},
        validate: {text: "Looks good? Rotate the image with the buttons and Press ok. Incase you want to re scan, press cancel and start the scanning procedure again."},
        rotate_neg: {text: "Rotate -90°"},
        rotate_pos: {text: "Rotate +90°"},
        disclaimer: {text: "I confirm that the photo and story may be used for socio-cultural, heritage, educational and scientific purposes on non-profit basis. Kindly provide us your concent by giving us your name and email address."},
        name: {text: "Name:"},
        email: {text: "Email address:"},
        phone: {text: "Mobile number:"},
        date:{text: "Date of the Photo:"},
        bedrijf: {text: "Horticulture Company:"},
        teelt: {text: "Crop:"},
        desc: {text: "Description:"},
        address: {text: "Address:"},
        photographer: {text: "Photographer:"},
        bedrijf_desc: {attr: "placeholder",text: "Name of the involved Horticulture Company"},
        teelt_desc: {attr: "placeholder",text: "Crop in which the company is specialized in"},
        desc_desc: {attr: "placeholder",text: "Short Description of the photo"},
        foto_desc: {attr: "placeholder",text: "Name of the photographer"},       
        uploading: {text: "Uploading..."},
        take_photo: {text: "Take back the photograph from the scanner and proceed to next station."},
        
        wait_audio : {text:"No scans found... Kindly proceed to desk 1 and scan your photograph"},
        start_rec: {text: "Provide us additional information about the photograph by briefly explaining it. You can Start recording by pressing the record button. After recording press the STOP button. Press OK or SKIP and proceed to the next section. "},
        finish_audio: {text: "Your audio has been saved. Please proceed to desk 3."},

        wait_loc : {text:"No scans found... Kindly proceed to desk 1 and scan your photograph"},
        place_pin: {text: "Do you know where the photograph was taken.?? If so use the map and place the pin on the place where it was taken. Alternatively, you can also type the address of the place on the search bar. Press OK after you are done and proceed to the next counter."},
        search: {attr: "placeholder", text: "Search..."},
        finish_loc: {text: "Your location has been saved. Thank you for your inputs. You can view other scans and results on the big screen."},

        recenter: {text: "Re-center"},
        route: {text: "Routes"},
        route1:{text:"Walking Route - Stroll through green Ghent"},
        route2:{text:"Biking Route - Horticulture in the Ghent neighbourhood"},
        route3:{text: "Biking Route - Teaching and research"},
        video: {text: "Video"},
        video1:{text:"Video: Grape cutting"},
        video2:{text:"Video: Hornbean drafting"},
        nearby_images: {text: "Photos in the neighbourhood"},
        top_images: {text: "Top images"},
        info:{text: "Information about the photo (In Dutch)"},
        visualization: {text: "Interactive map - Flore de Gand"},
        
        select_img: {text: "Select image from computer, max file size 10MB."},
        drag_drop: {text: "Click or drag image here..."},
    },
    nl: {
        ok: {text: "Ok"},
        skip: {text: "Overslaan"},
        cancel: {text: "Annuleren"},
        
        place_photo: {text: "Open de scanner en leg uw foto met de beeldzijde naar onder op de scanner. Sluit vervolgens de scanner en druk op de knop 'Scannen' op dit scherm. Uw scan wordt vervolgens gestart."},
        start_scan: {text: "Start het scannen"},
        scanning: {text: "Aan het scannen..."},
        validate: {text: "Is de scan ok? Druk dan op OK. Draai (indien nodig) de foto via de Draai -90°/+90° knoppen. Indien je niet tevreden bent kan je de scan ook annuleren en opnieuw beginnen."},
        rotate_neg: {text: "Draai -90°"},
        rotate_pos: {text: "Draai +90°"},
        disclaimer: {text: "Ik bevestig dat de foto en het verhaal mag gebruikt worden voor sociaal-culturele, erfgoed, educatieve en wetenschappelijke doeleinden en dit zonder winstoogmerk. Geef ons uw toestemming door uw naam en email hieronder in te vullen."},
        name: {text: "Naam:"},
        email: {text: "E-mailadres:"},
        phone: {text: "Mobiel nummer:"},
        date:{text: "Foto Datum:"},
        bedrijf: {text: "Tuinbouwbedrijf:"},
        teelt: {text: "Teelt:"},
        desc: {text: "Omschrijving:"},
        address: {text: "Adres:"},
        photographer: {text: "Fotograaf:"},
        bedrijf_desc: {attr: "placeholder",text: "Naam van het tuinbouwbedrijf"},
        teelt_desc: {attr: "placeholder",text: "Teelt waarin het tuinbouwbedrijf gespecialiseerd was of nog is"},
        desc_desc: {attr: "placeholder",text: "Inhoudelijke beschrijving van de foto"},
        foto_desc: {attr: "placeholder",text: "Naam van de fotograaf"},
        uploading: {text: "Opladen van de foto..."},
        take_photo: {text: "Neem de foto terug van onder de scanner en ga naar de volgende tafel waar je een verhaal kan toevoegen aan de foto."},

        wait_audio : {text:"Geen scans gevonden ... Gelieve terug naar tafel 1 te gaan om opnieuw te scannen"},
        start_rec: {text: "In deze stap kan je een verhaal toevoegen aan je foto. Begin met opnemen door op de record knop te duwen of druk op annuleren als u geen verhaal wil/kan toevoegen."},
        finish_audio: {text: "Your audio has been saved. Gelieve terug naar tafel 3 te gaan."},

        wait_loc : {text:"Geen scans gevonden ... Gelieve terug naar tafel 1 te gaan om opnieuw te scannen"},
        place_pin: {text: "Selecteer de locatie waar deze foto genomen werd door op de kaart de locatie aan te klikken of te zoeken op adres via de zoekbalk. Druk vervolgens op OK (indien locatie correct is) of op annuleren."},
        search: {attr: "placeholder", text: "Zoeken..."},
        finish_loc: {text: "Your location has been saved. Bedankt voor je input. Bekijk resultaten op het grote scherm."},

        recenter: {text: "Centreren"},
        route: {text: "Routes"},
        route1:{text:"Wandelkaart - Flaneren door groen Gent"},
        route2:{text:"Fietskaart - Sierteelt in de Gentse Rand"},
        route3:{text: "Fietskaart - Onderwijs en onderzoek"},
        video: {text: "Video"},
        video1:{text:"Video: Stekken van druiven"},
        video2:{text:"Video: Enten van haagbeuk"},
        nearby_images: {text: "Foto's in de buurt"},
        top_images: {text: "Top foto's"},
        info:{text: "Informatie over de foto"},
        visualization: {text: "Interactieve kaart - Flore de Gand"},

        select_img: {text: "Selecteer een foto op je computer, maximum grootte 10MB."},
        drag_drop: {text: "Klik om een bestand te zoeken of sleep een foto naar hier..."},
    },
}
