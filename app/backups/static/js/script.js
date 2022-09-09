console.log("Script - Beginning here");
window.onload = function() {
    console.log("window loaded - here");
    /*
    Script chargé des requetetes Ajax de recherche puis affichage des resultats (avec les petits effets)
    Le tronc commun est tout d'abord géré avec les URL.
    L'avancée dans la recherche se fait grace aux div presents ou non dans le DOM (La même page est chargée plusieurs fois) 
    */
    if ((document.URL.includes("archive_info")) || (document.URL.includes("archive_filter"))){
        // decoupe URL
        let url = window.location.href;
        // console.log(url);
        let posit = url.lastIndexOf('/') + 1;
        let repo = url.substring(posit);
        let url_sans_repo = url.substring(0,posit-1);
        posit = url_sans_repo.lastIndexOf('/') + 1;
        let repo_id = url_sans_repo.substring(posit);
        let is_archive = url.indexOf('archive_info');

        // Si existent -> Detail + recherche effectuée -> 2 colonnes Resultat + bouton restore
        let target_detail = document.querySelector('#archive_detail_col1');
        let target_detail2 = document.querySelector('#archive_detail_col2');
        // L'effet graphique de chargement
        let button_loader_div = document.querySelector('#button-loader-div');
        
        /*
        Ici la recherche 
        - Animation (patientez SVP)
        - Ajax (Recherche )
        - Suppression Animation
        - Affichage résultat
        */
        if (button_loader_div){
            // préparation animation
            let button_loader = document.querySelector('#button-loader');
            let my_button = document.createElement('button');
            my_button.type="button";
            my_button.classList.add("btn", "btn-primary");
            my_button.textContent="Patientez SVP !"; 
            button_loader.appendChild(my_button);
            // affichage animation
            let anim_loader = document.querySelector("#anim_loader");
            let my_wrapper = document.createElement('div');
            let my_pulse = document.createElement('div');
            my_wrapper.classList.add("wrapper");
            my_pulse.classList.add("pulse");
            anim_loader.appendChild(my_wrapper);
            my_wrapper.appendChild(my_pulse)
            /* 
            Ajax (Recherche)
            Gestion du filter (presence ou non)
            Le div peut exister meis etre vide (non renseigné dans le form)
            J'ai préféré conserver le test sur le dic puis traité l'existence du "myfilter" apres pour detacher les traitements
                par excran (info et detail)
            */
            let my_url = ""
            if (document.URL.includes("archive_info")){
                my_url = "/backups/get_list_archive/" + repo_id + "/" + repo
            } else {
                let my_filter = document.querySelector("#my-filter").value
                //console.log(my_filter);
                if (my_filter) {
                    my_url = "/backups/get_list_archive/" + repo_id + "/" + repo + "/" + my_filter}
                else {
                    my_url = "/backups/get_list_archive/" + repo_id + "/" + repo
                }
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
                    if (data2.length === 40000){ alert ("Attention - Résultat tronqué à 40000 lignes !")} ;
                    // suppression du bouton et de l'anim ==> Traitement terminé !
                    button_loader_div.parentElement.removeChild(button_loader_div);
                    /*
                    Gestion ecran (detail ou info !!!!)
                    Une simple textarea dans info ou une select (VirtualSelect)
                    */
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
                        // Affichage bouton restore
                        let my_button = document.createElement('button');
                        my_button.innerHTML = "Restore";
                        my_button.classList.add("btn");
                        my_button.classList.add("btn-warning")
                        my_button.classList.add("align-middle")
                        my_button.id = "restore_button"
                        target_detail2.appendChild(my_button);
                        /* 
                        * Click Restore button
                        */
                        my_button.addEventListener('click', () => { 
                            // console.log("VU Click");
                            // recupere les valeurs selectionnées (les indices)
                            const array_index = document.querySelector('#my_select').value;
                            // console.log(array_index);
                            /*
                            Les indices récupérés sont ceux du tableau original 
                            Boucle sur le tableau des indices et recupere la valeur pour la mettre en tableau
                            Met le tableau en JSON.
                            Construit l'URL en mettant en parametre le json
                            Envoi la requete sans rien attendre
                            */
                            let files_to_restore = []
                            for (const index of array_index){
                                const file_to_restore = data2[index];
                                files_to_restore.push(file_to_restore);
                            }
                            // console.log(files_to_restore);
                            let files_json = encodeURIComponent(JSON.stringify(files_to_restore))
                            // console.log(files_json)
                            let my_url =  "/backups/restore/" + repo_id + "/" + repo + "?files=" + files_json
                            // console.log(my_url);
                            fetch(my_url);
                            let msg = "La restore a été lancée sur le serveur de backup ! \n Cela peut prendre quelques minutes \n Les fichiers se trouvent dans /home/partage/taq_partage/restore \n \
et sont donc accessibles depuis n'importe quel serveur !";
                            alert(msg);
                        }, false);
                    }
                });
            })
            .catch(error => {
                console.log("Erreur" + error);
            })
        }
    }



}
