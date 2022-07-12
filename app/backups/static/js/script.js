console.log("ici");
window.onload = function() {
    console.log("window loaded");
    // decoupe URL
    if ((document.URL.includes("archive_info")) || (document.URL.includes("archive_filter"))){
        let url = window.location.href;
        console.log(url);
        let posit = url.lastIndexOf('/') + 1;
        let repo = url.substring(posit);
        let url_sans_repo = url.substring(0,posit-1);
        posit = url_sans_repo.lastIndexOf('/') + 1;
        let repo_id = url_sans_repo.substring(posit);

        
        let target_detail = document.querySelector('#archive_detail');
        let button_loader_div = document.querySelector('#button-loader-div')
        
        // affichage bouton si affiché (filter)
        if (document.querySelector("#button-loader-div")){ 
            let button_loader = document.querySelector('#button-loader');
            let my_button = document.createElement('button');
            my_button.type="button";
            my_button.classList.add("btn", "btn-primary");
            my_button.textContent="Patientez SVP !"; 
            // target_detail.parentNode.insertBefore(my_button,target_detail)
            button_loader.appendChild(my_button);
            // affichage animation
            let anim_loader = document.querySelector("#anim_loader");
            let my_wrapper = document.createElement('div');
            let my_pulse = document.createElement('div');
            my_wrapper.classList.add("wrapper");
            my_pulse.classList.add("pulse");
            anim_loader.appendChild(my_wrapper);
            my_wrapper.appendChild(my_pulse)
            
            let my_url = ""
            if (document.URL.includes("archive_info")){
                my_url = "/backups/get_list_archive/" + repo_id + "/" + repo
            } else {
                let my_filter = document.querySelector("#my-filter").value
                console.log(my_filter);
                my_url = "/backups/get_list_archive/" + repo_id + "/" + repo + "/" + my_filter
            }
            // Ajax requete
            fetch(my_url)
            .then(response => {
                // Reponse OK mais pas 200 !!!! 
                if (response.status !== 200) {
                    console.log("Erreur RC : " + response.status);
                    return;
                }
                // Recupération datas
                response.json().then(function(data){
                    let data2 = data[0]['data'];
                    if (data2.length === 400){ alert ("Attention - Résultat tronqué à 400 lignes !")} ;
                    // mise des lifgnes dans une  textarea
                    let my_textarea = document.createElement('textarea');
                    for (const ligne of data2) {
                        my_textarea.value += ligne;
                        my_textarea.value += '\n';
                    }
                    my_textarea.rows = 15
                    my_textarea.cols = 100
                    my_textarea.classList.add("ms-5", "mt-3")
                    target_detail.appendChild(my_textarea);
                    // suppression du bouton et de l'anim ==> Traitement terminé !
                    button_loader_div.parentElement.removeChild(button_loader_div)
                })
            })
            .catch(error => {
                console.log("Erreur" + error);
            })
        }
    }



}
