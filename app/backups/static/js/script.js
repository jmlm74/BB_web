console.log("Script");
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
        let is_archive = url.indexOf('archive_info');

        
        let target_detail = document.querySelector('#archive_detail_col1');
        let target_detail2 = document.querySelector('#archive_detail_col2');

        let button_loader_div = document.querySelector('#button-loader-div');
        
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
                    // suppression du bouton et de l'anim ==> Traitement terminé !
                    button_loader_div.parentElement.removeChild(button_loader_div);
                    
                    if (is_archive != -1){
                        // mise des lignes dans une  textarea <=> Archive Info
                        let my_textarea = document.createElement('textarea');
                        for (const ligne of data2) {
                            my_textarea.value += ligne;
                            my_textarea.value += '\n';
                        }
                        my_textarea.rows = 15
                        my_textarea.cols = 100
                        my_textarea.classList.add("ms-5", "mt-3")
                        target_detail.appendChild(my_textarea);
                    } else {
                        // Select pour restore <=> Archive detail                 
                        let my_div = document.createElement('div');
                        my_div.id = "my_select";
                        my_div.classList.add("ms-5")
                        my_div.classList.add("mt-3")
                        target_detail.appendChild(my_div);
                        let options_array = [];
                        let cprt = 0;
                        for (const ligne of data2){
                            const option = { label: ligne, value: cprt ,customData: 'data-tooltip=ligne'};
                            cprt++;
                            options_array.push(option);
                        };
                        // la mise en forme sexy
                        VirtualSelect.init({
                            ele: '#my_select',
                            options: options_array,
                            multiple: true,
                            tooltipMaxWidth: '800px',
                            dropboxWidth: '500px',
                            keepAlwaysOpen: true
                        });
                        let my_button = document.createElement('button');
                        my_button.innerHTML = "Restore";
                        my_button.classList.add("btn");
                        my_button.classList.add("btn-warning")
                        my_button.classList.add("align-middle")

                        target_detail2.appendChild(my_button);
                    }
                });
            })
            .catch(error => {
                console.log("Erreur" + error);
            })
        }
    }



}
